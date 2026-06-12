"""Auto-update service — framework for applying result-driven horse updates.

This is a v1 framework: it provides the mechanism to apply field-level
updates with manual-edit protection and change logging, but does NOT
define any concrete update rules for specific fields.

EXTENSION POINT: To add field-specific auto-update rules:
  1. Assemble horse_updates dict in result_service after settlement.
  2. Call apply_auto_updates() with the assembled updates.
  3. The framework handles manual-edit checks and logging automatically.

Example:
    horse_updates = {
        1: {"previous_result": "1着", "weight": "524kg"},
        2: {"previous_result": "3着"},
    }
    logs = await apply_auto_updates(db, race_id=42, horse_updates=horse_updates)
"""

from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auto_update import HorseAutoUpdateLog
from app.models.horse import Horse


async def apply_auto_updates(
    db: AsyncSession,
    race_id: int,
    horse_updates: dict[int, dict[str, Any]],
) -> list[HorseAutoUpdateLog]:
    """Apply field-level auto-updates to horses with manual-edit protection.

    For each horse in horse_updates:
      - Loads the Horse record and its manually_updated_fields list.
      - Skips any field present in manually_updated_fields (manual priority).
      - Updates non-protected fields and logs changes to HorseAutoUpdateLog.

    Args:
        db: Database session.
        race_id: ID of the race that triggered the update (for traceability).
        horse_updates: Mapping of horse_id → {field_name: new_value, ...}.

    Returns:
        List of HorseAutoUpdateLog entries for each applied change.
    """
    if not horse_updates:
        return []

    created_logs: list[HorseAutoUpdateLog] = []

    # Pre-validate all horse_ids exist before applying any updates
    # This ensures atomicity: if any horse is missing, no partial updates occur.
    for horse_id in horse_updates:
        horse = await db.get(Horse, horse_id)
        if horse is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "NOT_FOUND",
                    "message": f"马匹 {horse_id} 不存在",
                },
            )

    # Get valid column names for field validation
    horse_columns = {c.key for c in inspect(Horse).columns}

    for horse_id, fields in horse_updates.items():
        # Re-fetch horse (already validated above, but fetch fresh for update)
        horse = await db.get(Horse, horse_id)

        # Determine protected (manually edited) fields
        # Handle None/empty list consistently — no falsy trap
        current_protected = horse.manually_updated_fields
        protected_list: list[str] = (
            list(current_protected) if isinstance(current_protected, list) else []
        )

        for field_name, new_value in fields.items():
            # Validate field_name is a valid Horse column
            if field_name not in horse_columns:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "INVALID_FIELD",
                        "message": f"无效的字段名: {field_name}",
                    },
                )

            # Skip fields that were manually edited
            if field_name in protected_list:
                continue

            # Capture old value for logging
            old_value = getattr(horse, field_name, None)

            # Apply the update
            setattr(horse, field_name, new_value)

            # Create change log entry
            log_entry = HorseAutoUpdateLog(
                horse_id=horse_id,
                race_id=race_id,
                field_name=field_name,
                old_value=str(old_value) if old_value is not None else None,
                new_value=str(new_value) if new_value is not None else None,
                trigger_source="settlement",
            )
            db.add(log_entry)
            created_logs.append(log_entry)

        # Flush after processing each horse, then refresh for consistency
        await db.flush()
        await db.refresh(horse)

    return created_logs
