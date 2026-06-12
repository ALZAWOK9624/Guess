---
baseline_commit: 52a977a
---

# Story 3.3: Voting Frontend Interaction

Status: done

## Story

As a **logged-in user**,
I want **to complete voting on a race detail page through intuitive interaction and see real-time vote distribution**,
so that **I can quickly cast my vote on mobile and see what my friends have chosen**.

## Acceptance Criteria

### AC-1: Voting UI for unvoted user on voting race

**Given** a logged-in user visits a `voting` race detail page (`/races/:id`)
**When** the user has not yet voted
**Then** a golden VoteButton is displayed at the bottom of the page with text "投票"
**And** all horse cards show no selection markers
**And** the VotingDetail component below the horse list displays all users' current vote distribution in format "用户名 → 马匹名"
**And** the horse list items are clickable for selection (HorseSelectCard mode)

### AC-2: Horse selection interaction

**Given** the user taps "投票" or taps directly on a horse card
**When** a horse card is tapped/selected
**Then** the selected horse card border changes to gold (`--color-accent, #B8960C`) + shows a checkmark
**And** only one horse can be selected at a time (radio-style)
**And** a confirmation button activates after selection

### AC-3: Confirm vote

**Given** the user has selected a horse and taps the confirmation button
**When** the vote is submitted via API
**Then** the VoteButton transitions to confirmed state: green background (`--color-success, #2D7A4F`) with text "✓ 已投：{马名}"
**And** the VotingDetail component refreshes in-place to show the user's vote in the distribution
**And** the vote is optimistically updated on the frontend (show result immediately, handle failure with rollback + toast)

### AC-4: Modify vote

**Given** a user has already voted on a `voting` race
**When** they tap "修改投票"
**Then** the horse selection interface re-opens
**And** the previous selection is shown as pre-selected
**And** selecting a different horse and confirming replaces the vote
**And** the VoteButton updates to show the new horse name

### AC-5: Locked race — no voting

**Given** a race is in `locked` or `settled` status
**When** a logged-in user visits the race detail page
**Then** the VoteButton shows "投票已截止" (greyed out, non-interactive)
**And** the user who voted can see their final choice highlighted
**And** the user who did NOT vote sees "投票已截止。你未参与本场竞猜。"

### AC-6: Guest triggers login redirect

**Given** a guest (unauthenticated) user visits a `voting` race
**When** they tap the VoteButton
**Then** they are redirected to `/login?redirect=/races/{id}`
**And** no popup/modal interruption is shown

### AC-7: Real-time vote distribution refresh

**Given** a race in `voting` status
**When** any user submits or modifies a vote
**Then** the VotingDetail component refreshes to reflect the latest data
**And** uses a lightweight polling strategy (refresh votes data on successful own vote submission, with optional manual refresh)

### AC-8: Mobile-friendly voting flow (≤3 taps)

**Given** a mobile user completes voting on a `voting` race
**When** following the full voting flow from page load to vote submission
**Then** core operation: select horse (1 tap) → confirm (1 tap) = 2 taps total
**And** modify vote: tap modify (1 tap) → select (1 tap) → confirm (1 tap) = 3 taps total

## Tasks / Subtasks

- [x] **AC-1~8**: Create Vote types (`frontend/src/types/vote.ts`)
  - [x] `VoteRequest` — `race_horse_id: number`
  - [x] `VoteResponse` — id, user_id, race_id, race_horse_id, horse_name, created_at, updated_at
  - [x] `VoteListEntry` — user_id, username, race_horse_id, horse_name, created_at
  - [x] `VoteListResponse` — list of VoteListEntry

- [x] **AC-1~7**: Create Vote API calls (`frontend/src/api/votes.ts`)
  - [x] `submitVote(raceId, raceHorseId)` — `POST /api/v1/races/{race_id}/votes`
  - [x] `getRaceVotes(raceId)` — `GET /api/v1/races/{race_id}/votes`
  - [x] Export from module

