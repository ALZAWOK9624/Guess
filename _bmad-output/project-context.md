---
project_name: 'guess'
user_name: 'tkd'
date: '2026-07-01'
story: 'horse-card-display-improvement'
sections_completed:
  ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'code_quality', 'workflow', 'critical_rules']
status: 'complete'
rule_count: 95
optimized_for_llm: true
---


# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

| Layer | Technology | Version | Notes |
|-------|-----------|---------|-------|
| Frontend Framework | Vue 3 | ^3.5.34 | Composition API + `<script setup>` |
| Build Tool | Vite | ^8.0.16 | HMR, vue plugin |
| Language | TypeScript | ~6.0.2 | Strict mode |
| State Management | Pinia | ^2.3.1 | `use{Name}Store` pattern |
| Router | Vue Router 4 | ^4.6.4 | Lazy loaded routes |
| HTTP Client | Axios | ^1.17.0 | Interceptors for auth/refresh |
| CSS | CSS Variables + scoped CSS | — | JRA design system, no UI library |
| Package Manager | pnpm | ^9+ | Frontend only; workspace uses `nodeLinker: hoisted` |
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
- `HorseDetailCard.vue` 用于展示马匹 10 属性快照数据，接收 `snapshotData` prop（可空，通过 `withDefaults` 提供默认值）。新增 `votable`、`voted`、`submitting` 三个 props 支持点击投票交互：`votable` 时显示 `cursor: pointer` + hover 高亮，`voted` 时显示金色边框 + "✓ 已投"徽章。emit `voteToggle` 事件供父组件处理投票逻辑。
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
- Admin routes prefixed `/admin/`, sharing `AppLayout` with all other pages. No separate layout — admin nav is in a dropdown menu.
- Auth guard implementation in `router/index.ts`: `beforeEach` with `useAuthStore()` guards admin routes (`isAdmin`), auth-required routes (`requiresAuth`), and guest-only pages (login/register/reset-password).
- **RouteMeta must be extended** for custom meta fields used in guards: add `declare module 'vue-router' { interface RouteMeta { requiresAuth?: boolean; isAdmin?: boolean } }` in router/index.ts. This avoids `as Record<string, unknown>` type assertions.
- Guest page name list (`guestPageNames: string[]`) extracted to module-level constant in router/index.ts — NOT defined inside beforeEach.
- `@` path alias configured in both `vite.config.ts` and `tsconfig.app.json` — use `@/pages/`, `@/components/`, etc.
- Responsive navigation via `AppLayout` (global wrapper in `App.vue`): desktop top nav (≥768px, green bg) and mobile bottom nav (<768px, with SVG icons + text). Admin users see a "管理" dropdown trigger in both navs. Admin pages share the same AppLayout — no separate layout wrapping.
- `safe-area-inset-bottom` applied via `viewport-fit=cover` meta + CSS `env(safe-area-inset-bottom)` — always add to mobile fixed elements
- `prefers-reduced-motion: reduce` respected globally in `base.css` — overrides all animations/transitions. 全局 `scroll-behavior: smooth` 也被覆盖为 `auto`。
- `*:focus-visible` 全局统一样式在 `base.css` 中定义（2px 竞马绿 outline + 2px offset），所有可聚焦元素自动继承。组件内如需自定义 focus 样式，使用 scoped CSS 覆盖。
- **ARIA combobox 模式**：搜索下拉组件（如 `HorseSearchSelect.vue`）必须遵循 combobox 无障碍模式：`role="combobox"` + `:aria-expanded="showDropdown"`（动态绑定，不能硬编码 `"false"`）+ `aria-controls` 指向 listbox + `role="listbox"` + `role="option"` + `aria-selected`。`aria-expanded` 必须响应式绑定到下拉展开状态。
- Admin nav in `AppLayout`: desktop header nav-links and mobile bottom nav both have a "管理" dropdown trigger. Dropdown shows 仪表盘/创建比赛/马匹管理/邀请码. Closes on click-outside, Escape, and route change. Desktop dropdown drops downward; mobile dropdown rises upward from bottom bar.

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
- Admin routes are top-level routes (no child layout) — they share `AppLayout` with all other pages. The nav bar has a "管理" dropdown for admin sub-navigation.
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
- `DashboardPage.vue`（`/admin` 路由）为管理后台比赛列表主页，显示所有比赛及其 GradeBadge/StatusBadge/日期/参赛数，提供「编辑」（跳转 `/admin/races/:id/edit`）、「锁定」（仅 voting 状态金色边框按钮，调用 `POST /api/v1/races/{race_id}/lock` 后原地更新 status）、「结果录入」（仅 locked/settled 状态）、「删除」（仅非已结算比赛可见）操作按钮。锁定按钮使用 `lockingId` ref 防重复点击，锁定后按钮禁用显示"锁定中…"。使用 PageState 枚举模式管理 loading/empty/error/success 状态。
- DNF/scratched horses score 0 points and are excluded from deduction calculation denominators
- Custom scoring rules apply only to the current race — not saved as templates
- Password reset uses **invite_code** only (no username needed) — looks up the bound user via `invite_code.bound_username`. All failure cases return the same `INVITE_CODE_MISMATCH` error to prevent user enumeration. ResetPasswordPage is a single-step form (invite_code + new_password).
- **邀请码系统三大变更**：
  1. **生成时绑定 QQ**：管理员在后台输入 QQ 号后点击生成邀请码，`bound_qq` 在创建时即设值，`status` 为 `unused`。
  2. **注册时校验 QQ**：`register()` 校验 `invite_code.bound_qq == request.qq`，不匹配返回 `QQ_MISMATCH`。
  3. **管理员删除级联**：`DELETE /api/v1/admin/invite-codes/{code}` 级联删除邀请码 + 绑定用户 + 用户投票（User FK CASCADE）。`unused` 码只删邀请码本身。
