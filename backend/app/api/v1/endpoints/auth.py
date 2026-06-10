"""Auth API endpoints — registration, login, token refresh."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenRefreshRequest,
)
from app.services.auth_service import login, refresh_token, register, reset_password

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


@router.post("/login", response_model=dict)
async def login_endpoint(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Authenticate user and return JWT tokens.

    Returns access_token, refresh_token, and user info on success.
    Returns 401 for invalid credentials.
    """
    result = await login(db, request)
    return {"data": result.model_dump()}


@router.post("/refresh", response_model=dict)
async def refresh_endpoint(
    request: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Refresh an expired access token using a valid refresh token.

    Returns a new access_token on success.
    Returns 401 for invalid/expired refresh tokens.
    """
    result = await refresh_token(db, request)
    return {"data": result.model_dump()}


@router.post("/reset-password", response_model=dict)
async def reset_password_endpoint(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Reset password using username + invite code verification.

    Requires: username + the invite_code that was bound to this user
    during registration.
    Returns 200 with user info on success.
    Returns 400 for invite_code/user mismatch.
    """
    result = await reset_password(db, request)
    return {"data": result.model_dump()}