- [x] **AC-1~4**: Create `VoteButton.vue` component (`frontend/src/components/VoteButton.vue`)
  - [x] Three visual states: `voting-unvoted` (gold CTA), `voting-voted` (green confirmed), `locked` (greyed out)
  - [x] Props: `raceStatus`, `votedHorseName`, `isLoggedIn`, `isGuest`
  - [x] Emit: `vote-click` for triggering selection flow
  - [x] Mobile touch target ≥ 44×44px
  - [x] Golden BG (#B8960C) for unvoted CTA, green BG (#2D7A4F) for confirmed, grey (#6B7280) for locked
  - [x] `@click` handler: if guest → trigger login redirect; if unvoted → emit vote-click; if voted → emit modify-click
  - [x] Text variants: "投票" / "✓ 已投：{马名}" / "修改投票" / "投票已截止"

- [x] **AC-2~4**: Create `HorseSelectCard.vue` component (`frontend/src/components/HorseSelectCard.vue`)
  - [x] Props: `horse` (RaceHorseSnapshot), `selected` (boolean), `disabled` (boolean)
  - [x] Emit: `select`
  - [x] Selected state: gold border (2px solid #B8960C) + checkmark overlay
  - [x] Unselected: normal border (1px solid var(--border-hairline, #D4DCD0))
  - [x] Disabled state: reduced opacity, no pointer events
  - [x] Touch target ≥ 44px height for each card row

- [x] **AC-1,7**: Create `VotingDetail.vue` component (`frontend/src/components/VotingDetail.vue`)
  - [x] Props: `votes` (VoteListEntry[]), `loading` (boolean)
  - [x] Display: list of "用户名 → 马匹名" entries
  - [x] Empty state: "暂无投票"
  - [x] Loading state: skeleton shimmer (3 rows of pulsing bars)
  - [x] Mobile-responsive single column

- [x] **AC-1~4**: Create `useVote.ts` composable (`frontend/src/composables/useVote.ts`)
  - [x] Reactive state: `selectedHorseId`, `votedHorseName`, `isSubmitting`, `votes`, `votesLoading`, `votesError`
  - [x] `selectHorse(raceHorseId)` — set selected horse (radio-style, replace previous selection)
  - [x] `confirmVote(raceId)` — call submitVote API, optimistic update, handle error rollback
  - [x] `modifyVote()` — reset selection state, allow re-selection
  - [x] `loadVotes(raceId)` — fetch and set vote distribution
  - [x] Error handling: catch API errors, rollback optimistic update, display toast message

- [x] **AC-1~8**: Modify `RaceDetailPage.vue` (`frontend/src/pages/RaceDetailPage.vue`)
  - [x] Import and integrate: VoteButton, HorseSelectCard, VotingDetail, useVote, useAuthStore
  - [x] Add voting section at bottom of page: HorseSelectCard list when in selection mode
  - [x] Fixed-position VoteButton bar at bottom (mobile) or inline (desktop)
  - [x] Guest vote button click → router.push with redirect
  - [x] Fetch race votes on mount (for voting races)
  - [x] Handle all PageState transitions with vote states
  - [x] Locked race: show locked indicators, final choice, or "未参与" message
  - [x] Use optimistic update pattern for vote submission
  - [x] Mobile: responsive layout, bottom-fixed CTA
  - [x] Desktop: inline CTA below horse list

- [x] **AC-1,7**: Update `frontend/src/api/races.ts` if needed for vote count refresh
  - [x] No changes needed — vote count is part of RaceDetail response; voting details are fetched separately via getRaceVotes

## UI / Interaction Spec

### VoteButton States

| State | Visual | Text | Behavior |
|-------|--------|------|----------|
| voting-unvoted (logged in) | Gold BG #B8960C, white text | "投票" | Click → emit vote-click (enter selection mode) |
| voting-unvoted (guest) | Gold BG #B8960C, white text | "投票" | Click → redirect to /login?redirect=/races/{id} |
| voting-voted | Green BG #2D7A4F, white text | "✓ 已投：{马名}" | Click → show "修改投票" option |
| voting-modify | Gold BG #B8960C, white text | "修改投票" | Click → re-enter selection mode |
| locked-voted | Grey BG #6B7280, white text | "投票已截止" | Non-interactive |
| locked-unvoted | Grey BG #6B7280, white text | "投票已截止。你未参与本场竞猜。" | Non-interactive |
| settled | Grey BG #6B7280, white text | "已结算" | Non-interactive |

### HorseSelectCard States

| State | Visual | Behavior |
|-------|--------|----------|
| unselected | Normal border 1px #D4DCD0 | Click → select this horse |
| selected | Gold border 2px #B8960C + checkmark ✓ | Click → deselect (or keep selected for radio-style) |
| disabled (locked/settled) | Reduced opacity, grey border | No interaction |

### Voting Flow Diagram (Mobile)

```
Page Load → See horse list + VotingDetail + VoteButton "投票"
    │
    ├── Guest taps "投票" → redirect to /login?redirect=/races/{id}
    │
    └── Logged-in user taps "投票"
        │
        ├── Enter selection mode: horse cards become HorseSelectCards
        │
        ├── User taps a horse card → card highlights gold
        │
        ├── User taps "确认投票" → optimistic update → API call
        │   │
        │   ├── SUCCESS: VoteButton → "✓ 已投：{马名}", VotingDetail refreshes
        │   │
        │   └── FAILURE: rollback selection, show error toast
        │
        └── User taps "修改投票" → re-enter selection mode with pre-selected
            │
            └── Repeat selection → confirm → vote updated
```

## Dev Notes

### Composition API Pattern

Use `<script setup lang="ts">` Composition API for all new components. Follow existing patterns from `RaceCard.vue`, `HorseDetailCard.vue`.

### Optimistic Vote Update Pattern

```typescript
// In useVote composable
async function confirmVote(raceId: number) {
  if (selectedHorseId.value === null) return
  
  // Save previous state for rollback
  const previousVotedName = votedHorseName.value
  
  // Optimistic update
  votedHorseName.value = selectedHorse.value?.snapshot_data.name ?? null
  isSubmitting.value = true
  
  try {
    const result = await submitVote(raceId, selectedHorseId.value)
    // Update with actual server data
    votedHorseName.value = result.horse_name
    // Refresh vote distribution
    await loadVotes(raceId)
  } catch (err: any) {
    // Rollback on failure
    votedHorseName.value = previousVotedName
    // Show error toast
    showError(err)
  } finally {
    isSubmitting.value = false
  }
}
```

### VoteButton Placement Strategy

- **Mobile (<768px)**: Fixed position at bottom of viewport (`position: fixed; bottom: 0`), with `safe-area-inset-bottom` padding. A semi-transparent shadow bar above the button. Content area has bottom padding to avoid overlap.
- **Desktop (≥768px)**: Inline below the horse list, full-width within the content container.

### HorseSelectCard vs HorseDetailCard

- **HorseDetailCard** (existing, Story 2.4): Full 10-attribute display. Used for general horse info viewing.
- **HorseSelectCard** (new, this story): Compact card with horse name + key attributes summary (name, jockey, weight) + selectable border. Used only in voting selection mode.
- Both read from the same `snapshot_data` prop type (`HorseSnapshotData`).

On mobile, the selection panel should overlay or expand inline within the page (not a separate modal) to keep the flow within 2 taps.

### Vote Distribution Refresh Strategy

- On successful vote submission: re-fetch `GET /api/v1/races/{race_id}/votes`
- On page load for voting races: fetch vote distribution
- Locked/settled races: fetch once on page load (no refresh needed — data is frozen)
- No periodic polling — refresh only on user action

### Existing Component Patterns to Follow

- **PageState enum**: Use `type PageState = 'loading' | 'empty' | 'error' | 'success'` pattern (from HomePage.vue)
- **Error handling**: Try/catch with `catch (err)` — no bare catch blocks
- **Route params**: `const raceId = Number(route.params.id)` pattern (from existing RaceDetailPage)
- **Auth store**: `useAuthStore()` for `isLoggedIn` and `isAdmin` checks
- **API client**: Through `apiClient` in `client.ts` (already includes auth interceptor)
- **CSS variables**: Use JRA design token CSS variables (--color-accent, --color-success, etc.)

### Type Definitions

```typescript
// frontend/src/types/vote.ts
export interface VoteRequest {
  race_horse_id: number
}

export interface VoteResponse {
  id: number
  user_id: number
  race_id: number
  race_horse_id: number
  horse_name: string
  created_at: string
  updated_at: string
}

export interface VoteListEntry {
  user_id: number
  username: string
  race_horse_id: number
  horse_name: string
  created_at: string
}

export interface VoteListResponse {
  data: VoteListEntry[]
}
```

### API Call Pattern

```typescript
// frontend/src/api/votes.ts
import apiClient from './client'
import type { VoteRequest, VoteResponse, VoteListEntry } from '@/types/vote'

export async function submitVote(raceId: number, raceHorseId: number): Promise<VoteResponse> {
  const res = await apiClient.post<{ data: VoteResponse }>(`/races/${raceId}/votes`, {
    race_horse_id: raceHorseId,
  } as VoteRequest)
  return res.data.data
}

export async function getRaceVotes(raceId: number): Promise<VoteListEntry[]> {
  const res = await apiClient.get<{ data: VoteListEntry[] }>(`/races/${raceId}/votes`)
  return res.data.data
}
```

### Files to Create/Modify

| Action | File | Description |
|--------|------|-------------|
| **NEW** | `frontend/src/types/vote.ts` | VoteRequest, VoteResponse, VoteListEntry types |
| **NEW** | `frontend/src/api/votes.ts` | submitVote(), getRaceVotes() API calls |
| **NEW** | `frontend/src/components/VoteButton.vue` | Voting button with 6 visual states |
| **NEW** | `frontend/src/components/HorseSelectCard.vue` | Selectable horse card for voting |
| **NEW** | `frontend/src/components/VotingDetail.vue` | Vote distribution display |
| **NEW** | `frontend/src/composables/useVote.ts` | Voting composable with optimistic update |
| **MODIFY** | `frontend/src/pages/RaceDetailPage.vue` | Integrate voting UI components |

### Architecture Compliance

- **Endpoints layer**: Already exists from Story 3.2 — `POST/GET /api/v1/races/{id}/votes`
- **Frontend components**: New VoteButton, HorseSelectCard, VotingDetail in `src/components/`
- **Frontend composable**: New `useVote` in `src/composables/`
- **Frontend API layer**: New `votes.ts` in `src/api/`
- **Frontend types**: New `vote.ts` in `src/types/`
- **No backend changes needed** — all required API endpoints were created in Story 3.2
- **No router changes needed** — `/races/:id` route already exists

### Testing Requirements

- **VoteButton component tests**: Verify all 6 visual states render correct text/color
- **HorseSelectCard component tests**: Verify selected/unselected/disabled states
- **useVote composable tests**: Verify optimistic update, rollback, error handling
- **RaceDetailPage integration test**: Verify voting flow end-to-end with mock API

## Previous Story Intelligence (Story 3.2 — Voting Backend)

### Dev Notes & Learnings

- **Vote API**: `POST /api/v1/races/{race_id}/votes` accepts `race_horse_id` (not `horse_id`). The frontend must pass the **race_horse_id** from RaceHorseSnapshot — not the global horse_id.
  - RaceHorseSnapshot has `horse_id` field — but the API expects `race_horse_id`. Frontend must correctly use the index/ID from the `race_horses` join table.
  - **IMPORTANT**: The `RaceDetail` response does NOT currently include `race_horse_id` in `RaceHorseSnapshot`. The endpoint needs to be checked — if `race_horse_id` is missing, the API needs to be updated or the frontend should use array index as position reference.
  - **UPDATE**: The `RaceHorseSnapshot` type has `horse_id` — but for voting, the backend needs `race_horse_id`. Verify `GET /api/v1/races/{id}` returns `race_horse_id` in the snapshot. If not, add it to the backend response schema.

- **Vote query**: `GET /api/v1/races/{race_id}/votes` returns `{ data: [{ user_id, username, race_horse_id, horse_name, created_at }] }` — publicly accessible.
- **Vote upsert**: Re-vote uses the same endpoint — POST with same user+race creates/updates.
- **Race status flow**: `voting → locked → settled` — frontend must handle all three states.

### Problems Encountered & Solutions

- **Post-vote eager-load pattern**: `create_or_update_vote()` does an extra query with `selectinload(Vote.race_horse_rel)` after flush to resolve horse name. Frontend receives the `horse_name` in the response.
- **Lock operation**: `POST /api/v1/races/{race_id}/lock` is admin-only. Frontend AdminLayout / DashboardPage handles lock UI (to be built in later stories — Story 3.4+).

### Backend Schema Check

The `RaceDetail` response includes `RaceHorseSnapshot` with fields:
```typescript
{ horse_id, snapshot_data, position }
```

For voting, the frontend needs `race_horse_id` to map to the join table. **Check if the backend `GET /api/v1/races/{id}` endpoint returns `race_horse_id` in the horse snapshots.** If not, the backend `schemas/race.py` RaceHorseSnapshot schema must be updated to include `race_horse_id`.

Alternatively (fallback), the race's horse list maintains a stable ordering — the frontend can use the index as `race_horse_id` but this is fragile. The correct approach is to update the backend schema.

## Project Context Reference

- [Source: project-context.md#Critical Implementation Rules] PageState enum pattern, CSS variables, naming conventions
- [Source: project-context.md#Framework-Specific Rules] Vue 3 Composition API, `<script setup lang="ts">`, scoped CSS
- [Source: project-context.md#Frontend patterns] Teleport modals, debounced search, PATCH edit mode
- [Source: project-context.md#Critical Don't-Miss Rules] No `!important`, no bare catch, no useAuthStore import in client.ts
- [Source: epics.md#Story 3.3] Story 3.3 acceptance criteria
- [Source: architecture.md#Frontend Architecture] Component tree, composable pattern, api/client.ts pattern
- [Source: DESIGN.md] Color tokens, spacing system, typography
- [Source: EXPERIENCE.md] VoteButton behavior, HorseSelectCard behavior, VotingDetail behavior
- [Source: frontend/src/pages/RaceDetailPage.vue] Current page structure (loading/error/success states, header, horse list)
- [Source: frontend/src/api/races.ts] API call pattern (apiClient.get, response type structure)
- [Source: frontend/src/stores/authStore.ts] Auth store pattern (isLoggedIn, isAdmin computed properties)
- [Source: frontend/src/router/index.ts] Route configuration, auth guards

## Dev Agent Record

### Agent Model Used

Deepseek-V4-Flash

### Key Technical Decisions

1. **No vuedraggable dependency**: This story does NOT need drag-and-drop. The DragCard component and sorting will be in Story 3.4.

2. **race_horse_id availability**: **CRITICAL** — Before starting implementation, verify that `GET /api/v1/races/{id}` returns `race_horse_id` in each horse snapshot entry. If missing, update `backend/app/schemas/race.py` to include it, plus add a `selectinload(Race.race_horses)` or ensure the race_horses relationship is eager-loaded.

3. **VoteButton is NOT a modal trigger**: The HorseSelectCard selection should expand inline within the page (below the horse list) rather than opening a modal. This keeps the interaction within ≤2 taps on mobile.

4. **VoteButton uses fixed positioning on mobile**: Must respect `safe-area-inset-bottom` for iOS devices.

5. **No periodic polling for vote distribution**: Vote distribution refreshes only on successful own vote submission. The backend does not have WebSocket support (architectural decision), and periodic polling would be wasteful for a small-user platform.

6. **Optimistic update with rollback**: Frontend shows the confirmation immediately and reverts on API failure with a toast/error message. This provides instant feedback.

### Potential Pitfalls

- If `race_horse_id` is missing from the API response, the frontend cannot submit votes correctly. **Verify this first.**
- The existing `RaceDetailPage.vue` uses `const raceId = Number(route.params.id)` — must use the same pattern.
- Horse selection is radio-style (not checkbox) — only one horse can be selected at a time.

### Completion Notes

- **Backend schema fix**: Added `race_horse_id` to `RaceHorseResponse` schema and all 3 endpoint responses (GET/POST/PATCH) in `races.py`. This was critical — the frontend needs `race_horse_id` (FK to race_horses join table) to submit votes, but the schema was missing it.
- **Frontend types**: Created `frontend/src/types/vote.ts` with VoteRequest, VoteResponse, VoteListEntry. Added `race_horse_id` to `RaceHorseSnapshot` in `types/race.ts`.
- **Frontend API**: Created `frontend/src/api/votes.ts` with `submitVote()` and `getRaceVotes()`.
- **VoteButton.vue**: 7-state voting button component (voting-unvoted-loggedin, voting-unvoted-guest, voting-voted, voting-modify, locked-voted, locked-unvoted, settled). Fixed position on mobile, inline on desktop. Respects `safe-area-inset-bottom`.
- **HorseSelectCard.vue**: Selectable horse card with gold border + checkmark for selected state. Radio-style selection. 48px min height for touch targets.
- **VotingDetail.vue**: Vote distribution display with loading skeleton, empty state ("暂无投票"), and vote list ("用户名 → 马匹名").
- **useVote.ts**: Composable with optimistic update pattern — shows result immediately, rolls back on API failure with error message.
- **RaceDetailPage.vue**: Full voting integration. Handles all states: voting-unvoted, voting-voted, locked-voted, locked-unvoted, settled, guest redirect. Selection mode triggers inline HorseSelectCard list with confirm/cancel buttons. Vote distribution fetched on mount for voting/locked races.
- **No new npm dependencies** — all components built with existing Vue 3 + CSS variables.
- **Backward compatible**: All 151 existing backend tests pass with zero regression. Frontend type-checks cleanly with `vue-tsc --noEmit`.

### File List

| **NEW** | `frontend/src/types/vote.ts` | Vote type definitions |
| **NEW** | `frontend/src/api/votes.ts` | Vote API calls |
| **NEW** | `frontend/src/components/VoteButton.vue` | VoteButton component (7 states) |
| **NEW** | `frontend/src/components/HorseSelectCard.vue` | Horse selection card |
| **NEW** | `frontend/src/components/VotingDetail.vue` | Vote distribution display |
| **NEW** | `frontend/src/composables/useVote.ts` | Voting composable with optimistic update |
| **MODIFY** | `frontend/src/pages/RaceDetailPage.vue` | Integrate voting UI components |
| **MODIFY** | `frontend/src/types/race.ts` | Add `race_horse_id` to RaceHorseSnapshot |
| **MODIFY** | `backend/app/schemas/race.py` | Add `race_horse_id` to RaceHorseResponse |
| **MODIFY** | `backend/app/api/v1/endpoints/races.py` | Include `race_horse_id` in horse responses (3 endpoints) |

### Review Findings

#### decision-needed

- [x] [Review][Decision] 核心投票流程需要 3 次点击，超过 AC-8 的 ≤2 约束 — 已修复：移除确认按钮，选马即提交（≤2 次点击 ✅）
- [x] [Review][Decision] 修改投票流程需要 4 次点击，超过 AC-8 的 ≤3 约束 — 已修复：移除修改中间态，点已投按钮直接进入选择模式，选不同马即提交（≤3 次点击 ✅）

#### patch

- [x] [Review][Patch] `voting-modify` 状态已定义但永远无法到达 [VoteButton.vue] — 已修复：删除未使用的 `voting-modify` 类型和死代码分支
- [x] [Review][Patch] 修改投票时未预选之前的选择 (AC-4 违反) [useVote.ts:78-82] — 已修复：`enterSelectionMode()` 现在根据 `votedHorseName` 查找并预选对应马匹
- [x] [Review][Patch] 锁定/已结算状态下已投票用户的最终选择未高亮 (AC-5 违反) [RaceDetailPage.vue:159-167] — 已修复：给 HorseDetailCard 添加 `.voted-horse` 类，锁定状态下用户投票的马匹显示金色边框
- [x] [Review][Patch] `confirmVote` 中 `loadVotes` 异常可能导致状态不一致 [useVote.ts:62-64] — 已修复：`loadVotes` 现在有独立 try/catch，失败不影响投票状态
- [x] [Review][Patch] 组件卸载时投票请求可能产生副作用 [useVote.ts:44-70] — 已修复：添加 `onUnmounted` + `unmounted` 标志，异步操作完成后检查组件是否仍挂载
- [x] [Review][Patch] HorseSelectCard 的 `role="radio"` 缺少 `name` 属性关联单选组 [HorseSelectCard.vue:17] — 已修复：添加可选的 `name` prop，传递 `vote-group-{raceId}`
- [x] [Review][Patch] `loadVotes` 失败后保留旧投票分布数据 [useVote.ts:80-83] — 已修复：catch 块中 `votes.value = []`
- [x] [Review][Patch] VoteButton `handleClick` 中 guest 分支死代码 [VoteButton.vue:51-53] — 已修复：删除不可达分支，仅保留 loggedin 和 voted 逻辑
- [x] [Review][Patch] 投票列表 key 使用 user_id+race_horse_id 组合可能冲突 [VotingDetail.vue:24] — 已修复：使用 `index` 作为 key

#### defer

- [x] [Review][Defer] 401 Token 过期时 Axios 拦截器重定向与 confirmVote catch 块竞争 [client.ts:30-59] — 此为 Axios 拦截器全局行为，非本故事引入的问题。在 token 刷新失败的场景下，拦截器的全页重定向可能在 confirmVote 的 catch 块执行前发生。 deferred, pre-existing
