"""Race API endpoints — CRUD for race management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_optional_user
from app.core.database import get_db
from app.models.race import RaceStatus
from app.models.user import User
from app.schemas.race import (
    AddRaceHorseRequest,
    CustomScoring,
    GateOrderUpdate,
    RaceCreate,
    RaceDetailResponse,
    RaceHorseUpdate,
    RaceListResponse,
    RaceUpdate,
)
from app.services import race_service, vote_service

router = APIRouter(prefix="/api/v1/races", tags=["races"])


@router.get("")
async def list_races(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_optional_user),
):
    """Get all races. Supports optional ?status=xxx filter. Public endpoint."""
    from app.models.vote import Vote
    races = await race_service.get_races(db, status)
    items = []
    race_ids = [race.id for race in races] if current_user else None
    voted_race_ids: set[int] = set()
    if current_user and race_ids:
        vote_stmt = select(Vote.race_id).where(
            Vote.user_id == current_user.id,
            Vote.race_id.in_(race_ids),
        )
        vote_result = await db.execute(vote_stmt)
        voted_race_ids = {row[0] for row in vote_result.all()}
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
            has_voted=race.id in voted_race_ids,
            created_at=race.created_at,
        ))
    return {"data": [item.model_dump() for item in items]}



def _build_horse_dict(rh) -> dict:
    """Build a horse dict from a RaceHorse ORM object."""
    return {
        "race_horse_id": rh.id,
        "horse_id": rh.horse_id,
        "snapshot_data": rh.snapshot_data,
        "position": rh.position,
        "gate": rh.gate,
        "weight": rh.weight,
        "jockey": rh.jockey,
    }


def _sort_horses_by_gate(race_horses: list) -> list:
    """Sort race horses by gate ascending, with null gates last, then by id."""
    return sorted(
        race_horses,
        key=lambda h: (h.gate if h.gate is not None else 9999, h.horse_id),
    )


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
        horses=[_build_horse_dict(rh) for rh in _sort_horses_by_gate(race.race_horses)],
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
        horses=[_build_horse_dict(rh) for rh in _sort_horses_by_gate(race.race_horses)],
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
        horses=[_build_horse_dict(rh) for rh in _sort_horses_by_gate(race.race_horses)],
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


@router.post("/{race_id}/horses", status_code=201)
async def add_race_horse(
    race_id: int,
    data: AddRaceHorseRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """Add a single horse to a voting race. Admin only."""
    race_horse = await race_service.add_horse_to_race(
        db, race_id, data.horse_id, data.weight, data.jockey
    )
    return {"data": _build_horse_dict(race_horse)}


@router.patch("/{race_id}/horses/gate")
async def update_gate_order(
    race_id: int,
    data: GateOrderUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """Update gate order for all horses in a voting race. Admin only."""
    race = await race_service.update_gate_order(db, race_id, data.order)
    vc = await race_service.get_race_vote_count(db, race.id)
    detail = RaceDetailResponse(
        id=race.id,
        name=race.name,
        date=race.date,
        grade=race.grade.value,
        status=race.status.value,
        custom_scoring=CustomScoring(**race.custom_scoring) if race.custom_scoring else None,
        horses=[_build_horse_dict(rh) for rh in _sort_horses_by_gate(race.race_horses)],
        vote_count=vc,
        created_at=race.created_at,
        updated_at=race.updated_at,
    )
    return {"data": detail.model_dump()}


@router.patch("/{race_id}/horses/{race_horse_id}")
async def update_race_horse(
    race_id: int,
    race_horse_id: int,
    data: RaceHorseUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """Update per-race weight/jockey for a race horse. Admin only."""
    race_horse = await race_service.update_race_horse(
        db, race_id, race_horse_id, data.weight, data.jockey
    )
    return {"data": _build_horse_dict(race_horse)}
