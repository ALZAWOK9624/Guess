---
title: '拖拽卡片时视口边缘自动滚动'
type: 'feature'
created: '2026-07-09'
status: 'in-progress'
baseline_commit: '3fd229e9f6166724e39d19577d1c9b9d50433e91'
context: ['{project-root}/_bmad-output/project-context.md']
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 桌面端 HTML5 拖拽和移动端触控拖拽期间，用户无法滚动页面以查看视口外的卡片。当马匹数量较多或需将卡片拖拽到列表远端时，只能先放下卡片、手动滚动、再重新拖动，操作体验割裂。

**Approach:** 在拖拽过程中，当拖拽点（鼠标/手指）进入视口上 1/5 或下 1/5 区域时自动平滑滚动页面，同时在对应边缘显示渐隐视觉提示。实现为独立 composable，同时在 ResultsPage 和 RaceDetailPage 的桌面/移动端拖拽路径中集成。

## Boundaries & Constraints

**Always:**
- 上 1/5 区域触发向上滚动，下 1/5 区域触发向下滚动
- 滚动速度与拖拽点距边缘的距离成正比（越靠近边缘越快）
- 仅在拖拽激活期间（isDragging/touchDragIndex >= 0）启动自动滚动
- 滚动目标容器：优先查找 `.scroll-container`（桌面端），回退到 `window`
- 离开触发区域后立即停止滚动
- 保留现有的绿色插入指示线（drag-over-top）行为不变
- 移动端 jiggle 模式中已有的 `touch-action: manipulation` 保持不变
- 视觉提示必须适配 `prefers-reduced-motion: reduce`
- 不新增任何 API 调用或 npm 依赖

**Ask First:**
- （无——全部决策已明确）

**Never:**
- 不修改 HTML5 DnD 的 drop 逻辑（插入位置计算保持 midY 判断）
- 不在非拖拽状态下显示自动滚动视觉提示
- 不移除现有的滚动禁用逻辑（如长按拖拽中的 `body overflow hidden` — 由新逻辑替代）
- 不使用 `setInterval`——全部使用 `requestAnimationFrame`

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 桌面端鼠标拖拽至视口上 1/5 | `dragover` 事件，`clientY < viewportHeight * 0.2` | `.scroll-container` 向上平滑滚动；顶部显示向上渐隐箭头 | N/A |
| 桌面端鼠标拖拽至视口下 1/5 | `dragover` 事件，`clientY > viewportHeight * 0.8` | `.scroll-container` 向下平滑滚动；底部显示向下渐隐箭头 | N/A |
| 桌面端鼠标离开触发区域 | `clientY` 在 0.2–0.8 范围内 | 停止滚动，箭头消失 | N/A |
| 移动端触控拖拽至视口上 1/5 | `touchmove`，手指 `clientY < viewportHeight * 0.2` | 页面向上平滑滚动；顶部显示渐隐提示 | N/A |
| 移动端触控拖拽至视口下 1/5 | `touchmove`，手指 `clientY > viewportHeight * 0.8` | 页面向下平滑滚动；底部显示渐隐提示 | N/A |
| 拖拽结束 | dragend / touchend / touchcancel | 停止所有自动滚动，清除视觉提示 | N/A |
| 已滚动到顶部，继续向上触发 | `scrollTop === 0`，`clientY < viewportHeight * 0.2` | 不滚动（无变化），但仍显示视觉提示 | N/A |
| 已滚动到底部，继续向下触发 | 已达 scrollHeight 底部 | 不滚动，但仍显示视觉提示 | N/A |
| reduced-motion 用户偏好 | `prefers-reduced-motion: reduce` | 视觉提示显示为静态（无脉冲动画），滚动仍生效 | N/A |

</frozen-after-approval>

## Code Map

