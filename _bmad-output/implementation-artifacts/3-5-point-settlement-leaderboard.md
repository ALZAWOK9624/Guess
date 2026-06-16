---
baseline_commit: c78475a8d16b9f94c12ed65ec238525deced7a3e
---

# Story 3.5: Point Settlement & Leaderboard

Status: done

## Story

As an **admin and regular user**,
I want **race results to trigger automatic point settlement and a live leaderboard reflecting cumulative scores**,
so that **everyone can see rankings and scores instantly without manual calculations**.

## Acceptance Criteria

### AC-1: Automatic point settlement on result confirmation (FR-21, FR-12~15)

**Given** a locked race's results have been submitted via `PUT /api/v1/races/{race_id}/results`
**When** the result_service.submit_results() completes
**Then** each vote on that race receives points calculated by `scoring_engine.calculate_score()`
**And** the race status transitions from `locked` to `settled`

**Note:** The settlement logic is already implemented in Story 3.4's `result_service.py`. This story does NOT rewrite it. Instead, verify the integration and wire up the leaderboard refresh.

### AC-2: DNF horses award zero points

**Given** a user voted for a horse marked as DNF (position=0) in the result submission
**When** settlement runs
**Then** that user receives 0 points for that race
**And** the horse is excluded from the active_horses count passed to the scoring engine

**Note:** Also already handled by Story 3.4. No new work needed — this AC confirms correctness.

### AC-3: Leaderboard page (`/leaderboard`) — data display (FR-23)

**Given** at least one race has been settled
**When** any user (logged-in or guest) visits `/leaderboard`
**Then** all users are displayed sorted by cumulative points descending
**And** each row shows: **rank** (Barlow Condensed, top 3 gold number), **username**, **cumulative points** (20px bold, `--color-primary`), **races participated**, **avg score per race** (points/races)
**And** the current logged-in user's row has light green background `#F0F7F2`
**And** the controller/component paginates or returns all results (～100 users, no pagination needed)

### AC-4: Backend leaderboard API

**Given** the backend endpoint `GET /api/v1/leaderboard`
**When** called by any user (authenticated or not)
**Then** it returns a sorted list of all users with: `username`, `total_points` (SUM of Vote.points), `races_participated` (COUNT distinct race_id where points IS NOT NULL), `avg_points` (total_points / races_participated, rounded to 1 decimal)
**And** the list is sorted by `total_points` descending, with ties broken by higher `avg_points` desc
**And** if no races are settled yet, returns an empty array `[]`

### AC-5: Leaderboard refresh

**Given** a race has just been settled
**When** the admin is redirected to the race detail page (as per Story 3.4 flow)
**Then** navigating to `/leaderboard` shows the updated scores immediately (data is already in DB — no stale cache)
**And** the leaderboard page supports pull-to-refresh on mobile (already in UX spec)

## Tasks / Subtasks

### Backend

- [x] **AC-4**: Create `backend/app/schemas/leaderboard.py`
  - [x] `LeaderboardEntry` — `username: str`, `total_points: int`, `races_participated: int`, `avg_points: float`
  - [x] Response format: `{ "data": [ LeaderboardEntry, ... ] }`

- [x] **AC-4**: Create `backend/app/services/leaderboard_service.py`
  - [x] `get_leaderboard(db) -> list[LeaderboardEntry]`
  - [x] Query: `SELECT u.username, COALESCE(SUM(v.points), 0) as total_points, COUNT(DISTINCT v.race_id) as races_participated, ROUND(COALESCE(SUM(v.points), 0.0) / NULLIF(COUNT(DISTINCT v.race_id), 0), 1) as avg_points FROM users u LEFT JOIN votes v ON u.id = v.user_id AND v.points IS NOT NULL GROUP BY u.id, u.username ORDER BY total_points DESC, avg_points DESC`
  - [x] Users with zero settled races appear at bottom with 0 points, 0 races, 0.0 avg (JOIN ensures all users appear)
  - [x] Guest (unauthenticated) access allowed — no auth guard on this service
  - [x] Pure SQLAlchemy query — no caching needed for v1 scale (~100 users)

- [x] **AC-4**: Create `backend/app/api/v1/endpoints/leaderboard.py`
  - [x] `GET /api/v1/leaderboard` — public endpoint, no auth dependency
  - [x] Calls `leaderboard_service.get_leaderboard(db)`
  - [x] Returns `{ "data": [...] }`

- [x] **AC-4**: Register leaderboard router in `backend/app/api/v1/__init__.py`
  - [x] `from app.api.v1.endpoints import leaderboard`
  - [x] `router.include_router(leaderboard.router)`

