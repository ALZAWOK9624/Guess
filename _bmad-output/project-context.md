---
project_name: 'guess'
user_name: 'tkd'
date: '2026-06-12'
sections_completed:
  ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'code_quality', 'workflow', 'critical_rules']
status: 'complete'
rule_count: 80
optimized_for_llm: true
---


# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

| Layer | Technology | Version | Notes |
|-------|-----------|---------|-------|
| Frontend Framework | Vue 3 | ^3.5.34 | Composition API + `<script setup>` |
| Build Tool | Vite | ^8.0.12 | HMR, vue plugin |
| Language | TypeScript | ~6.0.2 | Strict mode |
| State Management | Pinia | ^2.3.1 | `use{Name}Store` pattern |
| Router | Vue Router 4 | ^4.6.4 | Lazy loaded routes |
| HTTP Client | Axios | ^1.17.0 | Interceptors for auth/refresh |
| CSS | CSS Variables + scoped CSS | — | JRA design system, no UI library |
| Package Manager | pnpm | ^9+ | Frontend only |
| Backend Framework | FastAPI | >=0.110 | Async native |
| ORM | SQLAlchemy 2.0 | >=2.0 | Async mode with asyncpg |
| Migration | Alembic | >=1.13 | Async template (`-t async`) |
| Database | PostgreSQL 16 | Docker image `postgres:16-alpine` | Local dev via Docker Compose |
| Auth | JWT (python-jose) | >=3.3 | access_token 30min + refresh 7d; `ExpiredSignatureError` vs `JWTError` handled separately |
| Password Hashing | passlib[bcrypt] | >=1.7 | CryptContext |
| Async Driver | asyncpg | >=0.29 | — |
| Python | Python | >=3.12 | — |
| Testing (Backend) | pytest + pytest-asyncio + aiosqlite | >=8 / >=0.23 / >=0.19 | `asyncio_mode = auto`; in-memory SQLite for isolated tests |
| Testing (Frontend) | vitest | — | Optional, not yet configured |
| Container | Docker Compose | — | PostgreSQL only; frontend/backend run locally |

## Critical Implementation Rules

### Language-Specific Rules

**TypeScript/Vue:**
- Component files: **PascalCase** (`RaceCard.vue`), non-component: **camelCase** (`useAuth.ts`, `apiClient.ts`)
- Pinia stores: `use{Name}Store` pattern (`useRaceStore`, `useAuthStore`)
- Page components must be **lazy loaded** via dynamic `import()` in router
- Vue Router: `createWebHistory()` — no hash mode
- TypeScript types in `src/types/`, organized by domain (auth.ts, race.ts, horse.ts, vote.ts, leaderboard.ts)
- CSS variables: **kebab-case** (`--color-primary`, `--spacing-4`)
- API字段在前后端之间使用 **snake_case**（不转换 camelCase）
- **PageState 枚举模式**：列表页面使用 `type PageState = 'loading' | 'empty' | 'error' | 'success'`，搜索/下拉组件可使用扩展版 `'idle' | 'loading' | 'empty' | 'error' | 'success'`（`idle` 表示初始未搜索状态，下拉隐藏）。骨架屏显示 loading 态，精确微文案显示 empty 态，"加载失败，请刷新重试"+刷新按钮显示 error 态。
- `RaceCard.vue` 支持 `skeleton` prop，未来故事可直接使用 `<RaceCard skeleton />` 渲染骨架屏。
- `HorseSearchSelect.vue` 使用 `defineModel<Horse[]>('selectedHorses')` 实现 v-model 双向绑定 — 新增组件应优先使用 `defineModel` 替代手动 `emit('update:...')` 模式。
- `HorseDetailCard.vue` 用于展示马匹 10 属性快照数据，接收 `snapshotData` prop（可空，通过 `withDefaults` 提供默认值）。
- `GradeBadge.vue` 用于展示比赛等级徽章：G1（金色底#B8960C）、G2_JPN1（灰色底#6B7280）、YOUNG_G1（亮绿底#2D7A4F）、CUSTOM（灰色底虚线边框）。接收 `grade: string` prop。
- `StatusBadge.vue` 用于展示比赛状态胶囊：voting（绿底#2D7A4F）、locked（灰底#6B7280 + 🔒）、settled（深绿底#0D3A1F + ✓）。接收 `status: string` prop。
- `ConfirmDeleteModal.vue` 可复用删除确认弹窗组件，接收 `title`, `itemName`, `message`, `loading` props，emit `confirm` / `cancel`。使用 `<Teleport to="body">` + `role="dialog"` + `aria-modal` + Esc 关闭 + 遮罩层点击关闭。不可点击遮罩层外部关闭（防误触）。
- `CreateRacePage.vue` 使用 **grade radio selector** 模式（G1 / G2·JPN1 / 2岁G1 / 自定义），自定义等级时展开显示积分列表和扣分规则输入框。
- 全局 `@keyframes skeleton-shimmer` 定义在 `base.css` 中，所有骨架屏复用此动画。

