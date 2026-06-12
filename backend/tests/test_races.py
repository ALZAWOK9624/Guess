"""Tests for race CRUD service and API endpoints."""

from datetime import date, datetime

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_admin
from app.main import app
from app.models.horse import Horse
from app.models.race import RaceStatus
from app.schemas.horse import HorseCreate


# --- Override dependencies for admin access ---

async def override_get_admin():
    return type("AdminUser", (), {
        "id": 1,
        "username": "admin",
        "is_admin": True,
    })()


# --- Helpers ---

SAMPLE_HORSE = {
    "name": "Equinox",
    "sex": "牡",
    "age": 4,
    "origin": "日本",
    "sire": "Kitasan Black",
    "damsire": "Dance in the Dark",
    "weight": "520kg",
    "jockey": "C. Lemaire",
    "previous_result": "1着",
    "best_win": "有马纪念(G1)",
}

SAMPLE_HORSE_2 = {"name": "Epiphaneia"}
SAMPLE_HORSE_3 = {"name": "Duramente"}


async def _create_horse(db: AsyncSession, data: dict) -> Horse:
    """Helper: create a horse directly in the DB."""
    horse = Horse(**HorseCreate(**data).model_dump())
    db.add(horse)
    await db.flush()
    await db.refresh(horse)
    return horse


# --- Service Tests ---

