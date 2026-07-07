"""Leaderboard service — aggregated user rankings with tag filters.

Queries Vote.points (directly on the Vote model) to compute
cumulative scores, race counts, and per-race averages.
Supports filtering by race tags, horse count, and distance range.
"""

import sqlalchemy as sa
from sqlalchemy import Numeric, select, func, and_, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.vote import Vote
from app.models.race import Race, RaceHorse
from app.schemas.leaderboard import LeaderboardEntry


async def get_leaderboard(
    db: AsyncSession,
    age_range: list[str] | None = None,
    sex_restriction: list[str] | None = None,
    race_grade: list[str] | None = None,
    country: list[str] | None = None,
    distance_min: int | None = None,
    distance_max: int | None = None,
    horse_count_min: int | None = None,
    horse_count_max: int | None = None,
) -> list[LeaderboardEntry]:
    """Return all users sorted by cumulative points descending.

    Supports filtering by race tags and numeric ranges.
    Filters apply only to settled races with points — users who have
    no qualifying races still appear with 0 values.
    """

    # Build the vote-race join condition with optional filters
    vote_race_join = Vote.race_id == Race.id

    # Race tag filters (applied to the join condition)
    race_filters = [Race.id.isnot(None)]
    if age_range:
        race_filters.append(Race.age_range.in_(age_range))
    if sex_restriction:
        race_filters.append(Race.sex_restriction.in_(sex_restriction))
    if race_grade:
        race_filters.append(Race.race_grade.in_(race_grade))
    if country:
        race_filters.append(Race.country.in_(country))

    # Distance filter: parse numeric part from distance string
    if distance_min is not None or distance_max is not None:
        distance_expr = func.cast(
            func.regexp_replace(Race.distance, '[^0-9]', '', 'g'),
            sa.Integer,
        )
        if distance_min is not None:
            race_filters.append(distance_expr >= distance_min)
        if distance_max is not None:
            race_filters.append(distance_expr <= distance_max)

    # Horse count filter: count race_horses per race using a scalar subquery
    horse_count_subq = (
        select(func.count(RaceHorse.id))
        .where(RaceHorse.race_id == Race.id)
        .correlate(Race)
        .scalar_subquery()
    )
    if horse_count_min is not None:
        race_filters.append(horse_count_subq >= horse_count_min)
    if horse_count_max is not None:
        race_filters.append(horse_count_subq <= horse_count_max)

    # Build the vote join with race filters
    vote_join = (
        Vote.__table__.join(
            Race.__table__,
            and_(vote_race_join, *race_filters),
            isouter=True,
        )
    )

    total_points_col = func.coalesce(func.sum(Vote.points), 0)
    races_col = func.count(func.distinct(Vote.race_id))
    sum_points = func.coalesce(func.sum(Vote.points), 0.0)
    divisor = func.nullif(func.count(func.distinct(Vote.race_id)), 0)
    avg_points_col = func.round(
        sa.cast(sum_points / divisor, Numeric),
        1,
    )

    query = (
        select(
            User.username,
            total_points_col.label("total_points"),
            races_col.label("races_participated"),
            avg_points_col.label("avg_points"),
        )
        .outerjoin(
            vote_join,
            (User.id == Vote.user_id) & Vote.points.isnot(None),
        )
        .group_by(User.id, User.username)
        .order_by(
            total_points_col.desc(),
            avg_points_col.desc(),
        )
    )

    result = await db.execute(query)
    rows = result.all()

    return [
        LeaderboardEntry(
            username=row.username,
            total_points=int(row.total_points or 0),
            races_participated=int(row.races_participated or 0),
            avg_points=float(row.avg_points or 0.0),
        )
        for row in rows
    ]