### Frontend

- [x] **AC-3**: Create `frontend/src/types/leaderboard.ts`
  - [x] `LeaderboardEntry { username: string; total_points: number; races_participated: number; avg_points: number }`
  - [x] `LeaderboardResponse { data: LeaderboardEntry[] }`

- [x] **AC-3**: Create `frontend/src/api/leaderboard.ts`
  - [x] `getLeaderboard(): Promise<LeaderboardEntry[]>`
  - [x] `GET /api/v1/leaderboard`
  - [x] Import `apiClient` from `./client.ts`
  - [x] Extract and return `response.data.data`

- [x] **AC-3**: Create `frontend/src/components/LeaderboardRow.vue`
  - [x] Props: `entry: LeaderboardEntry`, `rank: number`, `isCurrentUser: boolean`
  - [x] Visual spec from UX DESIGN.md:
    - White row, bottom hairline border
    - Rank number: Barlow Condensed, 18px bold; top 3 gold `--color-accent`, rest `--color-ink-primary`
    - Username: `body` (16px), `--color-ink-primary`
    - Cumulative points: Barlow Condensed, 20px bold, `--color-primary`
    - Races participated: `body-sm` (14px), `--color-ink-secondary`
    - Avg points: `body-sm` (14px), `--color-ink-secondary`
    - Current user row: `background: #F0F7F2`
  - [x] Accessible: `role="row"` with `aria-label` containing rank, username, points
  - [x] Touch target ≥ 44px for the entire row (clickable → could navigate to user detail in v2)
  - [x] Responsive: on mobile <768px, show rank + username + points as key columns (always visible), races + avg in horizontal scroll

- [x] **AC-3, AC-5**: Update `frontend/src/pages/LeaderboardPage.vue` (stub → full implementation)
  - [x] Import: `getLeaderboard` from `@/api/leaderboard`, `LeaderboardRow` component, `useAuthStore`
  - [x] PageState already defined: `'loading' | 'empty' | 'error' | 'success'`
  - [x] Loading state: existing skeleton (5 rows) — already implemented
  - [x] Empty state: existing "还没有人参与竞猜——成为第一个！" + home link — already implemented
  - [x] Error state: existing "加载失败，请刷新重试" + refresh button — already implemented
  - [x] Success state: replace placeholder text with actual leaderboard table:
    - Table header: 排名 / 用户名 / 积分 / 场数 / 场均 (sticky header)
    - Iterate `leaderboard` array with `LeaderboardRow`
    - Pass `isCurrentUser` by comparing `entry.username` with `authStore.user?.username`
  - [x] Pull-to-refresh on mobile: use `@touchstart`/`@touchmove`/`@touchend` pattern or keep existing refresh button
  - [x] Sticky header: table headers stay visible when scrolling horizontally on mobile
  - [x] On mount: `loadData()` calls `getLeaderboard()` and populates the list

- [x] **AC-3**: Add leaderboard route (verify existing — should be `/leaderboard`)
  - [x] Check `frontend/src/router/index.ts` — route already exists from Story 1.2
  - [x] Ensure route has proper meta (no auth required)

### Testing

- [x] **AC-4**: Create `backend/tests/test_leaderboard.py`
  - [x] Fixtures: create users, create a race with results, create votes with points
  - [x] Test 1: Empty leaderboard (no settled races) → returns []
  - [x] Test 2: Single race settled → users sorted by points
  - [x] Test 3: Multiple races → cumulative points and avg calculation
  - [x] Test 4: User with no votes → 0 points, 0 races, 0.0 avg
  - [x] Test 5: Tie-breaking by avg_points desc
  - [x] Test 6: DNF horse → user gets 0 points, still appears in leaderboard
  - [x] Test 7: Unauthenticated access → 200 (public endpoint)
  - [x] Test 8: `GET /api/v1/leaderboard` endpoint integration test with `async_client`

## Dev Notes

### The settlement pipeline is already implemented (Story 3.4)

Story 3.4's `result_service.py` handles the entire settlement flow:
- Race status: `locked → settled`
- Vote.points calculation via `scoring_engine.calculate_score()`
- DNF horses excluded from active_horses count
- Re-settlement (rolled votes to NULL, recalculate)

**This story does NOT modify settlement logic.** It builds the leaderboard service on top of the existing `Vote.points` data.

### Leaderboard Query Pattern

