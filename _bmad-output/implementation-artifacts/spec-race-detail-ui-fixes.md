---
title: 'race-detail-ui-fixes'
type: 'bugfix'
created: '2026-07-09T10:03:00'
status: 'done'
baseline_commit: 'master'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 比赛详情页存在多个交互与布局问题：结束/修改结果按钮无法直接进入编辑模式，管理按钮在移动端布局散乱，马匹卡片在不同视图下的间距不一致，且移动端长按卡片会触发系统默认行为导致页面卡死。

**Approach:** 在 `RaceDetailPage.vue` 中让结果模式入口自动开启编辑模式，并重新排布管理操作按钮；在 `RaceDetailPage.vue` 中统一卡片间距；在 `HorseDetailCard.vue` 中仅对移动端禁用长按的默认系统交互。

## Boundaries & Constraints

**Always:**
- 保持现有业务逻辑与 API 调用不变。
- 仅在现有 Vue 单文件组件内做样式与局部交互调整。
- 移动端编辑按钮继续沿用 `mobile-only` 类，只在窄屏显示。

**Ask First:**
- 若需要引入新的依赖或新增独立组件。

**Never:**
- 修改比赛状态机、投票或权限判定逻辑。
- 重构拖拽排序核心实现。
- 在桌面端强行显示移动端编辑按钮。

## Code Map

- `frontend/src/pages/RaceDetailPage.vue` — 详情页主组件：管理按钮布局、编辑模式入口、卡片列表间距。
- `frontend/src/components/HorseDetailCard.vue` — 马匹卡片组件：防止移动端长按卡死的触摸样式。

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/pages/RaceDetailPage.vue` -- 让 `enterResultMode` 同时开启 `isJiggleMode`，点击“比赛结束”/“修改结果”后直接进入编辑模式。
- [x] `frontend/src/pages/RaceDetailPage.vue` -- 把移动端编辑按钮、锁定按钮与删除比赛按钮合并到同一管理操作栏（移动端编辑按钮与删除比赛同行；双端锁定按钮与删除比赛同行）。
- [x] `frontend/src/pages/RaceDetailPage.vue` -- 统一普通列表、结果排名区、DNF 区及添加/删除行的马匹卡片垂直间距为 12px。
- [x] `frontend/src/components/HorseDetailCard.vue` -- 在卡片根元素上条件阻止移动端 contextmenu，并在移动端媒体查询中保留 `touch-action: manipulation`、`-webkit-touch-callout: none`、`user-select: none`，防止移动端长按卡死，同时避免影响桌面端文本选择与右键菜单。

**Acceptance Criteria:**
- Given 管理员在锁定或已结算比赛页，当 点击“比赛结束”或“修改结果”按钮， then 页面立即进入结果排名模式且卡片自动抖动（编辑模式），无需再点编辑按钮。
- Given 管理员在投票中比赛页（移动端）， when 查看管理操作区， then “编辑”按钮与“删除比赛”按钮在同一行，且“锁定”按钮也与“删除比赛”按钮在同一行。
- Given 管理员在桌面端查看投票中比赛页， when 查看管理操作区， then “锁定”按钮与“删除比赛”按钮在同一行。
- Given 任意端查看马匹列表， when 在普通视图、结果排名视图、DNF 区之间切换， then 所有马匹卡片之间的垂直间距一致。
- Given 移动端任意模式， when 长按任意马匹卡片， then 不会触发系统选择/上下文菜单/放大镜，页面交互保持正常。

## Verification

**Commands:**
- `cd frontend && pnpm run build` -- expected: 构建无 TypeScript 与样式错误。

## Suggested Review Order

**Edit mode entry**

- 结束/修改结果按钮进入结果模式时同步开启编辑模式
  [`RaceDetailPage.vue:465`](../../frontend/src/pages/RaceDetailPage.vue#L465)

**Admin action layout**

- 投票状态：锁定、移动端编辑、删除比赛三按钮共置同一操作栏
  [`RaceDetailPage.vue:827`](../../frontend/src/pages/RaceDetailPage.vue#L827)
- 锁定状态：结束比赛与删除比赛共置同一操作栏
  [`RaceDetailPage.vue:861`](../../frontend/src/pages/RaceDetailPage.vue#L861)
- 已结算状态：修改结果与更新主胜鞍按钮
  [`RaceDetailPage.vue:875`](../../frontend/src/pages/RaceDetailPage.vue#L875)

**Card spacing**

- 统一普通列表、结果排名区、DNF 区的卡片垂直间距为 12px
  [`RaceDetailPage.vue:1512`](../../frontend/src/pages/RaceDetailPage.vue#L1512)
  [`RaceDetailPage.vue:1646`](../../frontend/src/pages/RaceDetailPage.vue#L1646)
  [`RaceDetailPage.vue:1665`](../../frontend/src/pages/RaceDetailPage.vue#L1665)
  [`RaceDetailPage.vue:1745`](../../frontend/src/pages/RaceDetailPage.vue#L1745)

**Mobile long-press protection**

- 移动端条件阻止 contextmenu，避免长按弹出系统菜单
  [`HorseDetailCard.vue:197`](../../frontend/src/components/HorseDetailCard.vue#L197)
  [`HorseDetailCard.vue:224`](../../frontend/src/components/HorseDetailCard.vue#L224)
- 抖动动画限制在移动端，桌面端结果模式不再强制抖动
  [`HorseDetailCard.vue:850`](../../frontend/src/components/HorseDetailCard.vue#L850)
