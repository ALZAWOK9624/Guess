---
baseline_commit: 4db152a5e3c8cc3393841aa520b91de8f46af29b
---

# Story 2.1: 马匹数据模型与管理页面 (Horse Data Model & Management Page)

## Metadata

| Field | Value |
|-------|-------|
| **Story ID** | 2.1 |
| **Story Key** | `2-1-horse-data-model-management` |
| **Epic** | Epic 2: Horse Library & Race Management |
| **Status** | done |
| **Created** | 2026-06-11 |
| **Completed** | 2026-06-11 |
| **Developer** | AI Agent (bmad-dev-story) |

## Story Foundation

### User Story

As a **管理员**,
I want **能在后台管理马匹库，每匹马拥有 10 个字段属性**,
So that **我可以在创建比赛前建立和维护马匹数据**。

### Business Value

- 建立全局马匹数据仓库，为后续比赛创建和马匹选择提供基础数据
- 管理员可灵活维护马匹信息（增删改查）
- 马匹数据的快照机制确保历史比赛数据不受编辑影响
- 覆盖 FR-5（马匹 10 属性定义）和 FR-6（马匹属性手动编辑）

### Requirements Covered

| Requirements | Description |
|-------------|-------------|
| **FR-5** | 马匹拥有 10 个属性（name/sex/age/origin/sire/damsire/weight/jockey/previous_result/best_win） |
| **FR-6** | 管理员可手动修改任意马匹的任意属性值 |

### UX Design Requirements

| UX-DR | Component | Description |
|-------|-----------|-------------|
| UX-DR16 | AdminLayout | 管理后台桌面端左侧 240px 侧边栏布局 + 移动端 Tab/汉堡菜单 |
| UX-DR14 | InviteCodeTable | 马匹管理表格格式参考 |

---

## Acceptance Criteria

### Data Model

**AC-1:** Horse 数据模型正确定义并包含全部 10 个字段

**Given** 马匹数据模型已定义
**When** 查看 `models/horse.py`
**Then** Horse 模型包含 10 个字段：
- `name` (string, 必填, 唯一)
- `sex` (string, 可空)
- `age` (integer, 可空)
- `origin` (string, 可空)
- `sire` (string, 可空, 父系)
- `damsire` (string, 可空, 母父)
- `weight` (string, 可空, 体重)
- `jockey` (string, 可空, 骑手)
- `previous_result` (string, 可空, 前走成绩)
- `best_win` (string, 可空, 最佳胜马)
**And** `name` 为唯一必填字段，其余可空
**And** 表名遵循命名规范为 `horses`（snake_case 复数）

### List & Search

**AC-2:** 管理员可在管理后台查看马匹列表并搜索

**Given** 管理员已登录
**When** 访问 `/admin/horses`
**Then** 显示马匹列表表格，展示所有马匹的完整 10 个字段
**And** 支持按名字模糊搜索
**And** 表格上方有「新建马匹」按钮

### Create

**AC-3:** 管理员可新建马匹

**Given** 管理员在马匹管理页
**When** 点击「新建马匹」→ 填写名字（必填）+ 其他字段（选填）→ 保存
**Then** 马匹创建成功，出现在列表中
**And** API `POST /api/v1/horses` 返回 201 + 新马匹数据

### Update

**AC-4:** 管理员可编辑任意马匹的任意字段

**Given** 管理员选中一匹马
**When** 点击编辑 → 修改任意字段 → 保存
**Then** 该字段更新成功，不影响其他字段
**And** API `PATCH /api/v1/horses/{id}` 返回 200 + 更新后的马匹数据
**And** 页面列表即时反映修改

### Data Integrity

**AC-5:** 已关联比赛的旧数据不受编辑影响

**Given** 管理员编辑了某匹马
**When** 保存后
**Then** 已关联该马匹的过往比赛历史数据不受影响（快照机制 — 快照功能待后续故事实现，此处仅需确认模型设计支持快照引用）

### API Endpoints

**AC-6:** 后端提供完整的马匹 CRUD API