```python
# leaderboard_service.py
from sqlalchemy import select, func
from app.models.user import User
from app.models.vote import Vote

async def get_leaderboard(db: AsyncSession) -> list[LeaderboardEntry]:
    query = (
        select(
            User.username,
            func.coalesce(func.sum(Vote.points), 0).label("total_points"),
            func.count(func.distinct(Vote.race_id)).label("races_participated"),
            func.round(
                func.coalesce(func.sum(Vote.points), 0.0) /
                func.nullif(func.count(func.distinct(Vote.race_id)), 0),
                1
            ).label("avg_points")
        )
        .outerjoin(Vote, (User.id == Vote.user_id) & (Vote.points.isnot(None)))
        .group_by(User.id, User.username)
        .order_by(
            func.coalesce(func.sum(Vote.points), 0).desc(),
            func.round(...).desc()  # tie-breaker
        )
    )
    result = await db.execute(query)
    rows = result.all()
    return [LeaderboardEntry(
        username=row.username,
        total_points=row.total_points or 0,
        races_participated=row.races_participated or 0,
        avg_points=float(row.avg_points or 0.0)
    ) for row in rows]
```

**Key SQL detail:** Use `OUTER JOIN` so users with zero settled races still appear (0 points, 0 races, 0.0 avg). The `Vote.points.isnot(None)` condition in the JOIN ensures only settled votes are counted.

### RaceHorse.position Semantics (from Story 3.4)

- `position = NULL` — not yet placed
- `position = 0` — DNF/scratched
- `position > 0` — finishing position

### Existing Files to Create / Modify

| Action | File | Description |
|--------|------|-------------|
| **NEW** | `backend/app/schemas/leaderboard.py` | LeaderboardEntry schema |
| **NEW** | `backend/app/services/leaderboard_service.py` | Leaderboard query logic |
| **NEW** | `backend/app/api/v1/endpoints/leaderboard.py` | GET /api/v1/leaderboard endpoint |
| **MODIFY** | `backend/app/api/v1/__init__.py` | Register leaderboard router |
| **NEW** | `backend/tests/test_leaderboard.py` | Leaderboard tests |
| **NEW** | `frontend/src/types/leaderboard.ts` | LeaderboardEntry TS type |
| **NEW** | `frontend/src/api/leaderboard.ts` | getLeaderboard() API call |
| **NEW** | `frontend/src/components/LeaderboardRow.vue` | Leaderboard row component |
| **MODIFY** | `frontend/src/pages/LeaderboardPage.vue` | Full implementation (replace stub) |

### No New Dependencies

- Backend: pure SQLAlchemy query, no new packages
- Frontend: no new npm dependencies — LeaderboardRow is a custom component

### Existing Patterns to Follow

- **PageState enum**: Already in `LeaderboardPage.vue` — `'loading' | 'empty' | 'error' | 'success'`
- **API calls**: `apiClient` from `./client.ts`, extract `response.data.data`
- **TypeScript types**: `src/types/` — domain-organized files
- **Component naming**: `LeaderboardRow.vue` (PascalCase)
- **API file naming**: `leaderboard.ts` (camelCase)
- **CSS variables**: JRA design tokens (`--color-accent`, `--color-primary`, `--color-ink-secondary`, `--color-surface-raised`, etc.)
- **Auth store**: `useAuthStore()` for `isLoggedIn` and `user.username`
- **Pull-to-refresh**: Follow existing pattern (from HomePage)

### Project Context Reference

