"""Admin API endpoints — invite code management."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.schemas.invite_code import InviteCodeResponse
from app.services import invite_code_service

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/invite-codes", response_model=dict)
async def list_invite_codes(
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """Get all invite codes, optionally filtered by search."""
    codes = await invite_code_service.get_invite_codes(db, search)
    return {"data": [InviteCodeResponse.model_validate(c) for c in codes]}


@router.post("/invite-codes", status_code=201, response_model=dict)
async def create_invite_code(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """Generate a new invite code."""
    code = await invite_code_service.create_invite_code(db)
    return {"data": InviteCodeResponse.model_validate(code)}


@router.patch("/invite-codes/{code}", response_model=dict)
async def invalidate_invite_code(
    code: str,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """Mark an invite code as disabled (only if unused)."""
    result = await invite_code_service.invalidate_invite_code(db, code)
    return {"data": InviteCodeResponse.model_validate(result)}
