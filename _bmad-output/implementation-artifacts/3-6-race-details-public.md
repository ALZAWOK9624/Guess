---
baseline_commit: bc444c1
---

# Story 3.6: Race Details Public View

Status: done

## Story

As an **all users (including guests)**,
I want **to view completed race results — final rankings, each user's vote and earned points — on the race detail page**,
so that **I can understand the full picture of a race and my friends' guessing performance**.

## Acceptance Criteria

### AC-1: Settled race — horses arranged by rank with position labels

**Given** a settled race (`Race.status == "settled"`)
**When** any user (logged in or guest) visits `/races/:id`
**Then** the horse list is sorted by `RaceHorse.position` ascending (1st, 2nd, 3rd...)
**And** each horse card shows a position label: `1st`, `2nd`, `3rd`, `4th`... (ordinal suffix), styled with Barlow Condensed bold
**And** horses with `position=0` (DNF) are listed last with label `DNF` in gray, opacity 0.5 (same as Story 3.4 DragCard DNF treatment)
**And** horses with `position=NULL` (not yet placed — should not occur for settled races) fall through gracefully

### AC-2: Per-horse vote list with usernames

**Given** a settled race
**When** viewing race details
**Then** under each horse, show a list of users who voted for that horse
**And** the list format: `username` line per voter (body-sm, `--color-ink-secondary`)
**And** if no votes for a horse, show `— 无人投给此马` in gray italic
**And** horses with zero votes do not take excessive visual space

### AC-3: Points display per vote

**Given** a settled race
**When** viewing race details
**Then** next to each user's vote, show the points earned for that race in format: `+10`, `-5`, `0`
**And** positive points are green (`--color-primary`), negative points are red (`--color-destructive`), zero is gray (`--color-ink-disabled`)
**And** points are styled with Barlow Condensed, 14px bold
**And** DNF horse votes show `0` in gray (since DNF = 0 points)

### AC-4: Voting race — real-time vote distribution (existing)

**Given** a race with status `voting`
**When** any user visits `/races/:id`
**Then** show real-time vote distribution: `username → horse name` — **this is already implemented in VotingDetail.vue, MUST NOT be duplicated**
**And** the voting detail refreshes after vote submission — **already handled by useVote composable**

### AC-5: Locked race — vote display

**Given** a locked race
**When** any user visits `/races/:id`
**Then** voting detail is frozen (shows final votes before locking) — **already implemented**
**And** logged-in users see their own vote highlighted — **already implemented**

### AC-6: Admin modify-result button

**Given** a settled race
**When** an admin views the race detail page
**Then** show an "修改结果" button linking to `/admin/races/{id}/results`
**And** the button is only visible to admin users (check `authStore.isAdmin`)
**And** styled as a secondary/outline action button (not primary CTA)

## Backend Tasks

### Task B1: Add `points` field to vote list response

**File:** `backend/app/schemas/vote.py`

- Add `points: int | None = None` to `VoteListEntry` schema

### Task B2: Include points in vote list endpoint for settled races

**File:** `backend/app/api/v1/endpoints/votes.py`

- In `list_votes` (`GET /api/v1/races/{race_id}/votes`):
  - The `vote_service.get_race_votes()` already returns vote objects with `points` loaded
  - Map `vote.points` to the response schema's new `points` field
  - **No change needed to service layer** — `Vote.points` is already loaded via `selectinload`

### Task B3: Add public race detail endpoint with vote grouping

**File:** `backend/app/schemas/result.py` (or create `backend/app/schemas/race_detail.py`)

Add schemas for the public result view:

```python
# In backend/app/schemas/result.py (or new file backend/app/schemas/race_detail.py)

class PublicVoteDetail(BaseSchema):
    username: str
    points: int | None  # None = unsettled, int = settled

class PublicResultHorse(BaseSchema):
    race_horse_id: int
    horse_id: int
    snapshot_data: dict  # already exists in race schemas
    position: int | None
    votes: list[PublicVoteDetail]  # users who voted for this horse
```

**File:** `backend/app/services/vote_service.py`

Add a new method:

```python
async def get_race_results_grouped_by_horse(
    db: AsyncSession, race_id: int
) -> list[dict]:
    """
    For a settled race, load all votes grouped by race_horse_id.
    Returns list of {race_horse_id, votes: [{username, points}]}
    Includes horses with zero votes (empty votes list).
    """
```

