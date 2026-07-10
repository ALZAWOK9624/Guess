"""Tests for result entry and settlement service."""

from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.change_log import ScoreChangeLog
from app.models.race import Race, RaceHorse, RaceStatus
from app.models.user import User
from app.models.vote import Vote
from app.schemas.result import ResultEntry, ResultPosition
from app.services import result_service


@pytest.fixture
async def seeded_race(db_session: AsyncSession) -> Race:
    """Create a locked race with 4 horses and 2 votes for testing."""
    admin = User(username="admin", password_hash="x", qq="10001", invite_code="AAA", is_admin=True)
    user1 = User(username="user1", password_hash="x", qq="10002", invite_code="BBB")
    user2 = User(username="user2", password_hash="x", qq="10003", invite_code="CCC")
    db_session.add_all([admin, user1, user2])
    await db_session.flush()

    race = Race(
        name="Test Race",
        date=date(2026, 6, 15),
        age_range="其他",
        sex_restriction="无",
        race_grade="G1",
        country="日本",
        distance="1200m",
        surface="草地",
        status=RaceStatus.LOCKED,
        creator_id=admin.id,
    )
    db_session.add(race)
    await db_session.flush()

    horses = []
    for i in range(4):
        rh = RaceHorse(
            race_id=race.id,
            horse_id=i + 1,
            snapshot_data={"name": f"Horse {i + 1}", "jockey": f"Jockey {i + 1}", "weight": "58kg"},
        )
        db_session.add(rh)
        horses.append(rh)
    await db_session.flush()

    # User 1 votes for horse 1, user 2 votes for horse 2
    vote1 = Vote(user_id=user1.id, race_id=race.id, race_horse_id=horses[0].id)
    vote2 = Vote(user_id=user2.id, race_id=race.id, race_horse_id=horses[1].id)
    db_session.add_all([vote1, vote2])
    await db_session.flush()

    # Re-fetch with relationships
    await db_session.refresh(race, ["race_horses", "votes"])

    # Attach users to response context for test assertions
    race._admin = admin
    race._user1 = user1
    race._user2 = user2
    race._horses = horses

    return race


@pytest.mark.asyncio
async def test_submit_results_fresh_settlement(db_session: AsyncSession, seeded_race: Race):
    """Test fresh settlement: locked → settled with correct points."""
    race = seeded_race
    horses = race._horses

    # Positions: Horse 1 = 1st, Horse 2 = 2nd, Horse 3 = 3rd, Horse 4 = 4th
    positions = [
        ResultPosition(race_horse_id=horses[0].id, position=1),
        ResultPosition(race_horse_id=horses[1].id, position=2),
        ResultPosition(race_horse_id=horses[2].id, position=3),
        ResultPosition(race_horse_id=horses[3].id, position=4),
    ]
    data = ResultEntry(positions=positions)

    result = await result_service.submit_results(db_session, race.id, data)

    assert result["status"] == "settled"
    assert len(result["scores"]) == 2

    # Verify race status in DB
    stmt = select(Race).where(Race.id == race.id)
    db_race = (await db_session.execute(stmt)).scalar_one()
    assert db_race.status == RaceStatus.SETTLED

    # Verify positions
    for rh in db_race.race_horses:
        expected_pos = next(p.position for p in positions if p.race_horse_id == rh.id)
        assert rh.position == expected_pos

    # G1 with 4 active horses (no penalty for ≤5): 1st = +10, 2nd = +5, 3rd = +3, 4th = +2
    # User1 voted for Horse 1 (1st) → 10 points
    # User2 voted for Horse 2 (2nd) → 5 points
    stmt = select(Vote).where(Vote.race_id == race.id).order_by(Vote.user_id)
    votes = (await db_session.execute(stmt)).scalars().all()
    assert votes[0].points == 10  # User1
    assert votes[1].points == 5   # User2


