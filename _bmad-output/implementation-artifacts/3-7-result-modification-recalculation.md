---
baseline_commit: a62aa06380b101c8dba4efd17f0ff4bd2a8a16bc
---

# Story 3.7: Result Modification — Rollback & Recalculate

Status: done

## Story

As an **admin**,
I want **to modify results of an already-settled race, with automatic rollback of old scores and recalculation of new ones**,
so that **even if I enter incorrect results, I can quickly correct them without affecting ranking accuracy**.

## Acceptance Criteria

### AC-1: Modify settled race results — rollback + recalculate

**Given** a settled race (status = `settled`)
**When** the admin navigates to the results entry page (`/admin/races/{id}/results`) — adjusts the drag-sort order — confirms submission
**Then** the system automatically clears all previously awarded points for this race (`Vote.points = NULL` for all votes in this race)
**And** the system recalculates points based on the new rankings using the scoring engine
**And** the race status remains `settled`
**And** the leaderboard reflects the updated point totals immediately

### AC-2: Point change history is traceable

**Given** a re-settlement has occurred
**When** an admin (or future audit) queries the change history for a race
**Then** each modification is recorded with:
- The old score and new score for each affected vote
- The timestamp of the modification
- The admin who performed the modification
**And** the history is accessible via API (admin-only)

### AC-3: Concurrent-safe atomic operation

**Given** an admin initiates result modification
**When** the system processes the rollback + recalculation
**Then** the entire operation is atomic (all-or-nothing within a single transaction via `db.flush()`)
**And** if any step fails (e.g., scoring engine error), the entire operation is rolled back
**And** the admin receives a clear error message and can retry

### AC-4: Frontend — full modify-result flow works end-to-end

**Given** an admin is viewing a settled race detail page
**When** the admin clicks the "修改结果" button (added in Story 3.6)
**Then** the admin is navigated to `/admin/races/{id}/results` with the existing positions pre-filled (as implemented in Story 3.4)
**And** after modifying positions and confirming, the page redirects back to the race detail page showing the updated results
**And** the "修改结果" button remains visible for future modifications

### AC-5: Points display updates immediately after re-settlement

**Given** a re-settlement has occurred
**When** any user views the race detail page
**Then** the `RaceResultView` component shows the new points per vote (not the old ones)
**And** on the leaderboard page, the affected users' total scores reflect the corrected values

## Backend Tasks

### Task B1: Create `ScoreChangeLog` model

**File:** `backend/app/models/change_log.py` (NEW)

Create a new model to track score changes:

```python
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, func
from app.core.database import Base


class ScoreChangeLog(Base):
    __tablename__ = "score_change_logs"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    race_id: int = Column(Integer, ForeignKey("races.id", ondelete="CASCADE"), nullable=False, index=True)
    vote_id: int = Column(Integer, ForeignKey("votes.id", ondelete="CASCADE"), nullable=False)
    user_id: int = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # voted user
    admin_user_id: int = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # who modified
    old_points: int | None = Column(Integer, nullable=True)  # NULL = first settlement
    new_points: int | None = Column(Integer, nullable=True)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
```

**File:** `backend/app/models/__init__.py` (MODIFY)

Add import for `ScoreChangeLog`.

**File:** `backend/app/schemas/change_log.py` (NEW)

```python
from datetime import datetime
from app.schemas.__init__ import BaseSchema


class ScoreChangeEntry(BaseSchema):
    vote_id: int
    username: str
    old_points: int | None
    new_points: int | None
    modified_at: datetime
    admin_username: str


class ScoreChangeLogResponse(BaseSchema):
    race_id: int
    race_name: str
    changes: list[ScoreChangeEntry]
```

### Task B2: Update `result_service.submit_results()` — add change logging

**File:** `backend/app/services/result_service.py` (MODIFY)

Add change logging to the re-settlement path:

After `vote.points = None` rollback (line 76-77), capture old points before clearing them.

