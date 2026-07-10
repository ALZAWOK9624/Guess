---
title: 'Fix Leaderboard Filter — Race Tag Join Condition Ineffective'
type: 'bugfix'
created: '2026-07-10'
status: 'done'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The leaderboard page's race-tag filters (age_range, sex_restriction, race_grade, country, surface) have no effect. The backend applies filters to the `Vote LEFT JOIN Race` connection condition, but LEFT JOIN preserves all Vote rows regardless of whether a matching Race exists. Non-matching votes still have `points IS NOT NULL`, so they pass the outer User→Vote join condition and are included in the SUM aggregation.

**Approach:** Replace the join-condition filtering in `leaderboard_service.py` with a filtered subquery: SELECT only Votes joined to matching Races, then LEFT JOIN Users to that filtered set. Also fix the frontend's `hasActiveFilters()` which omits `surface`.

## Boundaries & Constraints

**Always:**
- Users with no qualifying votes must still appear in the leaderboard with 0 points
- Admin users remain excluded from the leaderboard
- Same 6 tag filters + 3 numeric range filters remain supported
- All existing filter options and values stay the same

**Ask First:**
- None

**Never:**
- Do NOT change the API contract (same query params, same response shape)
- Do NOT add new dependencies or ORM patterns
- Do NOT alter the distance/horse_count range filter logic (those are not broken)

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Single tag filter | `?age_range=2岁` | Only points from races with age_range='2岁' counted; other races' votes excluded | N/A |
| Multi-tag same category | `?age_range=2岁&age_range=3岁` | Points from races with either age_range='2岁' OR '3岁' counted | N/A |
| Cross-category AND filter | `?age_range=2岁&surface=草地` | Only votes where race has age_range='2岁' AND surface='草地' | N/A |
| User has qualifying + non-qualifying votes | User A: 10pts from matching race + 5pts from non-matching race | User A shows 10pts (non-matching excluded) | N/A |
| User has only non-qualifying votes | User B: 5pts from non-matching race only | User B shows 0pts, races_participated=0 | N/A |
| Surface-only filter with badge | `filters.surface=['草地']` | Filter badge shown, clear button visible | N/A |
| No filters active | No query params | All settled-race votes counted (current behavior preserved) | N/A |

</frozen-after-approval>

## Code Map

- `backend/app/services/leaderboard_service.py` — Core backend query logic; current join-condition approach is the root cause
- `frontend/src/pages/LeaderboardPage.vue` — Frontend filter UI; `hasActiveFilters()` missing surface check

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/services/leaderboard_service.py` — Replace Vote→Race LEFT JOIN with filter in ON clause with a filtered subquery (Vote INNER JOIN Race WHERE race_filters) then User LEFT JOIN subquery. Remove the `vote_join` / `vote_race_join` intermediate join construction.
- [x] `frontend/src/pages/LeaderboardPage.vue` — Add `filters.value.surface?.length` to `hasActiveFilters()` condition (line 31).

**Acceptance Criteria:**
- Given an active age_range filter, when leaderboard data loads, then only votes from races matching the filter contribute to point totals
- Given combined multi-category filters, when leaderboard data loads, then only votes from races matching ALL active filters are counted
- Given a user with zero qualifying votes after filtering, when leaderboard data loads, then the user appears with 0 points and 0 races
- Given only surface filter active, when the page renders, then the filter badge and "清除筛选" button are visible

## Design Notes

The core issue: this SQL pattern does NOT filter:
```sql
-- WRONG: filter in LEFT JOIN ON clause — left table rows always survive
Vote LEFT JOIN Race ON vote.race_id = race.id AND race.age_range IN ('2岁')
```

The correct pattern uses a subquery to pre-filter Votes:
```sql
-- RIGHT: filter votes first, only then join users
User LEFT JOIN (
    SELECT vote.user_id, vote.points, vote.race_id
    FROM vote JOIN race ON vote.race_id = race.id
    WHERE vote.points IS NOT NULL AND race.age_range IN ('2岁')
) AS fv ON user.id = fv.user_id
```

When no filters are active, the original simple join behavior is preserved — the subquery is only used when at least one filter is provided.

## Suggested Review Order

**Core query fix** — the filtered subquery approach replaces broken join-condition filtering

- Entry point: `has_filters` branch dispatches to filtered Vote→Race INNER JOIN subquery with WHERE clauses that actually exclude non-matching votes
  [`leaderboard_service.py:38`](../../backend/app/services/leaderboard_service.py#L38)

- Tag filters (`age_range`, `surface`, etc.) applied as `.where()` on the INNER JOIN subquery — these are real filters, not LEFT JOIN ON conditions
  [`leaderboard_service.py:54`](../../backend/app/services/leaderboard_service.py#L54)

- Distance and horse_count range filters apply identically but now as subquery WHERE clauses instead of join conditions
  [`leaderboard_service.py:66`](../../backend/app/services/leaderboard_service.py#L66)

- Main aggregation now references `filtered_votes.c.points` / `.race_id` — the subquery column aliases, not direct Vote table columns
  [`leaderboard_service.py:97`](../../backend/app/services/leaderboard_service.py#L97)

- User LEFT JOINs the filtered subquery on `user_id` — users with no qualifying votes still appear with 0 points
  [`leaderboard_service.py:115`](../../backend/app/services/leaderboard_service.py#L115)

**UI completeness** — surface filter badge visibility fix

- `hasActiveFilters()` now includes `surface` so the filter badge and clear button appear when only surface is selected
  [`LeaderboardPage.vue:33`](../../frontend/src/pages/LeaderboardPage.vue#L33)

## Verification

**Commands:**
- `cd backend && python -m pytest tests/ -k leaderboard -v` — expected: all leaderboard tests pass
- `cd frontend && pnpm build` — expected: build succeeds without TypeScript errors