class TestRaceService:

    @pytest.mark.asyncio
    async def test_create_race(self, db_session: AsyncSession):
        from app.services.race_service import create_race
        from app.schemas.race import RaceCreate

        h1 = await _create_horse(db_session, SAMPLE_HORSE)
        h2 = await _create_horse(db_session, SAMPLE_HORSE_2)

        data = RaceCreate(
            name="日本德比",
            date=date(2026, 6, 15),
            grade="G1",
            horse_ids=[h1.id, h2.id],
        )
        race = await create_race(db_session, data, creator_id=1)

        assert race.id is not None
        assert race.name == "日本德比"
        assert race.grade.value == "G1"
        assert race.status.value == "voting"
        assert len(race.race_horses) == 2

        # Verify snapshot data
        for rh in race.race_horses:
            assert rh.snapshot_data is not None
            assert rh.snapshot_data["name"] in ["Equinox", "Epiphaneia"]
            assert "sex" in rh.snapshot_data
            assert rh.position is None

        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_create_race_custom_grade(self, db_session: AsyncSession):
        from app.services.race_service import create_race
        from app.schemas.race import RaceCreate, CustomScoring, PenaltyRule

        h1 = await _create_horse(db_session, SAMPLE_HORSE)
        h2 = await _create_horse(db_session, SAMPLE_HORSE_2)

        data = RaceCreate(
            name="自定义测试",
            date=date(2026, 6, 20),
            grade="CUSTOM",
            horse_ids=[h1.id, h2.id],
            custom_scoring=CustomScoring(
                positive_scores=[10, 7, 5, 3, 2, 1],
                penalty_rules=[PenaltyRule(position=-1, points=-5)],
            ),
        )
        race = await create_race(db_session, data, creator_id=1)

        assert race.custom_scoring is not None
        assert race.custom_scoring["positive_scores"] == [10, 7, 5, 3, 2, 1]
        assert race.custom_scoring["penalty_rules"] == [{"position": -1, "points": -5}]

        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_create_race_insufficient_horses(self, db_session: AsyncSession):
        # This validation is handled by Pydantic schema, tested via API
        from app.schemas.race import RaceCreate
        from pydantic import ValidationError

        h1 = await _create_horse(db_session, SAMPLE_HORSE)

        with pytest.raises(ValidationError):
            RaceCreate(
                name="单人比赛",
                date=date(2026, 6, 15),
                grade="G1",
                horse_ids=[h1.id],
            )

        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_get_races(self, db_session: AsyncSession):
        from app.services.race_service import create_race, get_races
        from app.schemas.race import RaceCreate

        h1 = await _create_horse(db_session, SAMPLE_HORSE)
        h2 = await _create_horse(db_session, SAMPLE_HORSE_2)
        h3 = await _create_horse(db_session, SAMPLE_HORSE_3)

        await create_race(db_session, RaceCreate(
            name="Race1", date=date(2026, 6, 15), grade="G1",
            horse_ids=[h1.id, h2.id],
        ), creator_id=1)
        await create_race(db_session, RaceCreate(
            name="Race2", date=date(2026, 6, 20), grade="G2_JPN1",
            horse_ids=[h2.id, h3.id],
        ), creator_id=1)

        races = await get_races(db_session)
        assert len(races) == 2

        # Test status filter
        races_voting = await get_races(db_session, status_filter="voting")
        assert len(races_voting) == 2

        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_get_race(self, db_session: AsyncSession):
        from app.services.race_service import create_race, get_race
        from app.schemas.race import RaceCreate

        h1 = await _create_horse(db_session, SAMPLE_HORSE)
        h2 = await _create_horse(db_session, SAMPLE_HORSE_2)

        created = await create_race(db_session, RaceCreate(
            name="FindMe", date=date(2026, 6, 15), grade="G1",
            horse_ids=[h1.id, h2.id],
        ), creator_id=1)

        found = await get_race(db_session, created.id)
        assert found is not None
        assert found.name == "FindMe"
        assert len(found.race_horses) == 2

        not_found = await get_race(db_session, 9999)
        assert not_found is None

        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_update_race_name(self, db_session: AsyncSession):
        from app.services.race_service import create_race, get_race, update_race
        from app.schemas.race import RaceCreate, RaceUpdate

        h1 = await _create_horse(db_session, SAMPLE_HORSE)
        h2 = await _create_horse(db_session, SAMPLE_HORSE_2)

        created = await create_race(db_session, RaceCreate(
            name="Original", date=date(2026, 6, 15), grade="G1",
            horse_ids=[h1.id, h2.id],
        ), creator_id=1)

        updated = await update_race(db_session, created.id, RaceUpdate(name="Updated"), user_id=1)
        assert updated.name == "Updated"

        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_delete_race(self, db_session: AsyncSession):
        from app.services.race_service import create_race, delete_race, get_race
        from app.schemas.race import RaceCreate
        from sqlalchemy import select

        h1 = await _create_horse(db_session, SAMPLE_HORSE)
        h2 = await _create_horse(db_session, SAMPLE_HORSE_2)

        created = await create_race(db_session, RaceCreate(
            name="DeleteMe", date=date(2026, 6, 15), grade="G1",
            horse_ids=[h1.id, h2.id],
        ), creator_id=1)

        await delete_race(db_session, created.id)

        found = await get_race(db_session, created.id)
        assert found is None

        # Verify cascade delete of race_horses
        from app.models.race import RaceHorse
        result = await db_session.execute(
            select(RaceHorse).where(RaceHorse.race_id == created.id)
        )
        remaining = result.scalars().all()
        assert len(remaining) == 0, "race_horses should be cascade-deleted"

        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_delete_race_settled(self, db_session: AsyncSession):
        from app.services.race_service import create_race, delete_race
        from app.schemas.race import RaceCreate

        h1 = await _create_horse(db_session, SAMPLE_HORSE)
        h2 = await _create_horse(db_session, SAMPLE_HORSE_2)

        created = await create_race(db_session, RaceCreate(
            name="SettledRace", date=date(2026, 6, 15), grade="G1",
            horse_ids=[h1.id, h2.id],
        ), creator_id=1)

        # Manually set status to SETTLED to simulate settled race
        created.status = RaceStatus.SETTLED
        await db_session.flush()

        with pytest.raises(HTTPException) as exc_info:
            await delete_race(db_session, created.id)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail["code"] == "RACE_SETTLED"

        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_delete_race_not_found(self, db_session: AsyncSession):
        from app.services.race_service import delete_race

        with pytest.raises(HTTPException) as exc_info:
            await delete_race(db_session, 99999)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail["code"] == "NOT_FOUND"

        await db_session.rollback()


# --- API Tests ---

