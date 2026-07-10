---
title: '预防弹窗点击外部关闭 - 首页 & 马匹管理'
type: bugfix
created: '2026-07-10'
status: done
route: one-shot
---

# 预防弹窗点击外部关闭 - 首页 & 马匹管理

## Intent

**Problem**: 首页创建比赛弹窗 和 马匹管理页添加/修改马匹弹窗 允许点击遮罩层外部区域关闭弹窗，与比赛详情页的添加马匹弹窗行为不一致。

**Approach**: 移除两个弹窗的 `@click.self` 事件处理器，使其行为与 RaceDetailPage 的添加马匹弹窗一致——只能通过"取消"按钮关闭。

## Suggested Review Order

1. `frontend/src/pages/HomePage.vue:268` — 移除 `.modal-backdrop` 的 `@click.self="closeCreateModal"` 属性
2. `frontend/src/pages/admin/HorsesPage.vue:462` — 移除 `.modal-overlay` 的 `@click.self="showModal = false"` 属性
3. `frontend/src/pages/RaceDetailPage.vue:1180` — 参考实现：此弹窗无 `@click.self`，已正确阻止外部点击关闭
