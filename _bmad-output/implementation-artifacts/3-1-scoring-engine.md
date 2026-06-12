---
baseline_commit: f1d18fe91d8f9f30b4caeddc1609c0dc82662e7d
---

# Story 3.1: Integrate Rules Engine (Scoring Engine)

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **system**,
I want **a pure-function scoring engine supporting 4 race-grade rules (G1, G2/JPN1, YOUNG_G1, Custom)**,
so that **when race results are confirmed, points for every user's vote are computed correctly and identically to manual calculation**.

## Acceptance Criteria

### AC-1: Pure function module with zero external dependencies

**Given** `scoring_engine.py` is implemented as a pure function module
**When** imported and used
**Then** the module has zero external dependencies (no FastAPI, no SQLAlchemy, no DB)
**And** the main entry function accepts (grade, total_horses, user_voted_position) and returns an integer score

### AC-2: G1 scoring with position-based penalties (FR-12)

**Given** a race of grade G1 with 8+ horses
**When** positive scoring: 1st=+10, 2nd=+5, 3rd=+3, 4th=+2, 5th=+1
**And** penalty scoring (≥8 horses): last place=-10, 2nd-to-last=-5, 3rd-to-last=-1
**Then** all boundary combinations match manual calculation 100%

| Horse Count | Positive Tiers | Penalty Tiers |
|-------------|----------------|---------------|
| ≥8 | +10/+5/+3/+2/+1 | -10(pos=-1), -5(pos=-2), -1(pos=-3) |
| 7 | +10/+5/+3/+2/+1 | -5(pos=-1), -1(pos=-2) |
| 6 | +10/+5/+3/+2/+1 | -1(pos=-1) |
| ≤5 | +10/+5/+3/+2/+1 | None |

### AC-3: G2/JPN1 scoring without penalties (FR-13)

**Given** a race of grade G2_JPN1
**When** scoring: 1st=+5, 2nd=+4, 3rd=+3, 4th=+2, 5th=+1
**Then** no negative points regardless of horse count
**And** 6th place and below = 0 points

### AC-4: YOUNG_G1 scoring — G1 positives, no penalties (FR-14)

**Given** a race of grade YOUNG_G1
**When** positive scoring same as G1 (+10/+5/+3/+2/+1)
**Then** no negative points regardless of horse count
**And** last place never receives negative points

### AC-5: Custom scoring with user-defined rules (FR-15)

**Given** a race of grade CUSTOM with `custom_scoring = {"positive_scores": [10,7,5,3,2,1], "penalty_rules": [{"position": -1, "points": -5}, {"position": -2, "points": -2}]}`
**When** a user picks the 1st-place horse
**Then** they get 10 points
**When** a user picks the last-place horse
**Then** they get 5 points for the 6th position minus 5 penalty = 0 total
**When** `penalty_rules` is None/empty
**Then** only positive scores apply, no negative points

### AC-6: DNF/scratched horses (edge case)

**Given** a horse is scratched or DNF
**When** a user voted for that horse
**Then** score is 0
**And** that horse is excluded from penalty-calculation denominators

### AC-7: Edge cases

**Given** a user votes for a horse that finishes outside positive-score positions
**When** no penalty applies
**Then** score is 0
**When** penalty applies
**Then** score is the penalty value (negative)

## API Contract

```python
def calculate_score(
    grade: str,                    # "G1" | "G2_JPN1" | "YOUNG_G1" | "CUSTOM"
    total_horses: int,             # total active (non-DNF) horses
    position: int,                 # final position of the horse user voted for (1-indexed)
    custom_scoring: dict | None = None,  # required when grade == "CUSTOM", else ignored
) -> int:
    """
    Pure function. Returns net points for the user's vote.

    - position is 1-indexed (1 = winner)
    - DNF/scratched horses should NOT be counted in total_horses; the caller filters them out.
    - custom_scoring shape: {"positive_scores": [int, ...], "penalty_rules": [{"position": int, "points": int}]}
    """
```

## Files to Create/Modify

| Action | File | Description |
|--------|------|-------------|
| **NEW** | `backend/app/services/scoring_engine.py` | Pure function scoring engine |
| **NEW** | `backend/tests/test_scoring_engine.py` | 100% branch coverage unit tests |

## Dev Notes

### Scoring Logic Detail

**G1 penalty calculation (key complexity):**
- "倒数第N名" means position = total_horses - N + 1 (1-indexed)
- E.g., 8 horses: "倒数第1名" = position 8, "倒数第2名" = position 7, "倒数第3名" = position 6
- When a position qualifies for both positive AND penalty scores (e.g., 8 horses, position 6 = 3rd-to-last), both apply: 0 (no positive) + (-1) = -1
- For 8 horses, position 5 = +1 (positive), position 6 = -1 (penalty), position 7 = -5, position 8 = -10
- For 8 horses, position 5 gets +1 AND no penalty (not in last 3)

**Custom scoring edge cases:**
- `positive_scores` list is 1-indexed: `positive_scores[0]` applies to 1st place
- If `position > len(positive_scores)`, position gets 0 from positive scores (then penalty may apply)
- `penalty_rules` positions are negative from end: -1 = last, -2 = 2nd-to-last, etc.
- Convert to absolute: `abs_position = total_horses + position + 1` (since position is negative)

