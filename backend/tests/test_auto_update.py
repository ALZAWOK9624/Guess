"""Tests for auto-update framework (Story 2.5).

Covers:
- HorseAutoUpdateLog model: create and query
- auto_update_service.apply_auto_updates: core logic with manual-edit protection
- horse_service.update_horse: manual edit tracking
- horse_service.reset_auto_protection: protection list reset
- API endpoints: reset-auto-protection
"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_admin
from app.main import app
from app.models.auto_update import HorseAutoUpdateLog
from app.models.horse import Horse
from app.schemas.horse import HorseCreate, HorseUpdate


# --- Override dependencies for admin access ---

async def override_get_admin():
    return {"username": "admin", "is_admin": True}


# --- Test Data ---

SAMPLE_HORSE = {"name": "Equinox", "sex": "牡", "age": 4, "origin": "日本"}
SAMPLE_HORSE_2 = {"name": "Epiphaneia", "sex": "牡", "age": 3}


# --- Helpers ---

async def _create_horse(db: AsyncSession, data: dict) -> Horse:
    from app.services.horse_service import create_horse
    horse_data = HorseCreate(**data)
    return await create_horse(db, horse_data)


# ============================================================
# Service Tests: auto_update_service.apply_auto_updates
# ============================================================

class TestAutoUpdateService:

    @pytest.mark.asyncio
    async def test_apply_auto_updates_normal(self, db_session: AsyncSession):
        """Normal update: field not in manual protection → updated + log created."""
        from app.services.auto_update_service import apply_auto_updates

        horse = await _create_horse(db_session, {"name": "TestHorse", "age": 4})
        assert horse.age == 4
        assert horse.manually_updated_fields is None

        logs = await apply_auto_updates(
            db_session, race_id=1, horse_updates={horse.id: {"age": 5, "sex": "牝"}}
        )

        # Verify horse was updated
        await db_session.refresh(horse)
        assert horse.age == 5
        assert horse.sex == "牝"

        # Verify logs created
        assert len(logs) == 2
        log_field_names = {l.field_name for l in logs}
        assert log_field_names == {"age", "sex"}
        for log in logs:
            assert log.horse_id == horse.id
            assert log.race_id == 1
            assert log.trigger_source == "settlement"
        # Verify old/new values
        age_log = [l for l in logs if l.field_name == "age"][0]
        assert age_log.old_value == "4"
        assert age_log.new_value == "5"

    @pytest.mark.asyncio
    async def test_apply_auto_updates_skips_manual(self, db_session: AsyncSession):
        """Protected field: in manually_updated_fields → skipped, no log."""
        from app.services.auto_update_service import apply_auto_updates

        horse = await _create_horse(db_session, {"name": "SkipMe", "age": 3})
        horse.manually_updated_fields = ["age"]
        await db_session.flush()

        logs = await apply_auto_updates(
            db_session, race_id=1, horse_updates={horse.id: {"age": 10, "sex": "牡"}}
        )

        # Verify age was NOT updated (protected), sex was updated (not protected)
        await db_session.refresh(horse)
        assert horse.age == 3  # Unchanged
        assert horse.sex == "牡"  # Updated

        # Only sex should have a log
        assert len(logs) == 1
        assert logs[0].field_name == "sex"

    @pytest.mark.asyncio
    async def test_apply_auto_updates_mixed(self, db_session: AsyncSession):
        """Mixed: some fields protected, others not."""
        from app.services.auto_update_service import apply_auto_updates

        horse = await _create_horse(db_session, {"name": "Mixed", "age": 5, "sex": "牡", "origin": "日本"})
        horse.manually_updated_fields = ["age", "origin"]
        await db_session.flush()

        logs = await apply_auto_updates(
            db_session, race_id=1,
            horse_updates={horse.id: {"age": 99, "origin": "USA", "sex": "牝"}}
        )

        await db_session.refresh(horse)
        assert horse.age == 5   # Protected
        assert horse.origin == "日本"  # Protected
        assert horse.sex == "牝"  # Updated

        assert len(logs) == 1
        assert logs[0].field_name == "sex"

    @pytest.mark.asyncio
    async def test_apply_auto_updates_empty_input(self, db_session: AsyncSession):
        """Empty horse_updates → empty return, no changes."""
        from app.services.auto_update_service import apply_auto_updates

        logs = await apply_auto_updates(db_session, race_id=1, horse_updates={})
        assert logs == []

    @pytest.mark.asyncio
    async def test_apply_auto_updates_nonexistent_horse(self, db_session: AsyncSession):
        """Non-existent horse_id → 404."""
        from app.services.auto_update_service import apply_auto_updates
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc:
            await apply_auto_updates(
                db_session, race_id=1, horse_updates={9999: {"age": 5}}
            )
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_apply_auto_updates_to_null(self, db_session: AsyncSession):
        """Setting a field to None should work and log correctly."""
        from app.services.auto_update_service import apply_auto_updates

        horse = await _create_horse(db_session, {"name": "NullTest", "age": 4, "sex": "牡"})

        logs = await apply_auto_updates(
            db_session, race_id=1, horse_updates={horse.id: {"sex": None}}
        )

        await db_session.refresh(horse)
        assert horse.sex is None

        assert len(logs) == 1
        assert logs[0].field_name == "sex"
        assert logs[0].old_value == "牡"
        assert logs[0].new_value is None


# ============================================================
# Service Tests: horse_service.update_horse manual tracking
# ============================================================

class TestHorseManualEditTracking:

    @pytest.mark.asyncio
    async def test_update_tracks_single_field(self, db_session: AsyncSession):
        from app.services.horse_service import create_horse, update_horse

        horse = await create_horse(db_session, HorseCreate(name="TrackMe"))
        assert horse.manually_updated_fields is None

        updated = await update_horse(
            db_session, horse.id, HorseUpdate(age=5)
        )
        assert updated.manually_updated_fields == ["age"]

    @pytest.mark.asyncio
    async def test_update_tracks_multiple_fields(self, db_session: AsyncSession):
        from app.services.horse_service import create_horse, update_horse

        horse = await create_horse(db_session, HorseCreate(name="Multi"))
        updated = await update_horse(
            db_session, horse.id, HorseUpdate(age=4, sex="牡", origin="日本")
        )
        assert sorted(updated.manually_updated_fields) == sorted(["age", "sex", "origin"])

    @pytest.mark.asyncio
    async def test_update_no_duplicate_marks(self, db_session: AsyncSession):
        from app.services.horse_service import create_horse, update_horse

        horse = await create_horse(db_session, HorseCreate(name="Dedup"))
        await update_horse(db_session, horse.id, HorseUpdate(age=5))
        updated = await update_horse(db_session, horse.id, HorseUpdate(age=6))

        assert len(updated.manually_updated_fields) == 1
        assert updated.manually_updated_fields == ["age"]

    @pytest.mark.asyncio
    async def test_update_does_not_track_name_change(self, db_session: AsyncSession):
        """Name changes should NOT be tracked as manual edits (name is identity, not auto-updatable)."""
        from app.services.horse_service import create_horse, update_horse

        horse = await create_horse(db_session, HorseCreate(name="Original"))
        updated = await update_horse(db_session, horse.id, HorseUpdate(name="Renamed"))
        assert updated.manually_updated_fields is None or len(updated.manually_updated_fields) == 0

    @pytest.mark.asyncio
    async def test_update_appends_to_existing_protection(self, db_session: AsyncSession):
        from app.services.horse_service import create_horse, update_horse

        horse = await create_horse(db_session, HorseCreate(name="Append"))
        horse.manually_updated_fields = ["age"]
        await db_session.flush()

        updated = await update_horse(db_session, horse.id, HorseUpdate(sex="牡"))
        assert "age" in updated.manually_updated_fields
        assert "sex" in updated.manually_updated_fields
        assert len(updated.manually_updated_fields) == 2

    @pytest.mark.asyncio
    async def test_update_to_null_tracks_field(self, db_session: AsyncSession):
        """Setting a field to None should also be tracked as manual edit."""
        from app.services.horse_service import create_horse, update_horse

        horse = await create_horse(db_session, HorseCreate(name="NullTrack", sex="牡"))
        updated = await update_horse(db_session, horse.id, HorseUpdate(sex=None))

        assert "sex" in updated.manually_updated_fields
        assert updated.sex is None


# ============================================================
# Service Tests: reset_auto_protection
# ============================================================

class TestResetAutoProtection:

    @pytest.mark.asyncio
    async def test_reset_clears_protection(self, db_session: AsyncSession):
        from app.services.horse_service import create_horse, reset_auto_protection

        horse = await create_horse(db_session, HorseCreate(name="ResetMe", age=4))
        horse.manually_updated_fields = ["age"]
        await db_session.flush()

        result = await reset_auto_protection(db_session, horse.id)
        assert result.manually_updated_fields is None

    @pytest.mark.asyncio
    async def test_reset_on_clean_horse(self, db_session: AsyncSession):
        """Reset on horse with no protection → idempotent, no error."""
        from app.services.horse_service import create_horse, reset_auto_protection

        horse = await create_horse(db_session, HorseCreate(name="CleanReset"))
        result = await reset_auto_protection(db_session, horse.id)
        assert result.manually_updated_fields is None

    @pytest.mark.asyncio
    async def test_reset_nonexistent_horse(self, db_session: AsyncSession):
        from app.services.horse_service import reset_auto_protection
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc:
            await reset_auto_protection(db_session, 9999)
        assert exc.value.status_code == 404


# ============================================================
# API Tests: reset-auto-protection endpoint
# ============================================================

class TestResetAutoProtectionAPI:

    @pytest.mark.asyncio
    async def test_reset_api_admin(self, db_session: AsyncSession):
        """Admin can reset auto protection."""
        from app.services.horse_service import create_horse

        app.dependency_overrides[get_db] = lambda: db_session
        app.dependency_overrides[get_current_admin] = override_get_admin

        horse = await create_horse(db_session, HorseCreate(name="APIReset", age=5))
        horse.manually_updated_fields = ["age"]
        await db_session.flush()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(f"/api/v1/horses/{horse.id}/reset-auto-protection")
            assert resp.status_code == 200
            data = resp.json()
            assert "data" in data
            # horse should be returned
            assert data["data"]["name"] == "APIReset"
            # manually_updated_fields should be in response (decision: exposed)
            assert "manually_updated_fields" in data["data"]
            assert data["data"]["manually_updated_fields"] is None

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_reset_api_no_auth(self, db_session: AsyncSession):
        """Non-admin → 401."""
        from app.services.horse_service import create_horse

        app.dependency_overrides[get_db] = lambda: db_session
        # Do NOT override get_current_admin

        horse = await create_horse(db_session, HorseCreate(name="NoAuthReset"))

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(f"/api/v1/horses/{horse.id}/reset-auto-protection")
            assert resp.status_code == 401

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_reset_api_not_found(self, db_session: AsyncSession):
        """Non-existent horse_id → 404."""
        app.dependency_overrides[get_db] = lambda: db_session
        app.dependency_overrides[get_current_admin] = override_get_admin

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/v1/horses/9999/reset-auto-protection")
            assert resp.status_code == 404

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_reset_api_idempotent(self, db_session: AsyncSession):
        """Resetting a horse with no protection is idempotent."""
        from app.services.horse_service import create_horse

        app.dependency_overrides[get_db] = lambda: db_session
        app.dependency_overrides[get_current_admin] = override_get_admin

        horse = await create_horse(db_session, HorseCreate(name="IdempotentReset"))

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(f"/api/v1/horses/{horse.id}/reset-auto-protection")
            assert resp.status_code == 200

        app.dependency_overrides.clear()


# ============================================================
# Model Tests: HorseAutoUpdateLog
# ============================================================

class TestHorseAutoUpdateLogModel:

    @pytest.mark.asyncio
    async def test_create_log_entry(self, db_session: AsyncSession):
        horse = await _create_horse(db_session, {"name": "LogHorse"})

        log = HorseAutoUpdateLog(
            horse_id=horse.id,
            race_id=42,
            field_name="age",
            old_value="4",
            new_value="5",
            trigger_source="settlement",
        )
        db_session.add(log)
        await db_session.flush()
        await db_session.refresh(log)

        assert log.id is not None
        assert log.horse_id == horse.id
        assert log.race_id == 42
        assert log.field_name == "age"
        assert log.old_value == "4"
        assert log.new_value == "5"
        assert log.trigger_source == "settlement"
        assert log.created_at is not None

    @pytest.mark.asyncio
    async def test_create_log_null_values(self, db_session: AsyncSession):
        horse = await _create_horse(db_session, {"name": "NullLog"})

        log = HorseAutoUpdateLog(
            horse_id=horse.id,
            race_id=None,
            field_name="sex",
            old_value=None,
            new_value="牡",
            trigger_source="settlement",
        )
        db_session.add(log)
        await db_session.flush()
        await db_session.refresh(log)

        assert log.race_id is None
        assert log.old_value is None
