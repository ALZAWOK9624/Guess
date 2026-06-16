---
title: 'Admin Layout: Sidebar → Top Nav Dropdown'
type: 'refactor'
created: '2026-06-16'
status: 'done'
route: 'one-shot'
---

## Intent

**Problem:** AdminLayout used a fixed 240px sidebar (desktop) + hamburger overlay (mobile), which took up horizontal space and felt heavy for a management panel with only 4 navigation items.

**Approach:** Replace the sidebar entirely with a compact green top navigation bar containing the brand, title, and a dropdown menu trigger for admin navigation. The dropdown closes on click-outside, Escape key, and route change.

## Suggested Review Order

1. `frontend/src/layouts/AdminLayout.vue:1` — Script: verify NavItem data is type-safe and v-html was removed in favor of inline SVG templates
2. `frontend/src/layouts/AdminLayout.vue:75` — Template: dropdown trigger uses `aria-expanded` + `aria-haspopup`, menu uses `role="menu"`/`role="menuitem"`; Escape key listener on document closes the dropdown
3. `frontend/src/layouts/AdminLayout.vue:136` — Styles: `nav-dropdown` has `max-height: 360px` + `overflow-y: auto` for overflow safety; `prefers-reduced-motion: reduce` disables the fade transition
4. `frontend/src/assets/styles/variables.css:80` — Removed unused `--sidebar-width: 240px` token
5. `_bmad-output/project-context.md:84` — Updated AdminLayout description to reflect top-nav + dropdown