- **邀请码只有两种状态**：`unused`（未绑定）和 `used`（已绑定），不再有 `disabled` 状态。
- **登录三种模式**（`LoginRequest` 所有字段可选，按优先级判断）：`invite_code`（无密码，查 `bound_username` 登录）/ `qq`（+密码查 `User.qq`）/ `username`（+密码查 `User.username`）。`unused` 码返回 `"该邀请码尚未绑定用户"`，不存在的码返回 `"用户名或密码错误"`。

**Voting System 模式（Story 3.2）：**
- Vote 模型：`(user_id, race_id)` 唯一约束实现一用户一票一赛。`race_horse_id` FK 指向 `race_horses.id`（**无** CASCADE——防止编辑比赛移除马匹时静默删除投票）。`user_id` 和 `race_id` FK 有 CASCADE（用户删除或比赛删除时级联清理）。
- **投票 Upsert 防竞态模式**：`vote_service.create_or_update_vote()` 使用 SELECT → check → INSERT/UPDATE 模式，外层包裹 `try/except IntegrityError`。当并发请求同时通过 SELECT（均未找到现有投票）时，第二个 INSERT 触发唯一约束冲突，`IntegrityError` 被捕获后回滚并重试 SELECT → UPDATE，返回 200。此模式替代 `ON CONFLICT DO UPDATE`（SQLAlchemy async + SQLite 测试兼容性考量）。
- **Post-vote eager-load 模式**：`create_or_update_vote()` 在 `flush()` + `refresh()` 后，额外执行一次带 `selectinload(Vote.race_horse_rel)` 的查询以解析马名。端点层不再单独调用 `get_race_votes()`（避免 N+1 和冗余查询）。
- **Lock 操作模式**：`POST /api/v1/races/{race_id}/lock` 为管理员专用端点（`Depends(get_current_admin)`）。使用否定检查 `if race.status != RaceStatus.VOTING`（而非列举非目标状态）以确保未来状态扩展的健壮性。仅 `voting` 状态可锁定。
**取消投票端点模式**：`DELETE /api/v1/races/{race_id}/votes` 为已登录用户专用端点。校验比赛处于 `voting` 状态后才能取消，通过 `await db.delete(vote)` + `flush()` 删除投票记录。服务层 `delete_vote()` 封装所有校验逻辑（比赛存在性、比赛状态、投票是否存在）。
**可选用户依赖模式**：`get_optional_user()` 用于公开端点中可选地展示用户特定数据。与 `get_current_user` 逻辑相同但捕获所有认证错误并返回 `None`（无 token/token 过期/token 无效 → 均返回 `None`）。用于 `list_races` 端点返回当前用户各比赛的 `has_voted` 状态。
- **编辑比赛防删票保护**：`race_service.update_race()` 在移除马匹时，先查询 `Vote` 表检查被移除的 `race_horse_ids` 是否存在投票。若有投票存在，返回 400 `HORSE_HAS_VOTES` 拒绝操作。此保护覆盖 Story 3.2 中移除的 race_horse_id FK CASCADE 限制（无 DB 级 CASCADE，改由应用层保护）。

