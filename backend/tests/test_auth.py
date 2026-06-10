"""Tests for user registration (Story 1.4)."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.core.database import Base
from app.core.security import verify_password
from app.main import app
from app.models.invite_code import InviteCode
from app.models.user import User


# --- In-memory SQLite test database ---

@pytest.fixture
async def db_session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        yield session

    await engine.dispose()


# --- Helper: create an unused invite code in DB ---

async def create_unused_invite_code(db: AsyncSession) -> InviteCode:
    """Helper to seed an unused invite code for testing."""
    code = InviteCode(
        code="TESTCODE",
        status="unused",
    )
    db.add(code)
    await db.flush()
    return code


async def create_used_invite_code(db: AsyncSession) -> InviteCode:
    """Helper to seed a used invite code."""
    code = InviteCode(
        code="USEDCODE",
        status="used",
        bound_username="existing_user",
        bound_qq="123456789",
    )
    db.add(code)
    await db.flush()
    return code


async def create_disabled_invite_code(db: AsyncSession) -> InviteCode:
    """Helper to seed a disabled invite code."""
    code = InviteCode(
        code="DISABLED",
        status="disabled",
    )
    db.add(code)
    await db.flush()
    return code


# --- Registration Error Tests ---

class TestRegisterErrors:
    """Test registration error branches (AC #2, #3, #4)."""

    @pytest.mark.asyncio
    async def test_register_invalid_invite_code(self, db_session: AsyncSession):
        """AC #3: Invalid/non-existent invite code returns error."""
        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "username": "newuser",
                    "password": "password123",
                    "qq": "12345678901",
                    "invite_code": "NONEXIST",
                },
            )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["code"] == "INVITE_CODE_INVALID"
        assert "无效" in data["detail"]["message"]

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_register_disabled_invite_code(self, db_session: AsyncSession):
        """AC #3: Disabled invite code returns error."""
        await create_disabled_invite_code(db_session)

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "username": "newuser",
                    "password": "password123",
                    "qq": "12345678901",
                    "invite_code": "DISABLED",
                },
            )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["code"] == "INVITE_CODE_INVALID"

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_register_used_invite_code(self, db_session: AsyncSession):
        """AC #2: Already used invite code returns error."""
        await create_used_invite_code(db_session)

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "username": "newuser",
                    "password": "password123",
                    "qq": "12345678901",
                    "invite_code": "USEDCODE",
                },
            )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["code"] == "INVITE_CODE_USED"
        assert "已被使用" in data["detail"]["message"]

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, db_session: AsyncSession):
        """AC #4: Duplicate username returns error."""
        # First, create a user with this username
        user = User(
            username="existing_user",
            password_hash="dummy_hash",
            qq="12345678901",
            invite_code="SOMECODE",
            is_admin=False,
        )
        db_session.add(user)
        await db_session.flush()

        # Also need a valid unused invite code
        await create_unused_invite_code(db_session)

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "username": "existing_user",
                    "password": "password123",
                    "qq": "12345678901",
                    "invite_code": "TESTCODE",
                },
            )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["code"] == "USERNAME_EXISTS"
        assert "已存在" in data["detail"]["message"]

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_register_empty_fields(self, db_session: AsyncSession):
        """AC #6: Missing/empty fields return 422."""
        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Empty username
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "username": "",
                    "password": "password123",
                    "qq": "12345678901",
                    "invite_code": "TESTCODE",
                },
            )

        assert response.status_code == 422

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_register_short_password(self, db_session: AsyncSession):
        """AC #7: Password shorter than 6 chars returns 422."""
        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "username": "newuser",
                    "password": "12345",  # 5 chars, too short
                    "qq": "12345678901",
                    "invite_code": "TESTCODE",
                },
            )

        assert response.status_code == 422

        app.dependency_overrides.clear()


# --- Registration Success Tests ---

class TestRegisterSuccess:
    """Test successful registration (AC #1, #5)."""

    @pytest.mark.asyncio
    async def test_register_success(self, db_session: AsyncSession):
        """AC #1, #5: Valid registration returns 201 with tokens and user info."""
        await create_unused_invite_code(db_session)

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "username": "newuser",
                    "password": "password123",
                    "qq": "12345678901",
                    "invite_code": "TESTCODE",
                },
            )

        assert response.status_code == 201
        data = response.json()["data"]
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["username"] == "newuser"
        assert data["user"]["qq"] == "12345678901"
        assert data["user"]["is_admin"] is False
        assert isinstance(data["user"]["id"], int)

        # Verify password is hashed in DB
        result = await db_session.execute(
            select(User).where(User.username == "newuser")
        )
        user = result.scalar_one()
        assert verify_password("password123", user.password_hash)
        assert user.invite_code == "TESTCODE"
        assert user.qq == "12345678901"
        assert user.is_admin is False

        # Verify invite code is bound (AC #1: status→used, bind username/qq)
        invite_result = await db_session.execute(
            select(InviteCode).where(InviteCode.code == "TESTCODE")
        )
        invite_code = invite_result.scalar_one()
        assert invite_code.status == "used"
        assert invite_code.bound_username == "newuser"
        assert invite_code.bound_qq == "12345678901"

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_register_auto_login_tokens(self, db_session: AsyncSession):
        """Verify the returned tokens are valid JWT with correct payload."""
        await create_unused_invite_code(db_session)

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "username": "autologin_user",
                    "password": "password123",
                    "qq": "98765432109",
                    "invite_code": "TESTCODE",
                },
            )

        assert response.status_code == 201
        data = response.json()["data"]

        # Verify access_token can be decoded
        from jose import jwt
        from app.core.config import settings
        payload = jwt.decode(
            data["access_token"],
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        assert payload["sub"] == "autologin_user"

        app.dependency_overrides.clear()