Implementation approach:
1. Load all `RaceHorse` for the race with `selectinload(RaceHorse.votes)` + `selectinload(Vote.user)`
2. Group votes by `race_horse_id` 
3. For each RaceHorse, build `PublicVoteDetail` list from its votes

**File:** `backend/app/api/v1/endpoints/races.py`

Add a new public endpoint (or modify existing `GET /{race_id}`):

```python
@router.get("/{race_id}/details")
async def get_race_detail_with_votes(race_id: int, db: AsyncSession = Depends(get_db)):
    """Returns full race detail with per-horse vote grouping for public view."""
    race = await race_service.get_race(db, race_id)
    if not race:
        raise HTTPException(status_code=404, detail=...)
    horse_votes = await vote_service.get_race_results_grouped_by_horse(db, race_id)
    # Return race detail + enriched horse data with vote info
```

**Alternative (simpler):** Instead of a new endpoint, extend the existing `GET /api/v1/races/{id}` endpoint to include a `horse_votes` field at the race detail level. This reduces the number of frontend API calls.

**RECOMMENDED APPROACH:** Extend the existing `RaceDetailResponse` schema to include an optional `horse_votes` field. Add the vote grouping logic to `vote_service.py` and use it in the races endpoint.

### Task B4: Test coverage

**File:** `backend/tests/test_races.py` (add tests)

Test scenarios for the public results view:
1. Settled race — horses sorted by position, votes grouped correctly
2. Settled race — DNF horse listed last with 0-point votes
3. Settled race — horse with zero votes shows empty votes list
4. Voting race — existing behavior unchanged
5. Locked race — existing behavior unchanged
6. Guest access — 200 (public endpoint)
7. Multiple users voted for same horse — all listed

## Frontend Tasks

### Task F1: Update vote types

**File:** `frontend/src/types/vote.ts`

```typescript
export interface VoteListEntry {
  user_id: number
  username: string
  race_horse_id: number
  horse_name: string
  points?: number | null  // NEW: only populated for settled races
  created_at: string
}
```

Add new types:

```typescript
// In frontend/src/types/race.ts

export interface PublicResultVote {
  username: string
  points: number | null
}

export interface RaceHorseResult {
  race_horse_id: number
  horse_id: number
  snapshot_data: Record<string, any>
  position: number | null
  votes: PublicResultVote[]
}

// In the RaceDetailResponse, add optional horse_votes field:
export interface RaceDetailResponse {
  // ... existing fields ...
  horse_votes?: RaceDetailHorseVotes  // only for settled races
}

export interface RaceDetailHorseVotes {
  horses: RaceHorseResult[]
}
```

### Task F2: Create `RaceResultView.vue` component

**File:** `frontend/src/components/RaceResultView.vue`

**NEW component** for showing settled race results (horse ranking + vote/points).

Props:
```typescript
interface Props {
  horses: RaceHorseResult[]  // sorted by position
}
```

**Visual specification (from DESIGN.md + EXPERIENCE.md):**

```
Component layout:
┌─────────────────────────────────────┐
│ 1st  [HorseDetailCard]              │
│      ┌─────────────────────────┐    │
│      │ user1 · +10 (green)     │    │
│      │ user3 · +10 (green)     │    │
│      └─────────────────────────┘    │
│─────────────────────────────────────│
│ 2nd  [HorseDetailCard]              │
│      ┌─────────────────────────┐    │
│      │ user2 · +5 (green)      │    │
│      └─────────────────────────┘    │
│─────────────────────────────────────│
│ ...                                 │
│─────────────────────────────────────│
│ DNF  [HorseDetailCard]              │
│      ┌─────────────────────────┐    │
│      │ user4 · 0 (gray)        │    │
│      └─────────────────────────┘    │
└─────────────────────────────────────┘
```

**Position labels:**
- `1st`, `2nd`, `3rd`: Gold background `var(--color-accent)` with white text, small badge
- `4th+`: Gray background `var(--color-ink-disabled)` with white text, small badge
- `DNF`: Gray background, italic text, on the DNF horse card (which has opacity 0.5)

**Vote list under each horse:**
- Each entry: `username` (body-sm, `--color-ink-secondary`) · `±N`(Barlow Condensed, 14px bold)
- Positive points: `--color-primary`
- Negative points: `--color-destructive`  
- Zero points: `--color-ink-disabled`
- No votes: `— 无人投给此马` (italic, `--color-ink-disabled`)
- Container: white background, rounded md, padding inside horse card area

**Accessibility:**
- Position labels use `aria-label` like "第一名", "第二名", "弃权"
- Vote list uses `aria-label` on each entry: "user1, +10分"
- Focusable container with proper heading hierarchy

