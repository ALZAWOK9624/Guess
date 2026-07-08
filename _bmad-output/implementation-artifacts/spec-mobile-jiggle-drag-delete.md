---
title: '移动端抖动编辑模式：拖拽排序 + 卡片删除'
type: 'feature'
created: '2026-07-08'
status: 'done'
baseline_commit: '7b42f25fed851a426b6a1ed4fbff193dcd054acd'
context: ['{project-root}/_bmad-output/project-context.md']
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 移动端管理员在比赛详情页的闸位拖拽和结果排名操作，当前使用 300ms 长按激活拖拽 + 底部"拖拽至此删除"区域。长按易与系统手势冲突，删除区浪费移动端宝贵屏幕空间，且结果排名模式在移动端缺少触控拖拽支持。

**Approach:** 在 RaceDetailPage 顶部（移动端）添加"编辑"切换按钮。激活后卡片进入持续抖动动画，可自由触控拖拽排序，右上角显示 ✕ 删除按钮。此模式同时覆盖闸位拖拽（voting 状态）和结果排名（locked/settled 状态），完全替代桌面端的拖拽至删除区逻辑。

## Boundaries & Constraints

**Always:**
- 仅移动端（<768px）+ 管理员用户可见/可用
- 闸位抖动模式仅 voting 状态有效，结果排名抖动模式仅 locked/settled 状态有效
- ✕ 按钮点击 → 弹出 ConfirmDeleteModal 确认后删除（复用已有组件）
- 抖动动画必须尊重 `prefers-reduced-motion: reduce`
- 拖拽期间使用 `touch-action: none` 阻止滚动（遵循现有触控安全模式）
- 桌面端交互完全不变
- API 调用不变（removeRaceHorse / updateGateOrder / submitResults）

**Ask First:**
- （无——用户已确认两者均覆盖 + 确认弹窗删除）

**Never:**
- 不修改桌面端 HTML5 DnD 逻辑
- 不添加新的 API 端点或 npm 依赖
- 不实现触觉反馈（haptic feedback）
- 非管理员用户不可见编辑按钮

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 管理员进入抖动模式 | voting 状态，点击"编辑"按钮 | 所有卡片开始抖动动画，可拖拽排序，显示 ✕ 按钮；底部删除区隐藏 | N/A |
| 抖动模式拖拽排序 | 拖拽卡片到新位置 | 实时交换数组，松手后自动提交闸位/名次顺序 | API 失败 → alert + 刷新数据回滚 |
| 抖动模式点击 ✕ | 点击卡片右上角 ✕ | 弹出 ConfirmDeleteModal 显示马匹名称 | API 失败 → alert，卡片保留 |
| 确认删除 | 弹窗中点击"删除" | 调用 removeRaceHorse，卡片从列表移除，数据刷新 | API 失败 → alert 错误信息 |
| 退出抖动模式 | 再次点击"编辑"按钮 | 抖动停止，✕ 按钮消失，拖拽禁用，回到普通视图 | N/A |
| 结果排名抖动模式 | locked/settled 状态，点击"编辑" | 进入抖动模式 + 保留 active/DNF 双列表 + DNF 区仍可交互（点击移回 active） | N/A |
| 非管理员 / 桌面端 | 无编辑按钮 | 编辑按钮完全不可见，现有逻辑不变 | N/A |
| 用户偏好 reduced-motion | 系统设置了减少动画 | 抖动动画禁用，仅显示 ✕ 按钮和拖拽功能 | N/A |

</frozen-after-approval>

## Code Map

- `frontend/src/pages/RaceDetailPage.vue` — 核心页面：添加 isJiggleMode 状态、编辑按钮、移动端触控拖拽重写、✕ 按钮删除连线
- `frontend/src/components/HorseDetailCard.vue` — 卡片组件：新 prop `showDeleteButton` / `isJiggling`、抖动 CSS 动画、✕ 按钮 UI、emit `deleteClick`
- `frontend/src/composables/useDragSort.ts` — 拖拽 composable：无需修改（gate/result 双模式已满足需求）

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/components/HorseDetailCard.vue` — 新增 `showDeleteButton` (boolean) 和 `isJiggling` (boolean) props；在 `.mobile-card-layout` 右上角添加 ✕ 删除按钮（仅 `showDeleteButton && !isDnf` 时渲染）；添加 `@keyframes jiggle` 动画（scoped CSS，约 ±1deg 旋转 + ±2px 位移，周期 0.3s）；`isJiggling` 时卡片应用该动画；emit `deleteClick` 事件 — 为抖动模式提供卡片级 UI 能力
- [x] `frontend/src/pages/RaceDetailPage.vue` — 添加 `isJiggleMode` ref（默认 false）；在 `.race-header` 区域添加移动端"编辑"切换按钮（仅 `isAdmin` 时渲染，使用 `.mobile-only` 类）；闸位拖拽（voting）：当 `isJiggleMode` 时，用 `touchstart`（即时激活，无 300ms 延迟）+ `touchmove`（实时重排）+ `touchend`（submitGateOrder）替代原有长按逻辑；结果排名（locked/settled）：当 `isJiggleMode` 时，为 active 和 dnf 列表的卡片绑定 touch 拖拽；两个模式都隐藏原有的 `.delete-zone`（当 `isJiggleMode` 时）；卡片传入 `:show-delete-button="isJiggleMode"` 和 `:is-jiggling="isJiggleMode"`；✕ 点击 → `deleteTarget` + `showDeleteConfirm = true`（复用已有 ConfirmDeleteModal）。退出抖动模式时清除拖拽状态 — 替换移动端 300ms 长按 + 拖拽删除区为 iOS 风格抖动编辑模式
- [x] 验证：`pnpm build` 通过，无 TypeScript 编译错误

**Acceptance Criteria:**
- Given 移动端管理员在 voting 状态的比赛详情页，when 点击"编辑"按钮，then 所有马匹卡片开始抖动动画、显示 ✕ 按钮、底部删除区和添加卡片区隐藏
- Given 抖动模式激活，when 触摸拖拽卡片到新位置后松手，then 闸位顺序自动提交并更新
- Given 抖动模式激活，when 点击卡片右上角 ✕ 并在弹窗中确认，then 该马匹从比赛中移除，卡片消失
- Given 移动端管理员在 locked 状态的比赛详情页，when 点击"编辑"按钮，then 卡片进入抖动模式，可拖拽 active 列表排序、点击 DNF 区马匹移回
- Given 抖动模式激活，when 再次点击"编辑"按钮，then 抖动停止、✕ 隐藏、恢复普通视图

## Spec Change Log

## Design Notes

抖动动画参考 iOS 主屏幕编辑模式：卡片以中心为轴做小幅度旋转 + 位移振荡，配合 `animation-direction: alternate` 产生往复效果。关键实现：

```css
@keyframes jiggle {
  0% { transform: rotate(0deg) translate(0, 0); }
  25% { transform: rotate(-0.8deg) translate(-1px, 0); }
  75% { transform: rotate(0.8deg) translate(1px, 1px); }
  100% { transform: rotate(0deg) translate(0, 0); }
}

