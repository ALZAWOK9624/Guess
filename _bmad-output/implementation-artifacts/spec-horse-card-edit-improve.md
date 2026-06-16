---
title: 'Horse card display and edit page improvement'
type: 'feature'
created: '2026-06-16'
status: 'done'
baseline_commit: '599d1f8ee81d343273c407153882c3cb4150277b'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Race page horse cards (HorseDetailCard) display info in a multi-row grid layout that wastes vertical space. Horse edit modal (HorsesPage) has 前走成绩 and 主胜鞍 as separate individual input fields without visual grouping.

**Approach:** (1) Condense HorseDetailCard to a single-line text format showing all key info inline. (2) Group 前走成绩 (3 sub-fields: name/date/position) and 主胜鞍 (2 sub-fields: name/date) into visually distinct bordered boxes on the edit form.

## Boundaries & Constraints

**Always:**
- HorseDetailCard retains all existing props/slots behavior — only template and style change
- HorseDetailCard single-line format: `[name] [sex][age] 产:[origin] 属:[location] 父:[sire] 母父:[damsire] 前走:[previous_result] 主胜鞍:[best_win]`
- Weight and jockey are removed from display (not in the condensed line) — they can be re-added in a future story
- The "已投" badge and vote interaction remain unchanged
- RaceResultView's usage of HorseDetailCard must work without breakage
- 前走成绩 box has 3 sub-fields: 比赛名, 日期, 名次, wrapped in a bordered box with header "前走成绩"
- 主胜鞍 box has 2 sub-fields: 比赛名, 日期, wrapped in a bordered box with header "主要胜鞍"
- Validation rules for 前走成绩 and 主胜鞍 remain unchanged
- The existing form-grid (2-column layout) is preserved — the two new boxes sit within the grid alongside other fields

**Ask First:** None.

**Never:**
- No backend changes — frontend only
- No changes to Horse types/schemas or API calls
- No breaking HorseDetailCard API (props/emits)
- No changes to RaceResultView's layout structure

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HorseDetailCard with null fields | All optional fields null | Shows `-` for missing values | Graceful fallback via existing `|| '-'` pattern |
| 前走成绩 partial fill | User fills only 2 of 3 sub-fields | Validation error: "前走成绩必须同时填写比赛名称、日期和名次" | Existing validation unchanged |
| 主胜鞍 partial fill | User fills only name w/o date | Validation error: "主要胜鞍必须同时填写比赛名称和日期" | Existing validation unchanged |

</frozen-after-approval>

## Code Map

- `frontend/src/components/HorseDetailCard.vue` — Horse card on race detail page; needs template+style rewrite for single-line format
- `frontend/src/pages/admin/HorsesPage.vue` — Horse edit modal; needs form layout restructure to group 前走成绩 and 主胜鞍 into bordered boxes

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/components/HorseDetailCard.vue` — Rewrite template to condensed single-line format; remove grid layout and weight/jockey display; keep vote interaction intact. Update scoped CSS accordingly.
- [x] `frontend/src/pages/admin/HorsesPage.vue` — Replace 3 separate 前走成绩 fields and 2 separate 主要胜鞍 fields with boxed sections each containing their sub-fields in rows within the same column. Keep existing validation.

**Acceptance Criteria:**
- Given a race detail page with horses, when the page loads, then each horse card shows all attributes in a single horizontal line
- Given a race result view, when the page loads, then horse cards inside result view also show single-line format
- Given the horse edit modal, when viewing 前走成绩 section, then the 3 sub-fields (name/date/position) appear inside one bordered box with "前走成绩" header
- Given the horse edit modal, when viewing 主要胜鞍 section, then the 2 sub-fields (name/date) appear inside one bordered box with "主要胜鞍" header
- Given the horse edit modal with partial 前走成绩, when saving, then the existing validation error appears
- Given the horse edit modal with partial 主胜鞍, when saving, then the existing validation error appears

## Verification

**Commands:**
- `cd frontend && pnpm dev` — verify both pages render without errors

**Manual checks (if no CLI):**
- Open a race detail page and confirm single-line horse card display
- Open admin horse edit modal and confirm boxed 前走成绩 / 主胜鞍 sections

## Suggested Review Order

**HorseDetailCard single-line rewrite**

- `infoLine` computed builds condensed attribute string from snapshot data
  [`HorseDetailCard.vue#L46`](../../frontend/src/components/HorseDetailCard.vue#L46)

- Template restructured: `.card-header` → `.card-inner` with flex row + `.info-line` for text overflow handling
  [`HorseDetailCard.vue#L68`](../../frontend/src/components/HorseDetailCard.vue#L68)

- CSS: `.info-line` uses text-overflow ellipsis on desktop, wraps on mobile
  [`HorseDetailCard.vue#L156`](../../frontend/src/components/HorseDetailCard.vue#L156)

**HorsesPage field grouping**

- 前走成绩: 3 sub-fields wrapped in bordered `.field-box`
  [`HorsesPage.vue#L260`](../../frontend/src/pages/admin/HorsesPage.vue#L260)

- 主要胜鞍: 2 sub-fields wrapped in bordered `.field-box`
  [`HorsesPage.vue#L279`](../../frontend/src/pages/admin/HorsesPage.vue#L279)

- Field box CSS with responsive grid (col-3 / col-2)
  [`HorsesPage.vue#L301`](../../frontend/src/pages/admin/HorsesPage.vue#L301)
