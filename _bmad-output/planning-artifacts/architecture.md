---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
workflowType: 'architecture'
status: 'complete'
completedAt: '2026-06-09'
inputDocuments:
  - briefs/brief-guess-2026-06-08/brief.md
  - prds/prd-guess-2026-06-09/prd.md
  - prds/prd-guess-2026-06-09/reconcile-brief.md
  - prds/prd-guess-2026-06-09/review-rubric.md
  - ux-designs/ux-guess-2026-06-09/DESIGN.md
  - ux-designs/ux-guess-2026-06-09/EXPERIENCE.md
workflowType: 'architecture'
project_name: 'guess'
user_name: 'tkd'
date: '2026-06-09'
---

# Architecture Decision Document — Guess

_本文档通过逐步发现的方式协作构建。随着我们逐个完成架构决策，各章节将逐步填充。_

## Project Context Analysis

### Requirements Overview

**26 个功能需求**，分布在 7 个模块：

| 模块 | FR 范围 | 核心职责 |
|------|---------|---------|
| 用户认证与邀请制注册 | FR-1 ~ FR-4 | 邀请码生成/绑定、注册、登录、游客只读 |
| 马匹库管理 | FR-5 ~ FR-9 | 10 属性马匹库、手动编辑/自动更新框架、赛事快照 |
| 比赛管理与等级规则 | FR-10 ~ FR-15 | 比赛 CRUD、4 种积分规则引擎（G1/G2/2岁G1/自定义） |
| 投票 | FR-16 ~ FR-18 | 一马投票、锁定前可改、锁定后冻结 |
| 结果录入与结算 | FR-19 ~ FR-22 | 拖拽排序录入、自动结算、修改后重算 |
| 排行榜与公开查看 | FR-23 ~ FR-25 | 全局排名、详情公开、投票实时展示 |
| 响应式界面 | FR-26 | 320px 起自适应、移动端 3 次点击内完成核心操作 |

**Non-Functional Requirements:**

- **性能**：100 用户、50+ 场比赛时页面响应 ≤ 2s（SM-5）
- **积分零差异**：系统结算与手工计算 100% 一致（SM-2）
- **实时性**：投票展示实时更新（FR-25），结算后排行榜即时刷新（FR-23）
- **移动优先**：最小宽度 320px，核心操作 ≤ 3 次点击（FR-26）
- **无障碍**：语义 HTML、44px 触摸目标、4.5:1 对比度、颜色+文字双重编码
- **容错**：结果修改→撤销旧积分→重算、网络错误乐观更新+后台重试

### Technical Constraints & Dependencies

- **技术栈已锁定**：Vue 3 + FastAPI + PostgreSQL（来自 Product Brief）
- **无外部 API**：赛马数据全部手动录入，不对接外部数据源
- **无第三方 OAuth**：仅用户名+密码+邀请码认证
- **单管理账号**（v1 不允许多管理员）
- **单色亮色模式**：竞马绿 + 冠军金，无暗色模式
- **无实时通信需求**：无 WebSocket/SSE 推送（投票刷新通过 API 轮询或乐观更新即可）

### Cross-Cutting Concerns

| 关注点 | 影响范围 |
|--------|---------|
| 积分规则引擎 | 核心业务逻辑——必须独立、可测试、零差错的纯函数模块 |
| 比赛状态机 | `投票中 → 已锁定 → 已结算`，每个状态转换有严格约束 |
| 马匹数据生命周期 | 全局库 + 比赛快照，手动编辑优先于自动更新 |
| 认证与权限 | 三种角色：游客（只读）、用户（投票）、管理员（管理） |
| 数据一致性 | 结果修改需全链路撤销重算，积分变更可追溯 |
| 移动端触摸交互 | 拖拽排序需区分触摸/鼠标，长按 300ms 激活 |

### Scale & Complexity

| 维度 | 评估 |
|------|------|
| 复杂性等级 | **中等**——非简单 CRUD，但亦非企业级。核心复杂度集中在积分引擎和状态机 |
| 技术领域 | 全栈 Web 应用（Vue3 SPA + FastAPI REST + PostgreSQL） |
| 预估架构组件 | 8-10 个：Auth、Horse Library、Race Management、Voting、Scoring Engine、Result Entry、Leaderboard、Admin Dashboard |

