"""Race API endpoints — CRUD for race management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.models.race import RaceStatus
from app.schemas.race import (
    CustomScoring,
    RaceCreate,
    RaceDetailResponse,
    RaceListResponse,
    RaceUpdate,
)
from app.services import race_service, vote_service

router = APIRouter(prefix="/api/v1/races", tags=["races"])


@router.get("")
async def list_races(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all races. Supports optional ?status=xxx filter. Public endpoint."""
    races = await race_service.get_races(db, status)
    items = []
    for race in races:
        vc = await race_service.get_race_vote_count(db, race.id)
        items.append(RaceListResponse(
            id=race.id,
            name=race.name,
            date=race.date,
            grade=race.grade.value,
            status=race.status.value,
            custom_scoring=CustomScoring(**race.custom_scoring) if race.custom_scoring else None,
            horse_count=len(race.race_horses),
            vote_count=vc,
            created_at=race.created_at,
        ))
    return {"data": [item.model_dump() for item in items]}


@router.get("/{race_id}")
async def get_race(
    race_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single race by ID with horse snapshots. Public endpoint."""
    race = await race_service.get_race(db, race_id)
    if race is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "比赛不存在"},
        )
    vc = await race_service.get_race_vote_count(db, race.id)

    # Load grouped votes for settled races
    horse_votes_data = None
    if race.status == RaceStatus.SETTLED:
        horse_votes_data = await vote_service.get_race_results_grouped_by_horse(db, race_id)

    detail = RaceDetailResponse(
        id=race.id,
        name=race.name,
        date=race.date,
        grade=race.grade.value,
        status=race.status.value,
        custom_scoring=CustomScoring(**race.custom_scoring) if race.custom_scoring else None,
        horses=[
            {
                "race_horse_id": rh.id,
                "horse_id": rh.horse_id,
                "snapshot_data": rh.snapshot_data,
                "position": rh.position,
            }
            for rh in sorted(race.race_horses, key=lambda h: h.horse_id)
        ],
        horse_votes={"horses": horse_votes_data} if horse_votes_data is not None else None,
        vote_count=vc,
        created_at=race.created_at,
        updated_at=race.updated_at,
    )
    return {"data": detail.model_dump()}


@router.post("", status_code=201)
async def create_race(
    data: RaceCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """Create a new race. Admin only. Creates horse snapshots."""
    race = await race_service.create_race(db, data, admin.id)
    vc = await race_service.get_race_vote_count(db, race.id)

    detail = RaceDetailResponse(
        id=race.id,
        name=race.name,
        date=race.date,
        grade=race.grade.value,
        status=race.status.value,
        custom_scoring=CustomScoring(**race.custom_scoring) if race.custom_scoring else None,
        horses=[
            {
                "race_horse_id": rh.id,
                "horse_id": rh.horse_id,
                "snapshot_data": rh.snapshot_data,
                "position": rh.position,
            }
            for rh in sorted(race.race_horses, key=lambda h: h.horse_id)
        ],
        vote_count=vc,
        created_at=race.created_at,
        updated_at=race.updated_at,
    )
    return {"data": detail.model_dump()}


@router.patch("/{race_id}")
async def update_race(
    race_id: int,
    data: RaceUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """Update a race's attributes. Admin only. Only voting races can be edited."""
    race = await race_service.update_race(db, race_id, data, admin.id)
    vc = await race_service.get_race_vote_count(db, race.id)

    detail = RaceDetailResponse(
        id=race.id,
        name=race.name,
        date=race.date,
        grade=race.grade.value,
        status=race.status.value,
        custom_scoring=CustomScoring(**race.custom_scoring) if race.custom_scoring else None,
        horses=[
            {
                "race_horse_id": rh.id,
                "horse_id": rh.horse_id,
                "snapshot_data": rh.snapshot_data,
                "position": rh.position,
            }
            for rh in sorted(race.race_horses, key=lambda h: h.horse_id)
        ],
        vote_count=vc,
        created_at=race.created_at,
        updated_at=race.updated_at,
    )
    return {"data": detail.model_dump()}


@router.delete("/{race_id}", status_code=204)
async def delete_race(
    race_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """Delete a race. Admin only. Only non-settled races can be deleted."""
    await race_service.delete_race(db, race_id)
