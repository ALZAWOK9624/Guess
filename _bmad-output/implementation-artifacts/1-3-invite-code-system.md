---
baseline_commit: 1399d094fbb4b8928820f4cb53fe625011c1b35b
---

# Story 1.3: 邀请码系统

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **管理员**,
I want **在管理后台生成和管理邀请码**,
So that **我可以控制谁可以注册加入圈子**。

## Acceptance Criteria

1. **Given** 管理员已登录
   **When** 访问 `/admin/invite-codes`
   **Then** 页面显示 InviteCodeTable 组件，表格列：邀请码 / 绑定状态 / 绑定用户名 / QQ号 / 操作（复制、失效）
   **And** 管理员可按用户名、邀请码、QQ号三个维度搜索

2. **Given** 管理员在邀请码管理页
   **When** 点击「生成邀请码」
   **Then** 系统生成一个唯一 8 位字母数字组合的邀请码，状态为「未绑定」
   **And** 新生成的码出现在表格顶部
   **And** API `POST /api/v1/admin/invite-codes` → 201

3. **Given** 管理员选中一个「未绑定」的邀请码
   **When** 点击「失效」
   **Then** 该邀请码状态变为「已失效」
   **And** 用户尝试用已失效的邀请码注册时拒绝并提示
   **And** API `PATCH /api/v1/admin/invite-codes/{code}` 更新状态

4. **Given** 管理员需查询用户绑定信息
   **When** 搜索用户名或 QQ 号
   **Then** 显示该用户绑定的邀请码和 QQ 号

5. **Given** 后端 API
   **When** `GET /api/v1/admin/invite-codes`（支持 `?search=xxx` 模糊搜索码/用户名/QQ）
   **Then** 返回所有邀请码列表（含绑定状态）
   **And** `POST /api/v1/admin/invite-codes` 生成新码
   **And** `PATCH /api/v1/admin/invite-codes/{code}` 更新状态为失效

6. **Given** 已绑定的邀请码
   **When** 管理员尝试将其失效
   **Then** 拒绝操作，提示「该邀请码已绑定用户，无法失效」

## Tasks / Subtasks

