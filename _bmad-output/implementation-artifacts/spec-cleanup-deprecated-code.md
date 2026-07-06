---
title: '清理项目中的废弃代码'
type: 'refactor'
created: '2026-07-06'
status: 'done'
baseline_commit: 'd77ebb761ab3ca9c7b62a3b95f286b26363cde71'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 项目在发展过程中留下了已废弃的代码、测试死代码和旧字段兼容逻辑，增加了维护成本并可能误导后续开发者。

**Approach:** 识别并删除/更新项目中已废弃的代码片段：删除未被引用的文件、移除旧投票模式残留状态、清理旧字段 `age` 的兼容读取，以及删除/更新仍在引用已废弃字段和行为的测试代码。

## Boundaries & Constraints

**Always:**
- 仅删除/修改已确认废弃的代码，不触碰当前业务逻辑。
- 保持现有测试覆盖率，对因字段重命名而失效的测试进行更新而非删除。
- 编辑后保持原有代码风格和 TypeScript/Python 类型正确性。
- 所有变更必须在 Git 工作区干净的前提下进行（当前工作树已 clean）。

**Ask First：**
- 若发现除已识别项之外的额外废弃代码，新增删除项前需向用户确认。

**Never：**
- 不修改仍在使用的业务逻辑或 API 行为。
- 不引入新的功能或重构未涉及的文件。
- 不直接删除 `backend/tests` 中仅因字段重命名而过时的测试（应改为 `birth_year`）。

## Code Map

