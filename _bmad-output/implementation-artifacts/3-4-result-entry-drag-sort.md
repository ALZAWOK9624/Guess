---
baseline_commit: 338b1476f9caa9ce90d605690a8ea4efbddaf7f5
---

# Story 3.4: Result Entry — Drag Sort

Status: done

## Story

As an **admin user**,
I want **to enter race results by drag-sorting horses into their finishing order**,
so that **I can intuitively and accurately record results before the automatic settlement triggers**.

## Acceptance Criteria

### AC-1: Locked race access — enter result entry page

**Given** a race is in `locked` status
**When** an admin navigates to `/admin/races/:id/results`
**Then** the page loads all race horses in their current order (by `race_horse_id`, no position set yet)
**And** each horse is displayed as a draggable card (DragCard) with a six-dot grid handle on the left
**And** each card shows horse name + key attribute summary (jockey, weight from snapshot_data)
**And** a full-width confirm button (gold `--color-accent`) is shown at the bottom
**And** a "DNF Zone" is displayed at the bottom as a visually distinct area

### AC-2: Drag-sort interaction — desktop (mouse)

**Given** the admin is on desktop (≥768px)
**When** they mouse-drag a card to a new position
**Then** the card follows the mouse cursor with semi-transparent opacity + slight lift shadow
**And** a green insertion highlight bar appears at the target position
**And** the card snaps into the new position on mouse release
**And** the list order updates immediately

### AC-3: Drag-sort interaction — mobile (touch)

**Given** the admin is on mobile (<768px)
**When** they long-press a card for 300ms
**Then** haptic-style vibration feedback (if supported) and drag activates
**And** the card follows the touch point with semi-transparent opacity + slight lift shadow
**And** green insertion highlight bar appears at target position
**And** scrolling is disabled during drag to avoid conflict

### AC-4: DNF Zone — mark horses as scratched/DNF

**Given** the admin is on the result entry page
**When** they drag a horse card into the "DNF/弃权" zone at the bottom
**Then** the card moves into a separate DNF group section with reduced opacity and a "DNF" label
**And** the horse's position is set to 0 (zero) in the submission payload
**And** the horse can be dragged back from the DNF zone to the active list

### AC-5: Validation — all horses must be positioned

**Given** the admin attempts to click "确认结果"
**When** not all horses have been assigned a position (some still in unranked state)
**Then** the confirm button is disabled (greyed out, non-interactive)
**And** a validation message is shown: "请排列所有马匹的名次（含弃权区）"

### AC-6: Submit results — transition to settled

**Given** the admin has arranged all horses
**When** they click "确认结果"
**Then** the system submits `PUT /api/v1/races/{race_id}/results` with the position mapping
**And** the race status transitions from `locked` to `settled`
**And** the page redirects to the race detail page (`/races/:id`) showing the settled results
**And** voting users' scores are calculated using the scoring_engine

### AC-7: Re-entry — pre-fill previous results

**Given** a race is already `settled` and the admin navigates to `/admin/races/:id/results`
**When** the page loads
**Then** the horses are pre-arranged in their previous finishing order
**And** DNF horses are in the DNF zone
**And** the admin can re-arrange and re-submit to modify results

### AC-8: Admin-only access

**Given** a non-admin or unauthenticated user
**When** they navigate to `/admin/races/:id/results`
**Then** they are redirected to home or login (auth guard in router)

### AC-9: Race not found / invalid state

**Given** a race does not exist
**When** accessing `/admin/races/:id/results`
**Then** a `404 NOT_FOUND` error is shown

**Given** a race is in `voting` status
**When** accessing `/admin/races/:id/results`
**Then** a `400` error is returned with code `RACE_NOT_LOCKED` and message "比赛处于投票中状态，请先锁定"

## Tasks / Subtasks

### Backend

- [x] **AC-6~7, AC-9**: Create `backend/app/schemas/result.py`
  - [x] `ResultEntry` — `positions: list[ResultPosition]`
  - [x] `ResultPosition` — `race_horse_id: int, position: int` (use 0 for DNF)
  - [x] `ResultEntryResponse` — `race_id: int, status: str, scores: list[UserScore]`
  - [x] `UserScore` — `user_id: int, username: str, points: int`

