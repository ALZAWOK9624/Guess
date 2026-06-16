---
baseline_commit: 1bd7ef85ac2e846f8e04de8fde7a96727d3902ed
---

# Story 3.2: Voting System Backend

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **logged-in user**,
I want **to cast a vote on an open race and change my selection before lock**,
so that **I can freely decide which horse to support before the race starts**.

As an **admin**,
I want **to lock voting when ready, freezing all selections**,
so that **no further changes are allowed before result entry**.

## Acceptance Criteria

### AC-1: Cast vote on voting race

**Given** a race in `voting` status
**When** a logged-in user sends `POST /api/v1/races/{race_id}/votes` with `race_horse_id`
**Then** a vote record is created, returning `201`
**And** each user has at most one active vote per race (re-vote overwrites the old vote)

### AC-2: Modify vote before lock

**Given** a user has already voted on a `voting` race
**When** they send `POST /api/v1/races/{race_id}/votes` with a different `race_horse_id`
**Then** the old vote is replaced, returning `200` with updated vote info
**And** modification is unlimited before lock

### AC-3: Reject vote on locked/settled race

**Given** a race in `locked` or `settled` status
**When** a user attempts to submit or modify a vote
**Then** return `400` with `{ "detail": { "code": "VOTE_LOCKED", "message": "投票已截止" } }`

### AC-4: Reject vote for unauthenticated user

**Given** a guest (unauthenticated) user
**When** attempting to submit a vote
**Then** return `401` with `{ "detail": { "code": "NOT_AUTHENTICATED", "message": "请先登录" } }`

### AC-5: Admin lock voting

**Given** an admin user
**When** `POST /api/v1/races/{race_id}/lock`
**Then** race status changes to `locked`, all votes are frozen
**And** locking requires admin privileges (`Depends(get_current_admin)`)
**And** already-locked/settled races return `400` with `RACE_LOCKED` or `RACE_SETTLED`

### AC-6: Public vote query

**Given** any viewer (logged-in or guest)
**When** `GET /api/v1/races/{race_id}/votes`
**Then** return all vote records for the race: user info + selected horse name
**And** voting races show current distribution; locked/settled races show frozen state

## Tasks / Subtasks

- [x] **AC-1/2**: Create Vote model (`backend/app/models/vote.py`)
  - [x] Fields: `id`, `user_id` (FK→users), `race_id` (FK→races), `race_horse_id` (FK→race_horses)
  - [x] Unique constraint `(user_id, race_id)` — one vote per user per race
  - [x] `created_at`, `updated_at` with timezone
  - [x] Export from `models/__init__.py`
  - [x] Add relationship on `Race` model (back_populates="votes")
- [x] **AC-1/2**: Create Vote schemas (`backend/app/schemas/vote.py`)
  - [x] `VoteCreate` — `race_horse_id: int`
  - [x] `VoteResponse` — id, user_id, race_id, race_horse_id, horse_name, created_at, updated_at
  - [x] `VoteListResponse` — list of VoteResponse
  - [x] Export from `schemas/__init__.py`
- [x] **AC-1/2**: Create Vote service (`backend/app/services/vote_service.py`)
  - [x] `create_or_update_vote(db, race_id, user_id, race_horse_id) -> Vote`
    - Validate race exists and is `voting`
    - Validate `race_horse_id` belongs to this race
    - Upsert: if existing vote for (user_id, race_id), overwrite; else create new
    - `flush()` → `refresh()` for auto-generated timestamps
  - [x] `get_race_votes(db, race_id) -> list[Vote]`
    - Return all votes for a race, with user and horse names
  - [x] `lock_race(db, race_id) -> Race`
    - Validate race exists and is `voting`
    - Set `race.status = RaceStatus.LOCKED`
    - `flush()` → `refresh()`
  - [x] Export from `services/__init__.py`
- [x] **AC-1~5**: Create vote endpoints (`backend/app/api/v1/endpoints/votes.py`)
  - [x] `POST /api/v1/races/{race_id}/votes` — `Depends(get_current_user)` (requires auth)
  - [x] `GET /api/v1/races/{race_id}/votes` — public
  - [x] `POST /api/v1/races/{race_id}/lock` — `Depends(get_current_admin)`
  - [x] Include router in `api/v1/__init__.py`