**Service & DB patterns:**
- `flush()` 后必须调用 `refresh()` 才能读取 `server_default`/`onupdate` 字段值（如 `created_at`、`updated_at`），否则 Pydantic `model_validate()` 会报 `MissingGreenlet` 错误。所有 CRUD 服务的 create/update 方法必须遵循 `flush()` → `refresh()` → return 模式。
- Pydantic schemas：PATCH endpoint 使用的 Update schema（如 `HorseUpdate`）必须包含与 Create schema（如 `HorseCreate`）相同的 `@field_validator`，包括 `.strip()` 处理——因为用户可通过 API 直接调用 PATCH 绕过前端校验。
- **PATCH 防 null 覆盖模式**：在 `update_race` 等 PATCH 服务中，`data.model_dump(exclude_unset=True)` 后必须过滤 `None` 值：`update_data = {k: v for k, v in update_data.items() if v is not None}`。否则客户端发送 `{"name": null}` 会覆盖数据库字段为 null 导致 500 错误。同时前端编辑页应通过差异检测**仅发送变更的字段**（参考 `EditRacePage.vue` 中 `getChangedHorseIds()` + `initialValues` 比较模式）。
- **手动编辑追踪模式**：Horse 模型有 `manually_updated_fields` JSON 字段（存储字段名列表），`horse_service.update_horse()` 自动追踪手动编辑的字段（`name` 和 `manually_updated_fields` 自身被排除）。自动更新框架 `auto_update_service.apply_auto_updates()` 检查此列表：在列表中的字段跳过更新（手动优先），不在列表中的字段更新并记录到 `HorseAutoUpdateLog`。管理员可通过 `POST /api/v1/horses/{id}/reset-auto-protection` 清空保护列表。
- **事务原子性模式**：`apply_auto_updates` 遵循"先全部验证再批量更新"模式——先验证所有 horse_id 存在，再逐个更新 + flush + refresh。调用方必须在同一事务中包裹此调用。
- **字段名校验模式**：通过 `inspect(Horse).columns` 获取有效列名集合，在 `apply_auto_updates` 中验证 `field_name` 是否有效，无效字段返回 400 `INVALID_FIELD`。避免 `setattr` 动态创建属性导致静默丢失更新。
- **变更日志模式**：`HorseAutoUpdateLog` 模型记录每次自动更新的字段级变更（old_value/new_value 为 Text 类型避免截断），`trigger_source` 标记触发来源（v1 固定 "settlement"）。外键：`horse_id` CASCADE, `race_id` SET NULL。
- **Alembic 迁移枚举经验**：使用 `sa.Enum` 创建 PostgreSQL 枚举时，SQLAlchemy 默认使用 Python enum 的**成员名**（大写）作为数据库枚举值。手写迁移创建枚举时需保持大小写一致。推荐使用 `op.execute("CREATE TYPE ... AS ENUM (...)")` + `ENUM(..., create_type=False)` 模式以实现幂等迁移。

**Scoring Engine 纯函数模式（Story 3.1）：**
- `scoring_engine.py` 必须是纯函数模块，零外部依赖，仅允许 `from typing import Any`。禁止导入 FastAPI、SQLAlchemy 或任何 DB 相关模块。
- 公共 API：`calculate_score(grade: str, total_horses: int, position: int, custom_scoring: dict | None = None) -> int`
- G1 扣分使用**绝对位置转换公式**：`penalty_position = total_horses + offset + 1`，其中 `offset` 为负数（-1=最后一名，-2=倒数第二名，依此类推）。
- G1 扣分分档：≥8匹扣末3名(-10/-5/-1)、7匹扣末2名(-5/-1)、6匹扣末1名(-1)、≤5匹无扣分。
- G2_JPN1：正分 +5/+4/+3/+2/+1，不扣分。
- YOUNG_G1：正分同 G1（+10/+5/+3/+2/+1），不扣分。
- CUSTOM：从 `custom_scoring` 字典读取 `positive_scores`（list[int]，1-indexed）和可选的 `penalty_rules`（list[dict]，position 为负偏移，points 为扣分值）。
- DNF/退赛：`position <= 0` 返回 0 分。
- 调用方负责过滤 DNF 马匹（不将其计入 `total_horses`）——引擎不做 DB 查询。
- `GradeEnum` 字符串值：`"G1"`, `"G2_JPN1"`, `"YOUNG_G1"`, `"CUSTOM"` ——直接在字符串参数中使用，不需要 import 枚举类。
- 100% 分支覆盖要求：测试必须覆盖 4 种等级的所有边界组合，包括 G1 的 4 种匹数分档（≥8/7/6/≤5）。