**Python/FastAPI:**
- Files and variables: **snake_case** (`get_current_user`, `race_service.py`)
- DB table names: **snake_case plural** (`users`, `races`, `horses`, `invite_codes`)
- All endpoints/services use `async def` — no sync endpoints
- API prefix `/api/v1/` for all endpoints
- Response format: success `{"data": ...}`, error `{"detail": {"code": "ERROR_CODE", "message": "..."}}`
- Endpoints only orchestrate — all business logic in `services/`
- DB session via `Depends(get_db)` from `deps.py`
- SQLAlchemy model columns use `mapped_column` type annotations
- pytest: `asyncio_mode = auto` in pyproject.toml

### Framework-Specific Rules

**Vue 3:**
- All components: `<script setup lang="ts">` Composition API
- Styles: **scoped CSS** + CSS custom properties (no UI library)
- Layout components in `src/layouts/`, page components in `src/pages/`, reusable components in `src/components/`
- Composable functions in `src/composables/` (`useAuth.ts`, `useVote.ts`, `useDragSort.ts`)
- Admin routes prefixed `/admin/`, using `AdminLayout` with 240px sidebar
- Auth guard implementation in `router/index.ts`: `beforeEach` with `useAuthStore()` for three guard layers:
  1. `isAdmin` → redirect to home for non-admin users
  2. `requiresAuth` → redirect to `/login?redirect={path}` for unauthenticated users
  3. Guest pages (login/register/reset-password) → redirect to home for logged-in users
- **RouteMeta must be extended** for custom meta fields used in guards: add `declare module 'vue-router' { interface RouteMeta { requiresAuth?: boolean; isAdmin?: boolean } }` in router/index.ts. This avoids `as Record<string, unknown>` type assertions.
- Guest page name list (`guestPageNames: string[]`) extracted to module-level constant in router/index.ts — NOT defined inside beforeEach.
- `@` path alias configured in both `vite.config.ts` and `tsconfig.app.json` — use `@/pages/`, `@/components/`, etc.
- Responsive navigation via `AppLayout` (global wrapper in `App.vue`): desktop top nav (≥768px, green bg) and mobile bottom nav (<768px, with SVG icons + text). Both hidden on admin routes via `v-if="!isAdminRoute"`
- `safe-area-inset-bottom` applied via `viewport-fit=cover` meta + CSS `env(safe-area-inset-bottom)` — always add to mobile fixed elements
- `prefers-reduced-motion: reduce` respected globally in `base.css` — overrides all animations/transitions. 全局 `scroll-behavior: smooth` 也被覆盖为 `auto`。
- `*:focus-visible` 全局统一样式在 `base.css` 中定义（2px 竞马绿 outline + 2px offset），所有可聚焦元素自动继承。组件内如需自定义 focus 样式，使用 scoped CSS 覆盖。
- **ARIA combobox 模式**：搜索下拉组件（如 `HorseSearchSelect.vue`）必须遵循 combobox 无障碍模式：`role="combobox"` + `:aria-expanded="showDropdown"`（动态绑定，不能硬编码 `"false"`）+ `aria-controls` 指向 listbox + `role="listbox"` + `role="option"` + `aria-selected`。`aria-expanded` 必须响应式绑定到下拉展开状态。
- `AdminLayout` sidebar (`z-index: 200`): desktop fixed 240px, mobile hamburger-triggered overlay with body scroll lock

