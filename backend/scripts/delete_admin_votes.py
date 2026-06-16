"""
One-time script to delete all vote records for the admin account.

Usage:
    cd backend
    python scripts/delete_admin_votes.py

Run this after deploying the admin-voting restriction to clean up
any existing votes cast by the admin user.
"""

import asyncio
import sys
from pathlib import Path

# Ensure backend/ is on sys.path so `from app.core.config import settings` works
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.user import User
from app.models.vote import Vote


async def main() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as db:
        # Find admin user
        result = await db.execute(select(User).where(User.username == "admin"))
        admin = result.scalar_one_or_none()

        if admin is None:
            print("[SKIP] Admin user not found — no votes to delete.")
            return

        # Count existing votes
        count_result = await db.execute(
            select(Vote).where(Vote.user_id == admin.id)
        )
        existing_votes = list(count_result.scalars().all())
        print(f"[INFO] Found {len(existing_votes)} vote(s) by admin user (id={admin.id}).")

        if not existing_votes:
            print("[SKIP] Admin has no votes — nothing to delete.")
            return

        # Delete all admin votes
        for vote in existing_votes:
            await db.delete(vote)

        await db.commit()
        print(f"[DONE] Deleted {len(existing_votes)} vote(s) for admin user '{admin.username}'.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