**Frontend patterns:**
- 管理后台 CRUD 页面使用 `<Teleport to="body">` 模态框进行创建/编辑操作，搜索框使用 300ms 防抖（`watch(search, debouncedSearch)` + `setTimeout`）。
- **PATCH 编辑模式的关键模式**：`handleSave` 在编辑时必须按字段逐一比较当前值与原始值的差异，**仅发送变更的字段**，而非发送所有字段为 `null`。否则后端 `exclude_unset=True` 无法区分"用户未修改"和"用户将某字段清空为 null"——发送 `null` 会覆盖数据库中的已有值。参考实现：`frontend/src/pages/admin/HorsesPage.vue` 中的 `handleSave`。
- 新建数据后不推荐 `unshift`，应 `push` 后按显示顺序 `sort()` 避免与后端排序不一致导致的视觉跳跃。

**VoteButton 状态机（Story 3.3）已迁移为卡片点击投票模式：**
- `VoteButton.vue` 已被移除，改为 `HorseDetailCard.vue` 直接支持点击投票
- `HorseDetailCard.vue` 新增 `votable`、`voted`、`submitting` props：`votable` 时显示 `cursor: pointer` + hover 高亮效果；`voted` 时显示金色边框 + "✓ 已投"徽章；`submitting` 时禁用点击
- 移动端不再有固定底部投票栏（`position: fixed; bottom: 0`）——投票交互直接在卡片上进行
- 锁定/已结算状态：通过 `.voted-horse-locked` CSS 类（金色边框）在 HorseDetailCard 上高亮用户投中的马匹

**useVote composable 模式（Story 3.3）：**
- `toggleVote(horse, raceId)` 替代旧的 `selectHorse` + `enterSelectionMode` 模式，实现三段逻辑：
  - **未投票** → 提交投票（`POST /races/{id}/votes`）
  - **已投该马再次点击** → 取消投票（`DELETE /races/{id}/votes`）
  - **已投他马点击新马** → 切换投票（`POST` 更新）
- 移除 `isInSelectionMode`、`enterSelectionMode`、`exitSelectionMode` 状态
- 新增 `votedRaceHorseId` 响应式字段追踪已投票马匹 ID，用于判断"是否同一匹马"
- 乐观更新模式：投票/取消均先乐观更新状态，API 失败时回滚
- 组件卸载保护：`let unmounted = false` + `onUnmounted(() => { unmounted = true })`，所有 `await` 后的状态更新前检查 `if (unmounted) return`

**RaceDetailPage 投票集成模式（Story 3.3）：**
- **移除** VoteButton、HorseSelectCard 引用；**移除** 选择模式（`selection-section`）、**移除** 底部投票栏（`vote-bar`）
- 比赛详情页中的赛马卡片（HorseDetailCard）直接可点击投票——点击卡片 = 投票/取消/切换
- 游客点击卡片 → 跳转登录页；管理员不可投票
- 新增投票提示条（`vote-hint`）：引导用户操作
- VotingDetail 组件在投票/锁定比赛时显示"用户名 → 马匹名"分布，刷新策略：仅在页面加载和投票成功后刷新，无轮询
- HorseSelectCard 已被删除，无单选组需求——每张卡片独立可点击

**HomePage 首场比赛列表投票状态模式：**
- **移除**"投票"按钮（原金色 `vote-entry` CSS 类）
- **新增** `vote-status` 徽章，仅在 voting 状态 + 已登录时显示用户的投票状态："未投票"（灰底灰框）/"已投票"（绿底绿框）
- 未登录用户不显示任何投票标记