### Architecture Compliance
- File location: `backend/app/services/scoring_engine.py` per architecture doc
- Pure function pattern — matches architecture mandate: "scoring_engine.py — pure function module, zero external dependencies, independently testable"
- No FastAPI/DB imports allowed — this is intentional to keep it testable
- The `CustomScoring` schema and `GradeEnum` already defined in `backend/app/schemas/race.py` and `backend/app/models/race.py` — use enum values as strings: "G1", "G2_JPN1", "YOUNG_G1", "CUSTOM"

### Testing Requirements
- **Must achieve 100% branch coverage** for all 4 rule types + edge cases
- pytest with `asyncio_mode = auto` (standard in this project)
- Test file: `backend/tests/test_scoring_engine.py`
- **No fixtures needed** — pure function means direct import and call
- Test matrix:
  - G1 with 5, 6, 7, 8, 10, 15 horses (each horse count = different penalty tier)
  - G2_JPN1 with 5, 8, 15 horses
  - YOUNG_G1 with 5, 8, 15 horses
  - Custom with various positive_scores and penalty_rules combos
  - DNF exclusion from penalty denominator
  - Position beyond positive_scores range
  - Negative position for custom penalty

### Previous Story Intelligence (from Epic 2 Retrospective)
- **PATCH null覆盖问题**: Already handled in existing patterns — not relevant to this pure function story
- **Database migration enum issue**: Not relevant — no DB changes in this story
- **Testing infrastructure is key**: This is the first story where the scoring engine's 100% branch coverage requirement applies. The scoring engine is referenced in SM-2 (积分零差异) — correctness is non-negotiable

### Git Intelligence (Recent Work Patterns)
- Recent commits show consistent patterns: each story creates service + tests + endpoint files
- Story 2.5 (auto-update framework) is most recent — established `flush()` → `refresh()` pattern, manual edit tracking
- Epic 2 retrospective emphasizes: testing infrastructure is critical (106 tests, zero regression)

### Critical Don't-Miss Rules (from project context)
1. **Do NOT import `useAuthStore` in client.ts** — circular dependency warning (not applicable here, pure function)
2. **Do NOT use sync endpoints** — all FastAPI endpoints must be async def (not directly applicable since scoring_engine is pure function, but callers will use it async)
3. **scoring_engine must be pure function** — zero external dependencies
4. **100% branch coverage required** for scoring engine — project context rule

### Project Context Reference
- [Source: project-context.md#Technology Stack & Versions] pytest + pytest-asyncio
- [Source: architecture.md#Implementation Patterns & Consistency Rules] API response format, naming
- [Source: epics.md] Epic 3 story 3.1 acceptance criteria (AC-1 through AC-7 above)
- [Source: schemas/race.py] CustomScoring schema definition
- [Source: models/race.py] GradeEnum definition

## Tasks / Subtasks

- [x] AC-1: Create scoring_engine.py as pure function module
  - [x] Define public API `calculate_score(grade, total_horses, position, custom_scoring=None) -> int`
  - [x] Create helper `_get_positive_score(grade, position) -> int` for positive score lookups
  - [x] Create helper `_get_penalty_score(grade, total_horses, position) -> int` for penalty deduction lookups
- [x] AC-2: Implement G1 scoring with tiered penalties
  - [x] Implement positive score table for G1 (+10, +5, +3, +2, +1)
  - [x] Implement penalty logic for ≥8, 7, 6, ≤5 horse tiers
- [x] AC-3: Implement G2/JPN1 scoring
  - [x] Implement positive score table (+5, +4, +3, +2, +1)
  - [x] Verify no penalty logic applies
- [x] AC-4: Implement YOUNG_G1 scoring
  - [x] Reuse G1 positive scores, skip penalties
- [x] AC-5: Implement Custom scoring
  - [x] Parse custom_scoring dict into positive scores and penalty rules
  - [x] Apply positive scores from custom list by position
  - [x] Apply custom penalty rules by end-relative position
- [x] AC-6: Handle DNF/scratched (input: position=0 or None → return 0)
- [x] AC-7: Edge cases (position beyond score list, custom empty penalty_rules
- [x] NEW: Create `backend/tests/test_scoring_engine.py` with 100% branch coverage
  - [x] G1 matrix: test all horse count tiers (5, 6, 7, 8, 10, 15) with all position combinations
  - [x] G2_JPN1: test with varying horse counts
  - [x] YOUNG_G1: test with varying horse counts
  - [x] Custom: test with various positive_scores and penalty_rules
  - [x] DNF edge cases: position=0 returns 0

## Dev Agent Record

### Agent Model Used

Deepseek-V4-Flash

### Debug Log References

- G1 penalty tier logic: position-to-absolute conversion uses `total_horses + offset + 1` formula
- Custom penalty rules use same absolute-position conversion with user-defined offsets
- No external dependencies — pure Python, no imports beyond typing

### Completion Notes List

- Created `backend/app/services/scoring_engine.py` with pure function `calculate_score()`
- Created `backend/tests/test_scoring_engine.py` with 25 test cases covering 100% branch coverage
- All 131 tests pass (106 existing + 25 new), zero regression
- Supports all 4 grade types: G1 (tiered penalties), G2_JPN1 (no penalties), YOUNG_G1 (G1 positives, no penalties), CUSTOM (user-defined)
- DNF/scratched horses: position ≤ 0 returns 0
- Custom grade correctly handles empty positive_scores, None penalty_rules, and position beyond positive_scores length

### File List

| Action | File |
|--------|------|
| NEW | `backend/app/services/scoring_engine.py` |
| NEW | `backend/tests/test_scoring_engine.py` |