## Starter Template Evaluation

### Primary Technology Domain

全栈 Web 应用 — Vue 3 SPA + FastAPI REST + PostgreSQL，基于 Product Brief 锁定的技术栈。

### 方案选择：手动搭建（自制 Monorepo 结构）

**选择理由：**
- 前端需要使用定制 JRA 美学组件系统，预置 UI 库（如 Element Plus）额外负担大于收益
- 项目规模小（~100 用户），手动搭建的基础设施成本可控
- 后端采用行业标准模式，无需全栈模板中的繁重框架

### 项目初始化结构

```
guess/
├── frontend/                  # Vue 3 + Vite 前端
│   ├── src/
│   │   ├── assets/            # 样式、图片、字体
│   │   ├── components/        # 全局组件（RaceCard, VoteButton 等）
│   │   ├── composables/       # 组合式函数
│   │   ├── layouts/           # 布局组件（移动端/桌面端）
│   │   ├── pages/             # 页面组件
│   │   ├── router/            # Vue Router 配置
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── api/               # API 调用层（Axios）
│   │   ├── types/             # TypeScript 类型定义
│   │   ├── App.vue
│   │   └── main.ts
│   ├── public/
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   └── pnpm-lock.yaml
│
├── backend/                   # FastAPI 后端
│   ├── app/
│   │   ├── api/               # API 路由层
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/ # 各模块端点
│   │   │   │   └── __init__.py
│   │   │   └── deps.py        # 依赖注入（DB session, current user）
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 配置管理（Pydantic Settings）
│   │   │   ├── security.py    # JWT 认证、密码哈希
│   │   │   └── database.py    # 数据库引擎与会话
│   │   ├── models/            # SQLAlchemy 数据模型
│   │   ├── schemas/           # Pydantic 请求/响应 schemas
│   │   ├── services/          # 业务逻辑层（含积分规则引擎）
│   │   ├── utils/             # 工具函数
│   │   └── main.py            # FastAPI 应用入口
│   ├── alembic/               # 数据库迁移
│   ├── tests/                 # Pytest 测试
│   ├── pyproject.toml
│   ├── alembic.ini
│   └── requirements.txt / uv.lock
│
├── docker-compose.yml         # 本地开发编排（PostgreSQL + API + 前端）
├── .env.example
├── .gitignore
└── README.md
```

### 前端初始化命令

```bash
npm create vite@latest frontend -- --template vue-ts
cd frontend
pnpm install
pnpm add vue-router pinia axios
pnpm add -D @types/node
```

### 前端架构决策

| 决策项 | 选择 | 理由 |
|--------|------|------|
| 构建工具 | Vite | Vue 3 官方推荐，HMR 极速 |
| 语言 | TypeScript | 类型安全，减少 runtime 错误 |
| 状态管理 | Pinia | Vue 3 官方推荐，轻量，TypeScript 友好 |
| 路由 | Vue Router 4 | Vue 3 官方路由方案 |
| HTTP 客户端 | Axios | 拦截器、请求取消、浏览器兼容性 |
| UI 组件 | 自定义组件 | JRA 精密美学，无需 UI 库 |
| 样式方案 | CSS Variables + scoped CSS | DESIGN.md 的色板/间距/圆角变量直接映射 |

### 后端架构决策

| 决策项 | 选择 | 理由 |
|--------|------|------|
| Web 框架 | FastAPI | 异步原生，自动 API 文档，Pydantic 集成 |
| ORM | SQLAlchemy 2.0 async | 成熟、异步支持、迁移生态 |
| 迁移 | Alembic | SQLAlchemy 官方迁移工具 |
| 配置 | Pydantic Settings | 类型安全的环境变量管理 |
| 认证 | JWT | 无状态、简单、前后端分离适用 |
| 密码哈希 | passlib[bcrypt] | 行业标准 |
| 测试 | Pytest + httpx | FastAPI 推荐的 TestClient 方案 |

## Core Architectural Decisions

### Data Architecture