**结果录入与结算模式（Story 3.4）：**
- **Result settlement 模式**：`result_service.submit_results()` 同时处理两种流程：`locked → settled`（首次结算）和 `settled → settled`（重新结算）。重新结算时先清空所有 `vote.points = NULL`，再重新计算。整个操作在同一事务中，`db.flush()` 确保原子性。
- **Vote.points 字段**：积分直接存储在 `Vote.points`（nullable int）。结算前为 NULL，结算后为实际积分值。排行榜查询使用 `SELECT user_id, SUM(points) FROM votes WHERE points IS NOT NULL GROUP BY user_id`。此设计避免创建独立积分表。
- **RaceHorse.position 语义**：`NULL` = 未排位（比赛未结算）、`0` = DNF/退赛、`>0` = 实际名次（1=冠军）。此三方语义在结算是更新，在比赛编辑时保持不变。
- **DNF 处理模式**：position=0 的马匹不参与 active_horses 计数，投票给 DNF 马匹的用户得 0 分。active_count 仅统计 `position > 0` 的马匹数量，传递给 scoring_engine 作为 `total_horses` 参数。
- **结果结算 API 模式**：`PUT /api/v1/races/{race_id}/results` 管理员专用端点，接收 `ResultEntry { positions: ResultPosition[] }`。位置校验由 schema 层执行：无重复正数位置、无负数位置、位置从 1 开始连续（无间隔）、所有 race_horse_id 均被覆盖。服务层额外校验比赛状态（拒绝 VOTING 状态的比赛）。
- **DragCard 组件模式**：`DragCard.vue` 使用原生 HTML5 `draggable="true"` 属性 + @dragstart/@dragend 事件。**emit 必须传递原生事件**：`emit('dragStart', index)` 和 `emit('dragEnd', $event)`（DragCard 根 div 上的 `@dragend` 必须传递 `$event` 以便父组件检测 DNF 区域拖放）。六点网格手柄（⠿，`touch-action: none`）区分拖拽区域。dragging 态应用 opacity 0.7 + box-shadow lift + scale(1.02)。DNF 态应用 opacity 0.5 + grey bg。骨架屏复用全局 `skeleton-shimmer` 动画。
- **useDragSort composable 模式**：`useDragSort.ts` 管理两个响应式列表（activeList + dnfList）。初始化时根据 existingPositions Map 进行预排序（重录入模式）。提供 `startDrag`/`commitReorder`/`moveToDnf`/`moveToActive`/`endDrag` 接口。**核心规则：dragover 时只做 preventDefault 不修改列表**（避免 DOM 重排导致浏览器丢失拖拽上下文），列表修改统一在 drop 事件中执行。`commitReorder(fromIndex, toIndex)` 在 activeList 内重排，`moveToDnf(index)` 从 active 移至 dnf，`moveToActive(index)` 从 dnf 移至 active。DNF 区域在 `ResultsPage.vue` 中通过容器级 `@drop="handleDnfDrop"` + `dragSource` 追踪实现，仅 `dragSource === 'active'` 的拖入才触发 `moveToDnf`。DNF 列表使用 `@click="handleDnfClick(index)"` 作为降级交互（桌面端点击移回 active）。
- **移动端触控拖拽模式**（AC-3）：`ResultsPage.vue` 使用 `@touchstart`（300ms setTimeout 延迟激活，`document.body.style.overflow = 'hidden'` 禁止滚动）→ `@touchmove`（e.preventDefault() + 通过 getBoundingClientRect 计算当前位置）→ `@touchend`（检测 DNF 区域 + 清除 body overflow）。`touch-action: none` 设置在拖拽手柄 CSS 上，避免触控与滚动冲突。拖拽结束后恢复 `document.body.style.overflow = ''`。
- **位置连续校验模式**：`ResultEntry.validate_positions()` 在 schema 层校验 `sorted(positive_positions) == list(range(1, len(positive_positions) + 1))`，确保名次无间隔。此校验防止管理员提交 1,3,4,5 等不连续位置导致评分引擎计算错误。

