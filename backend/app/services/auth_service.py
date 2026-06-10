"""Authentication service — registration, login, token management."""

from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
)
from app.models.invite_code import InviteCode
from app.models.user import User
from app.schemas.auth import RegisterRequest, RegisterResponse, UserInfo


async def register(
    db: AsyncSession, request: RegisterRequest
) -> RegisterResponse:
    """Handle user registration with invite code validation.

    Flow:
    1. Look up invite code by code string
    2. Validate invite code status is "unused"
    3. Check username uniqueness
    4. Hash password, create User, bind invite code
    5. Generate JWT tokens, return response
    """
    # Step 1: Look up invite code
    result = await db.execute(
        select(InviteCode).where(InviteCode.code == request.invite_code)
    )
    invite_code = result.scalar_one_or_none()

    if invite_code is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVITE_CODE_INVALID",
                "message": "邀请码无效或已被使用",
            },
        )

    # Step 2: Validate invite code status
    if invite_code.status == "used":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVITE_CODE_USED",
                "message": "邀请码已被使用",
            },
        )

    if invite_code.status == "disabled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVITE_CODE_INVALID",
                "message": "邀请码无效或已被使用",
            },
        )

    # Step 3: Check username uniqueness
    existing_user = await db.execute(
        select(User).where(User.username == request.username)
    )
    if existing_user.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "USERNAME_EXISTS",
                "message": "用户名已存在",
            },
        )

    # Step 4: Hash password
    password_hash = get_password_hash(request.password)

    # Step 5: Create User and bind invite code atomically
    user = User(
        username=request.username,
        password_hash=password_hash,
        qq=request.qq,
        invite_code=request.invite_code,
        is_admin=False,
    )
    db.add(user)

    # Step 6: Bind invite code
    invite_code.status = "used"
    invite_code.bound_username = request.username
    invite_code.bound_qq = request.qq

    # Flush to get user.id before generating JWT
    # Catch IntegrityError for concurrent username duplicate registration
    try:
        await db.flush()
    except IntegrityError:
        # Rollback to allow re-use of the session
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "USERNAME_EXISTS",
                "message": "用户名已存在",
            },
        )

    # Step 7: Generate JWT tokens
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    return RegisterResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserInfo(
            id=user.id,
            username=user.username,
            qq=user.qq,
            is_admin=user.is_admin,
        ),
    )