class TestRaceAPI:

    @pytest.mark.asyncio
    async def test_list_races_api(self, db_session: AsyncSession):
        from app.services.race_service import create_race
        from app.schemas.race import RaceCreate

        h1 = await _create_horse(db_session, SAMPLE_HORSE)
        h2 = await _create_horse(db_session, SAMPLE_HORSE_2)
        await create_race(db_session, RaceCreate(
            name="API Race", date=date(2026, 6, 15), grade="G1",
            horse_ids=[h1.id, h2.id],
        ), creator_id=1)

        app.dependency_overrides[get_db] = lambda: db_session

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/races")
            assert resp.status_code == 200
            data = resp.json()
            assert "data" in data
            assert len(data["data"]) > 0

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_create_race_api(self, db_session: AsyncSession):
        h1 = await _create_horse(db_session, SAMPLE_HORSE)
        h2 = await _create_horse(db_session, SAMPLE_HORSE_2)

        app.dependency_overrides[get_db] = lambda: db_session
        app.dependency_overrides[get_current_admin] = override_get_admin

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/v1/races", json={
                "name": "API日本德比",
                "date": "2026-06-15",
                "grade": "G1",
                "horse_ids": [h1.id, h2.id],
            })
            assert resp.status_code == 201
            data = resp.json()
            assert data["data"]["name"] == "API日本德比"
            assert data["data"]["grade"] == "G1"
            assert data["data"]["status"] == "voting"
            assert len(data["data"]["horses"]) == 2

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_create_race_custom_api(self, db_session: AsyncSession):
        h1 = await _create_horse(db_session, SAMPLE_HORSE)
        h2 = await _create_horse(db_session, SAMPLE_HORSE_2)

        app.dependency_overrides[get_db] = lambda: db_session
        app.dependency_overrides[get_current_admin] = override_get_admin

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/v1/races", json={
                "name": "自定义API测试",
                "date": "2026-06-20",
                "grade": "CUSTOM",
                "horse_ids": [h1.id, h2.id],
                "custom_scoring": {
                    "positive_scores": [10, 7, 5, 3, 2, 1],
                    "penalty_rules": [{"position": -1, "points": -5}],
                },
            })
            assert resp.status_code == 201
            data = resp.json()
            assert data["data"]["custom_scoring"] is not None
            assert data["data"]["custom_scoring"]["positive_scores"] == [10, 7, 5, 3, 2, 1]

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_race_detail_api(self, db_session: AsyncSession):
        from app.services.race_service import create_race
        from app.schemas.race import RaceCreate

        h1 = await _create_horse(db_session, SAMPLE_HORSE)
        h2 = await _create_horse(db_session, SAMPLE_HORSE_2)

        app.dependency_overrides[get_db] = lambda: db_session
        app.dependency_overrides[get_current_admin] = override_get_admin

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Create
            create_resp = await client.post("/api/v1/races", json={
                "name": "DetailTest",
                "date": "2026-06-15",
                "grade": "G1",
                "horse_ids": [h1.id, h2.id],
            })
            race_id = create_resp.json()["data"]["id"]

            # Get detail
            resp = await client.get(f"/api/v1/races/{race_id}")
            assert resp.status_code == 200
            data = resp.json()["data"]
            assert data["name"] == "DetailTest"
            assert len(data["horses"]) == 2
            # Verify snapshot data
            horse_names = [h["snapshot_data"]["name"] for h in data["horses"]]
            assert "Equinox" in horse_names

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_update_race_api(self, db_session: AsyncSession):
        from app.services.race_service import create_race
        from app.schemas.race import RaceCreate

        h1 = await _create_horse(db_session, SAMPLE_HORSE)
        h2 = await _create_horse(db_session, SAMPLE_HORSE_2)

        app.dependency_overrides[get_db] = lambda: db_session
        app.dependency_overrides[get_current_admin] = override_get_admin

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            create_resp = await client.post("/api/v1/races", json={
                "name": "OldName",
                "date": "2026-06-15",
                "grade": "G1",
                "horse_ids": [h1.id, h2.id],
            })
            race_id = create_resp.json()["data"]["id"]

            # Update
            resp = await client.patch(f"/api/v1/races/{race_id}", json={
                "name": "NewName",
            })
            assert resp.status_code == 200
            assert resp.json()["data"]["name"] == "NewName"

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_delete_race_api(self, db_session: AsyncSession):
        from app.services.race_service import create_race
        from app.schemas.race import RaceCreate

        h1 = await _create_horse(db_session, SAMPLE_HORSE)
        h2 = await _create_horse(db_session, SAMPLE_HORSE_2)

        app.dependency_overrides[get_db] = lambda: db_session
        app.dependency_overrides[get_current_admin] = override_get_admin

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            create_resp = await client.post("/api/v1/races", json={
                "name": "DeleteAPITest",
                "date": "2026-06-15",
                "grade": "G1",
                "horse_ids": [h1.id, h2.id],
            })
            race_id = create_resp.json()["data"]["id"]

            # Delete
            resp = await client.delete(f"/api/v1/races/{race_id}")
            assert resp.status_code == 204

            # Verify deleted
            get_resp = await client.get(f"/api/v1/races/{race_id}")
            assert get_resp.status_code == 404

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_delete_nonexistent_race_api(self, db_session: AsyncSession):
        """DELETE non-existent race → 404."""
        app.dependency_overrides[get_db] = lambda: db_session
        app.dependency_overrides[get_current_admin] = override_get_admin

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.delete("/api/v1/races/99999")
            assert resp.status_code == 404
            data = resp.json()
            assert data["detail"]["code"] == "NOT_FOUND"

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_delete_settled_race_api(self, db_session: AsyncSession):
        """DELETE settled race → 400."""
        from app.services.race_service import create_race
        from app.schemas.race import RaceCreate

        h1 = await _create_horse(db_session, SAMPLE_HORSE)
        h2 = await _create_horse(db_session, SAMPLE_HORSE_2)

        created = await create_race(db_session, RaceCreate(
            name="SettledDelete", date=date(2026, 6, 15), grade="G1",
            horse_ids=[h1.id, h2.id],
        ), creator_id=1)
        created.status = RaceStatus.SETTLED
        await db_session.flush()

        app.dependency_overrides[get_db] = lambda: db_session
        app.dependency_overrides[get_current_admin] = override_get_admin

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.delete(f"/api/v1/races/{created.id}")
            assert resp.status_code == 400
            data = resp.json()
            assert data["detail"]["code"] == "RACE_SETTLED"

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_delete_locked_race_api(self, db_session: AsyncSession):
        """DELETE locked race → 204."""
        from app.services.race_service import create_race
        from app.schemas.race import RaceCreate

        h1 = await _create_horse(db_session, SAMPLE_HORSE)
        h2 = await _create_horse(db_session, SAMPLE_HORSE_2)

        created = await create_race(db_session, RaceCreate(
            name="LockedDelete", date=date(2026, 6, 15), grade="G1",
            horse_ids=[h1.id, h2.id],
        ), creator_id=1)
        created.status = RaceStatus.LOCKED
        await db_session.flush()

        app.dependency_overrides[get_db] = lambda: db_session
        app.dependency_overrides[get_current_admin] = override_get_admin

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.delete(f"/api/v1/races/{created.id}")
            assert resp.status_code == 204

            # Verify deleted
            get_resp = await client.get(f"/api/v1/races/{created.id}")
            assert get_resp.status_code == 404

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_unauthenticated_delete_race_api(self, db_session: AsyncSession):
        """DELETE without admin auth → 401."""
        from app.services.race_service import create_race
        from app.schemas.race import RaceCreate

        h1 = await _create_horse(db_session, SAMPLE_HORSE)
        h2 = await _create_horse(db_session, SAMPLE_HORSE_2)

        created = await create_race(db_session, RaceCreate(
            name="NoAuthDelete", date=date(2026, 6, 15), grade="G1",
            horse_ids=[h1.id, h2.id],
        ), creator_id=1)

        app.dependency_overrides[get_db] = lambda: db_session
        # No admin override → unauthenticated

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.delete(f"/api/v1/races/{created.id}")
            assert resp.status_code == 401

        app.dependency_overrides.clear()
        app.dependency_overrides[get_db] = lambda: db_session
        # No admin override → no auth token

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/v1/races", json={
                "name": "NoAuth",
                "date": "2026-06-15",
                "grade": "G1",
                "horse_ids": [1, 2],
            })
            assert resp.status_code == 401

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_create_race_invalid_data_api(self, db_session: AsyncSession):
        app.dependency_overrides[get_db] = lambda: db_session
        app.dependency_overrides[get_current_admin] = override_get_admin

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Empty name
            resp = await client.post("/api/v1/races", json={
                "name": "",
                "date": "2026-06-15",
                "grade": "G1",
                "horse_ids": [1, 2],
            })
            assert resp.status_code == 422

            # Invalid grade
            resp = await client.post("/api/v1/races", json={
                "name": "Test",
                "date": "2026-06-15",
                "grade": "INVALID",
                "horse_ids": [1, 2],
            })
            assert resp.status_code == 422

            # Single horse
            resp = await client.post("/api/v1/races", json={
                "name": "Test",
                "date": "2026-06-15",
                "grade": "G1",
                "horse_ids": [1],
            })
            assert resp.status_code == 422

        app.dependency_overrides.clear()