@pytest.mark.asyncio
async def test_submit_results_with_dnf(db_session: AsyncSession, seeded_race: Race):
    """Test settlement with a DNF horse."""
    race = seeded_race
    horses = race._horses

    # Horse 4 is DNF (position = 0)
    positions = [
        ResultPosition(race_horse_id=horses[0].id, position=1),
        ResultPosition(race_horse_id=horses[1].id, position=2),
        ResultPosition(race_horse_id=horses[2].id, position=3),
        ResultPosition(race_horse_id=horses[3].id, position=0),  # DNF
    ]
    data = ResultEntry(positions=positions)

    await result_service.submit_results(db_session, race.id, data)

    # Check positions
    stmt = select(Vote).where(Vote.race_id == race.id).order_by(Vote.user_id)
    votes = (await db_session.execute(stmt)).scalars().all()

    # User1 voted for Horse 1 (1st), active horses = 3, G1 with 3 horses = no penalty
    # 1st = 10 points
    assert votes[0].points == 10

    # User2 voted for Horse 2 (2nd), active horses = 3, 2nd = 5 points
    assert votes[1].points == 5


@pytest.mark.asyncio
async def test_submit_results_user_votes_dnf_horse(db_session: AsyncSession, seeded_race: Race):
    """Test user who voted for a DNF horse gets 0 points."""
    race = seeded_race
    horses = race._horses

    # Move user2's vote to horse 4 (which will be DNF)
    user2_id = race._user2.id
    stmt = select(Vote).where(Vote.user_id == user2_id, Vote.race_id == race.id)
    vote2 = (await db_session.execute(stmt)).scalar_one()
    vote2.race_horse_id = horses[3].id
    await db_session.flush()

    # Horse 4 is DNF
    positions = [
        ResultPosition(race_horse_id=horses[0].id, position=1),
        ResultPosition(race_horse_id=horses[1].id, position=2),
        ResultPosition(race_horse_id=horses[2].id, position=3),
        ResultPosition(race_horse_id=horses[3].id, position=0),  # DNF
    ]
    data = ResultEntry(positions=positions)

    await result_service.submit_results(db_session, race.id, data)

    stmt = select(Vote).where(Vote.race_id == race.id).order_by(Vote.user_id)
    votes = (await db_session.execute(stmt)).scalars().all()

    assert votes[0].points == 10  # User1: 1st place, 10 points
    assert votes[1].points == 0   # User2: voted for DNF horse → 0 points


@pytest.mark.asyncio
async def test_submit_results_resettle(db_session: AsyncSession, seeded_race: Race):
    """Test re-settlement of an already settled race."""
    race = seeded_race
    horses = race._horses

    # First settlement
    positions1 = [
        ResultPosition(race_horse_id=horses[0].id, position=1),
        ResultPosition(race_horse_id=horses[1].id, position=2),
        ResultPosition(race_horse_id=horses[2].id, position=3),
        ResultPosition(race_horse_id=horses[3].id, position=4),
    ]
    await result_service.submit_results(db_session, race.id, ResultEntry(positions=positions1))

    # Re-settlement: swap 1st and 2nd
    positions2 = [
        ResultPosition(race_horse_id=horses[0].id, position=2),  # Was 1st, now 2nd
        ResultPosition(race_horse_id=horses[1].id, position=1),  # Was 2nd, now 1st
        ResultPosition(race_horse_id=horses[2].id, position=3),
        ResultPosition(race_horse_id=horses[3].id, position=4),
    ]
    result = await result_service.submit_results(db_session, race.id, ResultEntry(positions=positions2))

    assert result["status"] == "settled"

    # Check recalculated points
    stmt = select(Vote).where(Vote.race_id == race.id).order_by(Vote.user_id)
    votes = (await db_session.execute(stmt)).scalars().all()

    # User1 voted for Horse 1 (now 2nd) → 5 points
    assert votes[0].points == 5
    # User2 voted for Horse 2 (now 1st) → 10 points
    assert votes[1].points == 10


@pytest.mark.asyncio
async def test_submit_results_voting_race_rejected(db_session: AsyncSession):
    """Test that submitting results for a voting race returns error."""
    admin = User(username="admin2", password_hash="x", qq="20001", invite_code="DDD", is_admin=True)
    db_session.add(admin)
    await db_session.flush()

    race = Race(
        name="Voting Race",
        date=date(2026, 6, 15),
        age_range="其他",
        sex_restriction="无",
        race_grade="G1",
        country="日本",
        distance="1200m",
        surface="草地",
        status=RaceStatus.VOTING,
        creator_id=admin.id,
    )
    db_session.add(race)
    await db_session.flush()

    data = ResultEntry(positions=[ResultPosition(race_horse_id=999, position=1)])

    with pytest.raises(Exception) as exc_info:
        await result_service.submit_results(db_session, race.id, data)

    # Should raise an HTTPException with 400 status
    assert "RACE_NOT_LOCKED" in str(exc_info.value) or "400" in str(exc_info.value)