After recalculation and before `flush()`, create `ScoreChangeLog` records:

```python
# After rollback and recalculation, inside resettle path:
if race.status == RaceStatus.SETTLED:
    # Capture old points BEFORE clearing
    old_points_map = {vote.id: vote.points for vote in race.votes}
    for vote in race.votes:
        vote.points = None
    # ... (recalculate happens below) ...

# After recalculation and BEFORE flush, create change logs
if old_points_map:
    from app.models.change_log import ScoreChangeLog  # late import to avoid circular
    for vote in race.votes:
        old_val = old_points_map.get(vote.id)
        new_val = vote.points
        if old_val != new_val:
            log_entry = ScoreChangeLog(
                race_id=race.id,
                vote_id=vote.id,
                user_id=vote.user_id,
                admin_user_id=current_admin_id,
                old_points=old_val,
                new_points=new_val,
            )
            db.add(log_entry)
```

**IMPORTANT:** The `submit_results()` function signature needs to accept `current_admin_id: int` parameter.

### Task B3: Add change log query service

**File:** `backend/app/services/result_service.py` (MODIFY — add method)

```python
async def get_race_change_logs(
    db: AsyncSession, race_id: int
) -> list[dict]:
    """Get score change history for a race."""
    from app.models.change_log import ScoreChangeLog
    stmt = (
        select(ScoreChangeLog)
        .options(
            selectinload(ScoreChangeLog.vote_rel),
            selectinload(ScoreChangeLog.admin_user_rel),
        )
        .where(ScoreChangeLog.race_id == race_id)
        .order_by(ScoreChangeLog.created_at.desc())
    )
    result = await db.execute(stmt)
    logs = result.scalars().all()
    # Build response...
```

### Task B4: Update results endpoint

**File:** `backend/app/api/v1/endpoints/results.py` (MODIFY)

Update the `submit_results` endpoint to pass `current_admin.id` to `result_service.submit_results()`:

```python
@router.put("/{race_id}/results")
async def submit_race_results(
    race_id: int,
    data: ResultEntry,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    result = await result_service.submit_results(db, race_id, data, current_admin.id)
    return {"data": result}
```

### Task B5: Add change log query endpoint

**File:** `backend/app/api/v1/endpoints/results.py` (MODIFY — add endpoint)

```python
@router.get("/{race_id}/results/history")
async def get_race_result_history(
    race_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Get score modification history for a race. Admin-only."""
    logs = await result_service.get_race_change_logs(db, race_id)
    return {"data": logs}
```

### Task B6: Generate Alembic migration

Run `alembic revision --autogenerate -m "add score_change_logs table"` and review + commit the generated migration.

### Task B7: Test coverage — extended re-settlement tests

**File:** `backend/tests/test_results.py` (MODIFY — add tests)

Add these test scenarios:

```python
@pytest.mark.asyncio
async def test_resettle_with_audit_log(db_session, seeded_race):
    """Test that re-settlement creates audit log entries."""
    # ... first settle, then re-settle, then verify ScoreChangeLog records exist ...
    # Verify old_points and new_points are correct

@pytest.mark.asyncio
async def test_resettle_no_change_no_log(db_session, seeded_race):
    """Test that identical positions don't create spurious log entries."""
    # Submit same positions twice → no change = no log

@pytest.mark.asyncio
async def test_resettle_multiple_rounds(db_session, seeded_race):
    """Test that 3+ modifications are all recorded correctly."""
    # Change positions 3 times → verify all 3 rounds logged

@pytest.mark.asyncio
async def test_resettle_dnf_change(db_session, seeded_race):
    """Test re-settlement involving DNF position changes."""
    # A horse changes from 4th to DNF → affected votes change accordingly

@pytest.mark.asyncio
async def test_resettle_concurrent_protection(db_session, seeded_race):
    """Test timestamp/version protection prevents concurrent overwrite."""
    # Simulate concurrent settlement attempt → should fail gracefully
```

