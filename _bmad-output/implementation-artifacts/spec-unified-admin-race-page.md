---
title: 'Unified admin interactions on race page'
type: 'feature'
created: '2026-07-01'
baseline_commit: 'dfa859f86ec66191e4ac08bfc5cac858e1a8e837'
status: 'done'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Admin race operations (create race, edit name/date, add/modify horses, set gate order, lock race, enter results) are currently spread across separate admin pages. The race detail page is read-only for admins, forcing context switching.

**Approach:** Move all admin race interactions into the public race detail page and the home page, while keeping the existing admin pages as fallback. Introduce a per-race `gate` field to persist gate order, and add backend endpoints for incremental horse management and gate reordering.

## Boundaries & Constraints

**Always:**
- Follow existing stack (Vue 3 + Pinia + FastAPI + SQLAlchemy + snake_case API fields).
- Admin-only actions require `isAdmin`; all race mutations use existing admin endpoints or new admin-only endpoints.
- Only `voting` races can be edited/have horses added/have gate order changed; only `locked`/`settled` races can enter result ranking.
- Horse snapshots remain immutable; editable cells are per-race `weight` and `jockey` (stored on `RaceHorse` and mirrored into `snapshot_data`).
- Existing `CreateRacePage`, `EditRacePage`, and `ResultsPage` are kept as fallback but the primary flow is the race detail page.
- UI uses existing JRA design tokens, custom CSS only, and `ConfirmDeleteModal` for destructive actions.
- All async operations use `catch (err)` and surface user-friendly messages.

**Ask First:**
- If adding a new horse requires creating a brand-new horse record (not just selecting from the library), because the current scope assumes selection from the existing horse library.
- If existing admin pages (`CreateRacePage`/`EditRacePage`/`ResultsPage`) should be removed rather than kept as fallback.

**Never:**
- Do not allow non-admin users to see or trigger admin interactions.
- Do not modify horse library data from the race page (only per-race `weight`/`jockey` and `RaceHorse` snapshots).
- Do not change the voting status machine (`voting` → `locked` → `settled`).
- Do not use WebSocket/SSE; poll or explicit submit only.
- Do not add external UI libraries.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Admin creates race from home | Name + date + grade | Race created (0 horses allowed), navigate to detail | Validation errors shown inline |
| Admin edits race name/date | Double-click or pencil on header | Inline editor appears, PATCH only changed fields | Revert on error; show message |
| Admin adds horse | Click + card, select from library | `POST` adds RaceHorse, page refreshes | Reject duplicate horse; show error |
| Admin edits jockey/weight | Double-click cell | Inline input, save on blur/Enter, PATCH race_horse | Revert on error |
| Admin drags gate order | Voting state, drag card | `gate` values persisted, number on far right updates | N/A |
| Admin locks race | Voting state, click lock | `POST /lock`, status becomes `locked`, gate drag disabled | Show error if votes? no, lock is unconditional |
| Admin enters result mode | Locked state, click 比赛结束 | Page switches to result ranking mode, DNF zone shown | N/A |
| Admin confirms results | Result mode, click 确认结果 | `PUT /results`, race settled, leaderboard updated | Validation errors shown; remain in mode |
| Admin re-enters results | Settled state, click 修改结果 | Result ranking mode reopens with existing positions | Same as above |

</frozen-after-approval>

## Code Map

