# Investigation: 管理后台缺少锁定比赛功能

## Hand-off Brief

1. **What happened.** 管理员用户在管理后台找不到生成邀请码和锁定比赛的功能按钮。
2. **Where the case stands.** 已确认：邀请码功能在前端和后端均完整实现；锁定比赛的后端 API 已实现但前端完全缺失锁定按钮/入口。
3. **What's needed next.** 在前端 `DashboardPage.vue` 和/或比赛详情页添加"锁定比赛"按钮，调用 `POST /api/v1/races/{race_id}/lock`。

## Case Info

| Field            | Value                                                          |
| ---------------- | -------------------------------------------------------------- |
| Ticket           | N/A                                                            |
| Date opened      | 2026-06-16                                                     |
| Status           | Active                                                         |
| System           | Frontend: Vue 3 + TypeScript; Backend: Python FastAPI + SQLAlchemy |
| Evidence sources | 源代码审查（后端 endpoint、前端页面组件、路由配置、侧边栏菜单）  |

## Problem Statement

管理员用户登录后，在管理后台页面（`/admin`）无法找到"生成邀请码"和"锁定比赛"的操作入口。用户怀疑这两个功能尚未实现或未正确暴露。

## Evidence Inventory

| Source | Status | Notes |
| ------ | ------ | ----- |
| 后端 Admin 端点 (`admin.py`) | Available | `GET /api/v1/admin/invite-codes`, `POST /api/v1/admin/invite-codes`, `PATCH /api/v1/admin/invite-codes/{code}` |
| 后端 Lock 端点 (`votes.py`) | Available | `POST /api/v1/races/{race_id}/lock` - 需要管理员权限 |
| 前端邀请码页面 (`InviteCodesPage.vue`) | Available | 页面存在，包含 `InviteCodeTable` 子组件 |
| 前端邀请码表格组件 (`InviteCodeTable.vue`) | Available | 包含"生成邀请码"按钮、搜索框、列表、复制/失效操作 |
| 前端侧边栏 (`AdminLayout.vue`) | Available | 包含"邀请码"导航项（第84-90行），指向 `/admin/invite-codes` |
| 前端仪表盘 (`DashboardPage.vue`) | Available | 操作列仅有"编辑"和"删除"按钮，无"锁定比赛"按钮 |
| 前端 ResultsPage (`ResultsPage.vue`) | Available | 遇到 `RACE_NOT_LOCKED` 错误时仅显示提示"返回管理后台"，无锁定操作入口 |
| 前端 API 层 (`api/admin.ts`, `api/results.ts`) | Available | 未定义任何 `lockRace` API 调用 |

## Investigation Backlog

| # | Path to Explore | Priority | Status | Notes |
| - | --------------- | -------- | ------ | ----- |
| 1 | 确认用户账号是否为 `is_admin` | High | Open | 如果当前账号不是管理员，侧边栏和路由会完全隐藏管理后台入口 |

## Confirmed Findings

### Finding 1: 邀请码功能完整可用

**Evidence:** 
- 前端组件 `InviteCodeTable.vue:55-66` — `handleCreate()` 调用 `createInviteCode()`，通过 `POST /admin/invite-codes`
- 后端 `admin.py:25-32` — `create_invite_code` 端点已实现，需要管理员权限
- 侧边栏 `AdminLayout.vue:84-90` — 有"邀请码"导航项，链接到 `/admin/invite-codes`

**Detail:** 生成邀请码和邀请码管理的完整功能链（前端页面 → API → 后端服务）在所有层都已实现。管理员用户只需点击侧边栏的"邀请码"导航即可进入。

### Finding 2: 锁定比赛的 API 已实现但前端无入口

**Evidence:**
- 后端 `votes.py:79-94` — `lock_race` 端点：`POST /api/v1/races/{race_id}/lock`，需要 `get_current_admin` 依赖
- 后端 `vote_service.py:116-138` — `lock_race()` 将比赛状态从 `voting` 转为 `locked`
- 前端 API 层 (`api/` 目录) — **完全没有任何 lock API 调用**
- `DashboardPage.vue:149-162` — 操作列只有"编辑"和"删除"按钮
- `ResultsPage.vue:80-81` — 加载时检查 `RACE_NOT_LOCKED` 但仅提示"请先锁定"，然后给一个"返回管理后台"按钮

**Detail:** 后端的锁定 API 完整可用，但前端从 UI 入口到 API 调用层全面缺失。当管理员尝试进入结果录入页面时，如果比赛仍处于 `voting` 状态，页面会报错"比赛处于投票中状态，请先锁定"，然后引导用户"返回管理后台"——但管理后台也没有锁定按钮。

## Deduced Conclusions

### Deduction 1: "锁定比赛"功能属于未完成的前端开发遗漏

**Based on:** Finding 2

