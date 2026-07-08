---
title: 'mobile-ui-fixes'
type: 'bugfix'
created: '2026-07-08'
status: 'done'
route: 'one-shot'
---

# Mobile UI Fixes

## Intent

**Problem:** 当前网页在移动端存在多个严重的可用性问题：找不到登录/退出入口、管理下拉菜单无响应、FAB按钮被导航栏遮挡、比赛名被tag遮挡、马匹详情卡长按卡顿、以及卡片布局在移动端信息密度不合理。

**Approach:** 专为移动端 (<768px) 添加底部导航登录/退出项、修复管理下拉菜单交互、调整FAB按钮底部间距、纵向堆叠比赛卡片头部、为马匹详情卡片新增四行移动端专属布局、并禁用长按文本选择行为。

## Suggested Review Order

按关注程度从高到低排列：

1. `frontend/src/components/HorseDetailCard.vue` — 移动端四行布局是结构改动最大的部分，需确认：
   - 桌面端 `desktop-table` 正常显示，`mobile-card-layout` 隐藏
   - 移动端显示四行布局（骑手/属地 → 父/母父 → 前走 → 主胜）
   - 长按不再触发系统菜单或卡顿
2. `frontend/src/layouts/AppLayout.vue` — 移动端底部导航新增登录/退出图标按钮
3. `frontend/src/pages/HomePage.vue` — 移动端 FAB 底部间距 + 比赛名与 tag 分行
4. `frontend/_bmad-output/implementation-artifacts/deferred-work.md` — 本次 defer 的预存问题
