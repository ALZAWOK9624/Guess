"""Leaderboard API endpoint — public ranking data."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import leaderboard_service

router = APIRouter(prefix="/api/v1", tags=["leaderboard"])


@router.get("/leaderboard")
async def get_leaderboard(
    db: AsyncSession = Depends(get_db),
    age_range: list[str] | None = Query(None, description="年龄范围筛选（多选）"),
    sex_restriction: list[str] | None = Query(None, description="性别限定筛选（多选）"),
    race_grade: list[str] | None = Query(None, description="比赛等级筛选（多选）"),
    country: list[str] | None = Query(None, description="国家或地区筛选（多选）"),
    distance_min: int | None = Query(None, description="最小长度（米）"),
    distance_max: int | None = Query(None, description="最大长度（米）"),
    horse_count_min: int | None = Query(None, description="最少参赛马匹数"),
    horse_count_max: int | None = Query(None, description="最多参赛马匹数"),
):
    """Get the global leaderboard sorted by cumulative points descending.

    Supports optional filtering by race tags (age_range, race_grade, etc.)
    and numeric ranges (distance, horse_count). Tag filters support multi-select.

    Public endpoint — no authentication required.
    Returns all users including those with zero settled races.
    """
    entries = await leaderboard_service.get_leaderboard(
        db,
        age_range=age_range,
        sex_restriction=sex_restriction,
        race_grade=race_grade,
        country=country,
        distance_min=distance_min,
        distance_max=distance_max,
        horse_count_min=horse_count_min,
        horse_count_max=horse_count_max,
    )
    return {"data": [e.model_dump() for e in entries]}