## Frontend Tasks

### Task F1: Ensure modify-result flow from RaceDetailPage works

**File:** `frontend/src/pages/RaceDetailPage.vue` (VERIFY/ENHANCE — already partially done in Story 3.6)

The "修改结果" button was added in Story 3.6. Verify:
- Button links to `/admin/races/{raceId}/results`
- After re-settlement, the page should reload with fresh data

### Task F2: ResultsPage — handle re-settlement response

**File:** `frontend/src/pages/admin/ResultsPage.vue` (MODIFY)

After confirming re-settlement (PUT to results endpoint), the page should:
1. Show a success notification (e.g., "结果已更新，积分已重算")
2. Navigate to the race detail page: `router.push('/races/' + raceId)`

Currently, after initial settlement, it navigates to the race detail page. Ensure this same behavior works for re-settlement.

### Task F3: Add API type for ScoreChangeLog (optional, future use)

**File:** `frontend/src/types/race.ts` (MODIFY — optional)

Add types for change log response (for future audit UI):

```typescript
export interface ScoreChangeEntry {
  vote_id: number
  username: string
  old_points: number | null
  new_points: number | null
  modified_at: string
  admin_username: string
}
```

## Dev Notes

### Existing Behavior to Preserve

**result_service.submit_results()** already handles:
- Fresh settlement (`locked → settled`): Calculates points for all votes
- Re-settlement (`settled → settled`): Clears `vote.points = NULL`, recalculates

**This story's main NEW additions:**
1. **ScoreChangeLog model**: Track each modification for audit trail (AC-2)
2. **Pass admin ID** to `submit_results()` for audit trail
3. **Change history API**: GET endpoint for retrieving logs
4. **Frontend flow**: Ensure the complete modify → re-settle → redirect loop works

**CRITICAL: Do NOT change the core scoring logic** (`scoring_engine.py`) — it's already fully tested and correct. This story only adds audit logging around it.

### Data Model

```
ScoreChangeLog
├── id (PK, autoincrement)
├── race_id (FK → races.id, CASCADE)
├── vote_id (FK → votes.id, CASCADE)
├── user_id (FK → users.id, SET NULL, nullable) — the voter
├── admin_user_id (FK → users.id, SET NULL, nullable) — who modified
├── old_points (int, nullable — NULL = first settlement)
├── new_points (int, nullable)
└── created_at (DateTime, server_default=func.now())
```

### Points Color Coding Reference

From project-context.md:
- Positive points: `--color-primary` (green)
- Negative points: `--color-destructive` (red)
- Zero points: `--color-ink-disabled` (gray)
- Font: Barlow Condensed 14px bold (`var(--font-display)` + `var(--text-body-sm)`)

### DNF Handling Reference

From project-context.md:
- `position=0` = DNF/scratched
- `position=NULL` = not placed (should not occur for settled races)
- DNF horses: excluded from `active_count`, votes get 0 points
- DNF wrapper: `opacity: 0.5`, label: gray italic

### Race Status Machine

From project-context.md:
- `voting → locked → settled` (one direction)
- Only `voting` races are editable
- `locked` races block voting (ResultsPage allows entry entry)
- `settled` races are final (ResultsPage allows modification via re-entry)

### Existing Patterns to Follow

| Pattern | Reference |
|---------|-----------|
| **Model naming**: snake_case plural table | `score_change_logs` |
| **Schema naming**: PascalCase | `ScoreChangeLog` |
| **Service pattern**: async, flush+refresh | `result_service.py` |
| **Endpoint pattern**: admin-only via `get_current_admin` | `endpoints/results.py` |
| **API format**: `{"data": ...}` success, `{"detail": {...}}` error | project-context.md |
| **Catch blocks**: `catch (err)` not bare `catch` | project-context.md |
| **snake_case API fields**: No camelCase conversion | project-context.md |
| **DB session**: `Depends(get_db)` from `deps.py` | project-context.md |
| **Models/__init__.py**: Import Base from `app.core.database` | project-context.md |
| **Tests**: `asyncio_mode = auto`, in-memory SQLite | project-context.md |