@pytest.mark.asyncio
async def test_submit_results_race_not_found(db_session: AsyncSession):
    """Test that submitting results for a non-existent race returns error."""
    data = ResultEntry(positions=[ResultPosition(race_horse_id=1, position=1)])

    with pytest.raises(Exception) as exc_info:
        await result_service.submit_results(db_session, 99999, data)

    assert "NOT_FOUND" in str(exc_info.value) or "404" in str(exc_info.value)


@pytest.mark.asyncio
async def test_submit_results_duplicate_positions_rejected(db_session: AsyncSession, seeded_race: Race):
    """Test that duplicate positive positions are rejected."""
    race = seeded_race
    horses = race._horses

    positions = [
        ResultPosition(race_horse_id=horses[0].id, position=1),
        ResultPosition(race_horse_id=horses[1].id, position=1),  # Duplicate!
        ResultPosition(race_horse_id=horses[2].id, position=3),
        ResultPosition(race_horse_id=horses[3].id, position=4),
    ]

    with pytest.raises(Exception) as exc_info:
        # This should fail at validation in the schema
        ResultEntry(positions=positions)

    assert "Duplicate" in str(exc_info.value) or "duplicate" in str(exc_info.value)


@pytest.mark.asyncio
async def test_submit_results_endpoint_integration(
    db_session: AsyncSession, async_client: AsyncClient, seeded_race: Race
):
    """Integration test for the PUT endpoint."""
    race = seeded_race
    horses = race._horses

    # Override auth to return admin — use app directly
    from app.api.deps import get_current_admin
    from app.main import app
    async def override_admin():
        return race._admin

    app.dependency_overrides[get_current_admin] = override_admin
    try:
        payload = {
            "positions": [
                {"race_horse_id": horses[0].id, "position": 1},
                {"race_horse_id": horses[1].id, "position": 2},
                {"race_horse_id": horses[2].id, "position": 3},
                {"race_horse_id": horses[3].id, "position": 4},
            ]
        }
        resp = await async_client.put(f"/api/v1/races/{race.id}/results", json=payload)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["status"] == "settled"
        assert len(data["scores"]) == 2
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_resettle_with_audit_log(db_session: AsyncSession, seeded_race: Race):
    """Test that re-settlement creates ScoreChangeLog audit entries."""
    race = seeded_race
    horses = race._horses
    admin_id = race._admin.id

    # First settlement
    positions1 = [
        ResultPosition(race_horse_id=horses[0].id, position=1),
        ResultPosition(race_horse_id=horses[1].id, position=2),
        ResultPosition(race_horse_id=horses[2].id, position=3),
        ResultPosition(race_horse_id=horses[3].id, position=4),
    ]
    await result_service.submit_results(db_session, race.id, ResultEntry(positions=positions1), current_admin_id=admin_id)

    # Check first settlement created log entries (old_points=NULL → new_points=value)
    stmt = select(ScoreChangeLog).where(ScoreChangeLog.race_id == race.id).order_by(ScoreChangeLog.id)
    logs = (await db_session.execute(stmt)).scalars().all()
    assert len(logs) == 2  # 2 votes
    assert logs[0].old_points is None  # first settlement
    assert logs[0].new_points == 10  # User1: 1st place
    assert logs[1].old_points is None
    assert logs[1].new_points == 5   # User2: 2nd place
    assert logs[0].admin_user_id == admin_id

    # Re-settlement: swap 1st and 2nd
    positions2 = [
        ResultPosition(race_horse_id=horses[0].id, position=2),
        ResultPosition(race_horse_id=horses[1].id, position=1),
        ResultPosition(race_horse_id=horses[2].id, position=3),
        ResultPosition(race_horse_id=horses[3].id, position=4),
    ]
    await result_service.submit_results(db_session, race.id, ResultEntry(positions=positions2), current_admin_id=admin_id)

    # Check re-settlement created new log entries
    stmt = select(ScoreChangeLog).where(ScoreChangeLog.race_id == race.id).order_by(ScoreChangeLog.id)
    logs = (await db_session.execute(stmt)).scalars().all()
    assert len(logs) == 4  # 2 (first) + 2 (re-settlement)

    # Re-settlement logs: old points captured before modification
    assert logs[2].old_points == 10
    assert logs[2].new_points == 5   # User1: was 1st(+10), now 2nd(+5)
    assert logs[3].old_points == 5
    assert logs[3].new_points == 10  # User2: was 2nd(+5), now 1st(+10)
    assert logs[2].admin_user_id == admin_id
    assert logs[3].admin_user_id == admin_id


