---
title: 'fix-result-actions-layout-and-dnf-badge'
type: 'bugfix'
created: '2026-07-09'
status: 'done'
route: 'one-shot'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 比赛详情页中点击"修改结果"后，"确认结果"和"取消"按钮出现在页面最底端（拖拽排序区之后），距离原"修改结果"按钮位置很远，不符合交互直觉。同时，移动端 HorseDetailCard 的名次徽章中 DNF 文字以 16px 渲染导致过宽，在窄屏上难以容纳。

**Approach:** 将"确认结果"/"取消"按钮从页面底部的 `.result-actions` 移至页面顶部的 `.admin-actions-bar`（原"修改结果"按钮位置），通过 `resultMode === 'ranking'` 条件控制显示。在 HorseDetailCard 移动端媒体查询中为 `.badge-dnf` 单独设置更小字体（10px）和更窄 min-width（26px），覆盖 `.side-badge` 的通用移动端样式。

## Boundaries & Constraints

**Always:**
- 保持现有业务逻辑与 API 调用不变。
- 仅在现有 Vue 单文件组件内做模板与样式调整。

**Never:**
- 修改比赛状态机、投票或权限判定逻辑。

## Suggested Review Order

**Result actions repositioning**

- 新增 ranking 模式下的 admin-actions-bar，将"确认结果"/"取消"按钮提升至页面顶部
  [`RaceDetailPage.vue:887`](../../frontend/src/pages/RaceDetailPage.vue#L887)

- 移除底部原 `.result-actions` div 及关联 dead CSS（`.submit-error`、`.result-actions`）
  [`RaceDetailPage.vue:1762`](../../frontend/src/pages/RaceDetailPage.vue#L1762)

- 移动端 `.ranking-actions-bar` 纵向堆叠
  [`RaceDetailPage.vue:1873`](../../frontend/src/pages/RaceDetailPage.vue#L1873)

**Mobile DNF badge sizing**

- 移动端 `.badge-dnf` 字体缩小至 10px，min-width 减至 26px
  [`HorseDetailCard.vue:666`](../../frontend/src/components/HorseDetailCard.vue#L666)

## Verification

**Commands:**
- `cd frontend && pnpm run build` -- expected: 构建无 TypeScript 与样式错误。
</frozen-after-approval>
