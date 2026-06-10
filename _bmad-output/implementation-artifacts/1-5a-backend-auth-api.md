---
baseline_commit: 4a393c8
---

# Story 1.5a: 后端认证 API

Status: done

## Story

As a **系统**,
I want **后端提供完整的 JWT 认证 API（登录、令牌刷新、当前用户查询）**,
So that **前端可以安全地完成用户认证和会话管理**。

## Acceptance Criteria

1. **Given** 已注册用户
   **When** `POST /api/v1/auth/login` 携带正确的 `{"username": "...", "password": "..."}`
   **Then** 返回 200 + `{"data": {"access_token": "...", "refresh_token": "...", "user": {"id": int, "username": "...", "qq": "...", "is_admin": bool}}}`
   **And** access_token 有效期 30min，refresh_token 有效期 7天

2. **Given** 用户输入错误的凭据
   **When** `POST /api/v1/auth/login` 携带错误的用户名或密码
   **Then** 返回 401 `{"detail": {"code": "INVALID_CREDENTIALS", "message": "用户名或密码错误"}}`
   **And** 不泄露具体哪个字段错误

3. **Given** 用户拥有有效的 refresh_token
   **When** `POST /api/v1/auth/refresh` 携带 `{"refresh_token": "..."}`
   **Then** 返回 200 + `{"data": {"access_token": "..."}}`
   **And** 新的 access_token 同样有效期 30min

4. **Given** 用户提供无效或过期的 refresh_token
   **When** `POST /api/v1/auth/refresh`
   **Then** 返回 401 `{"detail": {"code": "INVALID_REFRESH_TOKEN", "message": "刷新令牌无效或已过期"}}`

5. **Given** 未认证用户
   **When** 请求需认证的 API（如 `POST /api/v1/votes`）
   **Then** 返回 401 `{"detail": {"code": "NOT_AUTHENTICATED", "message": "请先登录"}}`

6. **Given** `get_current_user` 依赖注入
   **When** 请求携带有效的 Authorization Bearer token
   **Then** 从 DB 查询 User 记录，返回完整的 user 对象（含 id, username, qq, is_admin 等）
   **And** 令牌过期时（`ExpiredSignatureError`）→ 返回 401 `TOKEN_EXPIRED`
   **And** 无效令牌时（`JWTError`，不含过期）→ 返回 401 `INVALID_TOKEN`

7. **Given** `get_current_admin` 依赖注入
   **When** 请求携带有效 token，但用户 is_admin=False
   **Then** 返回 403 `{"detail": {"code": "FORBIDDEN", "message": "需要管理员权限"}}`

8. **Given** 系统初始化后
   **When** 第一次启动
   **Then** 默认 admin 账号已存在（用户名: admin, 密码: admin123），可正常登录
   **And** 该 admin 账号 is_admin=True

## Tasks / Subtasks