**FastAPI:**
- App entry: `app/main.py` with `lifespan` for DB engine lifecycle
- Config: `app/core/config.py` via Pydantic Settings (reads from `.env`)
- Dependencies: `app/api/deps.py` — `get_db` (session), `get_current_user` (queries DB → User ORM), `get_current_admin` (requires admin)
- Auth check: `get_current_user` returns `None` for guests (no token), raises `TOKEN_EXPIRED` for expired tokens, `INVALID_TOKEN` for invalid tokens, `NOT_AUTHENTICATED` for valid token but user not found in DB. Returns full `User` ORM object.
- Admin check: `get_current_admin` depends on `get_current_user`, checks `user.is_admin` ORM property, raises 403 `FORBIDDEN` for non-admins
- Auth endpoints: `POST /api/v1/auth/login` (returns access_token + refresh_token + user), `POST /api/v1/auth/refresh` (returns new access_token from valid refresh_token). Both unauthenticated.
- Race endpoints (`endpoints/races.py`): `GET /api/v1/races` (public, list), `GET /api/v1/races/{id}` (public, detail with snapshots), `POST /api/v1/races` (admin, create), `PATCH /api/v1/races/{id}` (admin, edit only voting), `DELETE /api/v1/races/{id}` (admin, non-settled only).
- Endpoints: `app/api/v1/endpoints/` — one file per domain (auth, races, horses, votes, results, leaderboard, admin)
- API router: `app/api/v1/__init__.py` creates the APIRouter and includes all endpoint routers; `main.py` calls `app.include_router(api_v1_router)`
- Business logic: `app/services/` — one service per domain; uses `db.flush()` + `get_db` auto-commit pattern
- Data models: `app/models/` — SQLAlchemy declarative models extending `Base`
- **CRITICAL**: `models/__init__.py` MUST import `Base` from `app.core.database`, NOT redefine it. Alembic `env.py` uses `from app.core.database import Base` as its metadata source — duplicate Base classes cause migrations to miss models.
- CORS: configured in `main.py` (TODO: tighten for production deployment)

### Testing Rules

**Backend (pytest):**
- Config: `asyncio_mode = auto` in `pyproject.toml`, `testpaths = ["tests"]`
- Test directory: `backend/tests/`, one file per domain (`test_scoring_engine.py`, `test_auth.py`, etc.)
- `conftest.py` provides shared fixtures:
  - `db_session` — in-memory SQLite engine (`sqlite+aiosqlite:///:memory:`) with `StaticPool`, tables created via `Base.metadata.create_all`, engine disposed after each test
  - `async_client` — `httpx.AsyncClient` with `ASGITransport` pointing to the app, `get_db` overridden with `db_session`. Automatically clears `dependency_overrides` after each test
- For new test files, import shared fixtures from `conftest.py`; for API integration tests, use `async_client` fixture to automatically get DB injection
- Scoring engine (`scoring_engine.py`) must be pure function, zero external dependencies — unit test only
- HTTP integration tests use `httpx.AsyncClient` with FastAPI's `TestClient`
- All async tests run with `pytest-asyncio`

**Frontend (vitest):**
- Not yet configured — planned for future stories
- Test file convention: `src/__tests__/{name}.test.ts`

**Coverage expectation:**
- Scoring engine: 100% branch coverage for all 4 rule types (G1, G2, 2Y-G1, custom) + edge cases
- Service layer: cover all business logic paths (CRUD, search, error branches)
- Endpoint layer: integration tests for main flows + error cases (use dependency overrides for auth)

### Code Quality & Style Rules

**Naming conventions (must follow):**

| Scope | Convention | Example |
|-------|-----------|---------|
| Python files/variables | snake_case | `get_current_user()`, `auth_service.py` |
| Database table names | snake_case plural | `users`, `races`, `horses`, `invite_codes` |
| DB columns / foreign keys | snake_case | `user_id`, `race_name`, `created_at` |
| TS/Vue component files | PascalCase | `RaceCard.vue`, `AdminLayout.vue`, `InviteCodeTable.vue` |
| TS non-component files | camelCase | `useAuth.ts`, `apiClient.ts`, `authStore.ts` |
| TS functions/variables | camelCase | `getUserData()`, `currentUser` |
| Pinia stores | `use{Name}Store` | `useAuthStore`, `useRaceStore` |
| CSS custom properties | kebab-case | `--color-primary`, `--spacing-4` |
| API endpoints | plural REST | `/api/v1/races`, `/api/v1/horses` |
| API JSON fields | snake_case (frontend & backend consistent) | `user_id`, `race_name` |

**Code organization:**
- Backend: `endpoints/` (HTTP orchestration only) → `services/` (business logic) → `models/` (data models)
- Frontend: `pages/` → `components/` → `composables/` + `stores/` + `api/` + `types/`
- Styles separated into `variables.css` / `base.css` / `utilities.css`
- API calls encapsulated in `src/api/` — one file per domain
- TypeScript types in `src/types/` — one file per domain

**Dates:** ISO 8601 strings (`2026-06-09T15:00:00Z`)
**Null handling:** Use `null`, never empty strings or omitted fields

### Development Workflow Rules

**Git:**
- Repo initialized with initial commit `9e8be22` — `feat: project initialization scaffold`
- `.gitignore` excludes: `node_modules/`, `__pycache__/`, `.env`, `*.pyc`, `venv/`, `.vscode/`, `.idea/`, `dist/`, `.DS_Store`
- Story-driven: each story flows `backlog` → `ready-for-dev` → `in-progress` → `review` → `done`

