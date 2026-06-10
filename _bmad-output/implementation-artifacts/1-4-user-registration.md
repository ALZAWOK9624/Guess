---
baseline_commit: 1f220e297c6d40908d8a8926054667354052c1f4
---

# Story 1.4: 用户注册

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **赛马爱好者**,
I want **凭邀请码注册账号**,
So that **我可以加入圈子并参与投票**。

## Acceptance Criteria

1. **Given** 用户拥有一个有效邀请码
   **When** 访问 `/register` 并输入用户名（全局唯一）、密码、QQ号和邀请码
   **Then** 注册成功后自动登录并跳转至首页
   **And** 该邀请码状态变为「已绑定」，绑定该用户的用户名和QQ号

2. **Given** 用户输入已被使用的邀请码
   **When** 提交注册
   **Then** 显示错误提示「邀请码已被使用」
   **And** 停留在注册页

3. **Given** 用户输入无效或已失效的邀请码
   **When** 提交注册
   **Then** 显示错误提示「邀请码无效或已被使用」

4. **Given** 用户输入已存在的用户名
   **When** 提交注册
   **Then** 显示错误提示「用户名已存在」

5. **Given** 后端 API
   **When** `POST /api/v1/auth/register` 携带有效参数（`{"username": "...", "password": "...", "qq": "...", "invite_code": "..."}`）
   **Then** 返回 201 + `{ "data": { "access_token": "...", "refresh_token": "...", "user": { "id": int, "username": "...", "qq": "...", "is_admin": false } } }`
   **And** User 表中插入新记录，密码 bcrypt 哈希存储
   **And** InviteCode 表中对应记录 status 更新为 "used"，绑定 username 和 qq

6. **Given** 注册请求缺少必填字段（如空用户名、空密码、空邀请码）
   **When** 提交
   **Then** 返回 422 校验错误

7. **Given** 密码长度不足
   **When** 提交密码少于 6 位
   **Then** 返回 422，提示密码长度需至少 6 位

## Tasks / Subtasks