**排行榜模式（Story 3.5）：**
- **Leaderboard 聚合查询模式**：`leaderboard_service.get_leaderboard()` 使用 `OUTER JOIN votes ON (user.id = vote.user_id AND vote.points IS NOT NULL)` 确保所有用户（含 0 参与用户）出现。聚合列：`COALESCE(SUM(vote.points), 0)` 为 total_points、`COUNT(DISTINCT vote.race_id)` 为 races_participated、`ROUND(CAST(sum / divisor AS NUMERIC), 1)` 为 avg_points。**重要：PostgreSQL 的 `round(numeric, integer)` 要求第一个参数为 `NUMERIC` 类型，`double precision` 会导致 `function round(double precision, integer) does not exist` 错误。必须通过 `sa.cast(expression, Numeric)` 显式转换为 NUMERIC。** 排序：`total_points DESC, avg_points DESC`。Python 层对 NULL avg 做 `float(row.avg_points or 0.0)` 处理。
- **Leaderboard 公开端点模式**：`GET /api/v1/leaderboard` 无认证依赖（FR-23 要求公开访问），路由前缀 `/api/v1`。前端 `apiClient.get('/leaderboard')` 因 baseURL 为 `/api/v1` 正确匹配。
- **LeaderboardRow 组件模式**：`LeaderboardRow.vue` 使用原生 `<tr>`/`<td>`（非 div+flex 模拟），接收 `entry: LeaderboardEntry`, `rank: number`, `isCurrentUser: boolean` props。rank 使用 Barlow Condensed 18px bold，前三名使用 `--color-accent` 金色（`color: var(--color-accent, #B8960C)`），其余用 `--color-ink-primary`。积分使用 Barlow Condensed 20px bold `--color-primary`。当前用户行使用 `background: #F0F7F2`。场次/场均使用 body-sm 14px `--color-ink-secondary`。row 使用 `aria-label="{rank}名 {username} {points}分"`。
- **LeaderboardPage 模式**：`LeaderboardPage.vue` 使用 PageState 枚举（loading/empty/error/success）。success 态渲染原生 `<table>`（`<thead>`+`<th scope="col">`+`<tbody>`+`LeaderboardRow` as `<tr>`）。useDragSort composable 外的结构化表格数据优先使用原生 `<table>` 保证列对齐（与 DashboardPage、HorsesPage 一致）。empty 态条件：`data.length === 0 || data.every(e => e.races_participated === 0)`。
- **review 通过后的 story 状态转换**：code-review 发现被全部修复后，story 状态从 `review` → `done`。同时 sprint-status.yaml 同步更新。此流程在 code-review 工作流的 Step 6 中自动执行。
- **catch 规范**：所有 `catch` 块必须使用 `catch (err)`（非裸 `catch`），以便区分错误类型。即使在仅设置 error 状态的简单场景中也需遵守此规范。

**已结算结果展示模式（Story 3.6）：**
- **RaceResultView 组件模式**：`RaceResultView.vue` 用于在比赛详情页展示已结算比赛的完整排名、投票和积分。接收 `horses: RaceHorseResult[]` props（按 position 排序后的数组）。纯展示组件，无交互——与 VotingDetail（用于 voting/locked 状态）分离，不可混用。
- **horse_votes 端点扩展模式**：`GET /api/v1/races/{race_id}` 在已结算状态下扩展返回 `horse_votes` 字段：`{"horses": [{"race_horse_id": id, "horse_id": id, "snapshot_data": {...}, "position": 1, "votes": [{"username": "user", "points": 10}]}]}`。条件判断使用 `race.status == RaceStatus.SETTLED`（枚举比较，非字符串比较）。空列表判断使用 `is not None` 而非布尔真假（避免空列表 `[]` 被当作 falsy）。
- **get_race_results_grouped_by_horse 查询模式**：`vote_service.get_race_results_grouped_by_horse()` 使用 `select(RaceHorse).options(selectinload(RaceHorse.votes).selectinload(Vote.user))` 按马匹分组加载投票。排序：`case((position==0, 2), (is_(None), 3), else_=1)` 将正常马匹排前、DNF 排中、NULL 排后，再按 `position.asc().nulls_last()` 排序。
- **积分颜色编码模式**：正分 `--color-primary`（绿色）、负分 `--color-destructive`（红色）、零分 `--color-ink-disabled`（灰色）。所有分值使用 Barlow Condensed 14px bold（`var(--font-display)` + `var(--text-body-sm)`）。DNF 马匹投票固定显示 `0`（灰色），忽略实际 `vote.points` 值。
- **名次标签模式**：1st/2nd/3rd 金色底 `--color-accent` 白字、4th+ 灰底 `--color-ink-disabled` 白字、DNF 灰底斜体。aria-label 使用中文序数（"第一名"/"第二名"/"弃权"）。DNF 整个 wrapper 为 `opacity: 0.5`，但 `.no-votes` 文字覆盖为 `opacity: 1` 保持可读。
- **已结算比赛管理员按钮模式**：比赛详情页中 `v-if="isRaceSettled && authStore.isAdmin"` 渲染 "修改结果" 按钮（透明背景 + 竞马绿 1px 边框 + 绿色文字），hover 时反转（绿底白字）。链接到 `/admin/races/${raceId}/results`。使用 `router.push()` SPA 跳转。

