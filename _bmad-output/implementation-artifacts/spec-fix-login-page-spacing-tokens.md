---
title: 'Fix Login Page Spacing Token Alignment'
type: 'bugfix'
created: '2026-07-06'
status: 'done'
route: 'one-shot'
---

# Fix Login Page Spacing Token Alignment

## Intent

**Problem:** The login page (`frontend/src/pages/LoginPage.vue`) used non-existent CSS spacing variables (`--spacing-24`, `--spacing-20`, `--spacing-32`) that aren't defined in the JRA design system, causing all affected `padding` and `margin` declarations to silently fail (invalid `var()` → whole declaration dropped → values default to `0`). This collapsed all spacing on the page — card padding, title margin, form-field gaps, banner margins — resulting in a visually broken, cramped layout.

**Approach:** Replaced every invalid spacing variable reference with its correct design-system equivalent (`--spacing-6` for 24px, `--spacing-5` for 20px, `--spacing-8` for 32px, `--spacing-3` for 12px, `--spacing-4` for 16px). Also normalized adjacent hardcoded values to use design tokens where trivial (card shadow → `--shadow-md`, tab font 13px → 14px, tab padding from `8px 4px` → `--spacing-2` spacing token). Additionally fixed two related layout defects found during adversarial review: label-to-input margin (`--spacing-8` 32px → `--spacing-2` 8px) and submit-button spinner gap (`--spacing-8` 32px → `--spacing-2` 8px).

## Suggested Review Order

Concern ordering (one-shot, minimal blast radius):

1. `frontend/src/pages/LoginPage.vue:234` — Verify the complete `<style scoped>` block. All `var(--spacing-*)` references should match the JRA spacing scale defined in `variables.css` (`--spacing-1`=4px … `--spacing-16`=64px).
2. `frontend/src/pages/LoginPage.vue:298` — Confirm `.form-field label` margin-bottom changed from `--spacing-8` (32px, erroneously large) to `--spacing-2` (8px, normal label-to-input gutter).
3. `frontend/src/pages/LoginPage.vue:367` — Confirm `.submit-btn` gap changed from `--spacing-8` (32px, excessive between spinner and text) to `--spacing-2` (8px).
