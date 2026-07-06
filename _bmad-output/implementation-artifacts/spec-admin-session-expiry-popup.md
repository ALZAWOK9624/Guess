---
title: 'Admin Session Expiry Popup'
type: 'bugfix'
created: '2026-07-06'
status: 'done'
route: 'one-shot'
---

# Admin Session Expiry Popup

## Intent

**Problem:** Admins only discovered that their session had expired when they performed an action, because the app only reacted to 401 responses. There was no proactive notification while the page sat idle.

**Approach:** Parse the refresh token's `exp` claim in `authStore` and schedule a timer. When the timer fires, clear the auth state and immediately redirect admin users to the login page with a `?session=expired` query parameter so the login page shows a clear "session expired" message. Additionally, harden the Axios 401 interceptor so any unauthenticated request (not just refresh-token failures) redirects to the login page before the page can render a generic "loading failed" error.

## Suggested Review Order

1. `frontend/src/utils/jwt.ts` — JWT payload parsing and base64url padding handling.
2. `frontend/src/stores/authStore.ts` — timer lifecycle, admin-only scheduling, and redirect logic.
3. `frontend/src/api/client.ts` — 401 handling now redirects for any unauthenticated request and halts the promise to prevent caller error banners from flashing.
4. `frontend/src/pages/LoginPage.vue` — query param normalization and session-expired banner.
