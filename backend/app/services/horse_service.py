"""Horse data management business logic service."""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.horse import Horse
from app.schemas.horse import HorseCreate, HorseUpdate


async def get_horses(
    db: AsyncSession, name: str | None = None
) -> list[Horse]:
    """Get all horses, optionally filtered by name fuzzy search."""
    stmt = select(Horse).order_by(Horse.name.asc())

    if name:
        stmt = stmt.where(Horse.name.ilike(f"%{name}%"))

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_horse(db: AsyncSession, horse_id: int) -> Horse | None:
    """Get a single horse by ID."""
    result = await db.execute(select(Horse).where(Horse.id == horse_id))
    return result.scalar_one_or_none()


async def create_horse(db: AsyncSession, data: HorseCreate) -> Horse:
    """Create a new horse.

    Raises 409 if a horse with the same name already exists.
    """
    # Check for duplicate name
    existing = await db.execute(
        select(Horse).where(Horse.name == data.name)
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "HORSE_NAME_EXISTS",
                "message": f"马匹「{data.name}」已存在",
            },
        )

    horse = Horse(**data.model_dump())
    db.add(horse)
    await db.flush()
    await db.refresh(horse)
    return horse


async def update_horse(
    db: AsyncSession, horse_id: int, data: HorseUpdate
) -> Horse:
    """Update a horse's attributes. Only provided fields are updated.

    Raises 404 if horse not found.
    Raises 409 if the new name conflicts with an existing horse.
    """
    horse = await get_horse(db, horse_id)
    if horse is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "马匹不存在"},
        )

    update_data = data.model_dump(exclude_unset=True)

    # If name is being changed, check for duplicates
    if "name" in update_data and update_data["name"] != horse.name:
        existing = await db.execute(
            select(Horse).where(Horse.name == update_data["name"])
        )
        if existing.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "HORSE_NAME_EXISTS",
                    "message": f"马匹「{update_data['name']}」已存在",
                },
            )

    for field, value in update_data.items():
        setattr(horse, field, value)

    # Track manually edited fields for auto-update protection
    # Any field that gets updated via PATCH is added to the protection list
    # so auto-updates will skip it (manual edit takes priority).
    tracked_fields = [f for f in update_data.keys() if f not in ("name", "manually_updated_fields")]
    if tracked_fields:
        # Manually_updated_fields stores a list; handle None/empty list/falsy consistently
        current_protected = horse.manually_updated_fields
        protected_list = list(current_protected) if isinstance(current_protected, list) else []
        for f in tracked_fields:
            if f not in protected_list:
                protected_list.append(f)
        horse.manually_updated_fields = protected_list

    await db.flush()
    await db.refresh(horse)
    return horse


async def reset_auto_protection(
    db: AsyncSession, horse_id: int
) -> Horse:
    """Clear the manually_updated_fields protection list for a horse.

    After reset, all fields become eligible for auto-update overwrite.
    Raises 404 if horse not found.
    """
    horse = await get_horse(db, horse_id)
    if horse is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "马匹不存在"},
        )

    horse.manually_updated_fields = None
    await db.flush()
    await db.refresh(horse)
    return horse


async def delete_horse(db: AsyncSession, horse_id: int) -> None:
    """Delete a horse.

    Raises 404 if horse not found.
    Raises 409 if the horse is referenced by any race (future check).
    """
    horse = await get_horse(db, horse_id)
    if horse is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "马匹不存在"},
        )

    # TODO: Check for race references when race model is implemented
    # If race references exist, raise 409

    await db.delete(horse)
    await db.flush()