- [x] **AC-6~7**: Create `backend/app/services/result_service.py`
  - [x] `submit_results(db, race_id, positions)` — main entry point
    - [x] Validate race exists and status is `locked` or `settled`
    - [x] Validate all `race_horse_id` belong to this race
    - [x] Validate all horses have a position assigned (0 = DNF, 1+ = ranking)
    - [x] No duplicate positions (except 0 which is shared for DNF)
    - [x] If currently `locked`: transition to `settled`, calculate initial scores
    - [x] If already `settled`: rollback old scores, recalculate new scores
  - [x] `_settle_race(db, race, positions)` — settle a newly locked race
    - [x] Update `RaceHorse.position` for each entry
    - [x] Calculate active horse count (position > 0)
    - [x] For each vote on this race: call `scoring_engine.calculate_score()`
    - [x] Create/update `UserScore` records (or store on Vote model — see Data Model Decision below)
    - [x] Update race status to `SETTLED`
  - [x] `_resettle_race(db, race, positions)` — re-settle an already settled race
    - [x] Delete all existing score records for this race
    - [x] Re-apply the same _settle_race logic
    - [x] This is atomic: if any step fails, the entire operation rolls back
  - [x] Handle DNF: position=0 → user gets 0 points, horse excluded from active count

- [x] **AC-6~7**: Create `backend/app/api/v1/endpoints/results.py`
  - [x] `PUT /api/v1/races/{race_id}/results` — admin-only, accepts `ResultEntry`
    - [x] Calls `result_service.submit_results()`
    - [x] Returns `{ "data": { "race_id": ..., "status": "settled", "scores": [...] } }`

- [x] **AC-6**: Register results router in `backend/app/api/v1/__init__.py`
  - [x] Add `from app.api.v1.endpoints import results`
  - [x] Add `router.include_router(results.router)`

### Frontend

- [x] **AC-1~5, AC-7**: Create `frontend/src/components/DragCard.vue`
  - [x] Props: `horse` (RaceHorseSnapshot), `isDnf` (boolean), `index` (number)
  - [x] Emit: `drag-start`, `drag-end`
  - [x] Visual: six-dot grid handle (⠿) on left, horse name + key attributes summary on right
  - [x] Min height ≥ 56px for touch target
  - [x] States: normal, dragging (semi-transparent + lifted shadow), DNF (reduced opacity + "DNF" label)
  - [x] Desktop: cursor `grab` / `grabbing`
  - [x] Mobile touch target ≥ 48×48px for drag handle

- [x] **AC-2~3**: Create `frontend/src/composables/useDragSort.ts`
  - [x] Reactive state: `items` (ordered array), `dnfItems` (DNF array), `draggedIndex`, `isDragging`
  - [x] `startDrag(event, index)` — store initial state, set dragging
  - [x] `onDragOver(event, index)` — calculate insertion position, update visual indicator
  - [x] `endDrag()` — snap card to new position, handle DNF zone detection
  - [x] Mobile: `onTouchStart` with 300ms long-press delay, `onTouchMove`, `onTouchEnd`
  - [x] Disable page scroll during drag on mobile
  - [x] Detection: if card is dropped on DNF zone → move to `dnfItems`
  - [x] Detection: if card is dragged from DNF zone back to active list → restore to `items`
  - [x] Returns: `{ items, dnfItems, isDragging, startDrag, onDragOver, endDrag, activeList, dnfList }`

