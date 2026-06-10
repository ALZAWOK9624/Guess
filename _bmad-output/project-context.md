---
project_name: 'guess'
user_name: 'tkd'
date: '2026-06-10'
sections_completed:
  ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'code_quality', 'workflow', 'critical_rules']
status: 'complete'
rule_count: 60
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
- Auth guard placeholder in `router/index.ts` — full implementation in Story 1.5b
- `@` path alias configured in both `vite.config.ts` and `tsconfig.app.json` — use `@/pages/`, `@/components/`, etc.
- Responsive navigation via `AppLayout` (global wrapper in `App.vue`): desktop top nav (≥768px, green bg) and mobile bottom nav (<768px, with SVG icons + text). Both hidden on admin routes via `v-if="!isAdminRoute"`
- `safe-area-inset-bottom` applied via `viewport-fit=cover` meta + CSS `env(safe-area-inset-bottom)` — always add to mobile fixed elements
- `prefers-reduced-motion: reduce` respected globally in `base.css` — overrides all animations/transitions
- `AdminLayout` sidebar (`z-index: 200`): desktop fixed 240px, mobile hamburger-triggered overlay with body scroll lock

**FastAPI:**
- App entry: `app/main.py` with `lifespan` for DB engine lifecycle
- Config: `app/core/config.py` via Pydantic Settings (reads from `.env`)
- Dependencies: `app/api/deps.py` — `get_db` (session), `get_current_user` (auth placeholder), `get_current_admin` (requires admin)
- Auth check: `get_current_user` returns `None` for guests, raises `TOKEN_EXPIRED` for expired tokens, 401 for invalid tokens
- Admin check: `get_current_admin` depends on `get_current_user`, verifies `is_admin` flag, raises 403 for non-admins
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
- `conftest.py` provides basic fixtures; for isolated tests, create an in-memory SQLite engine with `aiosqlite` (`sqlite+aiosqlite:///:memory:`) — override `get_db` dependency and `get_current_admin` for API tests
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

**Security:**
- JWT secrets (`SECRET_KEY`, `JWT_SECRET`) MUST be changed from defaults before production
- CORS must be tightened for production (methods, headers)
- Login failure returns generic error: `"用户名或密码错误"` — no field-specific leak
- Passwords hashed via bcrypt (passlib CryptContext)
- Guests are read-only — voting requires authentication

**Performance:**
- No Redis/cache layer needed for v1 — direct DB queries suffice for ~100 users
- Route lazy loading configured (Vite auto-splits)
- No virtual scroll needed

**Edge cases:**
- Race horse data uses **snapshot** mechanism — horse attributes at creation time do NOT change when the library updates
- Settled races cannot be deleted — only result modification with full rollback/recalculate
- DNF/scratched horses score 0 points and are excluded from deduction calculation denominators
- Custom scoring rules apply only to the current race — not saved as templates

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

Last Updated: 2026-06-10