| 决策 | 选择 | 说明 |
|------|------|------|
| ORM 模式 | SQLAlchemy 2.0 async 声明式模型 | `mapped_column` 类型注解 |
| 迁移 | Alembic 自动生成 + 手动审查 | 标准模式 |
| 连接池 | FastAPI async session，每请求独立会话 | — |
| 缓存 | **v1 不需要** Redis/缓存层 | 100 用户数据量直接查库足够 |
| 本地数据库 | Docker Compose 仅运行 PostgreSQL 16 | 前后端本地开发 |

### Authentication & Security

| 决策 | 选择 |
|------|------|
| 认证方案 | JWT access token（30min）+ refresh token（7天） |
| 密码哈希 | passlib[bcrypt] |
| CORS | 仅允许前端域名 |
| API 限流 | v1 暂不实现 |
| HTTPS | 部署层处理（反向代理） |

### API & Communication Patterns

| 决策 | 选择 |
|------|------|
| 设计风格 | RESTful |
| 版本化 | URL 前缀 `/api/v1/` |
| 文档 | FastAPI 自动生成 Swagger UI + ReDoc |
| 错误格式 | `{ "detail": { "code": "string", "message": "string" } }` |
| 资源命名 | 复数形式（`/races`、`/horses`） |

### Frontend Architecture

| 决策 | 选择 |
|------|------|
| 组件粒度 | 原子 → 分子 → 页面 |
| 通信 | Props down / Events up + Pinia |
| 路由 | Vue Router 4，12 个表面，authGuard + loginGuard |
| 样式 | CSS 自定义属性映射 JRA 设计系统，scoped CSS |
| 性能 | 路由懒加载（Vite 自动分割），无虚拟滚动需求 |

### Infrastructure & Deployment

| 决策 | 选择 |
|------|------|
| 本地开发 | Docker Compose 仅 PostgreSQL，前后端本地 `--reload` |
| 生产部署 | VPS + Docker Compose（Nginx + API + DB） |
| CI | GitHub Actions 自动运行测试 |
| CD | 手动 `git pull && docker compose up --build -d` |
| 配置管理 | `.env` + Pydantic Settings |

## Implementation Patterns & Consistency Rules

### Naming Patterns

**Database Naming（Python/SQLAlchemy）：**
- 表名：**`snake_case` 复数** — `races`、`horses`、`votes`、`users`、`invite_codes`
- 列名：**`snake_case`** — `user_id`、`race_name`、`created_at`
- 外键：**`{table}_id`** 直接命名
- 索引：**Alembic 自动命名**

**API Naming（REST 端点）：**
- 端点：**复数 REST 风格** — `GET /api/v1/races`、`POST /api/v1/races/{id}/lock`
- 查询参数：**`snake_case`** — `?horse_name=xxx`
- 请求体/响应体字段：**`snake_case`**（FastAPI 默认），前后端一致，不做 camelCase 转换

**Code Naming（TypeScript/Vue）：**
- 组件文件：**PascalCase** — `RaceCard.vue`、`VoteButton.vue`
- 非组件文件：**camelCase** — `useAuth.ts`、`apiClient.ts`
- 函数/变量：**camelCase** — `getUserData()`、`currentUser`
- Pinia Store：**`use{Name}Store`** — `useRaceStore`、`useAuthStore`
- CSS 变量：**kebab-case** — `--color-primary`、`--spacing-4`

### API Response Formats

**统一响应结构：**
- 成功（单个）：`{ "data": { ... } }`
- 成功（列表）：`{ "data": [ ... ] }`
- 成功（分页）：`{ "data": [ ... ], "total": N, "page": N, "per_page": N }`
- 错误：`{ "detail": { "code": "ERROR_CODE", "message": "描述" } }`

**HTTP 状态码映射：**
- 200：GET 成功
- 201：POST 创建成功
- 400：参数错误
- 401：未认证
- 403：无权限
- 404：资源不存在
- 409：冲突
- 422：校验失败
- 500：服务端错误

**日期格式：** ISO 8601 字符串（`2026-06-09T15:00:00Z`）
**空值处理：** 用 `null`，不用空字符串或省略字段

### Structure Patterns

**后端（FastAPI）分层：**
- `endpoints/` → 仅 HTTP 编排，不含业务逻辑
- `services/` → 业务逻辑层
- `models/` → SQLAlchemy 数据模型
- `schemas/` → Pydantic 请求/响应 schema
- **`scoring_engine.py`** → 纯函数模块，零外部依赖，独立测试

