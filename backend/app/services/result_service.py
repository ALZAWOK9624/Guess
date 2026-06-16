"""Result entry business logic — drag-sort result submission and settlement."""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.race import Race, RaceHorse, RaceStatus
from app.models.vote import Vote
from app.schemas.result import ResultEntry, ResultPosition, UserScoreItem
from app.services.scoring_engine import calculate_score


async def submit_results(
    db: AsyncSession, race_id: int, data: ResultEntry, current_admin_id: int | None = None
) -> dict:
    """Submit race results — transition from locked to settled.

    If race is already settled, this re-settles (rollback + recalculate).
    All operations happen in a single transaction.
    When re-settling, ScoreChangeLog entries are created for audit trail.
    """
    # Load race with horses and votes eager-loaded
    stmt = (
        select(Race)
        .options(
            selectinload(Race.race_horses),
            selectinload(Race.votes).selectinload(Vote.user),
        )
        .where(Race.id == race_id)
    )
    result = await db.execute(stmt)
    race = result.scalar_one_or_none()

    if race is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "比赛不存在"},
        )

    if race.status == RaceStatus.VOTING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "RACE_NOT_LOCKED",
                "message": "比赛处于投票中状态，请先锁定",
            },
        )

    # Build position lookup: race_horse_id → position
    position_map: dict[int, int] = {}
    for entry in data.positions:
        position_map[entry.race_horse_id] = entry.position

    # Validate all race_horses are accounted for
    race_horse_ids = {rh.id for rh in race.race_horses}
    submitted_ids = set(position_map.keys())

    if submitted_ids != race_horse_ids:
        missing = race_horse_ids - submitted_ids
        extra = submitted_ids - race_horse_ids
        msg_parts = []
        if missing:
            msg_parts.append(f"缺少马匹: {missing}")
        if extra:
            msg_parts.append(f"多余的马匹: {extra}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_POSITIONS",
                "message": "; ".join(msg_parts),
            },
        )

    # Track old points before any modification (for audit log)
    is_resettle = race.status == RaceStatus.SETTLED
    old_points_map: dict[int, int | None] | None = None
    if is_resettle:
        old_points_map = {vote.id: vote.points for vote in race.votes}

    # If already settled, rollback old points first
    if is_resettle:
        for vote in race.votes:
            vote.points = None

    # Update RaceHorse positions
    for rh in race.race_horses:
        rh.position = position_map[rh.id]

    # Calculate active horse count (position > 0)
    active_count = sum(1 for p in position_map.values() if p > 0)

    # Calculate scores for each vote (collect before flush/refresh)
    for vote in race.votes:
        vote_rh = next(
            (rh for rh in race.race_horses if rh.id == vote.race_horse_id),
            None,
        )
        if vote_rh is None:
            vote.points = 0
        elif vote_rh.position is not None and vote_rh.position > 0:
            points = calculate_score(
                grade=race.grade.value,
                total_horses=active_count,
                position=vote_rh.position,
                custom_scoring=race.custom_scoring,
            )
            vote.points = points
        else:
            vote.points = 0

    # Create change log entries for every settlement (track value changes)
    from app.models.change_log import ScoreChangeLog  # late import to avoid circular

    for vote in race.votes:
        old_val = old_points_map.get(vote.id) if old_points_map else None
        new_val = vote.points
        # Only log if value actually changed
        if old_val != new_val:
            log_entry = ScoreChangeLog(
                race_id=race.id,
                vote_id=vote.id,
                user_id=vote.user_id,
                admin_user_id=current_admin_id,
                old_points=old_val,
                new_points=new_val,
            )
            db.add(log_entry)

    # Update race status to settled
    race.status = RaceStatus.SETTLED

    await db.flush()

    # Build response from the already-loaded votes (avoid re-accessing relationships)
    user_scores = []
    for vote in race.votes:
        username = vote.user.username if vote.user else "未知"
        user_scores.append(
            UserScoreItem(
                user_id=vote.user_id,
                username=username,
                points=vote.points if vote.points is not None else 0,
            )
        )

    # TODO(Story 2.5): Call auto_update_service.apply_auto_updates() after settlement.
    # try:
    #     from app.services import auto_update_service
    #     await auto_update_service.apply_auto_updates(db, race_id, horse_updates)
    # except Exception:
    #     import logging
    #     logging.warning("Auto-update failed after settlement (non-blocking)", exc_info=True)

    return {
        "race_id": race.id,
        "status": race.status.value,
        "scores": user_scores,
    }


async def get_race_change_logs(
    db: AsyncSession, race_id: int
) -> dict:
    """Get score change history for a race. Admin-only query."""
    from app.models.change_log import ScoreChangeLog

    stmt = (
        select(ScoreChangeLog)
        .options(
            selectinload(ScoreChangeLog.vote_rel).selectinload(Vote.user),
            selectinload(ScoreChangeLog.admin_user_rel),
        )
        .where(ScoreChangeLog.race_id == race_id)
        .order_by(ScoreChangeLog.created_at.desc())
    )
    result = await db.execute(stmt)
    logs = result.scalars().all()

    # Load race name
    race_stmt = select(Race).where(Race.id == race_id)
    race_result = await db.execute(race_stmt)
    race = race_result.scalar_one_or_none()
    race_name = race.name if race else f"Race #{race_id}"

    entries = []
    for log in logs:
        # Resolve username from vote's user relationship
        vote = log.vote_rel
        username = vote.user.username if vote and vote.user else "未知"
        admin_username = log.admin_user_rel.username if log.admin_user_rel else "未知"
        entries.append(
            {
                "vote_id": log.vote_id,
                "username": username,
                "race_id": log.race_id,
                "old_points": log.old_points,
                "new_points": log.new_points,
                "modified_at": log.created_at.isoformat() if log.created_at else None,
                "admin_username": admin_username,
            }
        )

    return {
        "race_id": race_id,
        "race_name": race_name,
        "changes": entries,
    }
