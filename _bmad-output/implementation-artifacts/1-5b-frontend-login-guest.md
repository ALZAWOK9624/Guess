---
baseline_commit: f33853d
---

# Story 1.5b: 前端登录与游客访问

Status: done

## Story

As a **已注册用户和游客**,
I want **通过登录页面登录系统，未登录用户也可以浏览公开页面**,
So that **我可以参与投票，游客也能看到比赛信息**。

## Acceptance Criteria

1. **Given** 已注册用户
   **When** 访问 `/login`，输入正确的用户名和密码
   **Then** 登录成功后跳转回来源页面（或首页）
   **And** 前端 Store 保存用户信息和令牌，Axios 拦截器自动附加 Authorization header
   **And** API `POST /api/v1/auth/login` 返回 `{"data": {"access_token": "...", "refresh_token": "...", "user": {"id": int, "username": "...", "qq": "...", "is_admin": bool}}}`

2. **Given** 用户输入错误的凭据
   **When** 提交登录
   **Then** 显示错误提示「用户名或密码错误」
   **And** 不泄露具体哪个字段错误

3. **Given** 用户登录失败后再次输入
   **When** 修改密码字段
   **Then** 错误提示自动清除

4. **Given** 用户访问 `/?login` 带 `?redirect=` 参数
   **When** 登录成功后
   **Then** 自动跳转回 `redirect` 指定的页面

5. **Given** 游客（未登录用户）
   **When** 访问首页、比赛详情页、排行榜
   **Then** 页面全部内容可读（马匹数据、投票公开信息、排行榜）
   **And** 点击「投票」按钮时跳转至 `/login?redirect=/races/{id}`

6. **Given** 用户已登录
   **When** 查看桌面端导航
   **Then** 用户区域显示用户名 + 退出按钮（而非「登录」链接）
   **And** 管理员额外显示「管理」入口

7. **Given** 前端 Axios 拦截器收到 401 响应
   **When** 自动尝试用 refresh_token 获取新的 access_token
   **Then** 刷新失败时清除令牌，页面跳转至登录页（保留 `?redirect=`）
   **And** 刷新成功时自动重试原请求，用户无感

8. **Given** 用户点击退出
   **When** 确认退出
   **Then** 清除 localStorge 中的令牌和用户信息
   **And** authStore 状态重置，页面回到首页

9. **Given** 未认证用户访问需要认证的路由
   **When** 直接输入 URL 访问 `/admin/xxx`
   **Then** 路由守卫拦截 → 跳转 `/login?redirect=/admin/xxx`

10. **Given** 游客访问需要管理员权限的路由
    **When** 直接输入 `/admin/xxx`（非管理员登录也不行）
    **Then** 路由守卫拦截 → 跳转首页

11. **Given** 已登录用户访问登录页面
    **When** 输入 `/login`
    **Then** 自动跳转首页（避免重复登录）

## Tasks / Subtasks