**前端（Vue 3）分层：**
- `pages/` → 页面组件，按路由命名
- `components/` → 可复用 UI 组件
- `composables/` → 组合式函数（useAuth, useVote）
- `stores/` → Pinia 状态管理
- `api/` → API 调用统一封装
- `types/` → TypeScript 类型定义

### Process Patterns

| 场景 | 约定 |
|------|------|
| 加载状态 | `idle → loading → success / error` 枚举驱动 |
| 错误处理 | 后端全局异常处理器，前端 Axios 拦截器统一处理 401/500 |
| 乐观更新 | 投票提交/修改使用乐观更新，失败回滚+提示 |
| 状态转换 | POST `{resource}/{id}/{action}` 模式（如 `/races/{id}/lock`） |

## Project Structure & Boundaries

### 完整项目目录结构

```
guess/
│
├── .github/
│   └── workflows/
│       └── ci.yml                       # GitHub Actions CI
│
├── backend/
│   ├── alembic/
│   │   ├── versions/                    # 迁移版本文件
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── auth.py          # FR-1~4: 注册/登录/找回密码
│   │   │   │   │   ├── races.py         # FR-10~11: 比赛 CRUD + 锁定
│   │   │   │   │   ├── horses.py        # FR-5~9: 马匹库管理
│   │   │   │   │   ├── votes.py         # FR-16~18: 投票
│   │   │   │   │   ├── results.py       # FR-19~22: 结果录入/结算
│   │   │   │   │   ├── leaderboard.py   # FR-23: 排行榜
│   │   │   │   │   └── admin.py         # FR-1: 邀请码管理
│   │   │   │   └── __init__.py
│   │   │   └── deps.py                  # 依赖注入（DB session, current user）
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py                # Pydantic Settings 配置管理
│   │   │   ├── security.py              # JWT 生成/验证、密码哈希
│   │   │   ├── database.py              # 异步引擎、session 工厂
│   │   │   └── exceptions.py            # 自定义异常 + 全局异常处理器
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py                  # User 模型（含 admin 标记）
│   │   │   ├── race.py                  # Race + RaceHorse 关联模型
│   │   │   ├── horse.py                 # Horse 模型（10 属性）
│   │   │   ├── vote.py                  # Vote 模型
│   │   │   └── invite_code.py           # InviteCode 模型
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                  # 注册/登录 request+response
│   │   │   ├── race.py                  # 比赛相关 schema
│   │   │   ├── horse.py                 # 马匹相关 schema
│   │   │   ├── vote.py                  # 投票相关 schema
│   │   │   ├── result.py                # 结果录入 schema
│   │   │   └── leaderboard.py           # 排行榜 schema
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py          # 注册/登录/令牌管理
│   │   │   ├── race_service.py          # 比赛 CRUD 业务逻辑
│   │   │   ├── horse_service.py         # 马匹库业务逻辑
│   │   │   ├── vote_service.py          # 投票业务逻辑
│   │   │   ├── result_service.py        # 结果录入 + 结算编排
│   │   │   ├── scoring_engine.py        # ⭐ 积分规则引擎（纯函数）
│   │   │   └── leaderboard_service.py   # 排行榜查询
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   └── invite_code.py           # 邀请码生成工具
│   │   └── main.py                      # FastAPI 应用入口
│   ├── tests/
│   │   ├── conftest.py                  # pytest fixtures（DB session, client）
│   │   ├── test_scoring_engine.py       # 积分规则引擎单元测试 ⭐
│   │   ├── test_auth.py
│   │   ├── test_races.py
│   │   ├── test_votes.py
│   │   ├── test_results.py
│   │   └── test_leaderboard.py
│   ├── alembic.ini
│   ├── pyproject.toml                   # Python 项目配置
│   └── README.md
│
├── frontend/
│   ├── public/
│   │   └── favicon.ico
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.ts                # Axios 实例 + 拦截器
│   │   │   ├── auth.ts                  # 认证 API
│   │   │   ├── races.ts                 # 比赛 API
│   │   │   ├── horses.ts                # 马匹 API
│   │   │   ├── votes.ts                 # 投票 API
│   │   │   └── leaderboard.ts           # 排行榜 API
│   │   ├── assets/
│   │   │   └── styles/
│   │   │       ├── variables.css        # CSS 自定义属性（JRA 设计令牌）
│   │   │       ├── base.css             # 全局样式、reset
│   │   │       └── utilities.css        # 工具类
│   │   ├── components/
│   │   │   ├── RaceCard.vue             # 比赛卡片（首页列表）
│   │   │   ├── GradeBadge.vue           # 等级徽章（G1/G2/2岁G1/自定义）
│   │   │   ├── StatusBadge.vue          # 状态胶囊（投票中/已锁定/已结算）
│   │   │   ├── VoteButton.vue           # 投票按钮（金色/确认态）
│   │   │   ├── HorseSelectCard.vue      # 马匹选择卡片
│   │   │   ├── VotingDetail.vue         # 投票明细展示
│   │   │   ├── LeaderboardRow.vue       # 排行榜行
│   │   │   ├── DragCard.vue             # 拖拽排序卡片
│   │   │   ├── HorseDetailCard.vue      # 马匹属性详情卡片
│   │   │   ├── InviteCodeTable.vue      # 邀请码管理表格
│   │   │   └── HorseSearchSelect.vue    # 马匹搜索选择器
│   │   ├── composables/
│   │   │   ├── useAuth.ts               # 认证状态逻辑
│   │   │   ├── useVote.ts               # 投票交互逻辑
│   │   │   └── useDragSort.ts           # 拖拽排序逻辑
│   │   ├── layouts/
│   │   │   ├── AppLayout.vue            # 公共布局（顶部/底部导航）
│   │   │   └── AdminLayout.vue          # 管理后台布局（侧边栏）
│   │   ├── pages/
│   │   │   ├── HomePage.vue             # / — 比赛列表首页
│   │   │   ├── RaceDetailPage.vue       # /races/:id — 比赛详情+投票
│   │   │   ├── LoginPage.vue            # /login
│   │   │   ├── RegisterPage.vue         # /register
│   │   │   ├── ResetPasswordPage.vue    # /reset-password
│   │   │   ├── LeaderboardPage.vue      # /leaderboard
│   │   │   ├── admin/
│   │   │   │   ├── DashboardPage.vue    # /admin
│   │   │   │   ├── CreateRacePage.vue   # /admin/races/new
│   │   │   │   ├── EditRacePage.vue     # /admin/races/:id/edit
│   │   │   │   ├── HorsesPage.vue       # /admin/horses
│   │   │   │   ├── ResultsPage.vue      # /admin/races/:id/results
│   │   │   │   └── InviteCodesPage.vue  # /admin/invite-codes
│   │   ├── router/
│   │   │   └── index.ts                 # 路由定义 + guards
│   │   ├── stores/
│   │   │   ├── authStore.ts             # 认证状态
│   │   │   ├── raceStore.ts             # 比赛列表/详情状态
│   │   │   └── leaderboardStore.ts      # 排行榜状态
│   │   ├── types/
│   │   │   ├── auth.ts                  # 认证类型定义
│   │   │   ├── race.ts                  # 比赛类型定义
│   │   │   ├── horse.ts                 # 马匹类型定义
│   │   │   ├── vote.ts                  # 投票类型定义
│   │   │   └── leaderboard.ts           # 排行榜类型定义
│   │   ├── App.vue
│   │   └── main.ts
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── package.json
│   └── pnpm-lock.yaml
│
├── docker-compose.yml                   # PostgreSQL 16 本地开发
├── .env.example
├── .gitignore
└── README.md
```