**审计日志与重算模式（Story 3.7）：**
- **ScoreChangeLog 审计模型模式**：`ScoreChangeLog` 模型（`models/change_log.py`）记录每次积分变更。字段包括 `race_id`（FK CASCADE）、`vote_id`（FK CASCADE）、`user_id`（FK CASCADE——投票者）、`admin_user_id`（FK CASCADE——操作管理员）、`old_points`（首次结算为 NULL）、`new_points`、`created_at`。`Vote` 和 `User` 模型各有反向关系指向此表。
- **结果重算审计模式**：`result_service.submit_results()` 在重算时：先 `is_resettle = race.status == RaceStatus.SETTLED` 判断是否重算，然后 `old_points_map = {vote.id: vote.points for vote in race.votes}` 捕获旧值，再 `vote.points = None` 清除旧积分，重算后遍历 votes 创建 `ScoreChangeLog` 条目（仅 `old_val != new_val` 时记录）。同一 `flush()` 内完成所有操作确保事务原子性。
- **Service 层延迟导入模式**：为避免循环导入，`ScoreChangeLog` 在 `result_service.py` 中使用函数内局部导入：`from app.models.change_log import ScoreChangeLog`。此模式适用于服务层需要引用新模型而模型层也引用服务层涉及的模型时的场景。
- **审计查询端点模式**：`GET /api/v1/races/{race_id}/results/history` 管理员专用端点，返回 `{"race_id": ..., "race_name": ..., "changes": [{"vote_id": ..., "username": ..., "race_id": ..., "old_points": ..., "new_points": ..., "modified_at": ..., "admin_username": ...}]}`。使用 `selectinload(ScoreChangeLog.vote_rel).selectinload(Vote.user)` 链式加载避免 N+1。

---

**马匹年龄动态计算模式（Story 4.x）：**
- Horse 模型不存储整数 `age`，改为存储 `birth_year`（出生年，如 2022）+ `hemisphere`（"north"/"south"）。
- 前端 `HorseDetailCard.vue` 提供 `computeAge(birthYear, hemisphere, onDate)` 函数动态计算年龄：
  - 北半球：1月1日起 `今年-出生年` 岁
  - 南半球：8月1日起 `今年-出生年` 岁
- 卡片接收 `birthYear`/`hemisphere`/`referenceDate` props（可选，不传则用当天日期）。
- 比赛页面向 `HorseDetailCard` 传入 `race.date` 作为 `referenceDate`，确保显示比赛中实际年龄。
- `RaceHorse.snapshot_data` 中 `age` 字段被 `birth_year` 替代，但保留对旧数据 `age` 的向后兼容读取：`snapshot_data.birth_year ?? snapshot_data.age`。

**出生国/所属地 新增选择模式（Story 4.x）：**
- 出生国（`origin`）下拉使用原生 `<select>`，底部选项 "+ 新增国家"，选中后切换为文本输入模式。
- 新增国家时必须选择南北半球（`north`/`south`），否则无法确认。
- 选择已有国家时自动填充 `hemisphere`（来自 `countryHemispheres` 映射，由后端 `getOriginsStats()` 返回各国家最常见的半球）。
- 所属地（`location`）与出生国完全独立的字段，逻辑相同但没有半球信息。
- 新增确认后不立即修改 `sortedCountries`/`sortedLocations`（防止未保存时出现幽灵数据），而是通过 `<option v-if="formOrigin && !sortedCountries.includes(formOrigin)">` 显示临时选项。
- 保存后通过 `refreshCountryList()` 从后端重新拉取统计数据。
- `POST /api/v1/horses/origins/{origin}/toggle-hemisphere` 端点用于翻转所有同产地马匹的半球（north↔south），前端在半球标签旁显示"切换半球"按钮。

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

Last Updated: 2026-07-01 (sync Vite to 8.0.16, add pnpm nodeLinker: hoisted note)
