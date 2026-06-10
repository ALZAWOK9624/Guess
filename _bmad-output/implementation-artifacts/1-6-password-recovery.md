---
baseline_commit: 33b6fda398fdf7a00857b077035841d5d851aed4
---

# Story 1.6: Password Recovery（密码找回）

Status: done

## Story

As a **忘记密码的用户**,
I want **凭用户名和邀请码重置密码**,
So that **我可以恢复账号访问**。

## Acceptance Criteria

1. **Given** 用户已注册但忘记密码
   **When** 访问 `/reset-password`，输入用户名和该用户绑定的邀请码
   **Then** 进入新密码设置页面
   **And** 设置新密码后，密码更新成功

2. **Given** 用户输入错误的邀请码
   **When** 提交密码找回
   **Then** 显示「邀请码与用户不匹配」

3. **Given** 后端 API
   **When** `POST /api/v1/auth/reset-password` 携带正确参数（username + invite_code + new_password）
   **Then** 返回 200，用户密码更新为新密码（bcrypt 哈希）

4. **Given** 用户提交新密码
   **When** 新密码长度 < 6 或 > 128
   **Then** 前端显示「密码至少需要 6 个字符」校验提示
   **And** 表单不提交

5. **Given** 登录页面底部链接
   **When** 用户点击「忘记密码？」
   **Then** 跳转到 `/reset-password`（已就绪，无需修改）

6. **Given** 已登录用户访问 `/reset-password`
   **When** 直接输入 URL
   **Then** 路由守卫自动跳转首页（已就绪，无需修改）

## Tasks / Subtasks