- [x] Task 1: 后端 User 数据模型 (AC: #5)
  - [x] 创建 `backend/app/models/user.py` — User 模型（id, username, password_hash, qq, invite_code, is_admin, created_at, updated_at）
  - [x] 在 `models/__init__.py` 中注册 User 模型
  - [x] 创建 Alembic 迁移 `002_create_users_table.py`

- [x] Task 2: 后端 Pydantic Schemas (AC: #5, #6)
  - [x] 创建 `backend/app/schemas/auth.py` — RegisterRequest（username: str(3-20), password: str(6-128), qq: str(5-20), invite_code: str(8)）、RegisterResponse（access_token, refresh_token, user: UserInfo）
  - [x] 统一响应格式：成功 `{"data": {...}}`，错误 `{"detail": {"code": "...", "message": "..."}}`

- [x] Task 3: 后端服务层 (AC: #1, #2, #3, #4)
  - [x] 创建 `backend/app/services/auth_service.py` — register(db, request) 业务逻辑
  - [x] 注册函数流程：①查询邀请码（不存在→"邀请码无效或已被使用"）②检查状态（used/disabled→"邀请码已被使用"）③检查用户名唯一性（重复→"用户名已存在"）④花括号密码 ⑤创建 User 记录 ⑥绑定邀请码（status→used, bound_username, bound_qq）⑦生成 JWT tokens ⑧返回注册结果
  - [x] 所有错误使用 HTTPException + 统一错误格式

- [x] Task 4: 后端 API 端点 (AC: #5)
  - [x] 创建 `backend/app/api/v1/endpoints/auth.py` — `POST /api/v1/auth/register`
  - [x] 端点无认证要求（可被游客访问）
  - [x] 在 `backend/app/api/v1/__init__.py` 中注册 auth router

- [x] Task 5: 后端测试 (AC: #2, #3, #4, #5, #6, #7)
  - [x] 创建 `backend/tests/test_auth.py` — 使用 SQLite in-memory 测试 DB
  - [x] 测试正常注册流程（含自动登录验证）
  - [x] 测试邀请码已使用/已失效/不存在的错误分支
  - [x] 测试用户名重复错误
  - [x] 测试密码过短和必填字段验证
  - [x] 测试注册成功后 InviteCode 正确绑定

- [x] Task 6: 前端类型定义 (AC: #1)
  - [x] 创建 `frontend/src/types/auth.ts` — RegisterRequest, RegisterResponse, UserInfo 接口

- [x] Task 7: 前端 API 层 (AC: #1)
  - [x] 创建 `frontend/src/api/auth.ts` — `register(data: RegisterRequest): Promise<RegisterResponse>` 调用后端注册 API

- [x] Task 8: 前端注册页面 (AC: #1, #2, #3, #4)
  - [x] 完整实现 `frontend/src/pages/RegisterPage.vue` — 注册表单 UI
  - [x] 注册成功：保存令牌到 authStore + localStorage，跳转首页
  - [x] 错误处理：服务器返回的错误信息精确显示在对应字段下方或表单顶部
  - [x] 表单验证：前端初步校验（非空、密码长度 >=6）
  - [x] 移动端适配：safe-area-inset-bottom、触摸目标 >= 44px

- [x] Task 9: 端到端验证
  - [x] 后端：pytest 全部通过，覆盖率达标
  - [x] 前端：TypeScript 编译通过，Vite 构建成功
  - [x] 手动验证：创建邀请码→用该码注册→验证登录状态→验证邀请码状态

## Dev Notes

### 要修改的文件（非新建）— UPDATE

| 文件 | 当前状态 | 修改内容 |
|------|---------|---------|
| `backend/app/models/__init__.py` | 已导入 InviteCode | 追加导入 User 模型 |
| `backend/app/api/v1/__init__.py` | 已包含 admin router | 追加注册 auth router |
| `frontend/src/stores/authStore.ts` | 基础状态（user, tokens, isAdmin） | 添加 `register()` action |
| `frontend/src/pages/RegisterPage.vue` | 占位符内容 | 完整实现注册页面 |
| `frontend/src/router/index.ts` | 已配置 `/register` 路由 | 无需修改（路由已就绪） |

### 要新建的文件

| 文件 | 说明 |
|------|------|
| `backend/app/models/user.py` | User SQLAlchemy 模型 |
| `backend/app/schemas/auth.py` | 注册请求/响应 Pydantic schemas |
| `backend/app/services/auth_service.py` | 注册业务逻辑 |
| `backend/app/api/v1/endpoints/auth.py` | auth 端点（register + 后续 login/refresh） |
| `backend/alembic/versions/002_create_users_table.py` | Alembic migration |
| `backend/tests/test_auth.py` | 注册功能测试 |
| `frontend/src/types/auth.ts` | 认证类型定义 |
| `frontend/src/api/auth.ts` | 认证 API 调用 |

### 数据模型设计

**User 表（`users`）：**

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    qq: Mapped[str] = mapped_column(String(20), nullable=False)
    invite_code: Mapped[str] = mapped_column(String(8), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

**重要设计决策：**
- `invite_code` 是 User 模型中的字符串字段（去规范化设计），用于记录用户注册所用的邀请码。这与 InviteCode 表中的 `bound_username`/`bound_qq` 双向冗余——边界情况由 service 层通过事务保证一致性。
- 不做外键关联——v1 规模小，字符串字段足够，避免不必要的循环引用。
- `is_admin` 默认 False。管理员账号在 Story 1.5a 中通过 seed 数据创建。

### API 端点规范

```
POST /api/v1/auth/register
    请求体: { "username": "string(3-20)", "password": "string(6-128)", "qq": "string(5-20)", "invite_code": "string(8)" }
    → 201 { "data": { "access_token": "jwt...", "refresh_token": "jwt...", "user": { "id": 1, "username": "xxx", "qq": "xxx", "is_admin": false } } }
    错误:
    → 400 { "detail": { "code": "INVITE_CODE_USED", "message": "邀请码已被使用" } }
    → 400 { "detail": { "code": "INVITE_CODE_INVALID", "message": "邀请码无效或已被使用" } }  // 已失效/不存在
    → 400 { "detail": { "code": "USERNAME_EXISTS", "message": "用户名已存在" } }
    → 422 { "detail": [...] }  // 字段校验失败
```

### 数据关系（上下游）

Story 1.3 已完成的 InviteCode 模型是本故事的依赖基础。注册时将：
1. 查询 `invite_codes` 表获得 `code`
2. 验证 `status == "unused"`
3. 更新 `invite_codes` 记录：`status = "used"`, `bound_username = username`, `bound_qq = qq`
4. 创建 `users` 记录

Story 1.5a（后端认证 API）将复用 auth endpoints 文件，添加 login + refresh 端点。Story 1.5b 实现前端的登录交互。

**当前 Stories 间的数据流：**
- Story 1.3: `invite_codes` 表的 CRUD（管理员侧）
- Story 1.4: ✅ `invite_codes` 读取+更新 + `users` 创建（本故事）
- Story 1.5a: `users` 读取 + JWT 认证 + login/refresh 端点
- Story 1.5b: 前端登录/游客交互

### 现有代码注意事项

1. **User 模型不存在** — 本故事需要创建第一个 User 模型。Alembic 配置已在 `env.py` 中设置 `from app.models import *`，添加 User 到 `models/__init__.py` 后 autogenerate 会自动检测。

2. **deps.py 依赖注入** — 当前 `get_current_user` 是占位实现（从 JWT 解析 username 但不查 DB）。本故事新增注册端点不需要 auth 保护（游客可注册），所以无需修改 deps.py。

3. **security.py 可用** — `get_password_hash()`、`create_access_token()`、`create_refresh_token()` 已在 Story 1.1 中实现，可直接在 auth_service 中调用。

4. **生成的令牌** — access_token 30 分钟有效期，refresh_token 7 天有效期。注册成功后直接返回两个令牌实现"注册即登录"。

5. **JWT 令牌 payload 应包含 sub=username** — 与 `deps.py` 中 `payload.get("sub")` 一致。

6. **前端 authStore 已有基础功能** — `setUser()`, `setTokens()`, `logout()` 方法已存在。注册成功后只需调用这两个方法即可完成登录。

7. **前端 client.ts 已有 localStorage 读写** — 通过 `localStorage.getItem('auth')` 读取令牌。注册成功后需将 `{ accessToken, refreshToken, user }` 存入 `localStorage.setItem('auth', ...)`。

8. **conftest.py 测试基础设施** — 当前 `backend/tests/conftest.py` 只有占位 fixture。本故事需要创建更完整的测试 fixture，建议：
   - 创建 `async_engine`（SQLite in-memory）
   - 创建 `async_session` fixture
   - 创建测试 DB 表（`await run_sync(Base.metadata.create_all)`）
   - 在 test_auth.py 中直接使用 session，或创建带 override 的 TestClient

### 注册表单 UI 设计要点

```
┌─────────────────────────┐
│         注册             │
│                         │
│  用户名                  │
│  ┌─────────────────┐    │
│  │ 请输入用户名      │    │
│  └─────────────────┘    │
│                         │
│  密码（至少 6 位）       │
│  ┌─────────────────┐    │
│  │ 请输入密码        │    │
│  └─────────────────┘    │
│                         │
│  QQ 号                   │
│  ┌─────────────────┐    │
│  │ 请输入 QQ 号      │    │
│  └─────────────────┘    │
│                         │
│  邀请码                  │
│  ┌─────────────────┐    │
│  │ 请输入邀请码      │    │
│  └─────────────────┘    │
│                         │
│  ┌─────────────────┐    │
│  │     注  册       │    │
│  └─────────────────┘    │
│                         │
│  已有账号？去登录        │
└─────────────────────────┘
```

- 每个输入框下方显示字段对应的错误信息
- 提交按钮在加载时显示 loading 状态并禁用
- 表单顶部可显示全局错误信息

### 微文案（必须精确匹配）

| 场景 | 文案 |
|------|------|
| 注册成功 | 自动跳转首页，无单独 Toast |
| 邀请码已被使用 | 「邀请码已被使用」 |
| 邀请码无效/已失效 | 「邀请码无效或已被使用」 |
| 用户名已存在 | 「用户名已存在」 |
| 密码太短（前端校验） | 「密码至少需要 6 个字符」 |
| 必填字段为空（前端校验） | 「{字段名}不能为空」 |

### 无障碍要求

- 表单使用 `<form>` 标签 + `@submit.prevent`
- 每个输入框绑定 `<label>`（或 `aria-label`）
- 错误信息使用 `aria-live="polite"` 区域
- 提交按钮在 loading 时禁用并添加 `aria-busy="true"`
- 触摸目标 ≥ 44×44px
- focus ring（2px `var(--color-primary)` 外描边）

### 测试标准

**后端（pytest + pytest-asyncio + aiosqlite）：**
- 正常注册：有效邀请码 → 201 + 令牌 + 用户数据
- 邀请码已使用：status=used 的码 → 400 "邀请码已被使用"
- 邀请码已失效：status=disabled 的码 → 400 "邀请码无效或已被使用"
- 邀请码不存在：找不到码 → 400 "邀请码无效或已被使用"
- 用户名重复：已存在的用户名 → 400 "用户名已存在"
- 密码过短：<6 字符 → 422
- 缺少必填字段：空用户名/空密码/空邀请码 → 422
- 注册成功后验证：InviteCode 表对应记录的 status="used" 并绑定 username/qq

**前端（手动验证）：**
- 表单字段验证触发
- 成功注册后 authStore 状态正确
- 错误信息正确显示
- 移动端布局正常

### 架构约束检查

- ✅ 后端三层分离：endpoints → services → models
- ✅ API 前缀 `/api/v1/`
- ✅ 统一响应格式 `{ "data": ... }` / `{ "detail": { "code": "...", "message": "..." } }`
- ✅ 蛇形命名（数据库、API 字段、Python 代码）
- ✅ 密码 bcrypt 哈希（通过 `security.py` 的 `get_password_hash`）
- ✅ JWT 令牌生成（通过 `security.py` 的 `create_access_token`/`create_refresh_token`）
- ✅ scoped CSS 组件样式，CSS 变量引用
- ✅ 无外部 UI 库
- ✅ 无 WebSocket/SSE
- ✅ 注册端点无认证要求

### References

- [Source: `epics.md` — Story 1.4 验收条件] — 全部 5 条 AC + API 规范
- [Source: `epics.md` — FR-2] — 用户凭邀请码注册需求详情
- [Source: `architecture.md` — 项目目录结构] — 后端 models/schemas/services/endpoints 分层
- [Source: `architecture.md` — 认证方案] — JWT access 30min + refresh 7d、passlib[bcrypt]
- [Source: `architecture.md` — 统一响应格式] — `{ "data": ... }` / `{ "detail": { "code": "...", "message": "..." } }`
- [Source: `architecture.md` — HTTP 状态码映射] — 201 创建成功、400 业务错误、422 校验错误
- [Source: `project-context.md` — 命名规范] — DB snake_case 复数、API snake_case、PascalCase 组件
- [Source: `project-context.md` — security.py] — `get_password_hash()`, `create_access_token()`, `create_refresh_token()`
- [Source: `project-context.md` — deps.py] — `get_current_user` 从 JWT payload 的 `sub` 提取 username
- [Source: `EXPERIENCE.md` — 微文案] — 注册相关错误提示
- [Source: `EXPERIENCE.md` — 无障碍要求] — focus ring、触摸目标、aria-live
- [Source: `Story 1.3` — Dev Notes] — InviteCode 模型设计、服务层模式、测试基础设施
- [Source: `Story 1.3` — Review Findings] — deps.py JWT 处理模式、前端错误处理、a11y 模式

## Dev Agent Record

### Previous Story Intelligence

**Story 1.3 已完成（邀请码系统）：**
- ✅ InviteCode 模型：code(unique 8char), status(unused/used/disabled), bound_username, bound_qq, created_at
- ✅ 管理端 API：GET/POST/PATCH `/api/v1/admin/invite-codes`
- ✅ `get_current_admin` 依赖注入（占位—真实 User 模型在 Story 1.5a）
- ✅ InviteCodeTable 前端组件：搜索、表格、复制、失效二次确认
- ✅ 测试：14 个 pytest 全部通过（SQLite in-memory）
- ✅ Alembic 迁移已应用

**Review 学习（Story 1.3）：**
- `ExpiredSignatureError` 与 `JWTError` 需区分处理
- 搜索 debounce 在组件卸载时需清除定时器
- 前端尝试操作失败时的错误处理需用可选链（optional chaining）
- 状态字段添加注释约束
- 操作按钮触摸目标至少 44px
- a11y：aria-label 需完整描述功能

**当前项目状态：**
- `deps.py` 返回的 user 对象是 `{"username": ..., "is_admin": False}` 字典（不查 DB）— 本文不依赖
- 前端 `authStore` 已有基础方法（setUser, setTokens, logout, isLoggedIn, isAdmin）
- 前端 `client.ts` 已有 Axios 拦截器（localStorage 读写、401 尝试 refresh、失败清除）
- 注册路由已在 `router/index.ts` 配置为 `/register`
- 管理后台（InviteCodesPage, InviteCodeTable）在 Story 1.3 已完成

### Completion Notes

**后端实现（Tasks 1-5）：**
- ✅ 创建 `User` 模型：username(unique), password_hash(bcrypt), qq, invite_code, is_admin(default False), timestamps
- ✅ 更新 `models/__init__.py`：注册 User 模型以支持 Alembic autogenerate
- ✅ 创建手动 Alembic 迁移 `002_create_users_table.py`
- ✅ `RegisterRequest` Pydantic schema：username(3-20), password(6-128), qq(5-20), invite_code(8) + field validators
- ✅ `auth_service.register()`：邀请码验证→用户名检查→密码哈希→创建用户→绑定邀请码→JWT 令牌生成
- ✅ `POST /api/v1/auth/register` 端点：无认证要求，返回 201 + tokens + user info
- ✅ 8 个 pytest 全部通过：覆盖正常注册、邀请码无效/已失效/已使用、用户名重复、密码过短、字段缺失

**前端实现（Tasks 6-8）：**
- ✅ `types/auth.ts`：RegisterRequest, RegisterResponse(access_token, refresh_token, user), UserInfo 接口
- ✅ `api/auth.ts`：`register()` 调用封装
- ✅ `RegisterPage.vue`：完整注册表单（用户名/密码/QQ/邀请码 4 字段 + 表单验证 + 错误展示 + loading 状态）
- ✅ `authStore.ts`：新增 `register()` action 和 `restoreSession()` 初始化方法
- ✅ 注册成功后保存令牌到 authStore + localStorage，自动跳转首页
- ✅ 前端表单校验：非空、密码 >=6 位、邀请码 8 位
- ✅ 移动端适配：min-height: 100dvh、触摸目标 >= 44px
- ✅ 无障碍：label 绑定、aria-live、aria-invalid、focus ring
- ✅ Vite 构建成功（113 模块，RegisterPage 独立 chunk 4.24 kB）

**端到端验证（Task 9）：**
- ✅ 22 个 pytest 全部通过（8 个新增 + 14 个已有），零回归
- ✅ TypeScript 编译通过（vue-tsc --noEmit）
- ✅ Vite 生产构建成功

### File List

**NEW:**
- `backend/app/models/user.py` — User SQLAlchemy model (10 columns)
- `backend/app/schemas/auth.py` — RegisterRequest/RegisterResponse + auth schemas
- `backend/app/services/auth_service.py` — register() business logic
- `backend/app/api/v1/endpoints/auth.py` — POST /api/v1/auth/register endpoint
- `backend/alembic/versions/002_create_users_table.py` — Alembic migration
- `backend/tests/test_auth.py` — 8 tests (error branches + success + JWT validation)
- `frontend/src/types/auth.ts` — Auth TypeScript type definitions
- `frontend/src/api/auth.ts` — Auth API call wrapper (register)

**UPDATE:**
- `backend/app/models/__init__.py` — Imported User model
- `backend/app/api/v1/__init__.py` — Registered auth router
- `frontend/src/stores/authStore.ts` — Added register() action + restoreSession()
- `frontend/src/pages/RegisterPage.vue` — Full registration form (replaced placeholder)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — Status update

## Review Findings

### Patch

- [x] [Review][Patch] `db.flush()` 缺少 IntegrityError 保护 [auth_service.py:92] — 已修复：添加 `try/except IntegrityError` 捕获，返回 USERNAME_EXISTS
- [x] [Review][Patch] `authStore.restoreSession()` 从未被调用 [authStore.ts:33] — 已修复：在 `App.vue` 的 `onMounted` 中调用 `restoreSession()`

### Defer

- [x] [Review][Defer] `response_model=dict` 模式 — 沿用已有代码模式（admin.py 同样使用），非本次变更引入。已在 deferred-work.md 记录
- [x] [Review][Defer] Service 层直接 raise HTTPException — 沿用已有模式（invite_code_service.py 同样做法），非本次变更引入
- [x] [Review][Defer] 测试依赖覆盖清理保护 — 测试中途失败可能残留 override，但测试间隔离良好，低风险