- [x] Task 1: 实现登录业务逻辑 (AC: #1, #2)
  - [x] 在 `auth_service.py` 中添加 `login(db, request: LoginRequest) -> LoginResponse`
  - [x] 查询 users 表：`select(User).where(User.username == request.username)`
  - [x] 用户不存在 → 401 `INVALID_CREDENTIALS`
  - [x] 密码验证：`verify_password(request.password, user.password_hash)`
  - [x] 密码不匹配 → 401 `INVALID_CREDENTIALS`（统一错误，不区分用户/密码）
  - [x] 生成 access_token + refresh_token（与注册逻辑一致）
  - [x] 返回 LoginResponse

- [x] Task 2: 实现令牌刷新业务逻辑 (AC: #3, #4)
  - [x] 在 `auth_service.py` 中添加 `refresh_token(db, request: TokenRefreshRequest) -> TokenRefreshResponse`
  - [x] decode refresh_token，提取 sub=username
  - [x] 查询 DB 验证用户仍存在
  - [x] 生成新的 access_token
  - [x] 无效/过期 refresh_token → 401 `INVALID_REFRESH_TOKEN`

- [x] Task 3: 添加 login + refresh 端点 (AC: #1, #2, #3)
  - [x] 在 `backend/app/api/v1/endpoints/auth.py` 中添加：
    - `POST /api/v1/auth/login` — 调用 `auth_service.login()`
    - `POST /api/v1/auth/refresh` — 调用 `auth_service.refresh_token()`
  - [x] 两个端点均无认证要求（游客可访问）

- [x] Task 4: 完整实现 `get_current_user` 依赖注入 (AC: #5, #6)
  - [x] 修改 `backend/app/api/deps.py` 中的 `get_current_user`
  - [x] 从 JWT payload 提取 sub=username
  - [x] 查询 DB：`select(User).where(User.username == username)`
  - [x] 用户不存在（用户被删除等）→ 401
  - [x] 认证用户返回完整 `User` 对象
  - [x] 访客（无 token）返回 `None`

- [x] Task 5: 完整实现 `get_current_admin` 依赖注入 (AC: #7)
  - [x] 修改 `backend/app/api/deps.py` 中的 `get_current_admin`
  - [x] 依赖 `get_current_user` 获取完整 User 对象
  - [x] 检查 `user.is_admin` 属性（而非字典的 `get("is_admin")`）
  - [x] 非管理员 → 403 `FORBIDDEN`

- [x] Task 6: Admin 种子账号 (AC: #8)
  - [x] 创建 `backend/app/utils/seed.py` — `seed_admin(db)` 函数
  - [x] 检查 admin 用户是否已存在（幂等）
  - [x] 若不存在，创建 admin 用户（username="admin", password=bcrypt("admin123"), is_admin=True）
  - [x] 在 `main.py` 的 `lifespan` startup 中调用 `seed_admin()`

- [x] Task 7: 后端测试 (AC: #1, #2, #3, #4, #5, #6, #7)
  - [x] 扩展 `backend/tests/test_auth.py`
  - [x] 测试登录成功（含 JWT 验证）
  - [x] 测试错误用户名 → 401
  - [x] 测试错误密码 → 401
  - [x] 测试 token 刷新成功
  - [x] 测试无效 refresh_token → 401
  - [x] 测试 get_current_user 返回完整 User 对象
  - [x] 测试 get_current_admin 拒绝非管理员
  - [x] 测试访客（无 token）返回 None
  - [x] 测试 admin 种子账号创建

## Dev Notes

### 要修改的文件（非新建）— UPDATE

| 文件 | 当前状态 | 修改内容 |
|------|---------|---------|
| `backend/app/services/auth_service.py` | 仅有 `register()` | 追加 `login()`, `refresh_token()` 函数 |
| `backend/app/api/v1/endpoints/auth.py` | 仅有 `POST /register` | 追加 `POST /login`, `POST /refresh` 端点 |
| `backend/app/api/deps.py` | get_current_user 返回字典占位 | 完整实现 DB 查询；get_current_admin 使用 ORM 对象属性 |
| `backend/app/main.py` | lifespan 仅创建引擎 | 追加调用 `seed_admin()` startup 逻辑 |
| `backend/tests/test_auth.py` | 仅有注册测试 | 追加登录/刷新/deps 测试 |

### 要新建的文件

| 文件 | 说明 |
|------|------|
| `backend/app/utils/seed.py` | admin 种子账号创建函数（幂等） |

### 无需修改（已就绪）

| 文件 | 说明 |
|------|------|
| `backend/app/schemas/auth.py` | LoginRequest, LoginResponse, TokenRefreshRequest, TokenRefreshResponse 已在 Story 1.4 中预创建 |
| `backend/app/core/security.py` | `verify_password()`, `create_access_token()`, `create_refresh_token()` 已实现 |
| `backend/app/core/config.py` | `jwt_secret`, `jwt_algorithm`, `access_token_expire_minutes`, `refresh_token_expire_days` 已配置 |

### API 端点规范

#### POST /api/v1/auth/login

```
请求体: { "username": "string", "password": "string" }
→ 200 { "data": { "access_token": "jwt...", "refresh_token": "jwt...", "user": { "id": 1, "username": "xxx", "qq": "xxx", "is_admin": false } } }
错误:
→ 401 { "detail": { "code": "INVALID_CREDENTIALS", "message": "用户名或密码错误" } }
```

#### POST /api/v1/auth/refresh

```
请求体: { "refresh_token": "string" }
→ 200 { "data": { "access_token": "jwt..." } }
错误:
→ 401 { "detail": { "code": "INVALID_REFRESH_TOKEN", "message": "刷新令牌无效或已过期" } }
```

### deps.py 完整实现方案

**get_current_user 改造要点：**

```python
# 当前（占位实现）:
# 返回 {"username": username, "is_admin": False} 字典

# 目标（完整实现）:
# 从 Authorization header 解析 JWT → 提取 sub=username
# → select(User).where(User.username == username) → scalar_one_or_none()
# → 用户不存在 → 401 NOT_AUTHENTICATED
# → 返回 User ORM 对象
```

**get_current_admin 改造要点：**

```python
# 当前:
# 使用 current_user.get("is_admin")（字典操作）

# 目标:
# user = await get_current_user(...)  → User ORM 对象
# if not user.is_admin: raise 403
# return user
```

**需要导入 User 模型到 deps.py：**
```python
from app.models.user import User
```

### 登录与注册代码复用

login() 函数的 token 生成与 register() 完全一致：
```python
access_token = create_access_token(data={"sub": user.username})
refresh_token = create_refresh_token(data={"sub": user.username})
```

### Admin 种子账号

UUID/随机密码不需要，因为是固定邀请制圈子：管理员 tkd 知道默认密码，上线后会自行修改。

```python
# backend/app/utils/seed.py
async def seed_admin(db: AsyncSession) -> None:
    """Create default admin account if not exists (idempotent)."""
    result = await db.execute(select(User).where(User.username == "admin"))
    if result.scalar_one_or_none() is not None:
        return  # Already exists

    admin = User(
        username="admin",
        password_hash=get_password_hash("admin123"),
        qq="0000000000",       # placeholder QQ
        invite_code="ADMIN001", # placeholder invite code
        is_admin=True,
    )
    db.add(admin)
    await db.flush()
```

在 `main.py` 的 lifespan 中调用：
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        from app.models import Base
        await conn.run_sync(Base.metadata.create_all)
    # Seed admin
    async with async_session_factory() as db:
        from app.utils.seed import seed_admin
        await seed_admin(db)
    yield
```

### 认证流程数据流

```
前端 Axios 拦截器
    │
    ├─ 401 → 尝试 refresh_token
    │    ├─ refresh 成功 → 更新 access_token，重试原请求
    │    └─ refresh 失败 → 清除令牌，跳转 /login?redirect=
    │
    └─ 正常请求 → Authorization: Bearer {access_token}
                      │
                      ▼
                 get_current_user (deps.py)
                      │
                      ├─ 无 token → 返回 None（游客）
                      │
                      ├─ 有效 token → 查 DB → 返回 User 对象
                      │
                      └─ 过期/无效 → 401 错误
```

### 测试方案

**测试架构：**
- 复用 Story 1.4 的 SQLite in-memory 测试数据库 fixture
- 新增 helper：`create_user(db, username, password, is_admin)` — 创建测试用户
- 新增 helper：`create_user_tokens(client, username, password)` — 登录获取 token

**测试用例（扩展 test_auth.py）：**

| 测试编号 | 测试场景 | 预期 |
|---------|---------|------|
| TC-1 | 有效凭据登录 | 200 + tokens + user info |
| TC-2 | 错误用户名 | 401 INVALID_CREDENTIALS |
| TC-3 | 错误密码 | 401 INVALID_CREDENTIALS |
| TC-4 | 有效 refresh 刷新 | 200 + new access_token |
| TC-5 | 无效 refresh_token | 401 INVALID_REFRESH_TOKEN |
| TC-6 | 过期 refresh_token | 401 INVALID_REFRESH_TOKEN |
| TC-7 | 受保护端点无 token | 401 NOT_AUTHENTICATED |
| TC-8 | get_current_user 返回完整 user | 含 id/username/qq/is_admin |
| TC-9 | get_current_admin 拒绝普通用户 | 403 FORBIDDEN |
| TC-10 | 访客（无 token）返回 None | get_current_user → None |
| TC-11 | admin 种子账号存在 | admin/admin123 可登录且 is_admin=True |

### 微文案（必须精确匹配）

| 场景 | 文案 |
|------|------|
| 登录失败（用户名或密码错误） | 「用户名或密码错误」 |
| 令牌过期 | 「登录已过期，请重新登录」 |
| 无效令牌 | 「无效的令牌」 |
| 刷新令牌无效或过期 | 「刷新令牌无效或已过期」 |
| 未认证访问受保护端点 | 「请先登录」 |
| 非管理员访问管理端点 | 「需要管理员权限」 |

### 现有代码注意事项

1. **auth_service.py 当前状态** — 仅有 `register()` 函数。`login()` 和 `refresh_token()` 需作为独立异步函数追加到同一文件。

2. **schemas/auth.py 已就绪** — `LoginRequest`, `LoginResponse`, `TokenRefreshRequest`, `TokenRefreshResponse` 已在 Story 1.4 创建，可直接用于端点响应。

3. **security.py 已就绪** — `verify_password(plain, hashed)` 返回 bool，可直接用于登录密码验证。

4. **deps.py 导入变更** — 需添加 `from app.models.user import User`。注意不要引入循环依赖：
   - `deps.py` 导入 `models/user.py` ✓（models 不依赖 api/）
   - `deps.py` 导入 `core/config.py` ✓（已有）
   - `deps.py` 导入 `core/database.py` ✓（已有）

5. **conftest.py 占位** — `backend/tests/conftest.py` 当前只有基本 fixture。建议将 SQLite in-memory engine fixture 从 `test_auth.py` 提取到 `conftest.py` 以便复用。

6. **测试中 app.dependency_overrides 管理** — 每次测试后调用 `app.dependency_overrides.clear()` 以防止泄漏。若将 db_session fixture 移到 conftest.py，所有测试文件共享一个清理策略。

7. **Main.py lifespan 当前实现** — 需确认是否已有 `create_all` 逻辑，在其后追加 seed_admin 调用。

### References

- [Source: `epics.md` — Story 1.5a 验收条件] — 所有 5 条 AC
- [Source: `epics.md` — FR-3] — 用户登录功能要求
- [Source: `architecture.md` — 认证方案] — JWT access 30min + refresh 7d、passlib[bcrypt]
- [Source: `architecture.md` — API 响应格式] — `{ "data": ... }` / `{ "detail": { "code": "...", "message": "..." } }`
- [Source: `architecture.md` — HTTP 状态码] — 200/201/401/403 映射
- [Source: `project-context.md` — deps.py 规范] — get_current_user 返回 None 对游客，401 错误
- [Source: `project-context.md` — security.py] — `verify_password()`, `create_access_token()`, `create_refresh_token()`
- [Source: `project-context.md` — 命名规范] — snake_case api 字段，三层分离
- [Source: `EXPERIENCE.md` — 微文案] — 登录失败「用户名或密码错误」
- [Source: `Story 1.4` — Dev Notes] — auth_service 模式、测试基础设施、deps.py 当前状态
- [Source: `Story 1.4` — Review Findings] — `ExpiredSignatureError` 与 `JWTError` 分离处理

## Dev Agent Record

### Git Intelligence Summary

最近的提交历史和模式：

| Commit | Description |
|--------|-------------|
| 4a393c8 | feat: Story 1.4 - user registration with invite code validation |
| 1f220e2 | feat: Story 1.3 - invite code system with management UI |
| 1399d09 | feat: Story 1.2 - JRA design tokens and responsive navigation |
| c73cf36 | chore: update sprint status - Story 1.1 done |
| d740f9b | docs: add project-context.md and finalize Story 1.1 |

**代码模式观察：**
- 后端采用 endpoints → services → models 三层架构
- 测试使用 SQLite in-memory + `app.dependency_overrides` 注入
- `response_model=dict` 模式用于所有端点
- Service 层直接 raise `HTTPException`（项目模式）

### Previous Story Intelligence

**Story 1.4 已完成（用户注册）：**
- ✅ User 模型 [user.py]: username(unique), password_hash(bcrypt), qq, invite_code, is_admin, timestamps
- ✅ Register schemas [schemas/auth.py]: 含 RegisterRequest + LoginRequest + TokenRefreshRequest 等
- ✅ auth_service.register(): 邀请码验证→密码哈希→用户创建→JWT 生成
- ✅ POST /api/v1/auth/register 端点
- ✅ auth endpoints 文件已创建 [endpoints/auth.py]
- ✅ auth router 已在 `__init__.py` 注册
- ✅ 8 个 pytest 全部通过
- ✅ authStore 已有基础方法（setUser, setTokens, logout）
- ✅ client.ts Axios 拦截器已配置（401 令牌刷新逻辑占位）

**Review 学习（Story 1.4）：**
- `ExpiredSignatureError` 与 `JWTError` 需要分开捕获处理
- `db.flush()` 缺少 `IntegrityError` 保护 → 已添加
- `authStore.restoreSession()` 需在 `App.vue` 的 `onMounted` 中调用
- 后端模式约定：`response_model=dict`，service 层直接 raise HTTPException
- 测试中 `app.dependency_overrides.clear()` 确保隔离

**当前代码状态：**
- `deps.py` 的 `get_current_user` 返回 `{"username": ..., "is_admin": False}` 字典 — 本故事需改为 DB 查询
- `deps.py` 的 `get_current_admin` 使用字典 `get("is_admin")` — 本故事需改为 ORM 属性
- `auth_service.py` 仅有 `register()` — 本故事追加 `login()` + `refresh_token()`
- `endpoints/auth.py` 仅有注册端点 — 本故事追加 login + refresh 端点
- `test_auth.py` 仅有注册测试 — 本故事追加登录/刷新/deps 测试

### Completion Notes

**后端实现（Tasks 1-6）：**
- ✅ `auth_service.py`: 新增 `login()` + `refresh_token()` 函数
  - login: 查DB用户→密码验证→JWT生成（统一401错误，不区分用户名/密码）
  - refresh_token: decode令牌→验证用户存在→新access_token（分开处理ExpiredSignatureError/JWTError）
- ✅ `endpoints/auth.py`: 新增 `POST /api/v1/auth/login` + `POST /api/v1/auth/refresh`
- ✅ `deps.py`: `get_current_user` 改为完整DB查询返回 User ORM 对象
  - 无token→None(游客)、过期→TOKEN_EXPIRED、无效→INVALID_TOKEN、用户不存在→NOT_AUTHENTICATED
- ✅ `deps.py`: `get_current_admin` 使用 `user.is_admin` ORM 属性（非字典 get）
- ✅ `backend/app/utils/seed.py`: 幂等创建 admin 账号（admin/admin123, is_admin=True）
- ✅ `main.py`: lifespan startup 中调用 seed_admin

**前端变更：** 无（Story 1.5b 实现前端登录交互）

**测试（Task 7）：**
- ✅ `conftest.py`: 提取 db_session 和 async_client fixture 给所有测试复用
- ✅ 23 个 pytest 全部通过：
  - 注册测试（6 错误分支 + 2 成功）→ 零回归
  - 登录测试（1 成功 + 3 错误分支）
  - 刷新测试（1 成功 + 2 错误分支）
  - deps 测试（3 个依赖注入 + 1 游客 + 1 admin 成功 + 1 admin 拒绝）

### File List — Summary

**NEW:**
- `backend/app/utils/seed.py` — Admin seed function (idempotent, admin/admin123)

**UPDATE:**
- `backend/app/services/auth_service.py` — Added login(), refresh_token()
- `backend/app/api/v1/endpoints/auth.py` — Added POST /login, POST /refresh
- `backend/app/api/deps.py` — Full get_current_user with DB; get_current_admin with ORM property
- `backend/app/main.py` — Call seed_admin in lifespan startup
- `backend/tests/conftest.py` — Extracted db_session + async_client fixtures (shared)
- `backend/tests/test_auth.py` — Refactored to use shared fixtures + added login/refresh/deps/seed tests (15 new tests, 23 total)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — Status update

## Review Findings

- [x] [Review][Patch] seed_admin 并发竞态 [seed.py:30] — `seed_admin()` 在 `db.add(admin)` + `db.flush()` 时没有 `IntegrityError` 保护。如果两个 worker 同时启动（K8s/Docker Compose scale），唯一约束会导致 500 错误。已修复：添加 `try/except IntegrityError` 回滚。

- [x] [Review][Patch] 测试路由污染 [test_auth.py:436] — `TestDeps` 中的测试动态注册路由器到全局 `app` 对象。路由 `/test-protected`, `/test-protected2`, `/test-guest`, `/test-admin-check`, `/test-admin-reject` 跨测试累积。如果测试顺序改变，可能导致路由冲突。已修复：使用 UUID 唯一路由路径避免冲突。

- [x] [Review][Defer] DB 查询在 JWT decode try/except 之外 [deps.py:57] — `get_current_user` 的 DB 查询在 JWT 解码的 `try/except` 块之外。如果 DB 连接失败，异常不会被 `JWTError` 处理器捕获，而是由 FastAPI 返回 500。这与原有模式一致（database.py 的 `get_db` 已有独立错误处理），非本故事引入。deferred, pre-existing
