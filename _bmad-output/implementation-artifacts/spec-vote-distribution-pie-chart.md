---
title: 'Vote Distribution Pie Chart'
type: 'feature'
created: '2026-07-06'
status: 'done'
baseline_commit: '3436ffcd2e883bafadafb1cfb5fa53baa8c09532'
context:
  - '{project-root}/_bmad-output/project-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The voting detail page currently shows a plain text list of (username → horse_name) entries, making it hard to visually grasp the vote distribution. Also, it's only shown for voting/locked races, not for settled races.

**Approach:** Replace the text list with a Chart.js doughnut chart where each segment represents a horse and its vote percentage. Show a tooltip on hover with vote count, percentage, and voter names. Show the chart for all race statuses (voting, locked, settled).

## Boundaries & Constraints

**Always:**
- Use Chart.js with vue-chartjs wrapper
- Colors for doughnut segments come from a curated palette (not random)
- Tooltip shows: horse name, vote count (X/Y), percentage (%), and voter usernames list
- Flat VoteListEntry[] is transformed to grouped-by-horse data in the component
- Chart must be responsive (resize with container)
- Keep the existing text list as a collapsible alternative view below the chart
- Preserve loading skeleton and empty state behavior

**Ask First:**
- Switching to a chart library other than Chart.js
- Adding additional chart types beyond doughnut/pie
- Backend API format changes

**Never:**
- No backend vote API changes — the existing `GET /api/v1/races/{race_id}/votes` endpoint already provides sufficient data
- No animations that violate `prefers-reduced-motion`
- No external UI libraries beyond chart.js + vue-chartjs

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Empty votes | votes array is empty | Show "暂无投票" message | N/A |
| Single horse | All votes for one horse | Full-color single segment (100%) | N/A |
| Multiple horses with ties | HorseA: 2, HorseB: 2, HorseC: 1 | Proportional segments with distinct colors | N/A |
| Load error | API returns error | Show error state | N/A |
| Loading state | Votes loading | Show skeleton shimmer placeholders | N/A |
| Hover over segment | Mouse enters doughnut segment | Tooltip: horse name, vote count, %, voter names | N/A |

</frozen-after-approval>

## Code Map

- `frontend/package.json` — Add `chart.js` and `vue-chartjs` dependencies
- `frontend/src/components/VotingDetail.vue` — Major rewrite: doughnut chart + grouped data + hover tooltip + collapsible text list
- `frontend/src/pages/RaceDetailPage.vue` — Remove status restriction on VotingDetail visibility; always load votes

## Tasks & Acceptance

**Execution:**
- [x] `frontend/package.json` — Add `chart.js ^4.4.8` and `vue-chartjs ^5.3.2` as dependencies
- [x] `frontend/src/components/VotingDetail.vue` — Rewrite: install and import Chart.js Doughnut chart; transform flat votes array to grouped-by-horse data; render doughnut chart with hover tooltip showing horse name, vote count, percentage, and voter names; keep existing text list as collapsible section below the chart; preserve loading skeleton and empty state
- [x] `frontend/src/pages/RaceDetailPage.vue` — Change `v-if` on `<VotingDetail>` to always render (remove status restriction); always call `loadVotes(raceId)` regardless of race status

**Acceptance Criteria:**
- Given a race detail page with existing votes, when the page loads, then a doughnut chart shows each horse's vote proportion with distinct segment colors
- Given the doughnut chart is displayed, when the user hovers over a segment, then a tooltip shows the horse name, vote count (e.g. "3/5 票"), percentage (e.g. "60%"), and a list of voter usernames
- Given a race in settled status, when the race detail page loads, then the VotingDetail with doughnut chart is visible below the race results
- Given a race with no votes, when the component loads, then "暂无投票" is displayed instead of an empty chart
- Given prefers-reduced-motion is set, when the chart renders, then no chart animations play

## Verification

**Commands:**
- `cd frontend && pnpm install` — expected: chart.js and vue-chartjs added to node_modules without errors
- `cd frontend && pnpm build` — expected: build succeeds without type errors

**Manual checks:**
- Open a race detail page (voting/locked/settled) and verify the doughnut chart renders with correct proportions
- Hover over each segment and verify the tooltip shows correct horse name, vote count, percentage, and voter names
- Verify the collapsible text list still works underneath the chart
- Test empty vote state (create new race with no votes)
- Test single horse (all votes to one horse)
- Test prefers-reduced-motion via browser DevTools

## Suggested Review Order

**Chart implementation (core change)**

- Doughnut chart component with grouped vote data, hover tooltip with voter names, collapsible text list
  [`VotingDetail.vue:1`](../../frontend/src/components/VotingDetail.vue#L1)

**Visibility expansion (behavior change)**

- Removed status restriction — VotingDetail now shows for all race states
  [`RaceDetailPage.vue:571`](../../frontend/src/pages/RaceDetailPage.vue#L571)

- Removed status restriction in template — always render VotingDetail
  [`RaceDetailPage.vue:872`](../../frontend/src/pages/RaceDetailPage.vue#L872)

**Dependency setup**

- Added chart.js and vue-chartjs
  [`package.json:16`](../../frontend/package.json#L16)
