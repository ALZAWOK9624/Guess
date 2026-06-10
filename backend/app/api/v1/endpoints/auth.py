"""Auth API endpoints — registration (login/refresh added in Story 1.5a)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.auth import RegisterRequest, RegisterResponse
from app.services.auth_service import register

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=dict, status_code=201)
async def register_endpoint(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Register a new user with an invite code.

    Returns JWT tokens and user info on success.
    """
    result = await register(db, request)
    return {"data": result.model_dump()}