@pytest.mark.asyncio
async def test_resettle_no_change_no_log(db_session: AsyncSession, seeded_race: Race):
    """Test that identical positions do not create new log entries."""
    race = seeded_race
    horses = race._horses
    admin_id = race._admin.id

    # First settlement
    positions = [
        ResultPosition(race_horse_id=horses[0].id, position=1),
        ResultPosition(race_horse_id=horses[1].id, position=2),
        ResultPosition(race_horse_id=horses[2].id, position=3),
        ResultPosition(race_horse_id=horses[3].id, position=4),
    ]
    data = ResultEntry(positions=positions)
    await result_service.submit_results(db_session, race.id, data, current_admin_id=admin_id)

    # First settlement should have 2 log entries
    stmt = select(ScoreChangeLog).where(ScoreChangeLog.race_id == race.id)
    logs_after_first = (await db_session.execute(stmt)).scalars().all()
    assert len(logs_after_first) == 2

    # Re-submit SAME positions — no actual points change
    await result_service.submit_results(db_session, race.id, data, current_admin_id=admin_id)

    # No additional log entries (old == new, so skipped)
    stmt = select(ScoreChangeLog).where(ScoreChangeLog.race_id == race.id)
    logs_after_second = (await db_session.execute(stmt)).scalars().all()
    assert len(logs_after_second) == 2  # Unchanged


@pytest.mark.asyncio
async def test_resettle_multiple_rounds(db_session: AsyncSession, seeded_race: Race):
    """Test that 3+ modifications are all recorded correctly."""
    race = seeded_race
    horses = race._horses
    admin_id = race._admin.id

    # Round 1: settle
    await result_service.submit_results(
        db_session, race.id,
        ResultEntry(positions=[
            ResultPosition(race_horse_id=horses[0].id, position=1),
            ResultPosition(race_horse_id=horses[1].id, position=2),
            ResultPosition(race_horse_id=horses[2].id, position=3),
            ResultPosition(race_horse_id=horses[3].id, position=4),
        ]),
        current_admin_id=admin_id,
    )

    # Round 2: swap 1 and 2
    await result_service.submit_results(
        db_session, race.id,
        ResultEntry(positions=[
            ResultPosition(race_horse_id=horses[0].id, position=2),
            ResultPosition(race_horse_id=horses[1].id, position=1),
            ResultPosition(race_horse_id=horses[2].id, position=3),
            ResultPosition(race_horse_id=horses[3].id, position=4),
        ]),
        current_admin_id=admin_id,
    )

    # Round 3: swap 3 and 4
    await result_service.submit_results(
        db_session, race.id,
        ResultEntry(positions=[
            ResultPosition(race_horse_id=horses[0].id, position=2),
            ResultPosition(race_horse_id=horses[1].id, position=1),
            ResultPosition(race_horse_id=horses[2].id, position=4),
            ResultPosition(race_horse_id=horses[3].id, position=3),
        ]),
        current_admin_id=admin_id,
    )

    # Only voted horses matter for log entries: user1→horse0, user2→horse1
    # Round 1: 2 entries (first settlement), Round 2: 2 entries (swap 1↔2)
    # Round 3: horses[2]↔horses[3] swap, but no votes for those → no new entries
    stmt = select(ScoreChangeLog).where(ScoreChangeLog.race_id == race.id).order_by(ScoreChangeLog.id)
    logs = (await db_session.execute(stmt)).scalars().all()
    assert len(logs) == 4  # Only first 2 rounds had changes for voted horses