- [x] Task 1: 后端添加 `POST /api/v1/auth/reset-password` 端点 (AC: #2, #3)
  - [x] 在 `backend/app/schemas/auth.py` 中添加 `ResetPasswordRequest` schema（username, invite_code, new_password）
  - [x] 在 `backend/app/schemas/auth.py` 中添加 `ResetPasswordResponse` schema（含 UserInfo）
  - [x] 在 `backend/app/services/auth_service.py` 中添加 `reset_password(db, request)` 函数
  - [x] 函数流程：查用户→查 invite_code→验证匹配→hash 新密码→更新→返回用户信息
  - [x] 用户不存在或 invite_code 不匹配时返回 400 `INVITE_CODE_MISMATCH`
  - [x] 在 `backend/app/api/v1/endpoints/auth.py` 中添加 reset-password 端点

- [x] Task 2: 更新后端测试 (AC: #3)
  - [x] 在 `backend/tests/test_auth.py` 中添加 `test_reset_password_success`
  - [x] 在 `backend/tests/test_auth.py` 中添加 `test_reset_password_wrong_invite_code`
  - [x] 在 `backend/tests/test_auth.py` 中添加 `test_reset_password_nonexistent_user`
  - [x] 验证密码正确更新后用新密码可登录

- [x] Task 3: 前端添加 reset-password API 调用 (AC: #3)
  - [x] 在 `frontend/src/types/auth.ts` 中添加 `ResetPasswordRequest` 和 `ResetPasswordResponse` 接口
  - [x] 在 `frontend/src/api/auth.ts` 中添加 `resetPassword(data)` API 函数

- [x] Task 4: 完整实现 ResetPasswordPage.vue 双步骤流程 (AC: #1, #2, #4)
  - [x] 第一步：用户名 + 邀请码表单（先验证身份）
  - [x] 第二步：新密码设置表单（已验证后展示）
  - [x] 表单验证：非空、密码 >= 6 位，密码确认匹配
  - [x] 错误处理：显示「邀请码与用户不匹配」
  - [x] 成功后跳转登录页（提示用户用新密码登录）
  - [x] 移动端适配：全宽、触摸目标 ≥ 44px、safe-area-inset-bottom
  - [x] 无障碍：`<label>` 绑定、`aria-live` error region、aria-busy、focus ring

- [x] Task 5: 端到端验证
  - [x] TypeScript 编译通过（vue-tsc --noEmit）
  - [x] Vite 构建成功
  - [x] 后端所有 pytest 通过（43 passed，零回归）
  - [x] 手动验证：注册→退出→密码找回→用新密码登录

## Dev Notes

### 后端实现说明

#### Schema 定义（`backend/app/schemas/auth.py`）

新增 Pydantic schemas：

```python
class ResetPasswordRequest(BaseModel):
    username: str
    invite_code: str
    new_password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if len(v) < 3 or len(v) > 20:
            raise ValueError("用户名长度需在 3-20 个字符之间")
        return v

    @field_validator("invite_code")
    @classmethod
    def validate_invite_code(cls, v: str) -> str:
        if len(v) != 8:
            raise ValueError("邀请码必须为 8 位字符")
        return v

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("密码至少需要 6 个字符")
        if len(v) > 128:
            raise ValueError("密码长度不能超过 128 个字符")
        return v


class ResetPasswordResponse(BaseModel):
    user: UserInfo
```

#### Service 函数（`backend/app/services/auth_service.py`）

新增 `reset_password()` 函数：

```python
async def reset_password(
    db: AsyncSession, request: ResetPasswordRequest
) -> ResetPasswordResponse:
    """Reset password using username + bound invite code verification.

    Flow:
    1. Look up user by username
    2. Look up invite_code by code string
    3. Verify invite_code is bound to this user
    4. Hash new password
    5. Update user's password_hash
    6. Return response with user info
    """
```

**关键逻辑：**
- 先查 User（`select(User).where(User.username == ...)`）
- 再查 InviteCode（`select(InviteCode).where(InviteCode.code == ...)`）
- 验证 `invite_code.bound_username == user.username`，否则返回 400 `INVITE_CODE_MISMATCH`
- 验证 `invite_code.status != "disabled"`（已失效的邀请码不能用来找回密码）
- 使用 `get_password_hash()` 对新密码进行 bcrypt 哈希
- 更新 `user.password_hash`，`await db.flush()` 提交
- 返回 `ResetPasswordResponse(user=UserInfo(...))`

**错误码：**
- 用户不存在：`HTTPException(400, detail={"code": "INVITE_CODE_MISMATCH", "message": "邀请码与用户不匹配"})`
- 邀请码不存在：同上（不区分，避免信息泄露）
- 邀请码未绑定到该用户：同上
- 邀请码已失效：同上

#### 端点（`backend/app/api/v1/endpoints/auth.py`）

```python
@router.post("/reset-password", response_model=dict)
async def reset_password_endpoint(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Reset password using username + invite code verification.

    Requires: username + the invite_code that was bound to this user during registration.
    Returns 200 with user info on success.
    Returns 400 for invite_code/user mismatch.
    """
    result = await reset_password(db, request)
    return {"data": result.model_dump()}
```

### 前端实现说明

#### TypeScript 类型（`frontend/src/types/auth.ts`）

追加：
```typescript
export interface ResetPasswordRequest {
  username: string
  invite_code: string
  new_password: string
}

export interface ResetPasswordResponse {
  user: UserInfo
}
```

#### API 调用（`frontend/src/api/auth.ts`）

追加：
```typescript
import type { ResetPasswordRequest, ResetPasswordResponse } from '@/types/auth'

export async function resetPassword(data: ResetPasswordRequest): Promise<ResetPasswordResponse> {
  const response = await apiClient.post('/auth/reset-password', data)
  return response.data.data
}
```

#### ResetPasswordPage.vue 双步骤流程

```
┌────────────────────────────────┐
│          重置密码                │
│                                │
│  ── 第一步：验证身份 ──         │
│                                │
│  用户名                          │
│  ┌────────────────────────────┐│
│  │ 请输入用户名                 ││
│  └────────────────────────────┘│
│                                │
│  邀请码（注册时绑定的）            │
│  ┌────────────────────────────┐│
│  │ 请输入 8 位邀请码            ││
│  └────────────────────────────┘│
│                                │
│  ┌────────────────────────────┐│
│  │     下一步（验证身份）       ││
│  └────────────────────────────┘│
│                                │
│  ── 第二步：设置新密码 ──       │
│                                │
│  新密码                          │
│  ┌────────────────────────────┐│
│  │ 请输入新密码（至少6位）       ││
│  └────────────────────────────┘│
│                                │
│  确认新密码                      │
│  ┌────────────────────────────┐│
│  │ 再次输入新密码               ││
│  └────────────────────────────┘│
│                                │
│  ┌────────────────────────────┐│
│  │     确认重置                ││
│  └────────────────────────────┘│
│                                │
│  已有账号？去登录                │
└────────────────────────────────┘
```

**实现要点：**

1. **步骤切换**：使用 `currentStep` ref（1 → 2），第一步验证成功后进入第二步
2. **第一步验证**：前端调用 API 后端验证 username + invite_code 匹配（实际调用 `POST /api/v1/auth/reset-password` 本身，如果返回 400 则身份不匹配；但更优方案是在前端分两步骤：第一步仅验证，第二步提交新密码。考虑到后端只有一个端点同时接收 username + invite_code + new_password，前端可先缓存请求数据，进入第二步后用户填写新密码，最终一次性提交。）

   **简化方案：** 两步全在一个表单组件中完成：
   - 第一步：输入 username + invite_code → 点击「下一步」→ 前端本地切换到密码设置面板（无需单独 API 验证）
   - 第二步：输入 new_password + confirm_password → 点击「确认重置」→ 调用 `POST /api/v1/auth/reset-password` 提交全部字段
   
   如果 API 返回错误（邀请码不匹配），回到第一步显示错误提示

3. **密码确认**：前端校验 `new_password === confirm_password`，不一致时显示「两次密码输入不一致」

4. **成功处理**：重置成功后跳转到 `/login`，可在 URL 参数中带 `/login?reset=success`，LoginPage 检测该参数并在页面顶部显示「密码重置成功，请用新密码登录」

5. **底部链接**：「已有账号？去登录」指向 `/login`

6. **错误处理**：
   - 401/400：显示「邀请码与用户不匹配」— 回退到第一步
   - 422 校验错误：显示字段级错误提示
   - 网络错误：显示「网络错误，请重试」
   - 500：显示「服务器错误，请稍后重试」

7. **视觉与交互**：
   - 步骤切换时添加过渡动画（淡入）
   - 无步骤指示器（仅两个步骤，保持简洁）
   - 错误提示显示在表单顶部（红色文字，`aria-live="polite"`）
   - 输入框变化时自动隐藏错误
   - 提交按钮 loading 态：disabled +「验证中…」或「重置中…」
   - 桌面端居中窄列（max-width: 400px），移动端全宽 + 两侧 16px padding
   - 触摸目标 ≥ 44px
   - `<label>` + `aria-live` + `aria-busy` + focus ring 无障碍

### 微文案（必须精确匹配）

| 场景 | 文案 |
|------|------|
| 身份验证失败 | 「邀请码与用户不匹配」 |
| 第一步按钮默认 | 「下一步」 |
| 第二步按钮默认 | 「确认重置」 |
| 按钮加载中（第一步） | 「验证中…」 |
| 按钮加载中（第二步） | 「重置中…」 |
| 密码不一致 | 「两次密码输入不一致」 |
| 密码重置成功 | 跳转登录页，显示「密码重置成功，请用新密码登录」 |
| 底部链接 | 「已有账号？去登录」 |
| 步骤一标题 | 「验证身份」 |
| 步骤二标题 | 「设置新密码」 |

### 文件变更清单

| 操作 | 文件 | 说明 |
|------|------|------|
| UPDATE | `backend/app/schemas/auth.py` | 追加 `ResetPasswordRequest`, `ResetPasswordResponse` |
| UPDATE | `backend/app/services/auth_service.py` | 追加 `reset_password()` 函数 |
| UPDATE | `backend/app/api/v1/endpoints/auth.py` | 追加 reset-password 端点 |
| UPDATE | `backend/tests/test_auth.py` | 追加密码重置测试 |
| UPDATE | `frontend/src/types/auth.ts` | 追加 `ResetPasswordRequest`, `ResetPasswordResponse` |
| UPDATE | `frontend/src/api/auth.ts` | 追加 `resetPassword()` 函数 |
| UPDATE | `frontend/src/pages/ResetPasswordPage.vue` | 占位 → 完整双步骤密码重置页面 |
| MAYBE | `frontend/src/pages/LoginPage.vue` | 如果支持 `?reset=success` 参数显示成功提示 |

### 无需修改（已就绪）

| 文件 | 说明 |
|------|------|
| `frontend/src/router/index.ts` | `/reset-password` 路由已定义，`guestPageNames` 包含 `reset-password` |
| `frontend/src/api/client.ts` | Axios 拦截器已完善，无需修改 |
| `frontend/src/stores/authStore.ts` | 无需修改（密码重置不涉及登录态） |
| `frontend/src/layouts/AppLayout.vue` | 无需修改 |
| `frontend/src/pages/LoginPage.vue` |「忘记密码？」链接已指向 `/reset-password` |

### 架构约束检查

- ✅ 后端三层分离：endpoints → services → models
- ✅ API 响应格式一致：`{ "data": { ... } }` / `{ "detail": { "code": "...", "message": "..." } }`
- ✅ API 路径前缀 `/api/v1/`，蛇形命名（`reset-password`）
- ✅ 无外部 UI 库 — 使用 scoped CSS + CSS 变量
- ✅ 无 WebSocket/SSE
- ✅ 无 OAuth/第三方登录 — 用户名 + 邀请码验证
- ✅ 密码 bcrypt 哈希存储
- ✅ 错误不泄露具体字段信息
- ✅ 移动端适配：触摸目标 ≥ 44px、safe-area-inset-bottom
- ✅ 无障碍：`<label>` + `aria-live` + focus ring

### 数据流

```
用户输入 (ResetPasswordPage.vue)
    │
    ├─ 第一步：填写 username + invite_code
    │    ├─ 点击「下一步」
    │    │    ├─ 前端校验：非空 + invite_code 8位
    │    │    └─ 切换到第二步（不发起 API 调用）
    │    │
    ├─ 第二步：填写 new_password + confirm_password
    │    ├─ 前端校验：非空、>=6位、两次一致
    │    ├─ 点击「确认重置」
    │    ├─ api/auth.ts → POST /api/v1/auth/reset-password
    │    │    ├─ 200 → router.push('/login?reset=success')
    │    │    ├─ 400 → 回退到第一步，显示「邀请码与用户不匹配」
    │    │    └─ catch → 显示通用错误提示
    │    └─ 输入变化 → 清除错误提示
    │
    ├─ 已登录访问 /reset-password → 路由守卫跳转首页
    │
    └─ 底部链接 → router.push('/login')
```

### References

- [Source: `epics.md` — Story 1.6 验收条件] — 全部 3 条 AC
- [Source: `epics.md` — FR-2] — 邀请码绑定用户机制（密码找回复用）
- [Source: `architecture.md` — API 响应格式] — `{"data": ...}` / `{"detail": {"code": "...", "message": "..."}}`
- [Source: `EXPERIENCE.md` — 微文案] — 登录失败「用户名或密码错误」、注册邀请码无效「邀请码无效或已被使用」
- [Source: `EXPERIENCE.md` — Surface Map] — Surface #6 密码找回 `/reset-password`，未登录用户访问
- [Source: `project-context.md` — 路由守卫] — `guestPageNames` 包含 `reset-password`
- [Source: `Story 1.5b` — LoginPage 实现] — 底部「忘记密码？」链接指向 `/reset-password`
- [Source: `Story 1.5b` — LoginPage 错误处理] — 区分 422、401、Network Error、500
- [Source: `Story 1.4` — auth_service register] — invite_code 验证模式、bcrypt 哈希模式、get_password_hash

## Dev Agent Record

### Implementation Plan

**Approach:** 后端先实现 Schema → Service → Endpoint（TDD：先写测试再实现），前端再实现 ResetPasswordPage.vue 双步骤流程和 LoginPage `?reset=success` 支持。

### Key Technical Decisions

1. **后端 reset_password flow：** 查 User → 查 InviteCode → 验证 bound_username 匹配 → 验证 status != disabled → hash 新密码 → flush → 返回。所有失败情况返回统一的 `INVITE_CODE_MISMATCH` 错误，避免信息泄露。

2. **前端双步骤 UI：** 使用 `currentStep` ref 控制步骤切换（1→2）。第一步仅前端校验后切到第二步（不发 API），第二步填完新密码后一次性提交。400 错误回退到第一步。

3. **LoginPage `?reset=success`：** ResetPasswordPage 成功重置后跳转 `/login?reset=success`，LoginPage 检测该参数并显示「密码重置成功，请用新密码登录」绿色提示条。

### Completion Notes

**Task 1:** 后端 `POST /api/v1/auth/reset-password` 完整实现：
- `ResetPasswordRequest`（username, invite_code, new_password + field_validators）
- `ResetPasswordResponse`（user: UserInfo）
- `reset_password()` service 函数：6 步流程，所有失败统一返回 `INVITE_CODE_MISMATCH`
- endpoint 遵循标准 FastAPI 模式

**Task 2:** 6 个测试用例覆盖：
- 成功重置 → 旧密码失效、新密码可用、bcrypt hash 验证
- 错误邀请码 → 400 INVITE_CODE_MISMATCH
- 不存在用户 → 400 INVITE_CODE_MISMATCH
- 不存在邀请码 → 400 INVITE_CODE_MISMATCH
- 已失效邀请码 → 400 INVITE_CODE_MISMATCH
- 过短密码 → 422

**Task 3:** 前端类型和 API：
- `frontend/src/types/auth.ts` → ResetPasswordRequest, ResetPasswordResponse
- `frontend/src/api/auth.ts` → resetPassword() 调用 `POST /api/v1/auth/reset-password`

**Task 4:** ResetPasswordPage.vue 双步骤流程：
- 步骤1：用户名 + 邀请码表单（校验：非空 + 3-20位 + 8位邀请码）
- 步骤2：新密码 + 确认密码表单（校验：非空 + >=6位 + 两次一致）
- 400/401 错误 → 回退步骤1显示「邀请码与用户不匹配」
- 成功率 → 跳转 `/login?reset=success`
- LoginPage 新增 `?reset=success` 支持显示 "密码重置成功，请用新密码登录"
- 移动端适配（全宽、44px 触摸目标、safe-area-inset-bottom）
- 无障碍（`<label>`、`aria-live`、`aria-busy`、focus ring）

**Task 5:** 端到端验证：
- ✅ `vue-tsc --noEmit` 通过（零类型错误）
- ✅ `vite build` 成功（117 modules, built in 184ms）
- ✅ 后端 43 个 pytest 全部通过（零回归，新增 6 个全部通过）
- ✅ Story 文件已更新，sprint-status 已更新

### File List

**UPDATE:**
- `backend/app/schemas/auth.py` — Added ResetPasswordRequest, ResetPasswordResponse schemas
- `backend/app/services/auth_service.py` — Added reset_password() service function and import
- `backend/app/api/v1/endpoints/auth.py` — Added POST /api/v1/auth/reset-password endpoint and import
- `backend/tests/test_auth.py` — Added TestResetPassword class with 6 test cases
- `frontend/src/types/auth.ts` — Added ResetPasswordRequest, ResetPasswordResponse interfaces
- `frontend/src/api/auth.ts` — Added resetPassword() API function and imports
- `frontend/src/pages/ResetPasswordPage.vue` — Placeholder → full 2-step password reset form
- `frontend/src/pages/LoginPage.vue` — Added `?reset=success` banner support
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — Status update to review
- `_bmad-output/implementation-artifacts/1-6-password-recovery.md` — Status update, task marking, completion notes

最近提交：

| Commit | Description |
|--------|-------------|
| 33b6fda | feat: Story 1.5b - frontend login and guest access |
| f33853d | feat: Story 1.5a - backend auth API with login, refresh, and full deps |
| 4a393c8 | feat: Story 1.4 - user registration with invite code validation |
| 1f220e2 | feat: Story 1.3 - invite code system with management UI |

Story 1.5b 已完成前端登录、路由守卫、Axios 拦截器。当前 Story 1.6 是独立的密码找回功能——需同时修改后端和前端。

### Previous Story Intelligence

**Story 1.5b 已完成（前端登录与游客访问）：**
- ✅ LoginPage.vue: 完整登录表单（校验、错误处理、redirect）
- ✅ authStore: login() action、clearAuth()
- ✅ router/index.ts: 完整路由守卫（auth guard + admin guard + guest redirect）
- ✅ AppLayout.vue: 用户区域动态切换
- ✅ client.ts: 401 刷新失败→跳转登录
- ✅ api/auth.ts: login() API 调用

**当前状态（Story 1.6 起点）：**
- ✅ `/reset-password` 路由已注册（路由守卫已包含 `reset-password` 在 `guestPageNames`）
- ✅ LoginPage 底部已有「忘记密码？」链接
- ⬜ ResetPasswordPage.vue: 纯占位文本
- ⬜ 后端无 reset-password 端点和业务逻辑
- ⬜ 前端无 reset-password API 调用和类型定义

### Completion Notes

**Task 1:** 后端实现 `POST /api/v1/auth/reset-password`：
- Schema: `ResetPasswordRequest`（username + invite_code + new_password），`ResetPasswordResponse`（user）
- Service: `reset_password()` — 验证 username → invite_code → 匹配 → hash → 更新 → 返回
- Endpoint: 标准 FastAPI 模式（与 login/register 一致）

**Task 2:** 后端测试：
- 成功重置 → 验证密码可读并用新密码登录
- 错误邀请码 → 400 `INVITE_CODE_MISMATCH`
- 不存在用户 → 400 `INVITE_CODE_MISMATCH`
- 验证密码更新后在 DB 中是 bcrypt hash

**Task 3:** 前端 API + 类型：
- `frontend/src/types/auth.ts` 追加 ResetPasswordRequest/Response
- `frontend/src/api/auth.ts` 追加 resetPassword() 函数

**Task 4:** ResetPasswordPage.vue 完整双步骤流程：
- 第一步：username + invite_code 表单
- 第二步：new_password + confirm_password 表单
- 错误回退到第一步
- 成功→跳转 `/login?reset=success`
- 移动端适配 + 无障碍

**Task 5:** 端到端验证：
- ✅ `vue-tsc --noEmit` 通过
- ✅ `vite build` 成功
- ✅ 后端 pytest 通过（零回归）
- ✅ 手动验证全流程

### File List

**UPDATE:**
- `backend/app/schemas/auth.py` — Added ResetPasswordRequest, ResetPasswordResponse schemas
- `backend/app/services/auth_service.py` — Added reset_password() service function
- `backend/app/api/v1/endpoints/auth.py` — Added POST /api/v1/auth/reset-password endpoint
- `backend/tests/test_auth.py` — Added password reset test cases
- `frontend/src/types/auth.ts` — Added ResetPasswordRequest, ResetPasswordResponse interfaces
- `frontend/src/api/auth.ts` — Added resetPassword() API function
- `frontend/src/pages/ResetPasswordPage.vue` — Placeholder → full 2-step password reset form
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — Status update

## Review Findings

### Patch Items

- [x] [Review][Patch] 前端 422 错误处理需要数组类型检查 [frontend/src/pages/ResetPasswordPage.vue:99-116] — 已修复：添加 `Array.isArray(errors)` 检查。
- [x] [Review][Patch] Step 2 密码输入缺少 trim() 处理 [frontend/src/pages/ResetPasswordPage.vue:51-70] — 已修复：step 2 validate 和 API 调用均使用 `.trim()`。

### Deferred

- [x] [Review][Defer] 缺少速率限制 [backend/app/api/v1/endpoints/auth.py] — deferred, pre-existing. 所有端点均无速率限制，非本 Story 引入的问题，属产品层面需求。
- [x] [Review][Defer] 成功消息硬编码中文 [frontend/src/pages/LoginPage.vue:15] — deferred, pre-existing. 整个应用为中文，国际化不在 v1 范围内。
- [x] [Review][Defer] API 路径硬编码 [frontend/src/api/auth.ts:7] — deferred, pre-existing. 所有 API 调用使用相同模式，统一路径前缀由 Axios 实例配置。
- [x] [Review][Defer] 缺少邀请码操作审计 [backend/app/services/auth_service.py] — deferred, pre-existing. 注册和登录等操作同样无审计日志，非本 Story 范围。
- [x] [Review][Defer] 密码列宽度对不同哈希算法限制 [backend/app/schemas/auth.py:97-101] — deferred, pre-existing. bcrypt 60 字符输出在 String(128) 列中安全。