.horse-detail-card.is-jiggling {
  animation: jiggle 0.3s ease-in-out infinite alternate;
  touch-action: none;
}
```

✕ 按钮位于卡片 `mobile-name-section` 右上角，`position: absolute; top: -8px; right: -8px`，28px 红色圆形，白色 ✕ 图标。添加 `z-index: 1` 确保在投票徽章之上。

编辑按钮位于 `.race-header` 区域，与返回按钮同行右侧。仅在 `isAdmin` 且比赛为 voting/locked/settled 时渲染。样式：与现有 `.lock-btn` 同级的 admin 按钮，带 pencil 图标（📝）。

## Verification

**Commands:**
- `cd frontend && pnpm build` — 无 TypeScript 编译错误

**Manual checks (if no CLI):**
- 移动端 Chrome DevTools 模拟 (<768px)：管理员在 voting 比赛 → 点击"编辑" → 卡片抖动、✕ 可见 → 拖拽重排 → 点击 ✕ 删除 → 点击"编辑"退出
- `prefers-reduced-motion: reduce` 下抖动动画不播放
- 桌面端：编辑按钮不可见，原有 DnD + 删除区逻辑完整保留

## Suggested Review Order

**入口：抖动模式状态机**

- 抖动模式开关 + 资格判断 + 退出清理；是整个功能的控制中枢
  [`RaceDetailPage.vue:43`](../../frontend/src/pages/RaceDetailPage.vue#L43)
- `toggleJiggleMode`：激活/退出时重置所有拖拽状态，退出时防悬挂指针
  [`RaceDetailPage.vue:88`](../../frontend/src/pages/RaceDetailPage.vue#L88)

**卡片组件：抖动动画 + ✕ 删除按钮**

- 新增 `showDeleteButton` / `isJiggling` props 和 `deleteClick` emit
  [`HorseDetailCard.vue:40`](../../frontend/src/components/HorseDetailCard.vue#L40)
- 移动端 name-section 中绝对定位的红色圆形 ✕ 按钮，`@click.stop` 防冒泡
  [`HorseDetailCard.vue:284`](../../frontend/src/components/HorseDetailCard.vue#L284)
- `@keyframes jiggle` 动画 + `.is-jiggling` 应用 + `touch-action: none` 阻止滚动
  [`HorseDetailCard.vue:833`](../../frontend/src/components/HorseDetailCard.vue#L833)
- `prefers-reduced-motion` 覆盖：抖动动画在无障碍偏好下禁用
  [`HorseDetailCard.vue:881`](../../frontend/src/components/HorseDetailCard.vue#L881)

**闸位拖拽：长按 → 即时触控**

- `handleGateTouchStart`：jiggle 模式直接激活，无 300ms 延迟
  [`RaceDetailPage.vue:400`](../../frontend/src/pages/RaceDetailPage.vue#L400)
- 编辑按钮 + 删除区隐藏在 jiggle 模式下的模板变更
  [`RaceDetailPage.vue:774`](../../frontend/src/pages/RaceDetailPage.vue#L774)
- 删除区/添加卡片条件渲染：`!isJiggleMode` 隐藏桌面拖拽删除区
  [`RaceDetailPage.vue:1010`](../../frontend/src/pages/RaceDetailPage.vue#L1010)

**结果排名：新增移动端触控拖拽**

- `handleResultTouchStart/Move/End/Cancel`：active/DNF 双列表触控逻辑
  [`RaceDetailPage.vue:543`](../../frontend/src/pages/RaceDetailPage.vue#L543)
- Active 列表卡片绑定 touch 事件 + jiggle props
  [`RaceDetailPage.vue:1037`](../../frontend/src/pages/RaceDetailPage.vue#L1037)
- DNF 列表卡片绑定 touch 事件（松手回 active zone）
  [`RaceDetailPage.vue:1079`](../../frontend/src/pages/RaceDetailPage.vue#L1079)

**生命周期：状态同步**

- 锁定比赛后退出抖动模式
  [`RaceDetailPage.vue:185`](../../frontend/src/pages/RaceDetailPage.vue#L185)
- 退出结果模式时退出抖动模式
  [`RaceDetailPage.vue:490`](../../frontend/src/pages/RaceDetailPage.vue#L490)
- `onUnmounted` 确保组件销毁时清理
  [`RaceDetailPage.vue:738`](../../frontend/src/pages/RaceDetailPage.vue#L738)