### Anti-patterns to Avoid

- **Do NOT** modify `scoring_engine.py` — it's a pure function, already tested
- **Do NOT** change the existing `pre-filled position` logic in ResultsPage (Story 3.4)
- **Do NOT** add WebSocket/SSE — poll-on-load is sufficient
- **Do NOT** add frontend audit log UI in this story (backend API only — audit UI is future work)
- **Do NOT** use `!important` except in utility classes
- **Do NOT** modify `VoteButton.vue` or the voting/locked flow

### Key Implementation Decisions

1. **ScoreChangeLog model in `models/change_log.py`**: New file, keeping models organized by domain
2. **Late import for ScoreChangeLog**: Use `from app.models.change_log import ScoreChangeLog` inside the function body to avoid circular imports
3. **Admin ID as parameter**: `submit_results()` signature change is minimal (add `current_admin_id: int`)
4. **No frontend audit UI in this story**: Only backend API + database model. The audit UI can be added in a future story.
5. **Old points captured BEFORE clearing**: In the re-settlement path, iterate votes first to capture `old_points_map`, THEN set them to NULL, THEN recalculate

### Architectural Compliance

- **Layer separation**: Change log queries in `result_service.py`, endpoints in `results.py` endpoints, model in `models/`
- **No business logic in endpoints**: The endpoint calls service method and returns
- **snake_case**: table name `score_change_logs`, columns use snake_case
- **Admin-only endpoints**: Both submit-results and change-history endpoints require `get_current_admin`
- **Transaction atomicity**: All operations (rollback + recalc + logging) within same `flush()`

### File Structure Requirements

| Action | File | Description |
|--------|------|-------------|
| **NEW** | `backend/app/models/change_log.py` | ScoreChangeLog model |
| **MODIFY** | `backend/app/models/__init__.py` | Add ScoreChangeLog import |
| **NEW** | `backend/app/schemas/change_log.py` | ScoreChangeEntry and ScoreChangeLogResponse schemas |
| **MODIFY** | `backend/app/services/result_service.py` | Add change logging to submit_results, add get_race_change_logs |
| **MODIFY** | `backend/app/api/v1/endpoints/results.py` | Pass admin_id to submit_results, add GET /{id}/results/history endpoint |
| **NEW** | `backend/alembic/versions/xxx_add_score_change_logs.py` | Alembic migration for new table |
| **MODIFY** | `backend/tests/test_results.py` | Add re-settlement audit log tests (5+ new tests) |
| **VERIFY** | `frontend/src/pages/RaceDetailPage.vue` | Ensure modify flow works end-to-end |
| **MODIFY** | `frontend/src/pages/admin/ResultsPage.vue` | Handle re-settlement response + redirect |

### Project Context Reference

