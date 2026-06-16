---
title: 'Admin Layout: Sidebar → AppLayout Dropdown'
type: 'refactor'
created: '2026-06-16'
status: 'done'
route: 'one-shot'
---

## Intent

**Problem:** AdminLayout had its own sidebar layout, and admin pages used a separate layout tree. "管理" in the nav bar navigated directly to `/admin`, bypassing the sub-navigation UX.

**Approach:** Flatten admin routes as top-level routes sharing AppLayout. Replace the "管理" `<router-link>` in the nav bar with a dropdown trigger that shows admin sub-items (仪表盘/创建比赛/马匹管理/邀请码). AdminLayout simplified to a pass-through. Works on both desktop header and mobile bottom nav.

## Suggested Review Order

1. `frontend/src/router/index.ts` — Admin routes are now top-level (no AdminLayout wrapper), each with `requiresAuth: true, isAdmin: true` meta
2. `frontend/src/layouts/AppLayout.vue:1` — Script: `isAdminRoute` removed; admin dropdown toggle with click-outside, Escape, route change listeners
3. `frontend/src/layouts/AppLayout.vue:39` — Template: desktop nav-links has `v-if="authStore.isAdmin"` dropdown button + nested `<nav role="menu">` items
4. `frontend/src/layouts/AppLayout.vue:92` — Template: mobile bottom nav has `admin-dropdown-area` with dropdown rising upward (`bottom: calc(100% + 8px)`)
5. `frontend/src/layouts/AdminLayout.vue` — Reduced to pass-through `<router-view />` only
6. `_bmad-output/project-context.md` — Updated AdminLayout/AppLayout descriptions