**Behavior:**
- Pure display component — no interactivity beyond links
- Horses sorted by position (1, 2, 3...) with DNF (0) at bottom
- Uses existing `HorseDetailCard` for horse info section (reuse, don't duplicate)

### Task F3: Update `RaceDetailPage.vue`

**File:** `frontend/src/pages/RaceDetailPage.vue`

Changes:
1. **Load settled data**: Add `loadSettledResults(raceId)` that calls the new API (or extended existing API) to get horse_votes
2. **State management**: Add `settledResults: RaceDetailHorseVotes | null = ref(null)` and `loadingSettled: PageState`
3. **Render settled view**: In `<template>`, for `race.status === 'settled'`, replace the current horse list area with `<RaceResultView :horses="settledResults.horses" />`
4. **Remove future/past tab logic** if it exists — settled races show one unified view
5. **Admin modify button**: If `authStore.isAdmin`, show "修改结果" button linking to `/admin/races/${raceId}/results`

**State transitions for settled view:**
- `loading` → skeleton (existing pattern from HorseDetailCard skeleton)
- `empty` → should not happen (race exists, horses exist)
- `error` → "加载失败，请刷新重试" + refresh button
- `success` → RaceResultView component

### Task F4: Add API method

**File:** `frontend/src/api/races.ts`

```typescript
export async function getRaceDetailWithVotes(raceId: number): Promise<RaceDetailHorseVotes> {
  const response = await apiClient.get(`/races/${raceId}/details`)
  return response.data.data.horse_votes
}
```

Or if extending existing endpoint:

```typescript
// No new method needed — existing getRaceDetail() already returns race detail
// Just access the new horse_votes field from the response
```

### Task F5: Test coverage

**File:** `frontend/src/__tests__/` (vitest, not yet configured — skip or add manually tested notes)

Manual testing scenarios:
1. Settled race with multiple users per horse
2. Settled race with DNF horse
3. Settled race with horse that has zero votes
4. Voting race — no result view shown, existing voting detail preserved
5. Guest access — all info visible, no auth prompt
6. Admin view — "修改结果" button visible
7. Non-admin view — "修改结果" button hidden

## Dev Notes

### Existing Behavior to Preserve

**RaceDetailPage.vue currently:**
- `onMounted`: loads race detail, based on status decides whether to load votes
- `voting/locked`: loads votes via `loadVotes(raceId)` → VotingDetail component
- `settled`: does NOT load votes — this is what we're adding
- `VoteButton` at bottom: shows appropriate state for each race status
- `HorseDetailCard` list: shows all horses with snapshot_data

**CRITICAL: Do NOT modify VotingDetail.vue or the voting flow.** VotingDetail is already correct for voting/locked states. The settled result view is a NEW rendering path, not a modification of the existing voting view.

### Data Shape for Settled Results

The horse list returned by `GET /api/v1/races/{id}` already has:
```json
{
  "race_horse_id": 1,
  "horse_id": 1,
  "snapshot_data": { "name": "...", ... },
  "position": 1  // or null, or 0 for DNF
}
```

We need to extend this with per-horse vote data. The most efficient approach:

**Option A (Recommended):** Add a new endpoint `GET /api/v1/races/{id}/details` that returns:
```json
{
  "data": {
    "id": 1,
    "name": "...",
    "status": "settled",
    "grade": "G1",
    "date": "...",
    "custom_scoring": null,
    "horse_votes": {
      "horses": [
        {
          "race_horse_id": 1,
          "horse_id": 1,
          "snapshot_data": {...},
          "position": 1,
          "votes": [
            {"username": "user1", "points": 10},
            {"username": "user3", "points": 10}
          ]
        },
        {
          "race_horse_id": 2,
          "horse_id": 2,
          "snapshot_data": {...},
          "position": 2,
          "votes": [
            {"username": "user2", "points": 5}
          ]
        },
        {
          "race_horse_id": 3,
          "horse_id": 3,
          "snapshot_data": {...},
          "position": 0,
          "votes": [
            {"username": "user4", "points": 0}
          ]
        }
      ]
    },
    "vote_count": 4,
    ...existing fields
  }
}
```

**Key SQL/ORM approach** for `get_race_results_grouped_by_horse`:
```python
from sqlalchemy.orm import selectinload

query = (
    select(RaceHorse)
    .options(
        selectinload(RaceHorse.votes).selectinload(Vote.user),
        selectinload(RaceHorse.race)  # if needed
    )
    .where(RaceHorse.race_id == race_id)
    .order_by(
        # NULL last, then 0 (DNF) last, then position ascending
        case((RaceHorse.position == 0, 2), (RaceHorse.position.is_(None), 3), else_=1),
        RaceHorse.position.asc().nulls_last()
    )
)
result = await db.execute(query)
race_horses = result.scalars().all()
```

**Alternative — extend existing endpoint:** Simply add the `horse_votes` field to `RaceDetailResponse`. The existing endpoint already loads RaceHorses with positions. We just add vote loading when status is settled.

### Position sorting logic

For the settled view, horses must be sorted:
1. Horses with `position > 0`: ascending by position (1, 2, 3...)
2. Horses with `position = 0` (DNF): at the bottom
3. Horses with `position = NULL`: should not happen for settled races, but handle gracefully

### UX State Patterns Reference

From EXPERIENCE.md state patterns:

| State | Visual |
|-------|--------|
| **已结算** (settled) | 马匹按最终名次排列，名次标签（1st/2nd/3rd…）显示。每位用户的投票旁显示该场所获积分。 |
| **加载中** | Skeleton 占位符 — HorseDetailCard skeleton (reuse from project-context.md) |
| **网络错误** | "加载失败，请刷新重试" + 刷新按钮 |

### Microcopy

| Scenario | Text |
|----------|------|
| No votes for a horse | `— 无人投给此马` |
| Modify result (admin) | `修改结果` |
| DNF label | `DNF` |
| DNF microcopy | `退赛` (tooltip or secondary label) |

### Anti-patterns to Avoid

- **Do NOT** modify VotingDetail.vue for settled state — create a separate component (RaceResultView)
- **Do NOT** reuse the voting/selection logic from RaceDetailPage for the settled view
- **Do NOT** use the voting distribution API (`GET /api/v1/races/{id}/votes`) for settled results — use a dedicated endpoint or extended race detail
- **Do NOT** add pagination — ~100 users, results fit on one page
- **Do NOT** add websocket/SSE — poll-on-load is sufficient (settled data doesn't change without admin action)
- **Do NOT** add animations or transitions — JRA design is restrained, settled results are static
- **Do NOT** use `!important` except in utility classes

### File Structure Requirements

| Action | File | Description |
|--------|------|-------------|
| **MODIFY** | `backend/app/schemas/vote.py` | Add `points: int \| None` to VoteListEntry |
| **MODIFY** | `backend/app/schemas/race.py` | Add `RaceDetailHorseVotes` and `PublicResultVote` schemas |
| **MODIFY** | `backend/app/services/vote_service.py` | Add `get_race_results_grouped_by_horse()` method |
| **MODIFY** | `backend/app/api/v1/endpoints/races.py` | Extend `GET /{race_id}` with horse_votes when settled, or add new details endpoint |
| **MODIFY** | `frontend/src/types/vote.ts` | Add `points?: number \| null` to VoteListEntry |
| **MODIFY** | `frontend/src/types/race.ts` | Add RaceHorseResult, PublicResultVote, RaceDetailHorseVotes types |
| **NEW** | `frontend/src/components/RaceResultView.vue` | Settled race results display component |
| **MODIFY** | `frontend/src/api/races.ts` | Add getRaceDetailWithVotes() or extend existing |
| **MODIFY** | `frontend/src/pages/RaceDetailPage.vue` | Add settled state loading and RaceResultView rendering |
| **MODIFY** | `backend/tests/test_races.py` | Add tests for settled result view |

### Existing Patterns to Follow

- **Component naming**: `RaceResultView.vue` (PascalCase)
- **API file naming**: `races.ts` (camelCase)
- **API calls**: `apiClient` from `./client.ts`, extract `response.data.data`
- **PageState enum**: `'loading' | 'empty' | 'error' | 'success'` — already used in RaceDetailPage
- **CSS variables**: JRA design tokens (--color-primary, --color-accent, --color-ink-secondary, --color-destructive, etc.)
- **Auth store**: `useAuthStore()` for `user.is_admin` check
- **Skeleton loading**: Reuse global `skeleton-shimmer` animation from `base.css`
- **RaceHorseSnapshot** already includes `position: number | null`
- **HorseDetailCard** already receives `snapshotData` prop

### Key Implementation Decisions

1. **Separate component for settled view**: Create `RaceResultView.vue` that receives sorted horses with vote data. Keep all settled-specific rendering isolated from the voting code path.

2. **Extend existing race detail endpoint**: Add `horse_votes` to the `GET /api/v1/races/{id}` response when race is settled. This avoids an extra API call from the frontend and keeps the data model clean.

3. **Sorting in backend**: The API returns horses already sorted by position (1st, 2nd... DNF last). Frontend simply renders in order.

4. **Zero-vote horses**: The backend always returns all race_horses (even those with 0 votes). The `votes` field is empty array for un-voted horses.

5. **DNF position=0**: Returned at the end of the list with empty votes or votes from users who picked that horse (who get 0 points).

### Architectural Compliance

- **Layer separation**: Vote grouping logic in `vote_service.py`, endpoint orchestration in `races.py` endpoints, pure display in frontend component
- **No business logic in endpoints**: The endpoint calls `vote_service.get_race_results_grouped_by_horse()` and returns the result
- **snake_case API fields**: Keep consistent — frontend doesn't convert
- **Public endpoint**: No auth guard for the race detail endpoint — guests can view (FR-24)
- **Performance**: Single query with selectinload — no N+1, no caching needed for ~100 users

### Project Context Reference

- [Source: project-context.md#Race status machine] Race status transitions: voting → locked → settled
- [Source: project-context.md#RaceHorse.position 语义] position=0 = DNF, position=NULL = not placed, position>0 = finishing position
- [Source: project-context.md#Vote.points 字段] Points stored directly on Vote model, NULL before settlement
- [Source: project-context.md#DNF 处理模式] DNF horses excluded from active_horses count, votes get 0 points
- [Source: project-context.md#Results 结算 API 模式] Settlement pipeline in result_service.py
- [Source: project-context.md#结果录入与结算模式] RaceHorse.position semantics
- [Source: project-context.md#Service & DB patterns] flush() → refresh() pattern
- [Source: project-context.md#PageState 枚举模式] PageState enum usage
- [Source: project-context.md#命名规范] Naming conventions
- [Source: project-context.md#Critical Don't-Miss Rules] Anti-patterns: no dark mode, no WebSocket/SSE, no UI libraries, snake_case API fields
- [Source: project-context.md#Frontend patterns] API calls via apiClient
- [Source: project-context.md#VoteButton 状态机] VoteButton state machine (not modified by this story)
- [Source: project-context.md#RaceDetailPage 投票集成模式] Current RaceDetailPage voting integration (not modified by this story — only extended)
- [Source: UX/EXPERIENCE.md#State Patterns] Settled state: horses by rank, position labels, points per vote
- [Source: UX/DESIGN.md#Components] Horse Detail Card, position labels, color tokens

## Dev Agent Record

### Technical Decisions

1. **RaceResultView as new component**: Isolates settled-result rendering from existing voting/locked rendering. Prevents regressions in the voting flow.

2. **Extend existing race detail endpoint**: Adding `horse_votes` to the existing `GET /api/v1/races/{id}` response is simpler and reduces frontend API calls compared to a separate endpoint.

3. **Backend sorts horses by position**: The ORM query handles sorting so the frontend trivially renders in order.

4. **Vote.points already available**: `Vote.points` is populated during settlement (Story 3.4/3.5). No new DB columns or migrations needed.

5. **No new model or migration**: `RaceHorse.position` and `Vote.points` already exist. Only new schemas, service methods, and frontend components.

### Potential Pitfalls

- **Do NOT modify VotingDetail.vue**: It's used for voting/locked races. Create a separate RaceResultView for settled races.
- **Position sorting edge cases**: Handle DNF (position=0) and NULL position gracefully. NULL should not occur for settled races but don't crash.
- **Empty votes list**: A horse with no votes should still appear in the list (just with empty vote list).
- **User with multiple votes**: Per-race unique constraint already ensures one vote per user per race. No issue.
- **Color contrast**: Negative points in red must meet 4.5:1 contrast on white background. Use `--color-destructive` (`#C53030`) which passes on white.
- **aria-label for position labels**: Screen readers need ordinal position in Chinese ("第一名", "第二名") not English suffixes.

### Previous Story Learnings (Story 3.5)

- **Leaderboard query pattern**: OUTER JOIN ensures all users (even zero-point) appear. For per-horse vote lists, INNER JOIN is correct (we only show users who actually voted).
- **Catch block pattern**: All `catch` blocks must use `catch (err)` not bare `catch`.
- **Component naming**: PascalCase, cebab-case for CSS variables.
- **PageState enum**: Always use `'loading' | 'empty' | 'error' | 'success'`.
- **Existing 167+ tests must pass**: No regression allowed.

### Review Findings (Code Review 2026-06-16)

**Patch (resolved):**
- [x] [Review][Patch] Points font-size 16px → 14px [RaceResultView.vue:198]
- [x] [Review][Patch] Points missing Barlow Condensed font-family [RaceResultView.vue:197]
- [x] [Review][Patch] DNF no-votes text at 0.5 opacity — hard to read [RaceResultView.vue:123-125]
- [x] [Review][Patch] Vote.points=null renders dangling `· ` prefix [RaceResultView.vue:87]
- [x] [Review][Patch] Fragile string comparison `race.status.value == "settled"` [races.py:60]
- [x] [Review][Patch] Empty list treated as falsy in horse_votes check [races.py:79]
- [x] [Review][Patch] Empty horses array shows empty section heading [RaceResultView.vue:40]

**Deferred (pre-existing, not introduced by this change):**
- [x] [Review][Defer] Full User ORM object loaded unnecessarily — pre-existing pattern in vote_service.get_race_votes [vote_service.py:173]
- [x] [Review][Defer] Internal DB primary keys exposed — pre-existing in RaceHorseResponse schema [races.py:72]
- [x] [Review][Defer] Concurrent settlement + read can show votes with null points — pre-existing isolation concern
- [x] [Review][Defer] Unbounded memory for large vote sets — applies to all vote queries

**Dismissed (by design / FR requirement / spec):**
- [x] [Review][Dismiss] Usernames publicly visible — FR-24 requires public vote display
- [x] [Review][Dismiss] DNF horses always show 0 points — AC-3 spec requirement
- [x] [Review][Dismiss] horse_votes.horses sorted by position vs main horses sorted by horse_id — intentional design
- [x] [Review][Dismiss] Empty race with no horses — race cannot reach settled without horses

- [x] All 6 acceptance criteria (AC-1 through AC-6) pass manual testing
- [x] Backend tests cover: settled race grouping, DNF handling, zero-vote horses, guest access, voting race no-votes, public access — 7 new tests
- [x] RaceResultView.vue renders correctly for all settled states (1st/2nd/3rd gold, 4th+ gray, DNF gray italic, vote list per horse, points display)
- [x] RaceDetailPage.vue: settled state loads and renders RaceResultView without affecting voting/locked behavior
- [x] VotingDetail.vue NOT modified — existing voting flow preserved
- [x] All 174 existing tests pass (zero regression — was 167 before, added 7 new)
- [x] Responsive: RaceResultView renders correctly on mobile (single column) and desktop

### Change Log

- Added `points` field to `VoteListEntry` schema (backend)
- Added `points` mapping in `list_votes` endpoint (backend)
- Added `horse_votes` field to `RaceDetailResponse` schema (backend)
- Added `get_race_results_grouped_by_horse()` method in `vote_service.py` (backend)
- Extended `GET /api/v1/races/{id}` to include `horse_votes` for settled races (backend)
- Added 7 new tests in `TestRaceSettledResults` class (backend)
- Added `points` to `VoteListEntry` TypeScript type (frontend)
- Added `RaceDetailHorseVotes`, `RaceHorseResult`, `PublicResultVote` types (frontend)
- Created `RaceResultView.vue` component for settled race display (frontend)
- Updated `RaceDetailPage.vue` with RaceResultView and admin modify button (frontend)

### File List

| Action | File |
|--------|------|
| **MODIFY** | backend/app/schemas/vote.py — Added points field to VoteListEntry |
| **MODIFY** | backend/app/schemas/race.py — Added horse_votes field to RaceDetailResponse |
| **MODIFY** | backend/app/services/vote_service.py — Added get_race_results_grouped_by_horse() |
| **MODIFY** | backend/app/api/v1/endpoints/races.py — Import vote_service, extend GET with horse_votes |
| **MODIFY** | backend/app/api/v1/endpoints/votes.py — Include points in list_votes response |
| **MODIFY** | frontend/src/types/vote.ts — Added points to VoteListEntry |
| **MODIFY** | frontend/src/types/race.ts — Added RaceDetailHorseVotes, RaceHorseResult, PublicResultVote types |
| **NEW** | frontend/src/components/RaceResultView.vue — Settled race results display component |
| **MODIFY** | frontend/src/pages/RaceDetailPage.vue — Import RaceResultView, add settled view + admin button |
| **MODIFY** | backend/tests/test_races.py — Added TestRaceSettledResults class (7 new tests) |