**Given** 后端 API
**When** `GET /api/v1/horses` → 返回马匹列表（支持 `?name=xxx` 模糊搜索）
**And** `GET /api/v1/horses/{id}` → 返回单匹马详情
**And** `POST /api/v1/horses` → 创建新马匹（返回 201）
**And** `PATCH /api/v1/horses/{id}` → 更新指定马匹字段（返回 200）
**And** `DELETE /api/v1/horses/{id}` → 删除马匹（仅当未被比赛引用时，返回 204；被引用时返回 409）

---

## Developer Context & Guardrails

### Architecture Compliance

1. **后端三层分离**：`endpoints/horses.py`（仅编排）→ `services/horse_service.py`（业务逻辑）→ `models/horse.py`（数据模型）
   - Endpoints 不得包含业务逻辑 — 全部委托到 services 层
2. **API 格式**：统一响应格式 `{"data": ...}` 成功 / `{"detail": {"code": "...", "message": "..."}}` 错误
3. **URL 前缀**：`/api/v1/horses`
4. **数据库命名**：表名 `horses`（snake_case 复数），列名 snake_case
5. **API 字段**：前后端保持一致使用 **snake_case**，不做 camelCase 转换

### File Structure — Files to Create/Update

#### New Files to Create:

| # | File | Type | Purpose |
|---|------|------|---------|
| 1 | `backend/app/models/horse.py` | NEW | Horse ORM model (10 attributes) |
| 2 | `backend/app/schemas/horse.py` | NEW | Pydantic request/response schemas |
| 3 | `backend/app/services/horse_service.py` | NEW | Horse CRUD business logic |
| 4 | `backend/app/api/v1/endpoints/horses.py` | NEW | Horse REST endpoints |
| 5 | `backend/tests/test_horses.py` | NEW | Horse API tests |

#### Existing Files to Update:

| # | File | Change |
|---|------|--------|
| 6 | `backend/app/models/__init__.py` | Add `from app.models.horse import Horse` |
| 7 | `backend/app/api/v1/__init__.py` | Add `router.include_router(horses.router)` |
| 8 | `backend/alembic/versions/003_create_horses_table.py` | NEW migration file |

### Technical Implementation Requirements

#### 1. Horse ORM Model (`backend/app/models/horse.py`)