**Local development:**
- PostgreSQL: `docker compose up -d` (port 5432)
- Backend: `cd backend && uvicorn app.main:app --reload` (port 8000)
- Frontend: `cd frontend && pnpm dev` (port 5173)
- API proxy: frontend Vite proxies `/api` → `http://localhost:8000`
- API docs: `http://localhost:8000/docs` (Swagger UI)

**Production deployment:**
- VPS + Docker Compose (Nginx reverse proxy + API + PostgreSQL)
- Config via `.env` + Pydantic Settings
- CI: GitHub Actions (not yet configured)

### Critical Don't-Miss Rules

**Anti-patterns (must NOT do):**
- Endpoints must NOT contain business logic — delegate to `services/`
- Do NOT convert API fields to camelCase on frontend — keep snake_case consistent
- Do NOT use sync endpoints — all FastAPI endpoints must be `async def`
- Do NOT add external UI libraries — use custom JRA components + CSS variables
- Do NOT use WebSocket/SSE — poll or optimistic updates only
- Do NOT implement OAuth/3rd-party login — username + password + invite code only
- Do NOT implement dark mode — v1 is light mode only
- Do NOT wrap admin routes with AppLayout nav — AppLayout already hides desktop header and mobile nav on `/admin` paths via `v-if="!isAdminRoute"`
- Do NOT use `!important` globally except in utility classes (`.hidden`, `.mobile-only`, `.desktop-only`) and reduced-motion override
- **Do NOT import `useAuthStore` in `client.ts`** — circular dependency (authStore → api/auth.ts → client.ts). Auth token source of truth is **localStorage**, read by request interceptor. Store's `accessToken` ref is synced via `persistAuth()`/`clearAuth()`/`restoreSession()`.
- Do NOT use bare `catch` blocks on async functions — always use `catch (err)` to enable error differentiation. Future stories should follow the async/await + structured error handling pattern.
- Do NOT duplicate `@keyframes skeleton-shimmer` in component scoped styles — use the global animation from `base.css` instead.

**Security:**
- JWT secrets (`SECRET_KEY`, `JWT_SECRET`) MUST be changed from defaults before production
- CORS must be tightened for production (methods, headers)
- Login failure returns generic error: `"用户名或密码错误"` — no field-specific leak. However, LoginPage.vue catch block also handles Network Error (→ "网络错误，请重试"), 422 validation errors (→ field-level messages), and 500 (→ "服务器错误，请稍后重试").
- Passwords hashed via bcrypt (passlib CryptContext)
- Guests are read-only — voting requires authentication
- Admin seed account: `app/utils/seed.py` creates default admin (username: `admin`, password: `admin123`, `is_admin=True`) on app startup. Idempotent — skips if already exists. Protected with `IntegrityError` guard for concurrent startup.

**Performance:**
- No Redis/cache layer needed for v1 — direct DB queries suffice for ~100 users
- Route lazy loading configured (Vite auto-splits)
- No virtual scroll needed

**Edge cases:**
- Race horse data uses **snapshot** mechanism — horse attributes at creation time are frozen in `RaceHorse.snapshot_data` JSON. Race detail pages read from snapshot_data, NOT the live Horse table. Editing a race does NOT update existing snapshots; new horses added via edit get fresh snapshots at add time.
- Race status machine: `voting` → `locked` → `settled` (one direction). Only `voting` races are editable. `locked` races block voting. `settled` races are final (can only modify results).
- Race grade enum: `G1`, `G2_JPN1`, `YOUNG_G1`, `CUSTOM`. Custom scoring uses JSON format: `{"positive_scores": [10,7,5,3,2,1], "penalty_rules": [{"position": -1, "points": -5}]}`.
- Settled races cannot be deleted — only result modification with full rollback/recalculate. `voting` 和 `locked` 状态的比赛可以删除（含级联删除投票记录）。删除操作需要管理员权限和二次确认弹窗，使用 `ConfirmDeleteModal` 组件。
- `DashboardPage.vue`（`/admin` 路由）为管理后台比赛列表主页，显示所有比赛及其 GradeBadge/StatusBadge/日期/参赛数，提供「编辑」（跳转 `/admin/races/:id/edit`）和「删除」（仅非已结算比赛可见）操作按钮。使用 PageState 枚举模式管理 loading/empty/error/success 状态。
- DNF/scratched horses score 0 points and are excluded from deduction calculation denominators
- Custom scoring rules apply only to the current race — not saved as templates
- Password reset uses **invite_code bound_username** as verification (no email/phone) — all failure cases (user not found, invite_code mismatch, disabled code) return the same `INVITE_CODE_MISMATCH` error to prevent user enumeration
- ResetPasswordPage uses a **two-step form**: step 1 collects username + invite_code (frontend-only validation), step 2 collects new password (triggers API call). 400 errors fall back to step 1.