- [x] **AC-1~6**: Update existing code
  - [x] `race_service.get_race_vote_count()` — query `Vote` table by `race_id` via `count()`
  - [x] Add `votes` relationship to `Race` model (for cascade delete)
  - [x] Add Alembic migration for `votes` table
- [x] **AC-1~6**: Create tests (`backend/tests/test_votes.py`)
  - [x] `conftest.py` fixtures for auth headers (use existing patterns)
  - [x] Test cast vote on voting race → 201
  - [x] Test modify vote → 200, old vote replaced
  - [x] Test re-vote returns 200 (upsert path)
  - [x] Test vote on locked race → 400 VOTE_LOCKED
  - [x] Test vote on settled race → 400 VOTE_LOCKED
  - [x] Test unauthenticated vote → 401
  - [x] Test admin lock → 200, status=locked
  - [x] Test non-admin lock → 403
  - [x] Test lock already-locked race → 400
  - [x] Test GET votes returns correct data (with user/horse names)
  - [x] Test GET votes for non-existent race → 404

## API Contract

```python
# POST /api/v1/races/{race_id}/votes
# Request body:
{
    "race_horse_id": int   # FK referencing race_horses.id
}
# Response 201 (new vote):
{ "data": { "id": 1, "user_id": 5, "race_id": 3, "race_horse_id": 12, "horse_name": "ウシュバテソーロ", "created_at": "2026-06-12T15:00:00Z", "updated_at": "2026-06-12T15:00:00Z" } }
# Response 200 (re-vote/update):
{ "data": { ... same structure ... } }
# Error 400: { "detail": { "code": "VOTE_LOCKED", "message": "投票已截止" } }
# Error 400: { "detail": { "code": "RACE_NOT_VOTING", "message": "比赛不在投票阶段" } }
# Error 400: { "detail": { "code": "INVALID_HORSE", "message": "马匹不属于该比赛" } }
# Error 401: { "detail": { "code": "NOT_AUTHENTICATED", "message": "请先登录" } }

# GET /api/v1/races/{race_id}/votes
# Response 200:
{ "data": [
    { "user_id": 5, "username": "tkd", "race_horse_id": 12, "horse_name": "ウシュバテソーロ", "created_at": "..." },
    { "user_id": 8, "username": "alice", "race_horse_id": 15, "horse_name": "ドウデュース", "created_at": "..." }
] }

# POST /api/v1/races/{race_id}/lock
# Response 200:
{ "data": { "id": 3, "name": "...", "status": "locked", ... } }
# Error 400: { "detail": { "code": "RACE_NOT_VOTING", "message": "比赛不在投票阶段" } }
```

## Files to Create/Modify

| Action | File | Description |
|--------|------|-------------|
| **NEW** | `backend/app/models/vote.py` | Vote model (user_id, race_id, race_horse_id, timestamps) |
| **MODIFY** | `backend/app/models/__init__.py` | Export Vote model |
| **MODIFY** | `backend/app/models/race.py` | Add `votes` relationship to Race model |
| **NEW** | `backend/app/schemas/vote.py` | VoteCreate, VoteResponse schemas |
| **MODIFY** | `backend/app/schemas/__init__.py` | Export vote schemas |
| **NEW** | `backend/app/services/vote_service.py` | Vote business logic |
| **MODIFY** | `backend/app/services/__init__.py` | Export vote_service |
| **NEW** | `backend/app/api/v1/endpoints/votes.py` | Vote + lock endpoints |
| **MODIFY** | `backend/app/api/v1/endpoints/__init__.py` | Register votes router in api_v1_router |
| **MODIFY** | `backend/app/api/v1/__init__.py` | Include votes endpoint router |
| **MODIFY** | `backend/app/services/race_service.py` | Update `get_race_vote_count()` to query Vote table |
| **NEW** | `backend/tests/test_votes.py` | Integration tests for voting |
| **NEW** | `backend/alembic/versions/xxxx_create_votes_table.py` | Alembic migration for votes table |

## Dev Notes

### Vote Model Design

```python
class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    race_id: Mapped[int] = mapped_column(Integer, ForeignKey("races.id", ondelete="CASCADE"), nullable=False)
    race_horse_id: Mapped[int] = mapped_column(Integer, ForeignKey("race_horses.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "race_id", name="uq_vote_user_race"),
    )
```