- [x] Task 1: 后端数据模型与数据库迁移 (AC: #5)
  - [x] 创建 `backend/app/models/invite_code.py` — InviteCode 模型（code=unique 8char, status=unused/used/disabled, bound_username, bound_qq, created_at）
  - [x] 创建 Alembic 迁移：`001_create_invite_codes_table.py`
  - [x] 在 `models/__init__.py` 中注册 InviteCode 模型以支持 autogenerate

- [x] Task 2: 后端邀请码工具函数 (AC: #2)
  - [x] 创建/更新 `backend/app/utils/invite_code.py` — `generate_invite_code()` 生成 8 位字母数字（大写+数字，排除易混淆字符 O/0/I/1）
  - [x] 确保生成的码在库中唯一（重试机制）

- [x] Task 3: 后端 Pydantic Schemas (AC: #5)
  - [x] 创建 `backend/app/schemas/invite_code.py` — InviteCodeResponse + InviteCodeListResponse
  - [x] 统一响应格式：成功 `{"data": {...}}`，列表 `{"data": [...]}`

- [x] Task 4: 后端服务层 (AC: #5)
  - [x] 创建 `backend/app/services/invite_code_service.py` — `get_invite_codes(db, search)`, `create_invite_code(db)`, `invalidate_invite_code(db, code)`
  - [x] `get_invite_codes` 支持按 code/username/qq 模糊搜索
  - [x] `invalidate_invite_code` 仅允许对 status=unused 的码操作，已绑定的返回错误

- [x] Task 5: 后端 API 端点 — 依赖注入 & 管理权限 (AC: #5)
  - [x] 更新 `backend/app/api/deps.py` — 添加 `get_current_admin` 依赖注入
  - [x] 创建 `backend/app/api/v1/endpoints/admin.py` — GET/POST/PATCH 三个端点
  - [x] 所有管理端点使用 `Depends(get_current_admin)` 保护
  - [x] 在主 router 中注册 admin endpoints

- [x] Task 6: 前端类型定义 (AC: #1)
  - [x] 创建 `frontend/src/types/admin.ts` — 添加 InviteCode 接口（code, status, bound_username?, bound_qq?, created_at）

- [x] Task 7: 前端 API 层 (AC: #1)
  - [x] 创建 `frontend/src/api/client.ts` — Axios 实例 + auth 拦截器
  - [x] 创建 `frontend/src/api/admin.ts` — getInviteCodes, createInviteCode, invalidateInviteCode

- [x] Task 8: 前端 InviteCodeTable 组件 (AC: #1, #3, #4)
  - [x] 创建 `frontend/src/components/InviteCodeTable.vue` — 表格组件，支持搜索框 + 表格展示
  - [x] 表格列：邀请码 / 绑定状态（未绑定/已绑定/已失效）/ 绑定用户名 / QQ号 / 操作
  - [x] 操作列：复制按钮（所有码可复制）+ 失效按钮（仅未绑定码）
  - [x] 搜索框支持在码/用户名/QQ三个维度搜索
  - [x] 移动端表格水平滚动支持（`overflow-x: auto`）

- [x] Task 9: 前端 InviteCodesPage 页面 (AC: #1)
  - [x] 更新 `frontend/src/pages/admin/InviteCodesPage.vue` — 页面布局 + InviteCodeTable 集成
  - [x] 页面标题 + 「生成邀请码」按钮
  - [x] 点击「生成邀请码」→ 调用 API → 新码无感插入表格顶部
  - [x] 加载状态骨架屏，网络错误提示

- [x] Task 10: 端到端验证
  - [x] 创建 Alembic 迁移文件确认表结构正确
  - [x] 手动验证 API：14 个 pytest 全部通过（创建→查询→失效→搜索→鉴权）
  - [x] 前端验证：TypeScript 编译通过，Vite 构建成功

## Dev Notes

### 要修改的文件（非新建）— 全部是 UPDATE

| 文件 | 当前状态 | 修改内容 |
|------|---------|---------|
| `backend/app/models/__init__.py` | 仅 docstring | 导入 InviteCode 模型 |
| `backend/app/api/deps.py` | 含基础 get_current_user | 添加 `get_current_admin` 依赖 |
| `backend/app/api/v1/endpoints/__init__.py` | 仅 docstring | 不需要修改（admin.py 被 router 自动发现） |
| `backend/app/api/v1/__init__.py` | 可能为空 | 确认 router 已注册 |
| `frontend/src/pages/admin/InviteCodesPage.vue` | 占位符内容 | 完整实现页面 |
| `frontend/src/api/client.ts` | Axios 实例 | 无需修改（已有基础拦截器） |
| `backend/app/main.py` | FastAPI 入口 | 确认 router 注册——已有 `app.include_router`，若未配置 admin router 则需追加 |

### 要新建的文件

| 文件 | 说明 |
|------|------|
| `backend/app/models/invite_code.py` | InviteCode SQLAlchemy 模型 |
| `backend/app/utils/invite_code.py` | 邀请码生成工具函数 |
| `backend/app/schemas/invite_code.py` | 邀请码 Pydantic schemas |
| `backend/app/services/invite_code_service.py` | 邀请码业务逻辑 |
| `backend/app/api/v1/endpoints/admin.py` | 管理端点（含邀请码 + 未来其他管理功能） |
| `backend/alembic/versions/xxxx_create_invite_codes_table.py` | Alembic migration |
| `frontend/src/components/InviteCodeTable.vue` | 邀请码表格组件 |
| `frontend/src/types/invite_code.ts` 或更新 `frontend/src/types/auth.ts` | 邀请码类型定义 |
| `frontend/src/api/admin.ts` | 管理后台 API（含邀请码 + 未来管理 API） |

### 数据模型设计

**InviteCode 表（`invite_codes`）：**

```python
class InviteCode(Base):
    __tablename__ = "invite_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(8), unique=True, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="unused")
    # status 枚举: "unused" | "used" | "disabled"
    bound_username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    bound_qq: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

### API 端点规范

```
GET  /api/v1/admin/invite-codes?search=xxx
     → 200 { "data": [ { "code": "AB12CD34", "status": "unused", "bound_username": null, "bound_qq": null, "created_at": "..." }, ... ] }
     ※ search 可选参数，模糊匹配 code / username / qq

POST /api/v1/admin/invite-codes
     → 201 { "data": { "code": "XY78ZK90", "status": "unused", ... } }
     ※ 请求体为空

PATCH /api/v1/admin/invite-codes/{code}
     → 200 { "data": { "code": "AB12CD34", "status": "disabled", ... } }
     ※ 仅允许状态为 unused 的码；已绑定的返回 400
     → 400 { "detail": { "code": "CODE_ALREADY_BOUND", "message": "该邀请码已绑定用户，无法失效" } }
     → 404 { "detail": { "code": "NOT_FOUND", "message": "邀请码不存在" } }
```

### 数据关系（Story 1.4 补充）

Story 1.3 中 InviteCode 表独立存在。User 模型中会有一个 `invite_code` 字段用于反向关联。

Story 1.4 当用户注册时：
1. 验证邀请码 status == "unused"
2. 将 InviteCode 的 status 设为 "used"，绑定 username 和 qq
3. 创建 User 记录

**当前 Stories 间的数据流：**
- Story 1.3: InviteCode 表的 CRUD（管理员侧）
- Story 1.4: 注册时读取/更新 InviteCode（用户侧）
- Story 1.5a: User 模型 + JWT 认证 + deps.py 从 DB 查用户
- Story 1.5b: 前端登录/游客交互

### 现有代码注意事项

1. **models/ 目前为空** — `backend/app/models/__init__.py` 只有 docstring。首个真实模型在 Story 1.3 创建。创建后需在 `__init__.py` 中显式导入 InviteCode，否则 Alembic autogenerate 不会检测到。

2. **deps.py get_current_user 现状** — 当前实现返回 `{"username": username, "is_admin": False}` 字典，从 JWT payload 解析且**不查询数据库**。Story 1.5a 才会实现从 DB 获取。对于 Story 1.3，需要添加 `get_current_admin` 依赖，它调用 `get_current_user` 并验证 `is_admin == True`。由于目前没有真正的 admin 用户逻辑，Story 1.3 需要：
   - 在 `deps.py` 中添加 `get_current_admin`（约定：管理员必须使用预置的 admin JWT）
   - **在 User 模型实现前（Story 1.5a），管理端点在开发测试时可通过 `Depends(get_current_admin)` 保护，测试时可通过已知的 JWT 令牌绕过**

3. **前端 authStore 现状** — 已有基础状态（user, tokens, isAdmin）。InviteCodesPage 将使用 `authStore.isAdmin` 判断权限（目前通过 AppLayout 和 AdminLayout 限制访问）。路由级守卫仍是空函数（Story 1.5b 实现）。

4. **前端 router 现状** — `/admin/invite-codes` 路由已配置，带有 `requiresAuth: true, isAdmin: true` 元数据。路由守卫 `beforeEach` 为空——到达后台页面的权限检查需等 Story 1.5b。

5. **Alembic 配置** — 使用 `alembic init -t async` 初始化，`env.py` 已配置指向 `app.models.Base.metadata`。添加模型后运行 `alembic revision --autogenerate -m "create invite_codes table"` 并审查生成的迁移脚本。

### 命名规范（必须遵守）

- 表名：`invite_codes`（snake_case 复数）
- 列名：`code`, `status`, `bound_username`, `bound_qq`, `created_at`
- Python 文件：`invite_code.py`, `invite_code_service.py`
- TypeScript 类型：`InviteCode`, `InviteCodeStatus`（enum type）
- API 端点：复数 REST `/api/v1/admin/invite-codes`
- API 字段：snake_case（前后端一致）

### 前端 InviteCodeTable 组件设计要点

```vue
<template>
  <div class="invite-code-table">
    <!-- 搜索输入框 -->
    <div class="search-bar">
      <input v-model="search" placeholder="搜索邀请码、用户名或QQ号..." @input="debouncedSearch" />
    </div>

    <!-- 表格（桌面端） / 卡片列表（移动端可选） -->
    <table>
      <thead>
        <tr>
          <th>邀请码</th>
          <th>状态</th>
          <th>绑定用户</th>
          <th>QQ</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="code in inviteCodes" :key="code.code">
          <td><code>{{ code.code }}</code></td>
          <td><span class="status-badge">{{ statusLabel(code.status) }}</span></td>
          <td>{{ code.bound_username || '-' }}</td>
          <td>{{ code.bound_qq || '-' }}</td>
          <td class="actions">
            <button @click="copy(code.code)">复制</button>
            <button v-if="code.status === 'unused'" @click="invalidate(code)">失效</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
```

状态标签：
- `unused`（未绑定）→ 绿色文本 + `尚未使用`
- `used`（已绑定）→ 灰色文本 + `已绑定`
- `disabled`（已失效）→ 红色文本 + `已失效`

### 邀请码生成算法

```python
import secrets
import string

# 排除 O/0/I/1 避免混淆
ALPHABET = string.ascii_uppercase.replace('O', '').replace('I', '') + string.digits.replace('0', '').replace('1', '')

def generate_invite_code() -> str:
    return ''.join(secrets.choice(ALPHABET) for _ in range(8))
```

在 service 层确保生成的码在数据库中唯一（最多重试 10 次，否则抛异常）。

### 微文案（必须精确匹配）

| 场景 | 文案 |
|------|------|
| 邀请码生成成功 | 无 Toast/弹窗——新码直接插入表格顶部 |
| 邀请码复制 | 使用 `navigator.clipboard.writeText()` 复制到剪贴板 |
| 失效操作确认 | 弹窗二次确认「确定使邀请码 {code} 失效？该操作不可撤销。」 |
| 失效成功 | 无 Toast——码的状态即时更新为「已失效」 |
| 已绑定码失效失败 | 错误提示「该邀请码已绑定用户，无法失效」 |
| 生成失败 | 错误提示「生成邀请码失败，请重试」 |
| 加载失败 | 错误提示「加载失败，请刷新重试」+ 刷新按钮 |
| 空列表 | 「还没有邀请码。点击「生成邀请码」创建第一个。」 |

### 无障碍要求

- 搜索输入框 `<label>` 绑定，或用 `aria-label="搜索邀请码"`
- 表格使用 `<table>` + `<th scope="col">`
- 操作按钮触摸目标 ≥ 44×44px
- 所有可聚焦元素有可见 focus ring（2px `var(--color-primary)` 外描边）

### 测试标准

**后端（pytest + pytest-asyncio）：**
- 创建 `backend/tests/test_invite_codes.py`
- 测试 `generate_invite_code()` — 格式正确（8位字母数字），唯一性
- 测试 `invite_code_service.py` 各方法 — CRUD、搜索、边界条件
- 测试 API 端点 — 正常流程 + 错误分支（已绑定码失效、不存在码、搜索）
- `conftest.py` — 若有异步 DB fixtures 则使用，否则 mock

**前端（目前无 vitest 配置）：** 手动验证为主

### 架构约束检查

- ✅ 后端三层分离：endpoints → services → models
- ✅ API 前缀 `/api/v1/`
- ✅ 统一响应格式 `{ "data": ... }` / `{ "detail": { "code": "...", "message": "..." } }`
- ✅ 蛇形命名（数据库、API 字段、Python 代码）
- ✅ scoped CSS 组件样式，CSS 变量引用
- ✅ 无外部 UI 库
- ✅ 无 WebSocket/SSE
- ✅ 管理端点通过 `Depends(get_current_admin)` 保护

### References

- [Source: `epics.md` — Story 1.3 验收条件] — 全部 5 条 AC + API 规范
- [Source: `epics.md` — FR-1] — 管理员生成邀请码需求详情
- [Source: `epics.md` — Story 1.4 依赖] — 注册流程依赖邀请码验证
- [Source: `architecture.md` — 项目目录结构] — 后端 models/schemas/services/endpoints 分层
- [Source: `architecture.md` — 命名规范] — DB/API/Frontend 三层命名规范表
- [Source: `architecture.md` — API 响应格式] — 统一响应结构与 HTTP 状态码映射
- [Source: `architecture.md` — 后端分层模式] — endpoints/services/models 三层分离
- [Source: `EXPERIENCE.md` — 微文案] — 12 种场景精确文案
- [Source: `EXPERIENCE.md` — 组件模式] — 邀请码表格行为规范
- [Source: `EXPERIENCE.md` — 无障碍] — focus ring、触摸目标、语义 HTML
- [Source: `EXPERIENCE.md` — 表格响应式] — 移动端水平滚动，关键列始终可见
- [Source: `Story 1.1` — Dev Notes] — 项目已建立、Alembic 配置、目录结构
- [Source: `Story 1.2` — Dev Notes] — authStore 占位、AdminLayout + AppLayout 实现、CSS 变量系统
- [Source: `Story 1.2` — Review Findings] — 管理后台布局层级与路由注意事项

## Dev Agent Record

### Agent Model Used

Deepseek-V4-Flash

### Previous Story Intelligence

Story 1.1 已建立项目骨架和基础配置。Story 1.2 已完成 JRA 设计令牌系统、AppLayout/AdminLayout 响应式导航、authStore 占位。Story 1.5a/b 才实现真实用户认证——当前 deps.py 返回的 user 对象不含数据库记录。

**关键学习（避免重复 Story 1.1/1.2 的 review 修正）：**
- ✅ AppLayout 已在 Admin 路由上隐藏桌面端顶部导航和移动端底部导航——无需重复
- ✅ invariant: 移动端侧边栏打开时需锁定 body 滚动
- ✅ safe-area-inset-bottom 需在底部固定元素上使用 `env(safe-area-inset-bottom)`
- ✅ `viewport-fit=cover` 已在 index.html meta 中配置
- ✅ Firefox scrollbar 样式需 `scrollbar-width: thin`
- ✅ Windows High Contrast Mode focus ring 需 `@media (forced-colors: active)`
- ✅ Google Fonts 已添加 dns-prefetch
- ✅ 100dvh 浏览器兼容回退（前置 `100vh`）

### Completion Notes

**后端实现（Tasks 1-5）：**
- ✅ 创建 `InviteCode` 模型：code(unique 8char), status(unused/used/disabled), bound_username, bound_qq, created_at
- ✅ 修复 `models/__init__.py`：从 `database.py` 导入 Base，避免重复定义导致的 Alembic 无法检测模型
- ✅ 创建手动 Alembic 迁移 `001_create_invite_codes_table.py`
- ✅ 邀请码生成：8位字母数字（排除 O/0/I/1），cryptographic randomness
- ✅ 服务层：三种 API 操作 + 按 code/username/qq 模糊搜索 + unused 状态保护
- ✅ `get_current_admin` 依赖注入，Story 1.5a 后可接入真实 User 模型
- ✅ API v1 router 重构：`__init__.py` 统一注册，`main.py` 包含

**前端实现（Tasks 6-9）：**
- ✅ 创建 `api/client.ts` — Axios + JWT 拦截器（Token 刷新预置， 1.5b 完整校验）
- ✅ `InviteCodeTable.vue` — 搜索+表格+骨架屏+空状态+错误提示+复制按钮+失效确认
- ✅ `InviteCodesPage.vue` — 标题+描述+集成 InviteCodeTable
- ✅ 后端 TypeScript 类型 `admin.ts`，前端 API 封装 `admin.ts`
- ✅ Vite 构建成功（vue-tsc 编译无错误）

**测试（Task 10）：**
- ✅ 14 个 pytest 全部通过（3 unit + 5 service + 5 API + 1 authorization）
- ✅ 覆盖边界：已绑定码拒绝失效、不存在的码返回 404、未认证返回 401
- ✅ 使用 SQLite in-memory 测试数据库，不依赖 Docker PostgreSQL
- ✅ 无回归：仅有 1 个测试文件，全部通过

### Change Log

- 2026-06-10: Story implementation complete. 10 tasks, 14 tests, all passing.

### File List

**NEW:**
- `backend/app/models/invite_code.py` — InviteCode SQLAlchemy model
- `backend/app/models/__init__.py` — Restructured to import Base from database.py + InviteCode
- `backend/app/utils/invite_code.py` — Code generation utility
- `backend/app/schemas/invite_code.py` — Pydantic schemas
- `backend/app/services/invite_code_service.py` — Business logic (create, list, search, invalidate)
- `backend/app/api/v1/endpoints/admin.py` — Admin API endpoints for invite codes
- `backend/app/api/v1/__init__.py` — API v1 router with admin endpoints registered
- `backend/alembic/versions/001_create_invite_codes_table.py` — Initial Alembic migration
- `backend/tests/test_invite_codes.py` — 14 tests (unit + integration + API)
- `frontend/src/api/client.ts` — Axios instance with auth interceptors
- `frontend/src/api/admin.ts` — Admin API calls
- `frontend/src/types/admin.ts` — InviteCode TypeScript types
- `frontend/src/components/InviteCodeTable.vue` — Full table component
- `frontend/src/pages/admin/InviteCodesPage.vue` — Full page (replaced placeholder)

**UPDATE:**
- `backend/app/api/deps.py` — Added `get_current_admin` dependency
- `backend/app/main.py` — Imported and registered API v1 router
- `backend/requirements.txt` — Added aiosqlite for test database

## Review Findings

### Patch (resolved)

- [x] [Review][Patch] `ExpiredSignatureError` 与 `JWTError` 区分处理 [deps.py:27-39] — 添加 `ExpiredSignatureError` 捕获返回 `TOKEN_EXPIRED`
- [x] [Review][Patch] 前端 `handleInvalidate` catch 块安全访问 [InviteCodeTable.vue:79] — 替换为可选链访问模式
- [x] [Review][Patch] 搜索 debounce 在组件卸载时清除定时器 [InviteCodeTable.vue:46-53] — 添加 `onUnmounted` 清理
- [x] [Review][Patch] `created_at` Pydantic 模型改为 `datetime`（非可选）[schemas/invite_code.py:13]
- [x] [Review][Patch] 迁移脚本 `created_at` `nullable=False` [001_create_invite_codes_table.py:29]
- [x] [Review][Patch] 未授权测试断言精确为 `401` [test_invite_codes.py:226]
- [x] [Review][Patch] 复制按钮添加 `aria-label` [InviteCodeTable.vue:156]
- [x] [Review][Patch] 搜索框 `aria-label` 完善描述 [InviteCodeTable.vue:110]
- [x] [Review][Patch] 操作按钮触摸目标改为 44px [InviteCodeTable.vue:232]
- [x] [Review][Patch] 确认对话框文案"使"→"将" [InviteCodeTable.vue:71]
- [x] [Review][Patch] `status` 字段添加注释约束 [models/invite_code.py:13]

### Deferred

- [x] [Review][Defer] 路径参数 `{code}` 含特殊字符风险 — deferred, 当前字符集不含特殊字符
- [x] [Review][Defer] 搜索无分页 — deferred, 当前规模~100用户，v1 无需分页
- [x] [Review][Defer] LIKE 通配符 `%`/`_` 被解释 — deferred, 非安全漏洞，可后续优化
- [x] [Review][Defer] 缺少速率限制 — deferred, v1 明确不做限流
- [x] [Review][Defer] `is_admin` 硬编码为 False — deferred, 已知占位，Story 1.5a 实现真实 User 模型时修复
- [x] [Review][Defer] 缺少 `updated_at` 审计列 — deferred, 可在后续迭代中增加
- [x] [Review][Defer] `invalidate` 未防御性检查 `bound_username`/`bound_qq` — deferred, 当前业务逻辑不会产生此状态
- [x] [Review][Defer] 缺少数目类型约束（`response_model=dict`）— 不影响功能，文档增强项
- [x] [Review][Defer] 邀请码字符集 `Z/2`、`S/5` 易混淆 — deferred, UX 增强项，可用更大字体缓解
- [x] [Review][Defer] `InviteCodeListResponse` 冗余包装 — deferred, 不影响功能
- [x] [Review][Defer] `navigator.clipboard` 回退路径已废弃 — deferred, 主流浏览器仍支持
- [x] [Review][Defer] SQLite 测试无法覆盖真实 DB 并发 — deferred, 已知局限，可接受