**Reasoning:** 
1. 后端完整实现了 `POST /api/v1/races/{race_id}/lock` 端点
2. 前端已知道需要先锁定才能录入结果（`ResultsPage.vue:80` 检查 `RACE_NOT_LOCKED`）
3. 但前端 `api/admin.ts` 和 `api/results.ts` 都没有封装 lock API 调用
4. `DashboardPage.vue` 也没有任何"锁定"按钮
5. 锁定比赛所需的前端组件（按钮、API 调用、状态判断逻辑）完全没有实现

**Conclusion:** 这是一个前端侧的开发遗漏——锁定的后端能力就绪，但前端从未实现触发锁定的 UI 和 API 调用。

## Hypothesized Paths

### Hypothesis 1: 当前登录的用户不是管理员

**Status:** Open

**Theory:** 用户可能使用了一个非管理员账号登录，导致管理侧边栏和路由完全不可见。

**Supporting indicators:** 管理后台路由守卫在 `router/index.ts` 中检查 `meta.isAdmin` 和 `user.is_admin`，非管理员会被重定向到首页。

**Would confirm:** 查看 `authStore` 中 `user.value.is_admin` 是否为 `true`。

**Would refute:** 用户能看到管理后台页面（仪表盘等）。

## Missing Evidence

| Gap | Impact | How to Obtain |
| --- | ------ | ------------- |
| 用户账号的 `is_admin` 状态 | 如果用户不是管理员，所有管理功能都不可见 | 查看前端 `authStore` 或后端数据库 `users` 表 |

## Source Code Trace

| Element | Detail |
| ------- | ------ |
| Error origin (邀请码不可见) | 不适用 — 功能已实现，可正常访问 `/admin/invite-codes` |
| Error origin (无法锁定比赛) | 前端 `DashboardPage.vue:149-162` — 操作列只渲染了"编辑"和"删除"按钮 |
| Trigger | 比赛创建后处于 `voting` 状态，需要管理员先锁定才能录入结果 |
| Condition | `race.status === 'voting'` 且未在前端提供状态转换触发器 |
| Related files | `backend/app/api/v1/endpoints/votes.py:79-94` (后端锁定API), `frontend/src/pages/admin/DashboardPage.vue` (应添加锁定按钮), `frontend/src/pages/admin/ResultsPage.vue` (检查锁定状态但无法触发锁定) |

## Conclusion

**Confidence:** High

**邀请码功能：** 完全可用。管理员用户只需通过侧边栏点击"邀请码"导航到 `/admin/invite-codes`，即可看到"生成邀请码"按钮和邀请码管理表格。该功能各层（后端 API → 前端 API 调用 → 前端组件 → 路由/侧边栏导航）均完整实现。

**锁定比赛功能：** 后端 API 就绪但前端完全缺失。这是一个明确的开发遗漏，需要在前端添加：
1. `api/admin.ts` 或 `api/races.ts` 中封装 `lockRace(raceId)` 调用
2. `DashboardPage.vue` 的表格操作列中，为 `voting` 状态的比赛添加"锁定"按钮
3. 锁定操作成功后刷新比赛列表

## Recommended Next Steps

### Fix direction

在 `DashboardPage.vue` 的操作列中，为 `status === 'voting'` 的比赛添加一个"锁定"按钮，调用 `POST /api/v1/races/{race_id}/lock` 后刷新列表。

推荐使用 `bmad-quick-dev` skill 来实现这个前端修改。

### Diagnostic

1. 检查用户是否确实为管理员 — 在浏览器中打开 DevTools > Application > Local Storage 查看 JWT token，或调用 `GET /api/v1/auth/me` 查看 `is_admin` 字段。
2. 如果能看到管理后台首页（仪表盘），证明已是管理员。
3. 尝试直接访问 `POST /api/v1/races/{race_id}/lock`（通过浏览器开发者工具或 Postman）确认后端功能是否正常。

## Reproduction Plan

1. 使用管理员账号登录
2. 点击页面右上角的"管理"链接
3. 观察侧边栏：可以看到"仪表盘"、"创建比赛"、"马匹管理"、"邀请码"
4. 点击"邀请码" → 可以看到邀请码页面，有"生成邀请码"按钮 ✓
5. 点击"仪表盘" → 比赛列表中有"编辑"和"删除"按钮，但没有"锁定"按钮 ✗
6. 点击某场比赛的"编辑"（`/admin/races/:id/edit`），确认比赛处于 `voting` 状态
7. 尝试访问 `/admin/races/:id/results` → 显示错误提示"比赛处于投票中状态，请先锁定"，"返回管理后台" ✗

## Side Findings

- `ResultsPage.vue:80-81` 的 `RACE_NOT_LOCKED` 错误处理中，引导用户"返回管理后台"，但返回后用户仍然无法锁定比赛——这是一个UX闭环断裂。
- 锁定比赛在业务流程中是 `voting` → `locked` → `settled` 的必要中间步骤，缺少锁定按钮导致整个结果录入流程无法启动。