- `frontend/src/layouts/AdminLayout.vue` — 已被弃用的 Admin 布局包装组件，当前 admin 路由直接作为顶层路由共享 `AppLayout`。
- `frontend/src/composables/useVote.ts` — 旧投票模式残留的状态与 API（`selectedHorseId`、`selectedHorse`、`votesError`、`reset`、`initialVotedHorseName`）。
- `frontend/src/types/race.ts` — `HorseSnapshotData` 中遗留的 `age` 字段声明。
- `frontend/src/components/HorseDetailCard.vue` — 对 `snapshot_data.age` 的兜底读取。
- `frontend/src/pages/RaceDetailPage.vue` — 三处对 `snapshot_data.age` 的兜底读取。
- `frontend/src/pages/admin/EditRacePage.vue` — 对 `snapshot_data.age` 的兜底读取。
- `backend/tests/test_invite_codes.py` — 测试已不存在的 `invalidate_invite_code` 服务和 `PATCH` 端点，以及已废弃的 `disabled` 状态。
- `backend/tests/test_auth.py` — 测试已废弃的 `disabled` 邀请码状态。
- `backend/tests/test_horses.py`、`backend/tests/test_races.py`、`backend/tests/test_auto_update.py` — 仍使用已废弃的 `age` 字段，需更新为 `birth_year`。

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/layouts/AdminLayout.vue` — 删除整个文件。
- [x] `frontend/src/composables/useVote.ts` — 移除 `selectedHorseId`、`selectedHorse` 两个 ref 及其在接口、`reset()`、return 中的声明；移除无调用方使用的 `votesError` 和 `reset()`；移除无意义的 `initialVotedHorseName` 参数。
- [x] `frontend/src/types/race.ts` — 删除 `HorseSnapshotData` 中的 `age?: number | null` 遗留字段。
- [x] `frontend/src/components/HorseDetailCard.vue` — 删除 `snapshot_data.age` 的兜底读取，仅保留 `birth_year`。
- [x] `frontend/src/pages/RaceDetailPage.vue` — 删除三处 `?? horse.snapshot_data.age` 的兜底读取。
- [x] `frontend/src/pages/admin/EditRacePage.vue` — 删除 `h.snapshot_data.age ??` 的兜底读取。
- [x] `backend/tests/test_invite_codes.py` — 删除 `test_invalidate`、`test_invalidate_bound_code_raises`、`test_invalidate_nonexistent_code_raises` 和 `test_invalidate_code` 中已废弃的 `disabled` 状态断言；更新为仅测试当前有效的 `unused`/`used` 状态和 `DELETE` 端点。
- [x] `backend/tests/test_auth.py` — 删除 `create_disabled_invite_code` helper、`test_register_disabled_invite_code` 和 `test_reset_password_disabled_invite_code`。
- [x] `backend/tests/test_horses.py` — 将所有 `age` 字段引用更新为 `birth_year`。
- [x] `backend/tests/test_races.py` — 将 `SAMPLE_HORSE` 中的 `age` 更新为 `birth_year`。
- [x] `backend/tests/test_auto_update.py` — 将全文的 `age` 字段引用更新为 `birth_year`。

**Acceptance Criteria:**
- Given 代码库中存在废弃的 `AdminLayout.vue` 文件，when 执行清理，then 该文件被删除且项目构建/路由不受影响。
- Given `useVote.ts` 中残留旧投票状态，when 执行清理，then 所有未使用的 ref 和函数被移除，且 `RaceDetailPage.vue` 仍可正常编译运行。
- Given 前端仍存在 `snapshot_data.age` 的兜底读取，when 执行清理，then 所有 `age` 兼容逻辑被移除，且 `birth_year` 显示正常。
- Given 后端测试仍引用已废弃的 `age` 字段和 `disabled` 邀请码状态，when 执行清理，then 测试文件同步更新或删除，且 `pytest` 后端测试套件通过。

## Verification

**Commands:**
- `cd backend && pytest` -- expected: all tests pass
- `cd frontend && pnpm run build` -- expected: build succeeds with no TS/Vue errors

</frozen-after-approval>

## Suggested Review Order

**Core validation**

- Reject deprecated disabled invite codes during registration
  [`auth_service.py:237`](../../backend/app/services/auth_service.py#L237)
- Reject deprecated disabled invite codes during login
  [`auth_service.py:65`](../../backend/app/services/auth_service.py#L65)

**Frontend state cleanup**

- Entry point: cleaned-up `useVote` composable no longer carries selection-mode state
  [`useVote.ts:17`](../../frontend/src/composables/useVote.ts#L17)
- Remove legacy `age` field from snapshot type
  [`race.ts:61`](../../frontend/src/types/race.ts#L61)

**Frontend `age` fallback removal**

- `HorseDetailCard` reads `birth_year` only
  [`HorseDetailCard.vue:113`](../../frontend/src/components/HorseDetailCard.vue#L113)
- Voting/locked list passes `birth_year` only
  [`RaceDetailPage.vue:764`](../../frontend/src/pages/RaceDetailPage.vue#L764)
- Result ranking passes `birth_year` only
  [`RaceDetailPage.vue:815`](../../frontend/src/pages/RaceDetailPage.vue#L815)
- DNF zone passes `birth_year` only
  [`RaceDetailPage.vue:851`](../../frontend/src/pages/RaceDetailPage.vue#L851)
- Edit race page maps `birth_year` only
  [`EditRacePage.vue:100`](../../frontend/src/pages/admin/EditRacePage.vue#L100)

**Build fix**

- Fix pre-existing `route.query` type mismatch in `LoginPage`
  [`LoginPage.vue:26`](../../frontend/src/pages/LoginPage.vue#L26)

**Removed file**

- Deleted unused `AdminLayout.vue`
  `frontend/src/layouts/AdminLayout.vue`

**Test updates**

- Invite code tests use `DELETE` and verify DB removal
  [`test_invite_codes.py:134`](../../backend/tests/test_invite_codes.py#L134)
- Auth tests remove deprecated disabled invite code cases
  [`test_auth.py:61`](../../backend/tests/test_auth.py#L61)
- Horse tests use realistic `birth_year` values
  [`test_horses.py:22`](../../backend/tests/test_horses.py#L22)
- Race tests use realistic `birth_year` values
  [`test_races.py:29`](../../backend/tests/test_races.py#L29)
- Auto-update tests use realistic `birth_year` values
  [`test_auto_update.py:30`](../../backend/tests/test_auto_update.py#L30)