@pytest.mark.asyncio
async def test_resettle_dnf_change(db_session: AsyncSession, seeded_race: Race):
    """Test re-settlement involving DNF position changes."""
    race = seeded_race
    horses = race._horses
    admin_id = race._admin.id

    # First settlement: Horse 1=1st, Horse 2=2nd, Horse 3=3rd, Horse 4=4th
    await result_service.submit_results(
        db_session, race.id,
        ResultEntry(positions=[
            ResultPosition(race_horse_id=horses[0].id, position=1),
            ResultPosition(race_horse_id=horses[1].id, position=2),
            ResultPosition(race_horse_id=horses[2].id, position=3),
            ResultPosition(race_horse_id=horses[3].id, position=4),
        ]),
        current_admin_id=admin_id,
    )

    # Re-settlement: Horse 4 becomes DNF (position=0)
    # Horse 1=1st, Horse 2=2nd, Horse 3=3rd, Horse 4=DNF
    await result_service.submit_results(
        db_session, race.id,
        ResultEntry(positions=[
            ResultPosition(race_horse_id=horses[0].id, position=1),
            ResultPosition(race_horse_id=horses[1].id, position=2),
            ResultPosition(race_horse_id=horses[2].id, position=3),
            ResultPosition(race_horse_id=horses[3].id, position=0),  # Now DNF
        ]),
        current_admin_id=admin_id,
    )

    # Check votes after re-settlement
    stmt = select(Vote).where(Vote.race_id == race.id).order_by(Vote.user_id)
    votes = (await db_session.execute(stmt)).scalars().all()

    # User1 voted for Horse 1 (1st, 3 active horses) → 10 points
    assert votes[0].points == 10
    # User2 voted for Horse 2 (2nd, 3 active horses) → 5 points
    assert votes[1].points == 5

    # Check log entries: first settlement (2 entries) + re-settlement
    # Re-settlement: user1 same (10→10, no change), user2 same (5→5, no change)
    # So no new log entries for re-settlement
    stmt = select(ScoreChangeLog).where(ScoreChangeLog.race_id == race.id)
    logs = (await db_session.execute(stmt)).scalars().all()
    assert len(logs) == 2  # Only first settlement logs


@pytest.mark.asyncio
async def test_resettle_log_without_admin_id(db_session: AsyncSession, seeded_race: Race):
    """Test that re-settlement logs are created even without admin_id for backward compat."""
    race = seeded_race
    horses = race._horses

    # First settlement WITHOUT admin_id
    positions1 = [
        ResultPosition(race_horse_id=horses[0].id, position=1),
        ResultPosition(race_horse_id=horses[1].id, position=2),
        ResultPosition(race_horse_id=horses[2].id, position=3),
        ResultPosition(race_horse_id=horses[3].id, position=4),
    ]
    await result_service.submit_results(db_session, race.id, ResultEntry(positions=positions1))
    # First settlement creates logs (old_points=NULL) even without admin_id
    stmt = select(ScoreChangeLog).where(ScoreChangeLog.race_id == race.id).order_by(ScoreChangeLog.id)
    logs = (await db_session.execute(stmt)).scalars().all()
    assert len(logs) == 2
    assert logs[0].old_points is None  # First settlement: old=NULL
    assert logs[0].new_points == 10
    assert logs[0].admin_user_id is None  # No admin_id provided

    # Re-settlement WITHOUT admin_id
    positions2 = [
        ResultPosition(race_horse_id=horses[0].id, position=2),
        ResultPosition(race_horse_id=horses[1].id, position=1),
        ResultPosition(race_horse_id=horses[2].id, position=3),
        ResultPosition(race_horse_id=horses[3].id, position=4),
    ]
    await result_service.submit_results(db_session, race.id, ResultEntry(positions=positions2))

    # Re-settlement adds 2 more log entries (total = 4)
    stmt = select(ScoreChangeLog).where(ScoreChangeLog.race_id == race.id).order_by(ScoreChangeLog.id)
    logs = (await db_session.execute(stmt)).scalars().all()
    assert len(logs) == 4
    assert logs[2].old_points == 10
    assert logs[2].new_points == 5
    assert logs[2].admin_user_id is None  # No admin_id provided
    assert logs[3].old_points == 5
    assert logs[3].new_points == 10
    assert logs[3].admin_user_id is None


