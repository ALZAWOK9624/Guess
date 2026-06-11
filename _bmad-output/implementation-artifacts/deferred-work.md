# Deferred Work Items

_This file tracks code review findings that were deferred for later resolution._

---

## Deferred from: code review of Story 2.1 (2026-06-11)

- **[Defer]** TODO: 删除马匹时检查 race 引用 (`horse_service.py:107-108`) — 当前未实现，等 race 模型实现后再处理（Epic 2 后续故事）。
- **[Defer]** `onupdate=func.now()` 在异步下的行为 — 当前测试通过，无实际影响。
- **[Defer]** GET 端点公开访问（非管理员）— 设计意图，马匹数据对所有登录用户可见。