- `backend/app/models/race.py` -- add `gate` column to `RaceHorse`.
- `backend/app/schemas/race.py` -- add `gate` to `RaceHorseResponse`; add `RaceHorseUpdate` schema; make `horse_ids` optional in `RaceCreate`.
- `backend/app/services/race_service.py` -- support creating race with 0 horses; add `update_race_horse`, `add_horse_to_race`, `update_gate_order`.
- `backend/app/api/v1/endpoints/races.py` -- add admin endpoints: `POST /{race_id}/horses`, `PATCH /{race_id}/horses/{race_horse_id}`, `PATCH /{race_id}/horses/gate`.
- `backend/app/api/v1/endpoints/votes.py` -- already exposes `POST /{race_id}/lock`.
- `backend/app/api/v1/endpoints/results.py` -- already exposes `PUT /{race_id}/results`.
- `frontend/src/types/race.ts` -- add `gate` to `RaceHorseSnapshot`; add `RaceHorseUpdatePayload`, `GateOrderPayload`.
- `frontend/src/api/races.ts` -- add `addRaceHorse`, `updateRaceHorse`, `updateGateOrder`.
- `frontend/src/pages/HomePage.vue` -- add admin "创建比赛" button + modal.
- `frontend/src/pages/RaceDetailPage.vue` -- admin header editing, lock button, result mode toggle, horse list with drag, + card, editable cells.
- `frontend/src/components/HorseDetailCard.vue` -- add `gate`/`position` badge props, editable `weight`/`jockey` cells, drag handle.
- `frontend/src/components/HorseSearchSelect.vue` -- reused for adding horses from the library.
- `frontend/src/composables/useDragSort.ts` -- extend to support single-list gate reordering (no DNF) and reuse for result mode.
- `frontend/src/api/results.ts` -- already exposes `submitResults`.

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/models/race.py` -- add `gate: Mapped[int | None]` to `RaceHorse`; generate Alembic migration.
- [x] `backend/app/schemas/race.py` -- add `gate` to `RaceHorseResponse`; create `RaceHorseUpdate` (weight, jockey); make `horse_ids` optional and allow empty list in `RaceCreate`.
- [x] `backend/app/services/race_service.py` -- allow 0 horses in `create_race`; add `add_horse_to_race`, `update_race_horse`, `update_gate_order`.
- [x] `backend/app/api/v1/endpoints/races.py` -- add `POST /{race_id}/horses`, `PATCH /{race_id}/horses/{race_horse_id}`, `PATCH /{race_id}/horses/gate`.
- [x] `frontend/src/types/race.ts` -- add `gate` field; add `RaceHorseUpdatePayload`, `GateOrderPayload`, `RaceCreatePayload` with optional `horse_ids`.
- [x] `frontend/src/api/races.ts` -- add `addRaceHorse`, `updateRaceHorse`, `updateGateOrder` calls.
- [x] `frontend/src/pages/HomePage.vue` -- add floating "+ 创建比赛" button for admin; modal with name/date/grade; navigate to new race.
- [x] `frontend/src/components/RaceHeaderEditor.vue` -- new inline editor for name/date with double-click + pencil trigger.
- [x] `frontend/src/components/HorseDetailCard.vue` -- display `gate` badge on far right; display `position` badge on far left; editable `weight`/`jockey` cells on double-click.
- [x] `frontend/src/components/AddHorseCard.vue` -- new + card same size as HorseDetailCard.
- [x] `frontend/src/pages/RaceDetailPage.vue` -- integrate admin header editor, lock button, add horse flow, gate drag (voting), result mode (locked/settled), confirm result submission.
- [x] `frontend/src/composables/useDragSort.ts` -- support gate-only mode (no DNF, single list) and preserve existing result mode.
- [x] `backend/alembic` -- create migration for `race_horses.gate` column.
- [x] `backend/tests/test_races.py` -- add tests for 0-horse creation, add horse, update horse, and gate ordering endpoints.

**Acceptance Criteria:**
- Given admin on home page, when clicking "创建比赛" and filling name/date/grade, then a new race is created and the browser navigates to it.
- Given admin on race detail page (voting), when double-clicking race name or date, then an inline editor appears and saving updates the race.
- Given admin on race detail page (voting), when clicking the + horse card, then a horse selector opens and the selected horse is added to the race.
- Given admin on race detail page (voting), when double-clicking a weight/jockey cell, then the cell becomes an input and saving updates the per-race value.
- Given admin on race detail page (voting), when dragging a horse card, then the gate number on the far right updates and the order is persisted.
- Given admin on race detail page (voting), when clicking "锁定", then the race becomes locked.
- Given admin on race detail page (locked), when clicking "比赛结束", then the page enters result ranking mode with a DNF zone and position numbers on the far left.
- Given admin in result ranking mode, when clicking "确认结果", then the race settles, points are calculated, leaderboard is updated, and other users see the result on refresh.
- Given admin on race detail page (settled), when clicking "修改结果", then result ranking mode reopens with current positions.

## Design Notes

**Inline editing pattern:**
- Race header uses a small `RaceHeaderEditor` component that toggles between display and `<input>` fields on double-click or pencil click. Save triggers `PATCH` with only changed fields; `Esc` cancels.
- Horse card cells use `contenteditable` or inline `<input>` with `blur`/`Enter` save and `Esc` cancel. Only `weight` and `jockey` cells are editable; clicking/dragging still works on non-editable areas.

**Gate vs result modes:**
- Gate mode: single list, no DNF, all cards have a far-right `gate` badge. Admin drag reorders the list; on drop, `PATCH /api/v1/races/{id}/horses/gate` is called with the new ordering.
- Result mode: two lists (active + DNF), far-left position badge. Reuses `useDragSort` and `submitResults` from `ResultsPage`, but embedded in `RaceDetailPage`.

**Creating a race with 0 horses:**
- The backend `RaceCreate` schema will make `horse_ids` optional (default empty list). `create_race` skips snapshot creation when empty. The minimum-2 validation only applies when horses are provided.

**Adding horses:**
- `POST /api/v1/races/{race_id}/horses` receives `{ horse_id: int, weight?: string, jockey?: string }`. It creates a `RaceHorse` with a fresh snapshot from the horse library. Duplicates by `horse_id` within the same race are rejected.

## Verification

**Commands:**
- `cd backend && python -m pytest tests/` -- all tests pass.
- `cd frontend && pnpm build` -- no type errors.

**Manual checks:**
- Home page shows "创建比赛" button only for admin; modal creates race and navigates to detail.
- Race detail page (voting) lets admin edit name/date, add horses, edit jockey/weight, drag gate order, and lock.
- Race detail page (locked) shows "比赛结束" which opens result ranking mode; confirming settles the race and updates leaderboard.
- Non-admin users see the same page without any admin controls.