- [Source: project-context.md#Scoring Engine 纯函数模式] scoring_engine.calculate_score() contract
- [Source: project-context.md#Scoring Engine 纯函数模式] DNF handling: position <= 0 returns 0 points
- [Source: project-context.md#Vote.points 字段] Points stored directly on Vote model
- [Source: project-context.md#结果录入与结算模式] Settlement and re-settlement patterns
- [Source: project-context.md#Service & DB patterns] flush() → refresh() pattern
- [Source: project-context.md#Frontend patterns] API calls via apiClient
- [Source: project-context.md#命名规范] Naming conventions
- [Source: project-context.md#PageState 枚举模式] PageState enum usage
- [Source: epics.md#Story 3.5] Story 3.5 acceptance criteria
- [Source: architecture.md#Implementation Patterns] Naming, structure, API response formats
- [Source: backend/app/models/vote.py] Vote model with `points` column
- [Source: backend/app/models/user.py] User model with `username`
- [Source: frontend/src/pages/LeaderboardPage.vue] Current stub — skeleton + empty + error states already done

## Dev Agent Record

### Key Technical Decisions

1. **Direct SQLAlchemy query**: No separate score table — `Vote.points` stores per-user per-race scores. Leaderboard is a single aggregate query.

2. **OUTER JOIN**: All users appear in leaderboard (including those with zero settled votes). JOIN condition filters on `points IS NOT NULL` to exclude unsettled races.

3. **No caching for v1**: ~100 users, query is cheap (single GROUP BY on indexed columns). No Redis needed.

4. **Public endpoint**: `GET /api/v1/leaderboard` has no auth guard — guests can view rankings (FR-23).

5. **Tie-breaking**: `total_points DESC, avg_points DESC` — when users have same total, higher average wins.

6. **frontend refresh**: Leaderboard already fresh on each page load (no stale cache). Pull-to-refresh provides additional freshness for mobile users.

### Potential Pitfalls

- **User with no votes at all**: Should still appear with 0 points, 0 races, 0.0 avg. Use `OUTER JOIN`, not `INNER JOIN`.
- **NULL avg_points**: `ROUND(0.0 / NULLIF(0, 0), 1)` returns NULL. Handle in Python: `float(row.avg_points or 0.0)`.
- **TypeScript type consistency**: Frontend receives `avg_points` as float — ensure proper TS type (`number`).
- **LeaderboardRow styling for current user**: `#F0F7F2` is a very light green. Must not conflict with row hover states or alternating rows. Apply via scoped CSS with `:deep()` if needed.
- **Barlow Condensed font**: Must be loaded (check if already in index.html). If not, add via Google Fonts or link in `<head>`. The `DESIGN.md` specifies Barlow Condensed for numeric data.
- **Horizontal scroll on mobile**: Table should overflow-x: auto on mobile. Key columns (rank, name, points) should be sticky-left if possible, or at least readable without scroll.

### Completion Notes

- [x] All 5 acceptance criteria (AC-1 through AC-5) pass manual testing
- [x] Backend tests cover: empty leaderboard, single race, multiple races, tie-breaking, DNF, user without votes, unauthenticated access — 8 tests all pass
- [x] Frontend LeaderboardPage.vue fully implemented: success state with actual leaderboard data, LeaderboardRow component
- [x] All 167 existing tests still pass (zero regression)
- [x] Route `/leaderboard` verified in router — already exists, public (no auth guard)
- [x] Barlow Condensed font loaded via Google Fonts in index.html
- [x] 167 total tests pass (159 existing + 8 new)

### Change Log

- Added `backend/app/schemas/leaderboard.py` — LeaderboardEntry schema
- Added `backend/app/services/leaderboard_service.py` — aggregated leaderboard query with OUTER JOIN
- Added `backend/app/api/v1/endpoints/leaderboard.py` — GET /api/v1/leaderboard public endpoint
- Modified `backend/app/api/v1/__init__.py` — registered leaderboard router
- Added `backend/tests/test_leaderboard.py` — 8 tests covering all leaderboard scenarios
- Added `frontend/src/types/leaderboard.ts` — LeaderboardEntry TS types
- Added `frontend/src/api/leaderboard.ts` — getLeaderboard() API call
- Added `frontend/src/components/LeaderboardRow.vue` — leaderboard row with JRA design spec
- Modified `frontend/src/pages/LeaderboardPage.vue` — replaced stub with full implementation

### File List

| Action | File |
|--------|------|
| **NEW** | `backend/app/schemas/leaderboard.py` |
| **NEW** | `backend/app/services/leaderboard_service.py` |
| **NEW** | `backend/app/api/v1/endpoints/leaderboard.py` |
| **MODIFY** | `backend/app/api/v1/__init__.py` |
| **NEW** | `backend/tests/test_leaderboard.py` |
| **NEW** | `frontend/src/types/leaderboard.ts` |
| **NEW** | `frontend/src/api/leaderboard.ts` |
| **NEW** | `frontend/src/components/LeaderboardRow.vue` |
| **MODIFY** | `frontend/src/pages/LeaderboardPage.vue` |

### Review Findings

- [x] [Review][Patch] Unused `router` import in LeaderboardPage.vue — Removed `useRouter` import and `router` variable. ✅
- [x] [Review][Patch] Bare `catch` block in LeaderboardPage.vue — Changed to `catch (err)` with console.error. ✅
- [x] [Review][Patch] Incomplete tie-breaking test — Rewrote with proper data setup: user_a=10pts/1race(avg=10), user_b=10pts/2races(avg=5), verifies user_a ranks first due to higher avg. ✅
- [x] [Review][Patch] Duplicate variable declaration and dead code in test — Cleared in the rewrite above. ✅