**Service & DB patterns:**
- `flush()` 后必须调用 `refresh()` 才能读取 `server_default`/`onupdate` 字段值（如 `created_at`、`updated_at`），否则 Pydantic `model_validate()` 会报 `MissingGreenlet` 错误。所有 CRUD 服务的 create/update 方法必须遵循 `flush()` → `refresh()` → return 模式。
- Pydantic schemas：PATCH endpoint 使用的 Update schema（如 `HorseUpdate`）必须包含与 Create schema（如 `HorseCreate`）相同的 `@field_validator`，包括 `.strip()` 处理——因为用户可通过 API 直接调用 PATCH 绕过前端校验。
- **PATCH 防 null 覆盖模式**：在 `update_race` 等 PATCH 服务中，`data.model_dump(exclude_unset=True)` 后必须过滤 `None` 值：`update_data = {k: v for k, v in update_data.items() if v is not None}`。否则客户端发送 `{"name": null}` 会覆盖数据库字段为 null 导致 500 错误。同时前端编辑页应通过差异检测**仅发送变更的字段**（参考 `EditRacePage.vue` 中 `getChangedHorseIds()` + `initialValues` 比较模式）。
- **手动编辑追踪模式**：Horse 模型有 `manually_updated_fields` JSON 字段（存储字段名列表），`horse_service.update_horse()` 自动追踪手动编辑的字段（`name` 和 `manually_updated_fields` 自身被排除）。自动更新框架 `auto_update_service.apply_auto_updates()` 检查此列表：在列表中的字段跳过更新（手动优先），不在列表中的字段更新并记录到 `HorseAutoUpdateLog`。管理员可通过 `POST /api/v1/horses/{id}/reset-auto-protection` 清空保护列表。
- **事务原子性模式**：`apply_auto_updates` 遵循"先全部验证再批量更新"模式——先验证所有 horse_id 存在，再逐个更新 + flush + refresh。调用方必须在同一事务中包裹此调用。
- **字段名校验模式**：通过 `inspect(Horse).columns` 获取有效列名集合，在 `apply_auto_updates` 中验证 `field_name` 是否有效，无效字段返回 400 `INVALID_FIELD`。避免 `setattr` 动态创建属性导致静默丢失更新。
- **变更日志模式**：`HorseAutoUpdateLog` 模型记录每次自动更新的字段级变更（old_value/new_value 为 Text 类型避免截断），`trigger_source` 标记触发来源（v1 固定 "settlement"）。外键：`horse_id` CASCADE, `race_id` SET NULL。
- **Alembic 迁移枚举经验**：使用 `sa.Enum` 创建 PostgreSQL 枚举时，SQLAlchemy 默认使用 Python enum 的**成员名**（大写）作为数据库枚举值。手写迁移创建枚举时需保持大小写一致。推荐使用 `op.execute("CREATE TYPE ... AS ENUM (...)")` + `ENUM(..., create_type=False)` 模式以实现幂等迁移。

**Frontend patterns:**
- 管理后台 CRUD 页面使用 `<Teleport to="body">` 模态框进行创建/编辑操作，搜索框使用 300ms 防抖（`watch(search, debouncedSearch)` + `setTimeout`）。
- **PATCH 编辑模式的关键模式**：`handleSave` 在编辑时必须按字段逐一比较当前值与原始值的差异，**仅发送变更的字段**，而非发送所有字段为 `null`。否则后端 `exclude_unset=True` 无法区分"用户未修改"和"用户将某字段清空为 null"——发送 `null` 会覆盖数据库中的已有值。参考实现：`frontend/src/pages/admin/HorsesPage.vue` 中的 `handleSave`。
- 新建数据后不推荐 `unshift`，应 `push` 后按显示顺序 `sort()` 避免与后端排序不一致导致的视觉跳跃。

---

## Usage Guidelines

**For AI Agents:**
- Read this file before implementing any code
- Follow ALL rules exactly as documented
- When in doubt, prefer the more restrictive option
- Update this file if new patterns emerge

**For Humans:**
- Keep this file lean and focused on agent needs
- Update when technology stack changes
- Review quarterly for outdated rules
- Remove rules that become obvious over time

Last Updated: 2026-06-12 (Epic 2 done + retrospective, migration enum uppercase fix)