### 需求到结构的映射

| 模块 | FR | 后端核心文件 | 前端核心文件 |
|------|-----|-------------|-------------|
| 认证 | FR-1~4 | `endpoints/auth.py`, `services/auth_service.py` | `pages/LoginPage.vue`, `stores/authStore.ts` |
| 马匹库 | FR-5~9 | `endpoints/horses.py`, `services/horse_service.py` | `pages/admin/HorsesPage.vue`, `components/HorseSearchSelect.vue` |
| 比赛管理 | FR-10~15 | `endpoints/races.py`, `services/race_service.py` | `pages/admin/CreateRacePage.vue`, `components/RaceCard.vue` |
| 投票 | FR-16~18 | `endpoints/votes.py`, `services/vote_service.py` | `pages/RaceDetailPage.vue`, `components/VoteButton.vue` |
| 结算 | FR-19~22 | `endpoints/results.py`, `services/result_service.py`, `scoring_engine.py` | `pages/admin/ResultsPage.vue`, `components/DragCard.vue` |
| 排行榜 | FR-23~25 | `endpoints/leaderboard.py`, `services/leaderboard_service.py` | `pages/LeaderboardPage.vue`, `components/LeaderboardRow.vue` |
| 响应式 | FR-26 | — | `layouts/AppLayout.vue`, CSS variables |