@pytest.mark.asyncio
async def test_resettle_zero_votes(db_session: AsyncSession):
    """Test re-settlement when a race has no votes."""
    admin = User(username="admin_zero", password_hash="x", qq="30001", invite_code="ZZZ", is_admin=True)
    db_session.add(admin)
    await db_session.flush()

    race = Race(
        name="Zero Vote Race", date=date(2026, 7, 1),
        age_range="其他", sex_restriction="无", race_grade="G1", country="日本", distance="1200m", surface="草地",
        status=RaceStatus.LOCKED, creator_id=admin.id,
    )
    db_session.add(race)
    await db_session.flush()

    horses = []
    for i in range(3):
        rh = RaceHorse(
            race_id=race.id, horse_id=i + 100,
            snapshot_data={"name": f"Horse {i + 1}"},
        )
        db_session.add(rh)
        horses.append(rh)
    await db_session.flush()

    # Settle (no votes)
    positions = [
        ResultPosition(race_horse_id=horses[0].id, position=1),
        ResultPosition(race_horse_id=horses[1].id, position=2),
        ResultPosition(race_horse_id=horses[2].id, position=3),
    ]
    result = await result_service.submit_results(db_session, race.id, ResultEntry(positions=positions), current_admin_id=admin.id)
    assert result["status"] == "settled"
    assert len(result["scores"]) == 0  # No votes → no scores

    # Re-settle (still no votes)
    positions2 = [
        ResultPosition(race_horse_id=horses[0].id, position=3),
        ResultPosition(race_horse_id=horses[1].id, position=2),
        ResultPosition(race_horse_id=horses[2].id, position=1),
    ]
    result2 = await result_service.submit_results(db_session, race.id, ResultEntry(positions=positions2), current_admin_id=admin.id)
    assert result2["status"] == "settled"

    # No log entries (no votes → no changes to log)
    stmt = select(ScoreChangeLog).where(ScoreChangeLog.race_id == race.id)
    logs = (await db_session.execute(stmt)).scalars().all()
    assert len(logs) == 0


@pytest.mark.asyncio
async def test_resettle_all_dnf(db_session: AsyncSession, seeded_race: Race):
    """Test re-settlement where all horses are DNF."""
    race = seeded_race
    horses = race._horses
    admin_id = race._admin.id

    # First settlement: Horse 1=1st, Horse 2=2nd, Horse 3=3rd, Horse 4=4th
    await result_service.submit_results(
        db_session, race.id,
        ResultEntry(positions=[
            ResultPosition(race_horse_id=horses[0].id, position=1),
            ResultPosition(race_horse_id=horses[1].id, position=2),
            ResultPosition(race_horse_id=horses[2].id, position=3),
            ResultPosition(race_horse_id=horses[3].id, position=4),
        ]),
        current_admin_id=admin_id,
    )

    # Re-settlement: All horses DNF (position=0)
    await result_service.submit_results(
        db_session, race.id,
        ResultEntry(positions=[
            ResultPosition(race_horse_id=horses[0].id, position=0),
            ResultPosition(race_horse_id=horses[1].id, position=0),
            ResultPosition(race_horse_id=horses[2].id, position=0),
            ResultPosition(race_horse_id=horses[3].id, position=0),
        ]),
        current_admin_id=admin_id,
    )

    # All votes now get 0 points (DNF → 0 points)
    stmt = select(Vote).where(Vote.race_id == race.id).order_by(Vote.user_id)
    votes = (await db_session.execute(stmt)).scalars().all()
    assert votes[0].points == 0  # User1: DNF horse → 0
    assert votes[1].points == 0  # User2: DNF horse → 0

    # Log entries: first settlement (2) + re-settlement (2) = 4
    stmt = select(ScoreChangeLog).where(ScoreChangeLog.race_id == race.id).order_by(ScoreChangeLog.id)
    logs = (await db_session.execute(stmt)).scalars().all()
    assert len(logs) == 4
    # Re-settlement entries: from 10→0 and 5→0
    assert logs[2].old_points == 10
    assert logs[2].new_points == 0
    assert logs[3].old_points == 5
    assert logs[3].new_points == 0
