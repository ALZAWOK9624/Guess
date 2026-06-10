# Deferred Work

## Deferred from: code review of Story 1.3 (2026-06-10)

- Path parameter `{code}` may have special char issues — current charset doesn't include problematic characters
- Search endpoint has no pagination — current scale (~100 users) doesn't need it
- LIKE wildcard `%`/`_` interpreted literally in search — not a security issue
- No rate limiting on admin endpoints — v1 explicitly does not implement rate limiting
- `is_admin` hardcoded to False in `get_current_user` — known placeholder, fixed in Story 1.5a
- Missing `updated_at` audit column on invite_codes table
- `invalidate_invite_code` only checks `status == "used"`, not `bound_username`/`bound_qq` — current logic doesn't produce this state
- `response_model=dict` used instead of typed models — doesn't affect correctness, only OpenAPI docs
- Confusable characters `Z/2`, `S/5` in invite code charset — UX enhancement
- `InviteCodeListResponse` wrapper is redundant — no functional impact
- `navigator.clipboard` fallback `execCommand('copy')` is deprecated — still supported in all major browsers
- SQLite in-memory tests don't cover real DB concurrency — known limitation

## Deferred from: code review of Story 1.4 - 用户注册 (2026-06-10)

- `response_model=dict` pattern — same pattern used in admin.py (Story 1.3), not introduced by this change
- Service layer directly raising HTTPException — same pattern used in invite_code_service.py, not introduced by this change
- Test dependency override cleanup not in try/finally — low risk as tests run in isolation