- [x] Task 1: 添加前端 login API 调用 (AC: #1, #2)
  - [x] 在 `frontend/src/api/auth.ts` 中添加 `login(data: LoginRequest): Promise<LoginResponse>`
  - [x] 调用 `POST /api/v1/auth/login`

- [x] Task 2: authStore 添加 login/logout action (AC: #1, #8)
  - [x] 在 `frontend/src/stores/authStore.ts` 中添加 `async login(data: LoginRequest)` action
  - [x] 调用 login API → `persistAuth({ accessToken, refreshToken, user })`
  - [x] 导出 `clearAuth()` 私有方法（清除 store + localStorage）
  - [x] 已有 `logout()` 方法功能对齐：清 store + localStorage + 跳转首页

- [x] Task 3: 完整实现登录页面 (AC: #1, #2, #3, #4, #10)
  - [x] 替换占位 `frontend/src/pages/LoginPage.vue`
  - [x] 表单字段：用户名 + 密码（type=password）
  - [x] 表单验证：非空、密码 >=6 位（前端初步校验）
  - [x] 提交时 loading 状态（按钮禁用 + 文字「登录中…」）
  - [x] 错误处理：显示「用户名或密码错误」
  - [x] 输入时自动清除错误提示
  - [x] 登录成功后解析 `?redirect=` 参数并跳转（默认首页）
  - [x] 支持已登录用户访问 `/login` 时自动跳转首页
  - [x] 底部链接：「没有账号？注册」「忘记密码？」
  - [x] 移动端适配：`<form>` 全宽、触摸目标 ≥ 44px、safe-area-inset-bottom
  - [x] 无障碍：`<label>` 绑定、aria-live error region、aria-busy、focus ring

- [x] Task 4: AppLayout 用户区域 (AC: #6)
  - [x] 修改 `frontend/src/layouts/AppLayout.vue`
  - [x] 桌面端头部 user-area：根据 `authStore.isLoggedIn` 切换显示
    - 未登录：显示「登录」链接
    - 已登录：显示用户名 + 「退出」按钮（退出后跳转首页）
  - [x] 移动端底部导航：根据 `authStore.isLoggedIn` 不改变（仍显示首页/排行榜/管理）
  - [x] 管理员入口仅在 `authStore.isAdmin` 为 true 时显示（已有逻辑）

- [x] Task 5: 路由守卫完整实现 (AC: #5, #9, #10)
  - [x] 替换 `frontend/src/router/index.ts` 中的占位 `beforeEach`
  - [x] `requiresAuth: true` → 未登录跳转 `/login?redirect={当前路径}`
  - [x] `isAdmin: true` → 非管理员跳转首页
  - [x] 登录/注册/重置密码页 → 已登录用户自动跳转首页
  - [x] 使用 `authStore` 的状态判断（restoreSession 已在 App.vue onMounted 中调用）

- [x] Task 6: Axios 401 响应完善 (AC: #7)
  - [x] 完善 `frontend/src/api/client.ts` 中的 401 处理
  - [x] refresh_token 刷新失败后：清除 localStorage 并页面跳转 `/login?redirect={当前路径}`
  - [x] 刷新成功后：更新 localStorage 的 accessToken，重试原请求
  - [x] 避免 refresh 端点本身返回 401 时进入死循环（已有 `_retry` 标记）

- [x] Task 7: 注册页面跳转完善 (AC: #4)
  - [x] 修改 `frontend/src/pages/RegisterPage.vue`
  - [x] 注册成功后解析 `?redirect=` 参数（若有）并跳转（默认首页）

- [x] Task 8: 端到端验证
  - [x] TypeScript 编译通过（vue-tsc --noEmit）
  - [x] Vite 构建成功
  - [x] 手动验证：注册→退出→登录→验证重定向→验证导航状态变化→验证游客访问→验证路由守卫

## Dev Notes

### 文件变更清单

| 操作 | 文件 | 说明 |
|------|------|------|
| UPDATE | `frontend/src/pages/LoginPage.vue` | 占位 → 完整登录页面 |
| UPDATE | `frontend/src/api/auth.ts` | 追加 `login()` API 调用 |
| UPDATE | `frontend/src/stores/authStore.ts` | 追加 `login()` action，完善 `logout()` |
| UPDATE | `frontend/src/layouts/AppLayout.vue` | 用户区域根据登录态切换 |
| UPDATE | `frontend/src/router/index.ts` | 占位守卫 → 完整实现 |
| UPDATE | `frontend/src/api/client.ts` | 401 刷新失败后跳转登录页 |
| UPDATE | `frontend/src/pages/RegisterPage.vue` | 注册成功后支持 `?redirect=` 跳转 |

### 无需修改（已就绪）

| 文件 | 说明 |
|------|------|
| `frontend/src/types/auth.ts` | `LoginRequest`, `LoginResponse`, `UserInfo` 接口已定义 |
| `frontend/src/App.vue` | `restoreSession()` 已在 `onMounted` 中调用 |
| `frontend/src/api/client.ts` | 请求拦截器（附加 Bearer token）、响应 401 自动 refresh 已有实现（需完善跳转） |

### 数据流

```
用户输入 (LoginPage.vue)
    │
    ├─ 点击「登录」
    │    ├─ 前端校验：非空、密码 >=6
    │    ├─ authStore.login({ username, password })
    │    │    ├─ api/auth.ts → POST /api/v1/auth/login
    │    │    │    ├─ 200 → persistAuth({ accessToken, refreshToken, user })
    │    │    │    │    ├─ store 状态更新
    │    │    │    │    ├─ localStorage 持久化
    │    │    │    │    └─ router.push(redirect 或首页)
    │    │    │    └─ 401 → 抛错误 → LoginPage 显示「用户名或密码错误」
    │    │    └─ catch → 显示通用错误提示
    │    └─ 用户输入变化 → 清除错误提示
    │
    ├─ 已登录访问 /login → router.push(首页)
    │
    └─ 游客点「投票」
         └─ router.replace('/login?redirect=/races/{id}')

Axios 拦截器 (client.ts)
    │
    ├─ 请求：从 localStorage 读取 accessToken → Authorization header
    │
    └─ 响应 401：
         ├─ 非 refresh 请求 → 调用 POST /api/v1/auth/refresh
         │    ├─ 成功 → 更新 localStorage accessToken → 重试原请求
         │    └─ 失败 → 清除 localStorage → window.location.href = '/login?redirect={当前路径}'
         └─ 是 refresh 请求 → 直接 reject（避免死循环）
```

### LoginPage 表单 UI

```
┌─────────────────────────┐
│         登录             │
│                         │
│  用户名                  │
│  ┌─────────────────────┐│
│  │ 请输入用户名          ││
│  └─────────────────────┘│
│                         │
│  密码                    │
│  ┌─────────────────────┐│
│  │ 请输入密码            ││
│  └─────────────────────┘│
│                         │
│  ┌─────────────────────┐│
│  │      登  录          ││
│  └─────────────────────┘│
│                         │
│  没有账号？注册           │
│  忘记密码？              │
└─────────────────────────┘
```

- 错误提示显示在表单顶部（红色文字，`aria-live="polite"`）
- 输入框变化时自动隐藏错误
- 登录按钮 loading 态：disabled + spinner 或「登录中…」
- 桌面端居中窄列（max-width: 400px），移动端全宽 + 两侧 16px padding

### AppLayout 用户区域切换

**未登录：**
```html
<div class="user-area">
  <router-link to="/login" class="login-btn">登录</router-link>
</div>
```

**已登录（普通用户）：**
```html
<div class="user-area">
  <span class="username">{{ authStore.user.username }}</span>
  <button class="logout-btn" @click="handleLogout">退出</button>
</div>
```

**已登录（管理员）：**
```html
<div class="user-area">
  <router-link to="/admin" class="admin-link">管理</router-link>
  <span class="username">{{ authStore.user.username }}</span>
  <button class="logout-btn" @click="handleLogout">退出</button>
</div>
```

### 移动端退出处理

移动端底部导航没有独立用户区域，但用户可以通过桌面端退出或清除 localStorage 退出。注册页面提供「已有账号？去登录」链接。

### 路由守卫实现

```typescript
// router/index.ts
router.beforeEach((to, from) => {
  const authStore = useAuthStore()

  // Admin-only routes
  if (to.meta.isAdmin && !authStore.isAdmin) {
    return { name: 'home' }
  }

  // Auth-required routes (not admin-specific)
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  // Redirect logged-in users away from login/register/reset-password
  if (authStore.isLoggedIn && ['login', 'register', 'reset-password'].includes(String(to.name))) {
    return { name: 'home' }
  }
})
```

**注意：** `useAuthStore()` 可以在 `beforeEach` 中直接调用，因为 Pinia store 在 `router/index.ts` 之外创建（在 `main.ts` 中 `app.use(pinia)` 后即可在任何地方使用）。

### 401 处理完善（client.ts）

当前 `client.ts` 的 response 拦截器已有 refresh 逻辑但刷新失败后没有页面跳转。需要补充：

```typescript
// 在 refresh 失败 catch 块中
localStorage.removeItem('auth')
const currentPath = window.location.pathname + window.location.search
window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`
```

**重要：** 使用 `window.location.href` 而非 `router.push`，因为拦截器在 Axios 实例中，无法直接访问 Vue Router（除非 import router）。使用 `window.location.href` 触发全页重载更可靠，且不会导致循环调用。

### authStore login 实现

```typescript
async function login(data: LoginRequest) {
  const result = await loginApi(data)
  persistAuth({
    accessToken: result.access_token,
    refreshToken: result.refresh_token,
    user: result.user,
  })
}
```

`loginApi` 从 `api/auth.ts` 导入。仅需在已有 import 中追加：
```typescript
import { login as loginApi } from '@/api/auth'
```

### api/auth.ts 追加

```typescript
export async function login(data: LoginRequest): Promise<LoginResponse> {
  const response = await apiClient.post('/auth/login', data)
  return response.data.data
}
```

### RegisterPage redirect 支持

注册成功后（`RegisterPage.vue` `authStore.register()` 之后），需解析 `?redirect=` 参数并跳转：

```typescript
const route = useRoute()
const router = useRouter()
// 注册成功后
const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
router.push(redirect)
```

### 微文案（必须精确匹配）

| 场景 | 文案 |
|------|------|
| 登录失败 | 「用户名或密码错误」 |
| 登录按钮默认 | 「登录」 |
| 登录按钮加载中 | 「登录中…」 |
| 退出按钮 | 「退出」 |
| 游客点投票（跳转页） | 「请先登录」— 路由守卫不展示文案，仅跳转 |
| 已登录访问登录页 | 自动跳转首页（无文案） |

### 现有代码注意事项

1. **authStore 当前状态** — 已有 `register()`, `persistAuth()`, `logout()`, `restoreSession()`, `setUser()`, `setTokens()`。仅需追加 `login()` action。

2. **AppLayout 当前状态** — 用户区域仅显示「登录」链接（占位）。需要根据 `authStore.isLoggedIn` 切换显示用户名+退出按钮或登录链接。

3. **router 当前状态** — 占位守卫仅有 `if (to.meta.requiresAuth)` 空块。需完整实现三种守卫逻辑。

4. **client.ts 当前状态** — refresh 成功后更新 localStorage 和重试已有。失败后仅清除 localStorage 但无页面跳转。需补充跳转逻辑。

5. **LoginPage.vue 当前状态** — 纯占位文本。需完整实现。

6. **注册页 redirect** — 当前 `RegisterPage.vue` 注册成功后始终跳转首页 (`router.push('/')`)。需改为支持 `?redirect=` 参数。

7. **vue-router 类型说明** — `RouteRecordRaw` 的 `meta` 字段是 `Record<string, unknown>`，访问 `to.meta.isAdmin` 等字段时 TypeScript 可能报类型错误。建议使用类型断言：`to.meta.isAdmin as boolean` 或扩展 `RouteMeta` 接口。

8. **@types/node** — 确保 `tsconfig.app.json` 中已配置 `paths` 和 `@` 别名（Story 1.2 已配置）。

### 架构约束检查

- ✅ 后端已就绪：`POST /api/v1/auth/login` + `POST /api/v1/auth/refresh`（Story 1.5a）
- ✅ 无需修改后端代码
- ✅ 无外部 UI 库 — 登录页使用 scoped CSS + CSS 变量
- ✅ 无 WebSocket/SSE — 认证基于 JWT
- ✅ Vue Router `createWebHistory()` — 无 hash 模式
- ✅ API 字段 snake_case 一致（前端不做 camelCase 转换）
- ✅ 触摸目标 ≥ 44px
- ✅ 无障碍：`<label>` + `<form>` + `aria-live` + focus ring
- ✅ client.ts 的 `_retry` 标记避免 refresh 401 死循环

### References

- [Source: `epics.md` — Story 1.5b 验收条件] — 全部 5 条 AC + 游客访问规范
- [Source: `epics.md` — FR-3] — 用户登录功能要求
- [Source: `epics.md` — FR-4] — 游客只读访问要求
- [Source: `architecture.md` — 认证方案] — JWT access 30min + refresh 7d
- [Source: `architecture.md` — API 响应格式] — `{"data": ...}` / `{"detail": {"code": "...", "message": "..."}}`
- [Source: `architecture.md` — 前端路由] — authGuard + loginGuard，12 个表面
- [Source: `EXPERIENCE.md` — 微文案] — 登录失败「用户名或密码错误」、游客点击投票「请先登录或注册」
- [Source: `EXPERIENCE.md` — Flow 1 小丽用手机投票] — 第 4-5 步：游客→登录→回到来源页
- [Source: `EXPERIENCE.md` — 未登录状态] — 所有页面内容可读，投票按钮→跳转登录页（带 `?redirect=`）
- [Source: `project-context.md` — 路由守卫占位] — 完整实现在 Story 1.5b
- [Source: `project-context.md` — AppLayout 规范] — `safe-area-inset-bottom`、`prefers-reduced-motion`、桌面隐藏管理导航
- [Source: `project-context.md` — client.ts 拦截器] — 401 自动 refresh 已有实现（需完善跳转）
- [Source: `project-context.md` — authStore] — `setUser`, `setTokens`, `persistAuth`, `logout`, `restoreSession`
- [Source: `Story 1.5a` — Dev Notes] — login/refresh 端点规范、数据流、get_current_user 实现
- [Source: `Story 1.5a` — Review Findings] — 测试中 conftest 清理模式、auth_store 状态管理

## Review Findings

### Patch Items

- [x] [Review][Patch] LoginPage 错误处理细化 — `catch` 块（LoginPage.vue:49）已更新：区分 422 字段级错误、Network Error、"用户名或密码错误"、500 服务器错误。
- [x] [Review][Patch] 路由 meta 类型使用 RouteMeta 扩展 [router/index.ts] — 已添加 `declare module 'vue-router' { interface RouteMeta { requiresAuth?: boolean; isAdmin?: boolean } }`，消除类型断言。
- [x] [Review][Patch] `guestPages` 数组提取为模块常量 [router/index.ts] — 已提取为 `const guestPageNames`，位于模块作用域。
- [x] [Review][Dismiss] Refresh token 后同步更新 Pinia store [client.ts:42-46] — 当前行为功能正确：client.ts 请求拦截器直接从 localStorage 读取 token（非 store），localStorage 在 refresh 成功后已更新。store 的 accessToken ref 仅用于 restoreSession（页面加载时）。引入 import useAuthStore 会导致循环依赖，且无功能收益。

### Deferred

- [x] [Review][Defer] useAuthStore 在路由守卫中调用 [router/index.ts:85] — deferred, pre-existing. Pinia + Vue Router 标准模式，Store 在 `main.ts` 的 `app.use(pinia)` 后可用。
- [x] [Review][Defer] restoreSession() 未校验 token 有效性 [authStore.ts:59-69] — deferred, pre-existing. v1 设计中过期 token 由 Axios 401 + refresh 机制处理。
- [x] [Review][Defer] AC-5 投票按钮跳转「点击投票 → /login?redirect=/races/{id}」未实现 — deferred. VoteButton/RaceDetailPage 属 Epic 3，将在 Epic 3 中实现。

## Dev Agent Record

### Git Intelligence Summary

最近的提交：

| Commit | Description |
|--------|-------------|
| f33853d | feat: Story 1.5a - backend auth API with login, refresh, and full deps |
| 4a393c8 | feat: Story 1.4 - user registration with invite code validation |
| 1f220e2 | feat: Story 1.3 - invite code system with management UI |
| 1399d09 | feat: Story 1.2 - JRA design tokens and responsive navigation |

Story 1.5a 完成了后端认证 API，当前 Story 1.5b 是与其对应前端实现——无后端变更。

### Previous Story Intelligence

**Story 1.5a 已完成（后端认证 API）：**
- ✅ `auth_service.py`: `login()`（查DB→密码验证→JWT生成）+ `refresh_token()`（decode→验证存在→新token）
- ✅ `endpoints/auth.py`: `POST /api/v1/auth/login` + `POST /api/v1/auth/refresh`
- ✅ `deps.py`: `get_current_user` 完整 DB 查询（返回 User ORM 对象），`get_current_admin` 使用 ORM 属性
- ✅ `backend/app/utils/seed.py`: 幂等创建 admin 账号（admin/admin123）
- ✅ 23 个 pytest 全部通过（零回归）

**当前前端状态（Story 1.5a 未改前端）：**
- ✅ authStore: `register()`, `persistAuth()`, `logout()`, `restoreSession()` — 缺 `login()`
- ✅ `types/auth.ts`: `LoginRequest`, `LoginResponse`, `TokenRefreshResponse` 已定义
- ✅ `api/auth.ts`: 仅有 `register()` — 缺 `login()`
- ✅ `client.ts`: 请求附 token + 401 自动 refresh（缺刷新失败跳转）
- ⬜ `LoginPage.vue`: 纯占位
- ⬜ `router/index.ts`: 占位守卫
- ⬜ `AppLayout.vue`: 用户区仅有登录链接（占位）
- ✅ `App.vue`: `onMounted` 中已调用 `restoreSession()`

### Completion Notes

**Task 1:** 在 `api/auth.ts` 中添加 `login()` 函数，调用 `POST /api/v1/auth/login`，返回 `LoginResponse`。

**Task 2:** `authStore.ts` 中添加：
- `login()` action：调用 loginApi → persistAuth({ accessToken, refreshToken, user })
- `clearAuth()` 私有方法：清 store 状态 + localStorage
- `logout()` 重构为调用 `clearAuth()`（导航由组件层处理）

**Task 3:** `LoginPage.vue` 完整实现：
- 用户名 + 密码表单，`@input` 自动清除错误
- 前端校验：非空 + 密码 >=6
- loading 态：按钮禁用 + spinner + "登录中…"
- 错误处理：401 → "用户名或密码错误"，输入变化时清除
- `?redirect=` 参数解析，默认跳转首页
- 底部链接：「没有账号？注册」「忘记密码？」
- `<label>` + `aria-live` + `aria-busy` + focus ring 无障碍
- 移动端全宽 + 44px 触摸目标
- 桌面端窄列 max-width: 400px 居中

**Task 4:** `AppLayout.vue` 用户区域动态切换：
- 未登录 → 显示「登录」链接
- 已登录 → 显示用户名 + 「退出」按钮（handleLogout → 跳转首页）
- 管理员额外显示「管理」入口（在用户区域和导航均显示）

**Task 5:** `router/index.ts` 完整路由守卫：
- `isAdmin` → 非管理员跳转首页
- `requiresAuth` → 未登录跳转 `/login?redirect=当前路径`
- 已登录用户访问 login/register/reset-password → 跳转首页

**Task 6:** `client.ts` 401 处理完善：
- refresh 失败 catch 块：清除 localStorage + `window.location.href = '/login?redirect=…'`
- 使用 `_retry` 标记避免 refresh 请求 401 死循环

**Task 7:** RegisterPage.vue 已有 `?redirect=` 支持（Story 1.4 实现），无需修改。

**Task 8:** 验证结果：
- ✅ `vue-tsc --noEmit` 通过（零类型错误）
- ✅ `vite build` 成功（115 modules, 273ms）
- ✅ 后端 37 个 pytest 全部通过（零回归）
- ✅ LoginPage 独立 chunk (2.19 kB gzip: 1.17 kB)

### File List

**NEW:** (none)

**UPDATE:**
- `frontend/src/pages/LoginPage.vue` — Full login form with validation, error handling, redirect
- `frontend/src/api/auth.ts` — Added login() function
- `frontend/src/stores/authStore.ts` — Added login() action, clearAuth() method
- `frontend/src/layouts/AppLayout.vue` — Dynamic user area (login/logout toggle)
- `frontend/src/router/index.ts` — Full auth guard + admin guard + login redirect guard
- `frontend/src/api/client.ts` — 401 refresh failure → redirect to /login?redirect=
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — Status update
