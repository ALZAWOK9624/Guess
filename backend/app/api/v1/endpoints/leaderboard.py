"""Leaderboard API endpoint — public ranking data."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import leaderboard_service

router = APIRouter(prefix="/api/v1", tags=["leaderboard"])


@router.get("/leaderboard")
async def get_leaderboard(
    db: AsyncSession = Depends(get_db),
):
    """Get the global leaderboard sorted by cumulative points descending.

    Public endpoint — no authentication required.
    Returns all users including those with zero settled races.
    """
    entries = await leaderboard_service.get_leaderboard(db)
    return {"data": [e.model_dump() for e in entries]}
