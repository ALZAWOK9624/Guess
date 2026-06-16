"""Invite code business logic service."""

import secrets

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invite_code import InviteCode
from app.models.user import User
from app.utils.invite_code import generate_invite_code, MAX_RETRIES


async def get_invite_codes(
    db: AsyncSession, search: str | None = None
) -> list[InviteCode]:
    """Get all invite codes, optionally filtered by search term."""
    stmt = select(InviteCode).order_by(InviteCode.created_at.desc())

    if search:
        search_term = f"%{search}%"
        stmt = stmt.where(
            or_(
                InviteCode.code.ilike(search_term),
                InviteCode.bound_username.ilike(search_term),
                InviteCode.bound_qq.ilike(search_term),
            )
        )

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_invite_code(db: AsyncSession, qq: str) -> InviteCode:
    """Generate a unique invite code bound to the given QQ number.

    Retries up to MAX_RETRIES times if the generated code already exists.
    Raises 500 if unable to generate a unique code.
    """
    for _ in range(MAX_RETRIES):
        code_str = generate_invite_code()
        existing = await db.execute(
            select(InviteCode).where(InviteCode.code == code_str)
        )
        if existing.scalar_one_or_none() is None:
            invite_code = InviteCode(code=code_str, bound_qq=qq)
            db.add(invite_code)
            await db.flush()
            return invite_code

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "code": "CODE_GENERATION_FAILED",
            "message": "无法生成唯一的邀请码，请重试",
        },
    )


async def delete_invite_code_cascade(db: AsyncSession, code: str) -> None:
    """Delete an invite code and cascade delete its bound user and votes.

    - Unused code: just deletes the invite code record.
    - Used code: also deletes the bound user (cascade deletes user's votes).
    """
    result = await db.execute(
        select(InviteCode).where(InviteCode.code == code)
        .execution_options(populate_existing=True)
    )
    invite_code = result.scalar_one_or_none()

    if invite_code is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "邀请码不存在"},
        )

    # If bound to a user, delete the user (cascade deletes votes)
    if invite_code.status == "used" and invite_code.bound_username:
        user_result = await db.execute(
            select(User).where(User.username == invite_code.bound_username)
        )
        user = user_result.scalar_one_or_none()
        if user:
            await db.delete(user)

    # Delete the invite code
    await db.delete(invite_code)
    await db.flush()