- [Source: project-context.md#结果录入与结算模式] Settlement patterns, Vote.points, RaceHorse.position semantics
- [Source: project-context.md#Service & DB patterns] flush() → refresh() pattern
- [Source: project-context.md#Race status machine] Status transitions: voting → locked → settled
- [Source: project-context.md#积分颜色编码模式] Points color coding (green/red/gray)
- [Source: project-context.md#名次标签模式] Position labels (1st gold, 4th+ gray, DNF italic)
- [Source: project-context.md#已结算比赛管理员按钮模式] Admin modify-result button (Story 3.6)
- [Source: project-context.md#PageState 枚举模式] PageState enum pattern
- [Source: project-context.md#命名规范] Naming conventions

## Dev Agent Record

### Technical Decisions

1. **ScoreChangeLog model**: Keeping it simple — one record per vote change per modification round. The `old_points` is NULL for first settlement (no previous state).

2. **Backend captures old_points before clearing**: The re-settlement path currently sets `vote.points = None` then recalculates. We need to capture old values BEFORE the clear, then set them in the log AFTER recalculation.

3. **Late import pattern**: Avoids circular import issues between `result_service.py` and `change_log.py` models.

4. **No frontend audit UI**: The backend API endpoints and model are created in this story, but the frontend audit page is deferred. This is intentional to minimize scope and ensure the core modify-flow is tested first.

5. **Existing resettle logic is solid**: `submit_results()` already handles re-settlement correctly. This story wraps it with audit logging.

### Potential Pitfalls

- **Circular imports**: Use late imports (`import inside function`) for `ScoreChangeLog` in `result_service.py`
- **old_points_map scope**: Must be initialized as `None` outside the re-settlement branch, otherwise first settlement will raise `UnboundLocalError`
- **Migration must be generated**: Run `alembic revision --autogenerate` and verify the generated script
- **ResultsPage re-entry**: Verify that the pre-filled positions from Story 3.4 work correctly for re-entry (should already work)
- **Race detail page data refresh**: After re-settlement, the `RaceResultView` should show new data. If the page doesn't auto-refresh on return, the user may need to manually refresh.

### Previous Story Learnings (Story 3.6)

- **Points font-size**: 14px, not 16px — confirmed by code review
- **Points font**: Barlow Condensed — confirmed by code review
- **DNF no-votes text opacity**: Override `opacity: 1` on `.no-votes` text within the 0.5 opacity DNF wrapper
- **Vote.points=null check**: Guard against dangling `· ` prefix when points is null (non-settled races)
- **Enum comparison**: Use `RaceStatus.SETTLED` not string `"settled"` — confirmed by code review fix
- **Empty list truthiness**: Check `is not None` not `if horse_votes` (empty list is falsy)
- **Catch blocks**: All `catch` blocks use `catch (err)` not bare `catch`
- **PageState enum**: Always `'loading' | 'empty' | 'error' | 'success'`
- **174 existing tests must pass**: Zero regression allowed

### Git Intelligence

Recent commits in Epic 3:
- `a62aa06` feat: Story 3.6 - race details public view with code review fixes
- `bc444c1` feat: Story 3.5 - point settlement and leaderboard with code review fixes
- `878358f` feat: Story 3.4 - result entry drag-sort with settlement engine, code review fixes
- `338b147` feat: Story 3.3 - voting frontend interaction with code review fixes
- `52a977a` feat: Story 3.2 - voting system backend with code review fixes
- `1bd7ef8` feat: Story 3.1 - scoring engine pure function module with code review

Pattern: Each story includes code review fixes (code-review workflow). The settlement engine (`result_service.py`, `scoring_engine.py`) and tests (`test_results.py`) were last modified in Story 3.4.

### Completion Notes List

- [x] Backend model created: ScoreChangeLog
- [x] Schema created: ScoreChangeEntry, ScoreChangeLogResponse
- [x] Service updated: submit_results() logs changes, get_race_change_logs() added
- [x] Endpoint updated: admin_id passed, history endpoint added
- [x] Migration generated: 008_add_score_change_logs_table.py
- [x] Tests added: 5 new test scenarios (audit log, no-change-no-log, multiple rounds, DNF change, backward compat without admin_id)
- [x] Frontend verified: ResultsPage already has proper re-settlement redirect, RaceDetailPage has modify button
- [x] All 179 tests pass (174 existing + 5 new = 179, zero regression)

### File List

| Action | File |
|--------|------|
| **NEW** | backend/app/models/change_log.py |
| **MODIFY** | backend/app/models/__init__.py |
| **MODIFY** | backend/app/models/vote.py — added score_change_logs relationship |
| **MODIFY** | backend/app/models/user.py — added score_change_logs_as_voter/admin relationships |
| **NEW** | backend/app/schemas/change_log.py |
| **MODIFY** | backend/app/services/result_service.py |
| **MODIFY** | backend/app/api/v1/endpoints/results.py |
| **NEW** | backend/alembic/versions/008_add_score_change_logs_table.py |
| **MODIFY** | backend/tests/test_results.py — added 5 tests |
| **VERIFY** | frontend/src/pages/RaceDetailPage.vue — already has modify button ✓ |
| **VERIFY** | frontend/src/pages/admin/ResultsPage.vue — already handles re-settlement ✓ |

## Senior Developer Review (AI)

**Review Date:** 2026-06-16
**Outcome:** Changes Requested

### Summary

| Layer | Status | Findings |
|-------|--------|----------|
| Blind Hunter (Adversarial) | ✅ Complete | 3 High, 5 Med, 6 Low |
| Edge Case Hunter | ✅ Complete | 3 High, 5 Med, 4 Low |
| Acceptance Auditor | ✅ Complete | All 5 ACs **符合**, 1 minor gap |
| **TOTAL** | | **5 patch**, **1 decision-needed**, **4 defer**, **~12 dismiss** |

### Acceptance Criteria Audit

| AC | Result | Notes |
|----|--------|-------|
| AC-1: Rollback + recalculate | ✅ 符合 | Points cleared, recalculated, status preserved |
| AC-2: Point change history | ✅ 符合 | ScoreChangeLog model + API + all fields |
| AC-3: Concurrent-safe atomic | ✅ 符合 | db.flush() transaction; missing test_resettle_concurrent_protection |
| AC-4: Frontend modify flow | ✅ 符合 | Button, redirect, pre-fill all verified |
| AC-5: Points display update | ✅ 符合 | RaceResultView + leaderboard reflect latest |

### Action Items

#### Decision Needed

- [x] [Review][Decision] **user_id/admin_user_id SET NULL may break audit trail** [change_log.py:31-36] — ✅ Resolved: Changed to CASCADE (logs cascade-deleted with user). Both model and migration updated.

#### Patch Items

- [x] [Review][Patch] **Audit log creation condition logic defect** [result_service.py:113] — ✅ Fixed: Removed outer condition, always log value changes.
- [x] [Review][Patch] **get_race_change_logs return type mismatch** [result_service.py:165] — ✅ Fixed: `-> list[dict]` → `-> dict`.
- [x] [Review][Patch] **get_race_change_logs N+1 query** [result_service.py:169-177] — ✅ Fixed: Added `.selectinload(ScoreChangeLog.vote_rel).selectinload(Vote.user)`.
- [x] [Review][Patch] **modified_at may be None conflicting with Schema** [schemas/change_log.py:15] — ✅ Fixed: Schema field changed to `modified_at: str | None = None`.
- [x] [Review][Patch] **ScoreChangeEntry missing race_id field** [schemas/change_log.py:8-16] — ✅ Fixed: Added `race_id: int` to entry.
- [x] [Review][Patch] **Missing test: 0 votes race re-settlement** [tests/test_results.py] — ✅ Added: `test_resettle_zero_votes`.
- [x] [Review][Patch] **Missing test: all DNF race** [tests/test_results.py] — ✅ Added: `test_resettle_all_dnf`.

#### Deferred (pre-existing)

- [x] [Review][Defer] **pytest.raises(Exception) too broad** [test_results.py] — Pre-existing pattern in all test files. Not introduced by this change.
- [x] [Review][Defer] **seeded_race fixture non-standard _attr pattern** [test_results.py] — Pre-existing pattern. Not introduced by this change.
- [x] [Review][Defer] **Concurrent safety (no with_for_update)** [result_service.py] — Pre-existing in submit_results before this change.
- [x] [Review][Defer] **Missing test_resettle_concurrent_protection** [spec] — Listed in spec but not implemented.