- Use `race_horse_id` FK to reference the specific join-table entry (not `horse_id` directly)
- Unique constraint `(user_id, race_id)` enforces one-vote-per-user-per-race at DB level
- The `ondelete="CASCADE"` on user_id and race_id ensures votes are cleaned up when parent records are deleted
- `RaceStatus` flow: `VOTING → LOCKED → SETTLED` — voting only allowed in `VOTING` state

### Upsert Pattern for Re-vote

```python
async def create_or_update_vote(db, race_id, user_id, race_horse_id) -> Vote:
    # 1. Validate race exists and status == VOTING
    # 2. Validate race_horse_id belongs to this race
    # 3. Check existing vote:
    stmt = select(Vote).where(Vote.user_id == user_id, Vote.race_id == race_id)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        existing.race_horse_id = race_horse_id
        vote = existing
        status_code = 200  # modified
    else:
        vote = Vote(user_id=user_id, race_id=race_id, race_horse_id=race_horse_id)
        db.add(vote)
        status_code = 201  # new

    await db.flush()
    await db.refresh(vote)
    return vote, status_code
```

### Race Model Update

Add to `Race` model (in `models/race.py`):
```python
votes: Mapped[list["Vote"]] = relationship(back_populates="race", cascade="all, delete-orphan")
```

And add to `Vote` model:
```python
race: Mapped["Race"] = relationship(back_populates="votes")
```

### Update race_service.get_race_vote_count()

Replace the placeholder `return 0` with an actual query:
```python
async def get_race_vote_count(db: AsyncSession, race_id: int) -> int:
    from app.models.vote import Vote
    stmt = select(func.count(Vote.id)).where(Vote.race_id == race_id)
    result = await db.execute(stmt)
    return result.scalar() or 0
```

### Architecture Compliance

- **Endpoints layer**: `votes.py` handles HTTP orchestration only — delegates to `vote_service.py`
- **Service layer**: `vote_service.py` contains all business logic (validations, status checks)
- **Auth pattern**: Use `Depends(get_current_user)` for vote endpoints (returns `None` for guests → 401); use `Depends(get_current_admin)` for lock endpoint
- **API format**: Follow existing patterns — success `{"data": ...}`, error `{"detail": {"code": "...", "message": "..."}}`
- **Response codes**: 201 for new vote, 200 for re-vote and lock, 400 for domain errors, 401 for auth, 403 for non-admin lock attempt, 404 for missing race

### Testing Requirements

- **Test file**: `backend/tests/test_votes.py`
- Use existing `conftest.py` fixtures: `db_session`, `async_client`
- Follow existing test patterns from `test_races.py`, `test_auth.py` — use dependency overrides for auth
- **Minimum coverage target**: all acceptance criteria tested, including:
  - Vote create + modify (upsert)
  - All race status validations (VOTING vs LOCKED vs SETTLED)
  - Auth failures (unauthenticated, non-admin lock)
  - Vote query (GET) — verify user/horse names resolved correctly
  - Edge cases: non-existent race, non-existent race_horse_id, race_horse_id not belonging to race

### Alembic Migration

Generate migration after creating the Vote model:
```bash
cd backend
alembic revision --autogenerate -m "create votes table"
```
Review the generated migration to ensure:
- Correct table name `votes`
- Foreign keys: `user_id` → `users.id` (CASCADE), `race_id` → `races.id` (CASCADE), `race_horse_id` → `race_horses.id`
- Unique constraint `(user_id, race_id)`

### Previous Story Intelligence (Story 3.1)

- **Scoring engine** is a pure function with zero external dependencies — not directly used in voting, but referenced by subsequent stories (3.5 settlement)
- **100% branch coverage** required for scoring engine — vote service tests don't need this level, but should cover all ACs
- **`flush()` → `refresh()` pattern** is established and must be followed for server_default fields
- **No DB migration in Story 3.1** — this story is the first to create a new model in Epic 3

### Git Intelligence (Recent Work Patterns)

- Last commit: `1bd7ef8` — "feat: Story 3.1 - scoring engine pure function module with code review"
- Previous commit: `f1d18fe` — "feat: Epic 2 completion and retrospective"
- Established patterns: each story creates service + endpoint + test files, Alembic migration for new models
- Testing infrastructure is solid: 131 existing tests, all passing with zero regression
- Code review process followed for all stories — Story 3.1 had code review before merge