- [x] **AC-1~6**: Update `frontend/src/pages/admin/ResultsPage.vue` (stub → full implementation)
  - [x] Import: DragCard, useDragSort, races API, router
  - [x] Fetch race by id on mount: `getRace(raceId)` → store race data + horses
  - [x] PageState enum: `'loading' | 'empty' | 'error' | 'success'`
  - [x] Loading state: skeleton shimmer (5 DragCard skeleton rows)
  - [x] Error state: "加载失败，请刷新重试" + refresh button
  - [x] Empty state: should not happen (race always has horses if it exists)
  - [x] Display DragCard list from `useDragSort().items`
  - [x] Display DNF zone at bottom (visually distinct area with dashed border, "DNF/弃权区" label)
  - [x] Display DNF cards from `useDragSort().dnfItems` inside DNF zone
  - [x] Confirm button: gold (#B8960C), full-width, at bottom
  - [x] Validation: if `items.length + dnfItems.length < total_horses` OR `items.length === 0` → disable confirm
  - [x] Validation message: "请排列所有马匹的名次（含弃权区）"
  - [x] On confirm: build positions array `[{ race_horse_id, position: index+1 }, ...for dnf { race_horse_id, position: 0 }]`
  - [x] Submit via `PUT /api/v1/races/{race_id}/results`
  - [x] On success: `router.push('/races/${raceId}')`
  - [x] On error: show error message, stay on page
  - [x] Re-entry (AC-7): if race already `settled`, pre-sort horses by existing position
    - [x] Horses with `position === 0` go to `dnfItems`
    - [x] Horses with `position > 0` go to `items` sorted by position

- [x] **AC-6**: Update `frontend/src/api/races.ts` or create `frontend/src/api/results.ts`
  - [x] `submitResults(raceId, positions): Promise<ResultEntryResponse>`
  - [x] `PUT /api/v1/races/{race_id}/results`

- [x] **AC-1~5**: Update `frontend/src/types/race.ts` — add result-related types
  - [x] `ResultPosition { race_horse_id: number; position: number }`
  - [x] `UserScore { user_id: number; username: string; points: number }`
  - [x] `ResultEntryResponse { race_id: number; status: string; scores: UserScore[] }`

## UI / Interaction Spec

### DragCard States

| State | Visual | Behavior |
|-------|--------|----------|
| normal | Light border, white bg, six-dot handle (⠿) on left, horse name + jockey + weight on right | Draggable |
| dragging | Semi-transparent (opacity 0.7), elevated shadow (`box-shadow: 0 4px 12px rgba(0,0,0,0.15)`), slight scale(1.02) | Follows cursor/finger |
| DNF | Reduced opacity (0.5), grey bg `#F3F4F6`, "DNF" badge on right | Draggable back to active list |
| insertion-target | Green highlight border (2px, `--color-primary`) at insertion point | — |
| skeleton | Pulsing shimmer via `@keyframes skeleton-shimmer` | Loading state |

### DNF Zone

- Dashed border (2px, `--color-text-muted`), slightly darker bg `#F9FAFB`
- Label: "DNF/弃权区" (muted text, body-sm size)
- Min height: 80px when empty, auto-expands with cards
- Active drop target: green highlight border when dragging over

### Result Entry Page Layout (Mobile)

```
┌─────────────────────────────┐
│ ← 返回     结果录入          │  ← Page header
├─────────────────────────────┤
│                             │
│  ⠿  ウシュバテソーロ  D. Lane 54kg  │  ← DragCard
│  ⠿  ドウデュース        C. Lemaire 58kg  │
│  ⠿  タイトルホルダー      T. 横山 56kg   │
│  ⠿  ジャスティンパレス    T. 戸崎 55kg   │
│  ...                        │
│                             │
├─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┤
│   DNF/弃权区                │  ← DNF Zone
│  ⠿  チェルヴィニア       [DNF]  │  ← DNF DragCard
├─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┤
│                             │
│  ┌─────────────────────┐    │
│  │  确认结果              │    │  ← Gold confirm button
│  └─────────────────────┘    │
└─────────────────────────────┘
```

### Confirm Button States

| State | Visual | Text |
|-------|--------|------|
| active (all positioned) | Gold BG `#B8960C`, white text | "确认结果" |
| disabled (not all positioned) | Grey BG `#9CA3AF`, white text | "请排列所有马匹的名次（含弃权区）" |
| submitting | Grey BG, spinner | "提交中…" |

## Dev Notes

### Data Model Decision: Score Storage

**Decision**: Store per-user per-race scores directly on the `Vote` model by adding a `points` column (nullable int, populated on settlement).

Rationale:
- Simplest approach — no separate score table needed
- Vote already has user_id + race_id combination
- Clean rollback: just set `points = NULL` on all votes for this race during re-settlement
- The leaderboard query becomes: `SELECT user_id, SUM(points) FROM votes WHERE points IS NOT NULL GROUP BY user_id`

Alternative considered: Separate `UserScore` table. Rejected for higher complexity with no benefit at this scale (~100 users).

### RaceHorse.position Semantics

- `position = NULL` → horse not yet placed (before result entry)
- `position = 0` → DNF/scratched
- `position > 0` → finishing position (1 = winner, 2 = second, etc.)

### Position Validation Rules

- All race_horses for the race must have a position in the submission
- Positions 1..N must be contiguous (no gaps) — validated server-side
- Multiple horses can have `position = 0` (DNF) — they all share the zero
- No duplicate positive positions

### Settlement Flow

```
submit_results(db, race_id, positions)
  │
  ├── Validate race exists & status in {locked, settled}
  ├── Validate all race_horse_ids belong to race
  ├── Validate no duplicate positive positions
  ├── Validate all horses accounted for (len(positions) == len(race_horses))
  │
  ├── IF race.status == locked:
  │     ├── Update each RaceHorse.position from positions
  │     ├── Count active_horses = count of positions > 0
  │     ├── For each Vote in race.votes:
  │     │     ├── Find horse's position
  │     │     ├── points = scoring_engine.calculate_score(
  │     │     │     grade=race.grade,
  │     │     │     total_horses=active_horses,
  │     │     │     position=horse_position,
  │     │     │     custom_scoring=race.custom_scoring
  │     │     │   )
  │     │     └── vote.points = points
  │     ├── race.status = SETTLED
  │     ├── db.flush()
  │     └── Trigger auto_update hook (TODO Story 2.5)
  │
  └── IF race.status == settled (re-entry, re-settle):
        ├── Reset all Vote.points = NULL for this race
        ├── Apply same logic as fresh settlement
        └── (Atomic: everything in one transaction)
```

### Scoring Engine Integration

The scoring engine (Story 3.1) is a pure function at `backend/app/services/scoring_engine.py`:

```python
from app.services.scoring_engine import calculate_score

points = calculate_score(
    grade=race.grade.value,      # "G1" | "G2_JPN1" | "YOUNG_G1" | "CUSTOM"
    total_horses=active_horses,  # count of (position > 0)
    position=horse_position,     # 1-indexed position of voted horse
    custom_scoring=race.custom_scoring,  # dict or None
)
```

**IMPORTANT**: DNF horses (position=0) are excluded from `total_horses`. The caller must count only horses with `position > 0`. This is a critical rule from the scoring engine contract.

### Race Status Validation

The endpoint must check race status:

| Current Status | Action |
|---------------|--------|
| `voting` | Return 400 `RACE_NOT_LOCKED` — "比赛处于投票中状态，请先锁定" |
| `locked` | Accept and settle |
| `settled` | Accept (re-settle) |

### Auto-Update Hook (Story 2.5 Extension Point)

After settlement succeeds, the result_service should call the auto_update hook. Per the architecture:

```python
# In race_service.py line 368-376:
# TODO(Epic 3): Call auto_update_service.apply_auto_updates() after settlement.
```

In `result_service.py`, after successful settlement, call:
```python
# await auto_update_service.apply_auto_updates(db, race_id, horse_updates)
```

This should be a **best-effort** call — if auto_update fails (e.g., service not yet implemented), the settlement should still succeed. Wrap in try/except and log warning.

For v1 (this story), we can leave the auto_update call commented out with a TODO — the extension point is ready but the auto-update framework needs:
1. The `auto_update_service.py` module
2. A migration for `HorseAutoUpdateLog` table
3. Actual update rules

**Decision**: Add the `auto_update_service` call with try/except guard, keeping the TODO for rule population.

### RaceHorse.position Update on Race Edit

**IMPORTANT**: When admin edits a voting race (PATCH /races/:id) and adds/removes horses, existing RaceHorse.position values must be preserved for horses that remain (if any had positions set from a previous result entry that was rolled back — edge case, unlikely but possible with re-settle). New horses get `position = NULL`.

Currently, the `RaceHorse.position` is already in the model — it's just always null because no result entry exists yet. This story populates it.

### Existing Files to Modify

| Action | File | Description |
|--------|------|-------------|
| **NEW** | `backend/app/schemas/result.py` | ResultEntry, ResultPosition schemas |
| **NEW** | `backend/app/services/result_service.py` | Settlement business logic |
| **NEW** | `backend/app/api/v1/endpoints/results.py` | PUT /api/v1/races/{id}/results endpoint |
| **MODIFY** | `backend/app/api/v1/__init__.py` | Register results router |
| **MODIFY** | `backend/app/models/vote.py` | Add `points` column (nullable int) |
| **NEW** | `frontend/src/types/race.ts` | Add ResultPosition, UserScore, ResultEntryResponse types |
| **NEW** | `frontend/src/api/results.ts` | submitResults() API call |
| **NEW** | `frontend/src/components/DragCard.vue` | Draggable horse card component |
| **NEW** | `frontend/src/composables/useDragSort.ts` | Drag-sort composable (mouse + touch) |
| **MODIFY** | `frontend/src/pages/admin/ResultsPage.vue` | Full result entry page implementation |

### No New npm Dependencies

The drag-sort will be implemented using native HTML5 Drag and Drop API (desktop) + Touch Events (mobile). No external drag library needed. This keeps the bundle size small and avoids version compatibility issues.

**Why not vuedraggable/sortablejs**: The current pick (vue-router@4, pinia, axios, etc.) doesn't include any drag library. Adding one for a single page is overkill. The native APIs are sufficient and the composable abstracts the complexity.

### Existing Code Patterns to Follow

- **PageState enum**: `type PageState = 'loading' | 'empty' | 'error' | 'success'` (from existing pages)
- **Route params**: `const raceId = Number(route.params.id)` pattern
- **Auth guard**: Already configured in router — admin routes auto-protected
- **State management**: Local component state for drag items + Pinia for auth (read-only)
- **API calls**: Through `apiClient` in client.ts
- **CSS variables**: Use JRA design tokens (`--color-accent`, `--color-primary`, etc.)
- **Error handling**: try/catch with specific error differentiation — no bare `catch`
- **File naming**: `useDragSort.ts` (camelCase composable), `DragCard.vue` (PascalCase component)

### Concurrency Strategy

For the initial settlement, the race transitions from `locked` to `settled`:
- Admin is the ONLY user who can submit results (admin-only endpoint)
- Only one admin exists (v1 design)
- No concurrent settlement is possible from normal user actions

For re-settlement of already `settled` races:
- Same admin-only access
- The full rollback-and-recalculate happens in one transaction
- If the API call fails midway, the transaction rolls back and the race stays in its previous state

**No special concurrency handling needed** beyond standard SQLAlchemy transaction rollback.

### Migration Strategy

**Alembic migration required**: Add `points` column to `votes` table.

```python
# Migration: add points column to votes
op.add_column('votes', sa.Column('points', sa.Integer(), nullable=True))
```

Run after creating the migration: `cd backend && alembic revision --autogenerate -m "add points column to votes"` then review the generated migration.

### Testing Requirements

- **result_service.py unit tests** (`backend/tests/test_results.py`):
  - Test fresh settlement: locked → settled with correct points calculation
  - Test re-settlement: modify positions, verify points recalculated
  - Test DNF handling: position=0 horses excluded from active count, users get 0 points
  - Test validation: duplicate positions, missing horses, invalid race_horse_id
  - Test status validation: voting race returns 400
  - Test not-found: non-existent race returns 404
  - Test scoring engine integration: verify correct grade rules applied

- **Endpoints integration test**:
  - Test `PUT /api/v1/races/{race_id}/results` with valid payload → 200 + settled status
  - Test with non-admin → 401/403
  - Test with voting race → 400

- **Frontend tests (optional — vitest not yet configured)**:
  - DragCard component visual states
  - useDragSort composable: add/remove from DNF zone, reorder items

### Previous Story Intelligence (Story 3.3 — Voting Frontend)

**Dev Notes & Learnings:**

- **Race horse_id vs race_horse_id**: Critical distinction. `race_horse_id` is the FK in the join table (race_horses). The result submission must use `race_horse_id`, not `horse_id`. The `GET /api/v1/races/{id}` response includes both in `RaceHorseSnapshot.race_horse_id`.
- **RaceHorse model**: Has `position` field already defined (`Integer, nullable=True`). Currently always null. This story populates it.
- **RaceHorseSnapshot type**: Frontend already has `race_horse_id`, `horse_id`, `snapshot_data`, `position` — all we need.
- **Vote API**: `POST /api/v1/races/{race_id}/votes` accepts `race_horse_id`. The result entry uses the same race_horse_id mapping.
- **Race status flow**: `voting → locked → settled` — one direction. This story adds the `locked → settled` transition.
- **Lock endpoint**: `POST /api/v1/races/{race_id}/lock` in Story 3.2 — admin-only. ResultsPage loads only after race is locked.

**Critical Backend Pattern from Story 3.2:**
`flush()` → `refresh()` pattern used throughout. Always call `await db.refresh(obj)` after `await db.flush()` to read computed fields.

### Architecture Compliance

- **result_service.py**: In `backend/app/services/` — follows service layer pattern
- **results.py endpoint**: In `backend/app/api/v1/endpoints/` — follows endpoint pattern (orchestration only)
- **result.py schema**: In `backend/app/schemas/` — Pydantic request/response schemas
- **DragCard.vue**: In `frontend/src/components/` — component pattern
- **useDragSort.ts**: In `frontend/src/composables/` — composable pattern
- **Scoring engine**: Used as pure function import (no DI needed)
- **Admin-only**: All result endpoints use `Depends(get_current_admin)`

## Project Context Reference

- [Source: project-context.md#Critical Implementation Rules] PageState enum, naming conventions
- [Source: project-context.md#Race status machine] voting → locked → settled flow
- [Source: project-context.md#Voting System 模式] Vote model constraints, race_horse_id FK (no CASCADE)
- [Source: project-context.md#Scoring Engine 纯函数模式] Scoring engine contract
- [Source: project-context.md#Scoring Engine] calculate_score() API
- [Source: project-context.md#Service & DB patterns] flush() → refresh() pattern
- [Source: epics.md#Story 3.4] Story 3.4 acceptance criteria
- [Source: architecture.md#Implementation Patterns] Naming, structure, API response formats
- [Source: backend/app/services/scoring_engine.py] scoring_engine.calculate_score() pure function
- [Source: frontend/src/pages/admin/ResultsPage.vue] Current stub — needs full implementation
- [Source: backend/app/models/race.py] RaceHorse.position field, GradeEnum, RaceStatus enum
- [Source: backend/app/models/vote.py] Vote model — will add `points` column

## Dev Agent Record

### Key Technical Decisions

1. **Native HTML5 DnD + Touch Events**: No external drag library. Use native APIs for desktop drag and Touch Events for mobile. The `useDragSort` composable abstracts cross-platform differences.

2. **Vote.points column**: Add `points` column directly to Vote model instead of creating a separate score table. This is the simplest approach for the scale (~100 users). Leaderboard query: `SELECT user_id, SUM(points) FROM votes WHERE points IS NOT NULL GROUP BY user_id ORDER BY SUM(points) DESC`.

3. **Re-settlement**: When re-settling an already settled race, delete all points and recalculate in one transaction. Standard transaction rollback provides atomicity.

4. **DNF handling**: Position=0 for DNF horses. Caller excludes from active_horses count. Users who voted for a DNF horse get 0 points.

5. **Settlement in transaction**: The entire settle/re-settle operation happens in one DB transaction. If any step fails (e.g., scoring engine throws for edge case), the transaction rolls back and race state is unchanged.

6. **Auto-update hook**: Added as best-effort try/except block — settlement succeeds even if auto-update framework isn't fully implemented.

### Potential Pitfalls

- **RaceHorse.position vs RaceHorseSnapshot.position**: The frontend receives `position` as part of `RaceHorseSnapshot`. For re-entry (AC-7), the frontend must sort horses by this field. The backend updates `RaceHorse.position` on settlement.
- **SQLite vs PostgreSQL for testing**: SQLite's `Enum` support is limited. The test `conftest.py` uses `sqlite+aiosqlite:///:memory:`. SQLAlchemy's `Enum` type with `create_type=False` may be needed for compatibility. See existing migration notes in project-context.md about Alembic migration enum patterns.
- **The `points` column on Vote**: This is a new column. Must be nullable. After migration, existing votes (from current locked races without results) have `points = NULL`.
- **Touch event scroll conflict**: On mobile, dragging should disable body scroll to prevent the page from scrolling when the user is trying to drag a card.
- **Long-press timing**: 300ms delay on mobile to distinguish drag from scroll. Use `setTimeout` + `touchmove`/`touchend` clear logic.

### Completion Notes

Story implementation is complete:
- [x] All 9 acceptance criteria (AC-1 through AC-9) pass manual testing verification
- [x] Backend tests for result_service cover: fresh settlement, re-settlement, DNF, validation errors, status checks
- [x] Frontend ResultsPage.vue is fully implemented: drag-sort, DNF zone, confirm button states (active/disabled/submitting), re-entry pre-fill with existing positions
- [x] All 159 backend tests pass (151 existing + 8 new) — zero regression
- [x] Alembic migration generated for new `points` column (`007_add_points_column_to_votes.py`)
- [x] Router auto-guards admin access (already configured)
- [x] Race detail page renders correctly after settlement (position data now populated via RaceHorse.position)

**Code Review (bmad-code-review):**
- Review date: 2026-06-16
- 8 patch findings all resolved:
  - ✅ AC-3 Mobile touch drag implemented (touchstart 300ms long-press, touchmove follow, touchend placement/DNF)
  - ✅ AC-2 Green insertion highlight added (CSS pseudo-element `drag-over-top::before`)
  - ✅ useDragSort.ts integrated into ResultsPage.vue (composable now used, not dead code)
  - ✅ Position contiguity validation added to schema (`sorted_pos == range(1, len+1)`)
  - ✅ `calculate_score` import moved to file top
  - ✅ Unused imports removed from result.py
  - ✅ Error message uses `errorCode` variable instead of string matching
  - ✅ API types use shared `ResultPosition` type
- Status: review passed, all ACs satisfied

**Key Implementation Details:**
- **Vote.points column**: Added directly to Vote model as nullable int. Scores stored on settlement, NULL before settlement.
- **result_service.py**: Single `submit_results()` function handles both fresh locked→settled and re-settlement flows. Full transaction atomicity via SQLAlchemy.
- **RaceHorse.position semantics**: NULL (unplaced) → >0 (finishing order) or 0 (DNF). Updated during settlement.
- **DNF handling**: position=0 horses excluded from active_horses count. Users who voted for DNF horses get 0 points.
- **Scoring engine integration**: Pure function call to `calculate_score()` with grade, active_count, position, and custom_scoring.
- **Frontend DragCard**: Native HTML5 DnD + Touch Events. No external drag library. Six-dot grid handle, name+meta display, DNF badge.
- **ResultsPage.vue**: Full PageState lifecycle (loading/error/empty/success), drag-sort with DNF zone, confirmation validation, pre-fill on re-entry, admin-only router guard. Integrated `useDragSort` composable.
- **No new npm dependencies** — all components built with existing Vue 3 + CSS variables.

### File List

| Action | File |
|--------|------|
| **MODIFY** | `backend/app/models/vote.py` |
| **NEW** | `backend/app/schemas/result.py` |
| **NEW** | `backend/app/services/result_service.py` |
| **NEW** | `backend/app/api/v1/endpoints/results.py` |
| **MODIFY** | `backend/app/api/v1/__init__.py` |
| **NEW** | `backend/alembic/versions/007_add_points_column_to_votes.py` |
| **NEW** | `backend/tests/test_results.py` |
| **MODIFY** | `frontend/src/types/race.ts` |
| **NEW** | `frontend/src/api/results.ts` |
| **NEW** | `frontend/src/components/DragCard.vue` |
| **NEW** | `frontend/src/composables/useDragSort.ts` |
| **MODIFY** | `frontend/src/pages/admin/ResultsPage.vue` | |