### 架构边界

- **API 边界**：前端通过 Axios 调用 `backend/api/v1/*`，不直接访问数据库
- **认证边界**：`deps.py` 中的 `get_current_user` 依赖注入保护所有需要认证的端点
- **业务逻辑边界**：`endpoints/` 不包含业务逻辑，全部委托到 `services/`
- **积分引擎边界**：`scoring_engine.py` 零外部依赖，纯输入→纯输出

## Architecture Validation Results

### Coherence Validation ✅

| 检查项 | 状态 |
|--------|------|
| 技术决策兼容性 | ✅ Vue 3 + Vite + FastAPI + PostgreSQL — 成熟组合，版本兼容 |
| 模式一致性 | ✅ 命名规范全程贯通（DB snake_case → API snake_case → 前端 camelCase 但 API 字段保持 snake_case）|
| 结构对齐 | ✅ 项目结构严格遵循 services/endpoints/models 三层分离，前端 components/pages/stores 职责清晰 |
| 通信模式 | ✅ REST API 统一格式，无冗余协议层 |

### Requirements Coverage Validation ✅

| 模块 | FR 覆盖 | 核心文件 |
|------|---------|---------|
| 认证（FR-1~4） | ✅ | `endpoints/auth.py` + `auth_service.py` + 前端 3 个页面 |
| 马匹库（FR-5~9） | ✅ | `endpoints/horses.py` + `horse_service.py` + 10 属性模型 |
| 比赛（FR-10~15） | ✅ | `endpoints/races.py` + `race_service.py` + 4 种规则引擎 |
| 投票（FR-16~18） | ✅ | `endpoints/votes.py` + `vote_service.py` + 乐观更新 |
| 结算（FR-19~22） | ✅ | `endpoints/results.py` + `scoring_engine.py` ⭐ |
| 排行榜（FR-23~25） | ✅ | `endpoints/leaderboard.py` + 实时刷新 |
| 响应式（FR-26） | ✅ | CSS variables + 两个布局组件 |

**NFR 覆盖：** 性能 SM-5 ✅（无缓存需求）、积分零差异 SM-2 ✅（独立纯函数）、移动优先 ✅、无障碍 ✅、容错 ✅

### Implementation Readiness Validation ✅

所有关键决策已记录、命名规范已锁定、71 个文件明确定义、边界清晰。

### Gap Analysis

| 优先级 | 差距 | 说明 |
|--------|------|------|
| 🟢 低 | Docker Compose 中 API + 前端部署服务 | 部署阶段补充，不阻塞开发 |
| 🟢 低 | 后端包管理器选择（uv/poetry/pip） | 实现时按习惯选择 |
| 🟢 低 | 马匹属性自动更新的具体规则 | PRD 明确 v1 仅搭框架 |

**无关键差距。**

### Architecture Completeness Checklist

**Requirements Analysis:** [x] 上下文分析 [x] 规模评估 [x] 技术约束 [x] 跨领域关注点
**Architectural Decisions:** [x] 决策记录 [x] 技术栈 [x] 集成模式 [x] 性能考量
**Implementation Patterns:** [x] 命名规范 [x] 结构模式 [x] 通信模式 [x] 流程模式
**Project Structure:** [x] 目录结构 [x] 组件边界 [x] 集成点 [x] 需求映射

### Architecture Readiness Assessment

**整体状态：** ✅ **READY FOR IMPLEMENTATION**
**置信度：** 高