### Critical Don't-Miss Rules

1. **Endpoints must NOT contain business logic** — delegate to `vote_service.py`
2. **PATCH null 覆盖模式** — Not relevant here (this is POST, not PATCH), but use `exclude_unset=True` / `exclude_none()` for any future PATCH on votes
3. **`flush()` → `refresh()` 模式** — Required after creating/updating Vote records for `server_default` fields
4. **API 字段保持 snake_case** — `race_horse_id`, `user_id` (no camelCase conversion)
5. **Response format** — Success `{"data": ...}`, error `{"detail": {"code": "ERROR_CODE", "message": "..."}}`
6. **Do NOT import `useAuthStore` in `client.ts`** — applies to frontend only, not relevant here
7. **Do NOT use sync endpoints** — all FastAPI endpoints must be `async def`

### Project Context Reference

- [Source: project-context.md#Technology Stack & Versions] FastAPI async, SQLAlchemy 2.0 async, pytest
- [Source: project-context.md#Framework-Specific Rules] Race status machine, API prefix `/api/v1/`
- [Source: project-context.md#Critical Implementation Rules] API response format, naming conventions
- [Source: epics.md#Story 3.2] Story 3.2 acceptance criteria (AC-1 through AC-6 above)
- [Source: architecture.md#Project Structure & Boundaries] File locations: endpoints/votes.py, services/vote_service.py, models/vote.py
- [Source: app/models/race.py] RaceStatus enum (VOTING, LOCKED, SETTLED), GradeEnum

## Dev Agent Record

### Agent Model Used

Deepseek-V4-Flash

### Debug Log References

- Vote upsert pattern: use SELECT + check + INSERT/UPDATE, NOT `on_conflict_do_update` (SQLAlchemy async + PostgreSQL compatibility)
- Race status validation: check `race.status != RaceStatus.VOTING` for all voting operations
- `get_race_vote_count()` query: use `func.count()` to avoid loading all rows into memory

### Completion Notes List

- Created `backend/app/models/vote.py` with Vote model (user_id, race_id, race_horse_id, unique constraint, timestamps, relationships)
- Created `backend/app/schemas/vote.py` with VoteCreate, VoteResponse, VoteListEntry schemas
- Created `backend/app/services/vote_service.py` with create_or_update_vote (upsert), get_race_votes (eager loaded), lock_race, resolve_horse_name
- Created `backend/app/api/v1/endpoints/votes.py` with POST/GET votes and POST lock endpoints
- Modified `backend/app/models/__init__.py` — export Vote model
- Modified `backend/app/models/race.py` — add `votes` relationship
- Modified `backend/app/models/user.py` — add `votes` relationship
- Modified `backend/app/models/race.py` — add `votes` relationship to RaceHorse model
- Modified `backend/app/api/v1/__init__.py` — register votes router
- Modified `backend/app/services/race_service.py` — update get_race_vote_count() to query Vote table
- Created `backend/alembic/versions/006_create_votes_table.py` — manual migration for votes table
- Created `backend/tests/test_votes.py` — 20 tests covering all ACs
- All 151 tests pass (131 existing + 20 new), zero regression

### File List

| **NEW** | `backend/app/models/vote.py` | Vote model |
| **MODIFY** | `backend/app/models/__init__.py` | Export Vote model |
| **MODIFY** | `backend/app/models/race.py` | Add votes relationship (Race + RaceHorse) |
| **MODIFY** | `backend/app/models/user.py` | Add votes relationship |
| **NEW** | `backend/app/schemas/vote.py` | VoteCreate, VoteResponse, VoteListEntry |
| **NEW** | `backend/app/services/vote_service.py` | Vote business logic |
| **NEW** | `backend/app/api/v1/endpoints/votes.py` | Vote + lock endpoints |
| **MODIFY** | `backend/app/api/v1/__init__.py` | Register votes router |
| **MODIFY** | `backend/app/services/race_service.py` | Update get_race_vote_count() |
| **NEW** | `backend/tests/test_votes.py` | 20 tests covering all ACs |
| **NEW** | `backend/alembic/versions/006_create_votes_table.py` | Alembic migration for votes table |