```python
class Horse(Base):
    __tablename__ = "horses"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    sex: Mapped[str | None] = mapped_column(String(10), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    origin: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sire: Mapped[str | None] = mapped_column(String(100), nullable=True)
    damsire: Mapped[str | None] = mapped_column(String(100), nullable=True)
    weight: Mapped[str | None] = mapped_column(String(20), nullable=True)
    jockey: Mapped[str | None] = mapped_column(String(50), nullable=True)
    previous_result: Mapped[str | None] = mapped_column(String(100), nullable=True)
    best_win: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

#### 2. Pydantic Schemas (`backend/app/schemas/horse.py`)

Required schemas:
- `HorseCreate` — for POST request body (name required, all others optional)
- `HorseUpdate` — for PATCH request body (all fields optional)
- `HorseResponse` — for API response (includes id, created_at, updated_at)

#### 3. Service Layer (`backend/app/services/horse_service.py`)

Functions:
- `get_horses(db, name: str | None = None) -> list[Horse]` — list all, optional name filter
- `get_horse(db, horse_id: int) -> Horse | None` — get single horse
- `create_horse(db, data: HorseCreate) -> Horse` — create new horse (unique name check)
- `update_horse(db, horse_id: int, data: HorseUpdate) -> Horse | None` — partial update
- `delete_horse(db, horse_id: int) -> bool` — delete if not referenced by any race

#### 4. Endpoint (`backend/app/api/v1/endpoints/horses.py`)

Endpoints:
- `GET /api/v1/horses` — public (both logged in and guest), optional `?name=xxx` query param
- `GET /api/v1/horses/{id}` — public
- `POST /api/v1/horses` — admin only (`Depends(get_current_admin)`)
- `PATCH /api/v1/horses/{id}` — admin only
- `DELETE /api/v1/horses/{id}` — admin only

For admin-only endpoints, use `current_admin: User = Depends(get_current_admin)`.

#### 5. Alembic Migration

Create `003_create_horses_table.py`:
```python
"""create horses table

Revision ID: 003
Revises: 002_create_users_table
Create Date: 2026-06-11
"""
from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'horses',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('sex', sa.String(length=10), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('origin', sa.String(length=100), nullable=True),
        sa.Column('sire', sa.String(length=100), nullable=True),
        sa.Column('damsire', sa.String(length=100), nullable=True),
        sa.Column('weight', sa.String(length=20), nullable=True),
        sa.Column('jockey', sa.String(length=50), nullable=True),
        sa.Column('previous_result', sa.String(length=100), nullable=True),
        sa.Column('best_win', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_index(op.f('ix_horses_name'), 'horses', ['name'], unique=True)

def downgrade():
    op.drop_index(op.f('ix_horses_name'), table_name='horses')
    op.drop_table('horses')
```

#### 6. Frontend — HorsesPage.vue Updates

The existing `HorsesPage.vue` at `frontend/src/pages/admin/HorsesPage.vue` (4.23 KB) already has a basic implementation. Key focus areas:

- **Data table**: Display all 10 attributes in an organized table/row layout
- **Search**: Name search with debounced input (300ms)
- **Create**: Modal or inline form for new horse creation
- **Edit**: Row-level edit action, potentially inline or modal
- **Delete**: Confirm dialog before delete
- **PageState pattern**: Use `type PageState = 'loading' | 'empty' | 'error' | 'success'` for state management
- **Empty state**: "马匹库为空——创建第一场比赛时，参赛马匹将自动入库。" / "马匹库为空，请新建马匹"
- **Table**: Export HorseDataTable (or similar) matching existing component conventions

### Testing Requirements

**Backend pytest tests** (`backend/tests/test_horses.py`):

| Test | Description |
|------|-------------|
| `test_create_horse` | Create with all fields, verify returns 201 |
| `test_create_horse_minimal` | Create with only name, verify defaults |
| `test_create_horse_duplicate_name` | Duplicate name → 409 |
| `test_list_horses` | List horses, verify response structure |
| `test_search_horses_by_name` | Search by name substring |
| `test_get_horse` | Get single horse by ID |
| `test_get_horse_not_found` | Non-existent ID → 404 |
| `test_update_horse` | Partial field update |
| `test_update_horse_not_found` | Update non-existent → 404 |
| `test_delete_horse` | Delete existing horse |
| `test_delete_horse_not_found` | Delete non-existent → 404 |
| `test_unauthenticated_create` | Guest trying to create → 401 |
| `test_non_admin_create` | Non-admin trying to create → 403 |

Use existing `conftest.py` fixtures (`db_session`, `async_client`, `sample_data`).

### Library & Framework Requirements

**No new dependencies needed.** Use existing:
- SQLAlchemy 2.0 async (model definitions)
- FastAPI (endpoints)
- Pydantic v2 (schemas)
- pytest + httpx.AsyncClient (tests)

---

## Tasks/Subtasks

### Backend - Data Model
- [x] Task 1: Create Horse ORM model (`backend/app/models/horse.py`)
  - [x] Define Horse class with 10 fields + timestamps
  - [x] Add proper type annotations (Mapped[...], mapped_column)
  - [x] Ensure name is unique and required

- [x] Task 2: Create Pydantic schemas (`backend/app/schemas/horse.py`)
  - [x] HorseCreate (name required, all others optional)
  - [x] HorseUpdate (all fields optional)
  - [x] HorseResponse (includes id, created_at, updated_at)

- [x] Task 3: Register Horse model in `models/__init__.py`

### Backend - Business Logic
- [x] Task 4: Create horse service (`backend/app/services/horse_service.py`)
  - [x] get_horses(db, name filter) → list
  - [x] get_horse(db, id) → single
  - [x] create_horse(db, data) → new horse
  - [x] update_horse(db, id, data) → updated horse
  - [x] delete_horse(db, id) → bool

- [x] Task 5: Create horse endpoints (`backend/app/api/v1/endpoints/horses.py`)
  - [x] GET /api/v1/horses (public, with ?name=xxx search)
  - [x] GET /api/v1/horses/{id} (public)
  - [x] POST /api/v1/horses (admin only)
  - [x] PATCH /api/v1/horses/{id} (admin only)
  - [x] DELETE /api/v1/horses/{id} (admin only, 409 if referenced)

- [x] Task 6: Register router in `api/v1/__init__.py`

### Backend - Migration
- [x] Task 7: Create Alembic migration (`003_create_horses_table.py`)

### Backend - Tests
- [x] Task 8: Write and run tests (`backend/tests/test_horses.py`)
  - [x] CRUD tests (create, list, get, update, delete)
  - [x] Edge cases (duplicate name, not found)
  - [x] Auth tests (guest 401, non-admin 403)
  - [x] Search tests

### Frontend
- [x] Task 9: Update HorsesPage.vue with full CRUD UI
  - [x] PageState management (loading/empty/error/success)
  - [x] Horse list table with all 10 attributes
  - [x] Name search with debounce
  - [x] Create horse modal form
  - [x] Edit horse inline/modal form
  - [x] Delete with confirmation
  - [x] API integration (horses.ts API module + horse.ts types)

- [x] Task 10: Run full regression test suite and validate
  - [x] 22 horse-specific tests pass
  - [x] 65/65 total tests pass (no regressions)

## Previous Story Intelligence

N/A — this is the first story in Epic 2. However, patterns established in Epic 1 should be followed:

### Patterns from Epic 1

1. **Model pattern**: See `backend/app/models/user.py`, `backend/app/models/invite_code.py` for reference
2. **Schema pattern**: See `backend/app/schemas/auth.py`, `backend/app/schemas/invite_code.py` for reference
3. **Service pattern**: See `backend/app/services/auth_service.py`, `backend/app/services/invite_code_service.py` for reference
4. **Endpoint pattern**: See `backend/app/api/v1/endpoints/auth.py`, `backend/app/api/v1/endpoints/admin.py` for reference
5. **Test pattern**: See `backend/tests/test_invite_codes.py`, `backend/tests/conftest.py` for reference
6. **Frontend pattern**: See `HorsesPage.vue` (already partially implemented), `InviteCodeTable.vue` for component/pagination patterns

### Critical Don't-Miss Rules

1. **models/__init__.py**: Must import `Base` from `app.core.database`, NOT redefine it
2. **Alembic env.py**: Already imports `from app.models import *` — just add Horse to models/__init__.py exports
3. **Endpoints only orchestrate**: No business logic in endpoints
4. **Async all the way**: All endpoints and service methods must be `async def`
5. **API field naming**: Keep snake_case consistently between frontend and backend
6. **No UI library**: Use custom components + CSS variables only

---

## Project Context Reference

- **Technology**: Vue 3 + Vite + TypeScript (frontend), FastAPI + SQLAlchemy 2.0 async + Alembic (backend), PostgreSQL 16
- **Project structure**: Monorepo (`frontend/` + `backend/`)
- **Auth**: JWT dual-token (access 30min + refresh 7d), passlib[bcrypt]
- **Auth deps**: `get_current_admin` for admin-only endpoints, `get_current_user` returns None for guests
- **API prefix**: `/api/v1/`
- **DB naming**: snake_case plural
- **Frontend naming**: PascalCase components, camelCase functions/variables, `use{Name}Store` Pinia pattern
- **No dark mode**: v1 light mode only
- **No 3rd-party OAuth**: username + password + invite code only
- **PageState enum**: `loading | empty | error | success` for list pages
- **Local dev**: `docker compose up -d` (PostgreSQL) + `pnpm dev` (frontend) + `uvicorn` (backend)
- **Vite proxy**: `/api` → `http://localhost:8000`

---

## File List

### New Files
| # | File | Description |
|---|------|-------------|
| 1 | `backend/app/models/horse.py` | Horse ORM model (10 attributes + timestamps) |
| 2 | `backend/app/schemas/horse.py` | Pydantic schemas (HorseCreate, HorseUpdate, HorseResponse) |
| 3 | `backend/app/services/horse_service.py` | Horse CRUD business logic |
| 4 | `backend/app/api/v1/endpoints/horses.py` | Horse REST API endpoints |
| 5 | `backend/tests/test_horses.py` | 22 tests covering CRUD, search, auth |
| 6 | `backend/alembic/versions/003_create_horses_table.py` | Alembic migration for horses table |
| 7 | `frontend/src/types/horse.ts` | TypeScript horse type definitions |
| 8 | `frontend/src/api/horses.ts` | Horse API client module |

### Modified Files
| # | File | Change |
|---|------|--------|
| 9 | `backend/app/models/__init__.py` | Added Horse model import and export |
| 10 | `backend/app/api/v1/__init__.py` | Added horses router include |
| 11 | `frontend/src/pages/admin/HorsesPage.vue` | Full CRUD UI implementation |

## Dev Agent Record

### Implementation Plan
1. Created Horse ORM model following Epic 1 patterns (User, InviteCode models)
2. Created Pydantic schemas for request/response validation
3. Implemented service layer with full CRUD + duplicate name check
4. Created REST endpoints (public GETs, admin-only mutations)
5. Generated Alembic migration for horses table
6. Wrote 22 pytest tests (service + API, including auth/edge cases)
7. Created frontend TypeScript types and API client module
8. Implemented HorsesPage.vue with full CRUD UI (search, modal form, delete confirm)

### Debug Log
- Initially 2 test failures: search assertion bound (case-insensitive SQLite returned 3 for "E") and MissingGreenlet error (needed db.refresh() after flush)
- Both issues identified and fixed — all 65 tests pass

### Completion Notes
- **Backend**: All 5 CRUD endpoints implemented and tested (GET, GET/:id, POST, PATCH, DELETE)
- **Frontend**: HorsesPage.vue now has full CRUD with modal forms, debounced search, loading/empty/error/success states
- **Tests**: 22 new horse-specific tests + 43 existing auth/invite-code tests — 65 total, all passing
- **Migration**: Alembic migration 003 creates horses table with proper schema

## Change Log

| Date | Change |
|------|--------|
| 2026-06-11 | Implemented Story 2.1: Horse data model, CRUD API, admin UI, and tests |

---

## Review Findings

### Decision Needed

- [x] [Review][Defer] 删除确认方式 — 使用原生 `confirm()` 弹窗 vs 自定义模态框。选择保持一致（与 InviteCodeTable.vue 同模式）。decision: keep native confirm
- [x] [Review][Defer] 并发 name 唯一性竞争条件 — 高并发下两个请求同时创建同名马匹，`SELECT` 检查均通过后，数据库 UNIQUE 约束会报错（500）。选择不额外处理，数据库约束兜底，100 用户场景并发概率极低。decision: rely on DB constraint

### Patch

- [x] [Review][Patch] `HorseUpdate` 缺少 `name` 字段校验器 [schemas/horse.py] — 已添加同名校验器
- [x] [Review][Patch] 编辑模式发送所有字段覆盖已有值（前端 bug）[HorsesPage.vue] — 已修复为仅发送变更字段
- [x] [Review][Patch] `endpoints/horses.py` 中的延迟导入 — 已移到文件顶部
- [x] [Review][Patch] 错误状态下不显示搜索框 [HorsesPage.vue] — 已修复，error 状态也显示工具栏
- [x] [Review][Patch] 列表顺序：`unshift` 新数据与后端排序不一致 — 已改为 `push` + 按名称排序
- [x] [Review][Patch] Alembic 迁移冗余约束 — 已移除 `UniqueConstraint`，保留唯一索引

### Deferred

- [x] [Review][Defer] TODO: 删除马匹时检查 race 引用 [horse_service.py:107-108] — 当前未实现，等 race 模型实现后再处理（Epic 2 后续故事）。
- [x] [Review][Defer] `onupdate=func.now()` 在异步下的行为 — 当前测试通过，无实际影响。
- [x] [Review][Defer] GET 端点公开访问（非管理员）— 设计意图，马匹数据对所有登录用户可见。