- `frontend/src/composables/useDragAutoScroll.ts` -- **NEW**：自动滚动 composable，接收 `container`、`enabled` ref、`clientY` ref，返回 `autoScrollDirection` ref 和启动/停止方法
- `frontend/src/pages/admin/ResultsPage.vue` -- 集成自动滚动：桌面 `@dragover` 传入鼠标 Y 坐标；移动端 `@touchmove` 传入手指 Y 坐标
- `frontend/src/pages/RaceDetailPage.vue` -- 集成自动滚动：闸位拖拽和结果排名拖拽的桌面 `@dragover`/`@drag` 和移动端 `@touchmove` 路径

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/composables/useDragAutoScroll.ts` -- 创建自动滚动 composable：接收 `containerRef`（可滚动的 DOM 元素或 null 表示 window）、`enabled`（Ref<boolean>）、`clientY`（Ref<number>）；计算滚动速度和方向；使用 `requestAnimationFrame` 平滑滚动；返回 `autoScrollDirection: Ref<'up' | 'down' | null>`（父组件用于视觉提示）— 为拖拽视口边缘滚动提供独立可复用的逻辑
- [x] `frontend/src/pages/admin/ResultsPage.vue` -- 集成 useDragAutoScroll：桌面端 `@dragover` handler 中更新 `dragClientY` ref；移动端 `@touchmove` handler 中更新 `dragClientY` ref；`enabled` 绑定 `isDragging || touchDragIndex >= 0`。在 drop zone 区域顶部/底部添加 `.scroll-hint-up` / `.scroll-hint-down` 视觉提示（半透明渐隐 + 向上/向下箭头图标）— 为结果录入页提供自动滚动能力
- [x] `frontend/src/pages/RaceDetailPage.vue` -- 集成 useDragAutoScroll（三处拖拽上下文）：闸位拖拽（gate mode）的 `@dragover` + `handleGateTouchMove`；结果排名的 `@dragover` + `handleResultTouchMove`。每处独立 `useDragAutoScroll` 实例或共享一个按 "当前活跃拖拽源" 切换 enabled 的实例。在拖拽区域顶部/底部添加 `.scroll-hint-up` / `.scroll-hint-down` 视觉提示 — 为比赛详情页的三套拖拽系统提供自动滚动能力
- [x] 验证：`cd frontend && pnpm build` 通过，无 TypeScript 编译错误

**Acceptance Criteria:**
- Given 桌面端在结果录入/闸位拖拽/结果排名拖拽中，when 鼠标拖拽卡片进入视口上 1/5 区域，then 页面向上平滑滚动且顶部显示渐隐向上箭头提示
- Given 桌面端拖拽中，when 鼠标拖拽卡片进入视口下 1/5 区域，then 页面向下平滑滚动且底部显示渐隐向下箭头提示
- Given 移动端 jiggle 模式拖拽中，when 手指拖拽卡片进入视口上 1/5 区域，then 页面向上平滑滚动且顶部显示渐隐箭头提示
- Given 移动端 jiggle 模式拖拽中，when 手指拖拽卡片进入视口下 1/5 区域，then 页面向下平滑滚动且底部显示渐隐箭头提示
- Given 拖拽结束（松手），when 触发 dragend/touchend/touchcancel，then 所有滚动停止且视觉提示立即消失
- Given 系统设置了 prefers-reduced-motion，when 触发自动滚动视觉提示，then 箭头为静态显示（无脉冲动画），滚动仍然正常工作

## Design Notes

**滚动速度公式**：`speed = baseSpeed × distanceRatio²`，其中 `baseSpeed = 8px/frame`，`distanceRatio = (thresholdDistance - actualDistance) / thresholdDistance`（0=刚进入区域, 1=已到边缘）。二次幂确保越靠近边缘速度越快，提供自然的加速感。使用 `requestAnimationFrame` 每帧调用 `scrollContainer.scrollBy(0, speed)` 实现 60fps 平滑滚动。

**视觉提示设计**：上下边缘各一个 `.scroll-hint` 容器（`position: fixed; left: 0; right: 0; height: 48px; pointer-events: none; z-index: 10`），内含居中箭头图标（SVG，32px，`color: var(--color-primary)`）+ 半透明渐变背景（`linear-gradient(to bottom, rgba(26,86,50,0.15), transparent)` 用于顶部，反向用于底部）。默认 `opacity: 0`，当 `autoScrollDirection === 'up'` 时顶部 fadeIn，`'down'` 时底部 fadeIn。transition 使用 `opacity 0.2s ease`。箭头添加 `@keyframes scroll-bounce` 弹跳动画（translateY ±4px, 0.6s alternate infinite），在 reduced-motion 下禁用为 `animation: none`。

**zone 检测与滚动触发集成**：在现有的 `@dragover` handler（桌面端）和 `@touchmove` handler（移动端）中，提取 `clientY` 并写入 `dragClientY` ref。useDragAutoScroll 在 `enabled && dragClientY > 0` 时内部判断并驱动滚动。这避免创建独立的 `@drag` 事件监听，最小化对现有 handler 的侵入。

## Verification

**Commands:**
- `cd frontend && pnpm build` -- expected: 零 TypeScript 错误，构建成功
