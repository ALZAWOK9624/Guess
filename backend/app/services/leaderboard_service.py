"""Leaderboard service — aggregated user rankings.

Queries Vote.points (directly on the Vote model) to compute
cumulative scores, race counts, and per-race averages.
"""

import sqlalchemy as sa
from sqlalchemy import Numeric, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.vote import Vote
from app.schemas.leaderboard import LeaderboardEntry


async def get_leaderboard(db: AsyncSession) -> list[LeaderboardEntry]:
    """Return all users sorted by cumulative points descending.

    All users appear in the result — those with zero settled races
    show 0 points / 0 races / 0.0 avg. The LEFT JOIN with a
    'points IS NOT NULL' condition ensures unsettled votes are
    excluded from aggregation.
    """
    total_points_col = func.coalesce(func.sum(Vote.points), 0)
    races_col = func.count(func.distinct(Vote.race_id))
    # Cast to NUMERIC so round(numeric, integer) works in PostgreSQL
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
        .outerjoin(Vote, (User.id == Vote.user_id) & Vote.points.isnot(None))
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
