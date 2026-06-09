---
stepsCompleted: [1, 2, 3]
inputDocuments:
  - prds/prd-guess-2026-06-09/prd.md
  - architecture.md
  - ux-designs/ux-guess-2026-06-09/DESIGN.md
  - ux-designs/ux-guess-2026-06-09/EXPERIENCE.md
---

# Guess - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Guess, decomposing the requirements from the PRD, UX Design, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR-1: 管理员生成邀请码，每码终生绑定一个用户，后台可查询/操作
FR-2: 用户凭有效邀请码注册（用户名+密码+QQ+邀请码），自动登录
FR-3: 已注册用户凭用户名与密码登录
FR-4: 游客只读访问所有公开页面，不可投票
FR-5: 马匹拥有 10 个属性（name/sex/age/origin/sire/damsire/weight/jockey/previous_result/best_win）
FR-6: 管理员可手动修改任意马匹的任意属性值
FR-7: 马匹属性自动更新框架（v1 仅搭框架和触发机制，规则后续配置）
FR-8: 创建比赛时从马匹库搜索选择马匹，库中没有可即时新建
FR-9: 比赛详情页展示所有参赛马匹的完整 10 项属性（基于创建时的快照）
FR-10: 管理员创建比赛（名称+日期+等级+参赛马匹），状态为"投票中"
FR-11: 管理员可删除未结算比赛（含投票记录），已结算不可删除
FR-12: G1 积分规则引擎（+10/+5/+3/+2/+1 正分 + 匹数分档末位扣分）
FR-13: G2/JPN1 积分规则引擎（+5/+4/+3/+2/+1，无扣分）
FR-14: 2 岁 G1 积分规则引擎（正分同 G1，无扣分）
FR-15: 自定义积分规则引擎（一次性正序积分列表 + 选填扣分规则）
FR-16: 已登录用户在"投票中"比赛选一匹马确认投票
FR-17: 用户可在锁定前无限次修改投票
FR-18: 锁定后用户不可新增或修改投票
FR-19: 管理员对比赛执行锁定投票操作（需二次确认，不可撤销）
FR-20: 管理员通过拖拽排序录入比赛结果
FR-21: 结果确认后系统自动按等级规则结算所有用户积分
FR-22: 管理员可随时修改已结算结果，系统自动撤销重算
FR-23: 全局排行榜展示所有用户累计积分降序排列
FR-24: 任何人（含游客）可查看已结算比赛详情（排名+投票+积分明细）
FR-25: 投票中比赛实时展示每位用户的投票选择
FR-26: 响应式布局适配 320px+ 移动端和桌面端

### NonFunctional Requirements

NFR-1 (SM-1): 投票效率 — 用户平均 30 秒内完成一次投票操作
NFR-2 (SM-2): 积分零差异 — 系统结算与手工按规则计算 100% 一致
NFR-3 (SM-3): 迁移率 — 前 10 场后 ≥90% 原参与者完成至少一次投票
NFR-4 (SM-4): 比赛创建效率 — 管理员 2 分钟内创建一场比赛
NFR-5 (SM-5): 性能 — 100 用户、50+ 场比赛下页面响应 ≤ 2s
NFR-6: 移动优先 — 核心操作在移动端 ≤ 3 次点击/触屏交互
NFR-7: 无障碍 — 语义 HTML、44px 触摸目标、4.5:1 对比度、颜色+文字双重编码
NFR-8: 容错 — 结果修改全链路撤销重算、网络错误乐观更新+后台重试
NFR-9: 实时性 — 投票展示实时更新，结算后排行榜即时刷新
NFR-10: 无暗色模式 — v1 仅亮色模式

### Additional Requirements

- 技术栈：Vue 3 + Vite + TypeScript（前端），FastAPI + SQLAlchemy 2.0 async + Alembic（后端），PostgreSQL 16
- 项目结构：手动搭建 monorepo (frontend/ + backend/)
- 认证方案：JWT access token（30min）+ refresh token（7天），passlib[bcrypt] 密码哈希
- API 设计：RESTful，URL 前缀 /api/v1/，统一响应格式（{data}/{detail}）
- 数据库命名：snake_case 复数表名
- 前端命名：PascalCase 组件，camelCase 函数/变量，use{Name}Store Pinia 模式
- 后端三层分离：endpoints（仅编排）→ services（业务逻辑）→ models（数据模型）
- 积分规则引擎：纯函数模块（scoring_engine.py），零外部依赖，独立可测试
- Docker Compose 本地开发（PostgreSQL 16），生产部署 VPS + Docker Compose（Nginx + API + DB）
- 部署配置：.env + Pydantic Settings

### UX Design Requirements

UX-DR1: 实现 JRA 品牌色系统（竞马绿 #1A5632、冠军金 #B8960C 等 12 色 CSS 自定义属性）
UX-DR2: 实现排版层级（Barlow Condensed 数字 + 系统字体栈中文，6 级字号 display/heading/subheading/body/body-sm/caption）
UX-DR3: 实现间距系统（4/8/12/16/20/24/32/40/48/64 px CSS 变量）
UX-DR4: 实现圆角系统（6/10/14/9999 px CSS 变量）
UX-DR5: 构建比赛卡片组件（RaceCard — 等级徽章+状态标签+比赛名+日期+参赛数+已投票数）
UX-DR6: 构建等级徽章组件（GradeBadge — G1 金底/G2 灰底/2岁G1 亮绿底/自定义灰虚线）
UX-DR7: 构建投票按钮组件（VoteButton — 金底 CTA → 绿底确认态 "✓ 已投：{马名}"）
UX-DR8: 构建排行榜行组件（LeaderboardRow — 前三金数字、当前用户淡绿背景 #F0F7F2）
UX-DR9: 构建拖拽排序卡片组件（DragCard — 六点网格手柄、强边框、≥56px 触摸高度）
UX-DR10: 构建状态胶囊组件（StatusBadge — 投票中绿/已锁定灰+🔒/已结算深绿+✓）
UX-DR11: 构建马匹属性卡片组件（HorseDetailCard — 10 属性键值对 + 已投票金色标记）
UX-DR12: 实现马匹搜索选择器组件（HorseSearchSelect — 模糊搜索+下拉勾选+标签+新建入口）
UX-DR13: 实现投票明细展示组件（VotingDetail — "用户名 → 马匹名" 列表）
UX-DR14: 实现邀请码管理表格组件（InviteCodeTable — 码/状态/用户/QQ/操作）
UX-DR15: 移动端底部固定导航（首页/排行榜/管理）+ 桌面端顶部导航（safe-area-inset-bottom）
UX-DR16: 管理后台桌面端左侧 240px 侧边栏布局 + 移动端 Tab/汉堡菜单
UX-DR17: 实现所有状态模式（空比赛列表、空排行榜、空马匹库、加载骨架屏、网络错误、投票中已投票、投票中未投票、已锁定、已结算、拖拽未完成等 12+ 种）
UX-DR18: 实现拖拽排序交互（移动端长按 300ms 激活，桌面端鼠标拖拽，插入位置绿色高亮条，弃权区）
UX-DR19: 实现登录重定向机制（?redirect= 参数，登录成功后回到来源页）
UX-DR20: 所有可交互元素移动端触摸目标 ≥ 44×44px，拖拽手柄 ≥ 48×48px
UX-DR21: 实现无障碍标准（语义 HTML heading 层级、focus ring 2px primary、aria 标签、prefers-reduced-motion）
UX-DR22: 实现响应式布局（768px 断点，<768px 单列，≥768px 桌面端，max-w-7xl 1280px）
UX-DR23: 实现骨架屏加载状态（比赛卡片骨架≤500ms、排行榜骨架）
UX-DR24: 实现微文案系统（投票确认/修改/锁定/空状态/错误提示等 12 种场景精确文案）
UX-DR25: 实现投票乐观更新 + 网络错误后台重试机制
UX-DR26: 实现马匹选择卡片交互（点击选中边框变金+勾选、确认按钮激活逻辑）
UX-DR27: 实现管理后台比赛表格与行操作（创建/删除/锁定/录入结果/修改结果入口）

### FR Coverage Map

| FR | Epic | Description |
|----|------|-------------|
| FR-1 | Epic 1 | 管理员生成邀请码 |
| FR-2 | Epic 1 | 用户凭邀请码注册 |
| FR-3 | Epic 1 | 用户登录 |
| FR-4 | Epic 1 | 游客只读访问 |
| FR-5 | Epic 2 | 马匹属性定义（10属性） |
| FR-6 | Epic 2 | 马匹属性手动编辑 |
| FR-7 | Epic 2 | 马匹属性自动更新框架 |
| FR-8 | Epic 2 | 创建比赛时从库中选择马匹 |
| FR-9 | Epic 2 | 赛事页面展示马匹详情 |
| FR-10 | Epic 2 | 管理员创建比赛 |
| FR-11 | Epic 2 | 管理员删除比赛 |
| FR-12 | Epic 3 | G1 积分规则引擎 |
| FR-13 | Epic 3 | G2/JPN1 积分规则引擎 |
| FR-14 | Epic 3 | 2岁 G1 积分规则引擎 |
| FR-15 | Epic 3 | 自定义积分规则引擎 |
| FR-16 | Epic 3 | 用户投票 |
| FR-17 | Epic 3 | 投票修改 |
| FR-18 | Epic 3 | 投票不可修改（锁定后） |
| FR-19 | Epic 3 | 管理员锁定投票 |
| FR-20 | Epic 3 | 拖拽排序录入结果 |
| FR-21 | Epic 3 | 系统自动结算积分 |
| FR-22 | Epic 3 | 管理员修改已结算结果 |
| FR-23 | Epic 3 | 全局排行榜 |
| FR-24 | Epic 3 | 比赛详情公开查看 |
| FR-25 | Epic 3 | 投票中比赛实时投票展示 |
| FR-26 | 全部 | 响应式布局（所有页面） |

## Epic List

### Epic 1: User Authentication & Platform Foundation

Enable users to join the platform via invite codes, register, login, reset password, and browse as guests. Lay the technical foundation: project scaffold, design token system, navigation layout, and responsive framework.

**FRs covered:** FR-1, FR-2, FR-3, FR-4
**NFRs covered:** NFR-6 (mobile), NFR-7 (a11y), NFR-8 (error handling foundation)
**UX-DRs covered:** UX-DR1~4 (design tokens), UX-DR15~16 (navigation), UX-DR19 (login redirect), UX-DR20~21 (touch targets & a11y), UX-DR22 (responsive), UX-DR23 (skeleton), UX-DR24 (microcopy)

### Epic 2: Horse Library & Race Management

Enable admin to manage the global horse library (10 attributes with manual edit + auto-update framework), create and delete races, select horses from the library for each race, and display complete horse details on race pages.

**FRs covered:** FR-5, FR-6, FR-7, FR-8, FR-9, FR-10, FR-11
**UX-DRs covered:** UX-DR5 (RaceCard), UX-DR6 (GradeBadge), UX-DR10 (StatusBadge), UX-DR11 (HorseDetailCard), UX-DR12 (HorseSearchSelect), UX-DR14 (InviteCodeTable), UX-DR16 (AdminLayout), UX-DR26 (horse selection card), UX-DR27 (admin race table)

### Epic 3: Voting, Scoring Engine & Leaderboard

Deliver the complete vote-to-settlement cycle: users vote on races (modifiable before lock), admin locks voting and enters results via drag-drop, system auto-settles points using the 4-rule scoring engine, and the leaderboard reflects real-time standings. Public race details show full vote distribution and point breakdowns.

**FRs covered:** FR-12, FR-13, FR-14, FR-15, FR-16, FR-17, FR-18, FR-19, FR-20, FR-21, FR-22, FR-23, FR-24, FR-25
**UX-DRs covered:** UX-DR7 (VoteButton), UX-DR8 (LeaderboardRow), UX-DR9 (DragCard), UX-DR13 (VotingDetail), UX-DR17 (all state patterns), UX-DR18 (drag interaction), UX-DR25 (optimistic voting)

## Epic 1: User Authentication & Platform Foundation

Enable users to join the platform via invite codes, register, login, reset password, and browse as guests. Lay the technical foundation: project scaffold, design token system, navigation layout, and responsive framework.

**Context:** Story 1.1 为绿地项目必要的基础设施搭建，不对用户可见。完成后 Epic 1 的后续故事才能启动。Story 1.2 之后用户即可访问页面。

### Story 1.1: 项目初始化与环境搭建

As a **开发团队**,
I want **项目初始化脚手架已搭建，后端+前端可启动，数据库可连接**,
So that **开发人员可以在统一环境中开始功能开发**。

**Acceptance Criteria:**

**Given** 开发环境已配置好
**When** 执行 `docker compose up -d`
**Then** PostgreSQL 16 容器启动成功，端口 5432 可连接
**And** `cd backend && uvicorn app.main:app --reload` 后 `GET /health` 返回 `200 OK`
**And** `cd frontend && pnpm dev` 后浏览器访问 `localhost:5173` 显示 Vite 欢迎页
**And** Alembic 初始化成功，`alembic init` 生成 migrations 目录

**Given** 项目已初始化
**When** 查看项目根目录
**Then** 目录结构符合架构文档中定义的 monorepo 布局（frontend/ + backend/ + docker-compose.yml）
**And** `.env.example` 包含所有必需环境变量（DATABASE_URL, SECRET_KEY, JWT_SECRET, CORS_ORIGINS）
**And** `.gitignore` 排除了 `node_modules/`, `__pycache__/`, `.env`, `*.pyc`

**Given** 后端已启动
**When** 执行 `GET /api/v1/health`
**Then** 返回 `{ "status": "ok", "version": "0.1.0" }`

### Story 1.2: 设计令牌系统与导航布局

As a **用户**,
I want **页面有统一的 JRA 品牌视觉风格和清晰的导航结构**,
So that **我在任何设备上都能流畅浏览和操作**。

**Acceptance Criteria:**

**Given** 前端 CSS 基础设施已搭建
**When** 浏览器加载任意页面
**Then** `:root` 中 CSS 自定义属性已定义：竞马绿/冠军金/暖白等 12 色、6 级排版字号、9 级间距值（4~64px）、4 级圆角值
**And** `variables.css`, `base.css`, `utilities.css` 三个文件按约定分离

**Given** 用户访问网站
**When** 在移动端（<768px）浏览器打开
**Then** 底部固定导航栏显示「首页」「排行榜」（管理员额外显示「管理」）
**And** 首页比赛列表为全宽单列布局，两侧 16px 边距
**And** 底部导航适配 safe-area-inset-bottom（iOS 刘海屏）

**Given** 用户在桌面端（≥768px）访问
**When** 打开首页
**Then** 顶部固定导航栏显示 Logo + 「首页」「排行榜」+ 登录/用户信息
**And** 内容区域居中，最大宽度 max-w-7xl (1280px)
**And** 管理员访问 `/admin` 路径时显示左侧 240px 侧边栏 + 主内容区

**Given** 用户在任何设备浏览
**When** 点击导航项
**Then** Vue Router 4 按约定路由跳转，路由懒加载生效

### Story 1.3: 邀请码系统

As a **管理员**,
I want **在管理后台生成和管理邀请码**,
So that **我可以控制谁可以注册加入圈子**。

**Acceptance Criteria:**

**Given** 管理员已登录
**When** 访问 `/admin/invite-codes`
**Then** 页面显示 InviteCodeTable 组件，表格列：邀请码 / 绑定状态 / 绑定用户名 / QQ号 / 操作（复制、失效）
**And** 管理员可按用户名、邀请码、QQ号三个维度搜索

**Given** 管理员在邀请码管理页
**When** 点击「生成邀请码」
**Then** 系统生成一个唯一 8 位字母数字组合的邀请码，状态为「未绑定」
**And** 新生成的码出现在表格顶部
**And** API 返回 `POST /api/v1/admin/invite-codes` → 201

**Given** 管理员选中一个「未绑定」的邀请码
**When** 点击「失效」
**Then** 该邀请码状态变为「已失效」
**And** 用户尝试用已失效的邀请码注册时拒绝并提示

**Given** 管理员需查询用户绑定信息
**When** 搜索用户名或 QQ 号
**Then** 显示该用户绑定的邀请码和 QQ 号

**Given** 后端 API
**When** `GET /api/v1/admin/invite-codes`
**Then** 返回所有邀请码列表（含绑定状态）
**And** `POST /api/v1/admin/invite-codes` 生成新码
**And** `PATCH /api/v1/admin/invite-codes/{code}` 更新状态为失效

### Story 1.4: 用户注册

As a **赛马爱好者**,
I want **凭邀请码注册账号**,
So that **我可以加入圈子并参与投票**。

**Acceptance Criteria:**

**Given** 用户拥有一个有效邀请码
**When** 访问 `/register` 并输入用户名（全局唯一）、密码、QQ号和邀请码
**Then** 注册成功后自动登录并跳转至首页
**And** 该邀请码状态变为「已绑定」，绑定该用户的用户名和QQ号

**Given** 用户输入已被使用的邀请码
**When** 提交注册
**Then** 显示错误提示「邀请码已被使用」
**And** 停留在注册页

**Given** 用户输入无效或已失效的邀请码
**When** 提交注册
**Then** 显示错误提示「邀请码无效或已被使用」

**Given** 用户输入已存在的用户名
**When** 提交注册
**Then** 显示错误提示「用户名已存在」

**Given** 后端 API
**When** `POST /api/v1/auth/register` 携带有效参数
**Then** 返回 201 + access_token + user 信息
**And** User 表中插入新记录，密码 bcrypt 哈希存储

### Story 1.5a: 后端认证 API

As a **系统**,
I want **后端提供完整的 JWT 认证 API（登录、令牌刷新、当前用户查询）**,
So that **前端可以安全地完成用户认证和会话管理**。

**Acceptance Criteria:**

**Given** 已注册用户
**When** `POST /api/v1/auth/login` 携带正确的用户名和密码
**Then** 返回 200 + `{ "access_token": "...", "refresh_token": "...", "user": { ... } }`
**And** access_token 有效期 30min，refresh_token 有效期 7天
**And** `POST /api/v1/auth/refresh` 接受 refresh_token 返回新的 access_token

**Given** 用户输入错误的凭据
**When** 登录
**Then** 返回 401，显示「用户名或密码错误」
**And** 不泄露具体哪个字段错误

**Given** 未认证用户
**When** 请求需认证的 API（如 POST /api/v1/votes）
**Then** 返回 401 `{ "detail": { "code": "NOT_AUTHENTICATED", "message": "请先登录" } }`

**Given** 后端依赖注入
**When** 查看 `deps.py`
**Then** `get_current_user` 依赖注入解析 JWT 并返回当前用户对象
**And** 令牌过期时返回 401，无效令牌时返回 401

### Story 1.5b: 前端登录与游客访问

As a **已注册用户和游客**,
I want **通过登录页面登录系统，未登录用户也可以浏览公开页面**,
So that **我可以参与投票，游客也能看到比赛信息**。

**Acceptance Criteria:**

**Given** 已注册用户
**When** 访问 `/login`，输入正确的用户名和密码
**Then** 登录成功后跳转回来源页面（或首页）
**And** 前端 Store 保存用户信息和令牌，Axios 拦截器自动附加 Authorization header

**Given** 用户访问 `/?login` 带 `?redirect=` 参数
**When** 登录成功后
**Then** 自动跳转回 `redirect` 指定的页面

**Given** 游客（未登录用户）
**When** 访问首页、比赛详情页、排行榜
**Then** 页面全部内容可读（马匹数据、投票公开信息、排行榜）
**And** 点击「投票」按钮时跳转至 `/login?redirect=/races/{id}`

**Given** 前端 Axios 拦截器
**When** 收到 401 响应
**Then** 自动尝试用 refresh_token 获取新的 access_token
**And** 刷新失败时清除令牌，跳转至登录页（保留 `?redirect=`）

### Story 1.6: 密码找回

As a **忘记密码的用户**,
I want **凭用户名和邀请码重置密码**,
So that **我可以恢复账号访问**。

**Acceptance Criteria:**

**Given** 用户已注册但忘记密码
**When** 访问 `/reset-password`，输入用户名和该用户绑定的邀请码
**Then** 进入新密码设置页面
**And** 设置新密码后，密码更新成功

**Given** 用户输入错误的邀请码
**When** 提交密码找回
**Then** 显示「邀请码与用户不匹配」

**Given** 后端 API
**When** `POST /api/v1/auth/reset-password` 携带正确参数
**Then** 返回 200，用户密码更新为新密码（bcrypt 哈希）

### Story 1.7: 无障碍、加载态与微文案

As a **所有用户**,
I want **界面在所有场景下都有清晰的加载、空状态和错误提示**,
So that **即使网络慢或操作出错，我也知道正在发生什么**。

**Acceptance Criteria:**

**Given** 页面加载中
**When** 比赛列表加载
**Then** 显示比赛卡片骨架屏（灰条模拟标题+属性行），不超过 500ms
**And** 排行榜页加载中显示表头 + 5 行骨架行

**Given** 列表为空
**When** 比赛列表为空且用户已登录
**Then** 显示「还没有比赛。管理员正在筹备中——」
**And** 排行榜为空时显示「还没有人参与竞猜——成为第一个！」+ 跳转首页链接
**And** 马匹库为空时显示「马匹库为空——创建第一场比赛时，参赛马匹将自动入库。」

**Given** 网络错误
**When** 加载数据失败
**Then** 显示「加载失败，请刷新重试」+ 刷新按钮
**And** 关键操作失败显示可重试的提示

**Given** 所有可交互元素
**When** 在移动端
**Then** 触摸目标 ≥ 44×44px，拖拽手柄 ≥ 48×48px
**And** 所有可聚焦元素有可见 focus ring（2px 竞马绿外描边，2px 偏移）

**Given** 用户启用 prefers-reduced-motion
**When** 页面加载
**Then** 所有动画（骨架屏脉冲、拖拽过渡）跳过

**Given** 各场景微文案
**When** 投票确认 → 显示「你已投给：{马名}」
**And** 投票锁定后 → 显示「投票已截止」
**And** 注册邀请码无效 → 显示「邀请码无效或已被使用」
**And** 等级徽章 → G1(金底白字) / G2(灰底白字) / 2岁G1(亮绿底白字) / 自定义(灰底虚线)
**And** 状态胶囊 → 投票中(绿底白字) / 已锁定(灰底白字+🔒) / 已结算(深绿底白字+✓)

## Epic 2: Horse Library & Race Management

Enable admin to manage the global horse library (10 attributes with manual edit + auto-update framework), create and delete races, select horses from the library for each race, and display complete horse details on race pages.

### Story 2.1: 马匹数据模型与管理页面

As a **管理员**,
I want **能在后台管理马匹库，每匹马拥有 10 个字段属性**,
So that **我可以在创建比赛前建立和维护马匹数据**。

**Acceptance Criteria:**

**Given** 马匹数据模型已定义
**When** 查看 `models/horse.py`
**Then** Horse 模型包含 10 个字段：name(必填), sex, age, origin, sire, damsire, weight, jockey, previous_result, best_win
**And** name 为唯一必填字段，其余可空
**And** 表名遵循命名规范为 `horses`（snake_case 复数）

**Given** 管理员已登录
**When** 访问 `/admin/horses`
**Then** 显示马匹列表表格，展示所有马匹
**And** 支持按名字模糊搜索

**Given** 管理员在马匹管理页
**When** 点击「新建马匹」→ 填写名字（必填）+ 其他字段（选填）→ 保存
**Then** 马匹创建成功，出现在列表中
**And** API `POST /api/v1/horses` 返回 201

**Given** 管理员选中一匹马
**When** 点击编辑 → 修改任意字段 → 保存
**Then** 该字段更新成功，不影响其他字段
**And** API `PATCH /api/v1/horses/{id}` 返回 200 + 更新后的马匹数据

**Given** 管理员编辑了某匹马
**When** 保存后
**Then** 已关联该马匹的过往比赛历史数据不受影响（快照机制）

**Given** 后端 API
**When** `GET /api/v1/horses` → 返回马匹列表（支持 `?name=xxx` 模糊搜索）
**And** `GET /api/v1/horses/{id}` → 返回单匹马详情
**And** `DELETE /api/v1/horses/{id}` → 删除马匹（仅当未被比赛引用时）

### Story 2.2: 马匹搜索选择器组件

As a **管理员**,
I want **创建比赛时能搜索马匹库并勾选参赛马，库中没有时可快速新建**,
So that **我可以高效完成比赛的参赛马配置**。

**Acceptance Criteria:**

**Given** 管理员正在创建比赛
**When** 点击参赛马匹输入框
**Then** 输入文字实时模糊搜索马匹库，下拉列表显示匹配结果
**And** 选中某匹马后，该马以标签形式显示在输入框下方（带 × 按钮可移除）

**Given** 搜索无结果
**When** 库中没有匹配的马匹
**Then** 下拉列表底部显示「新建马匹」快捷入口

**Given** 管理员点击「新建马匹」
**When** 弹出快捷表单（名字必填，其余选填）
**Then** 保存后马匹自动入库，并同时加入当前比赛的参赛列表

**Given** 已选马匹显示为标签
**When** 点击标签上的 ×
**Then** 该马匹从参赛列表中移除

### Story 2.3: 比赛创建与管理

As a **管理员**,
I want **能创建和编辑比赛，指定名称、日期、等级和参赛马匹**,
So that **用户可以浏览比赛并投票**。

**Acceptance Criteria:**

**Given** 管理员在管理后台
**When** 点击「创建比赛」
**Then** 进入表单页（`/admin/races/new`），填写比赛名称、日期（日期选择器）、等级（G1/G2·JPN1/2岁G1/自定义）
**And** 使用 HorseSearchSelect 选择参赛马匹，至少 2 匹
**And** 选择「自定义」等级时，额外显示正序积分列表输入框和选填的扣分规则输入框，并提示「自定义规则仅作用于本场比赛，不会保存为模板。」

**Given** 管理员提交创建表单
**When** 所有必填项已填
**Then** 比赛创建成功，状态为「投票中」，出现在首页比赛列表
**And** API `POST /api/v1/races` 返回 201

**Given** 比赛列表中包含新建的比赛
**When** 用户在首页浏览
**Then** RaceCard 组件展示：等级徽章（G1金/G2灰/2岁G1亮绿/自定义灰虚线）、比赛名、日期、状态胶囊（投票中绿底）、参赛马匹数、已投票人数
**And** 投票中比赛卡片右上角显示金色投票入口

**Given** 管理员在管理后台
**When** 选中一场投票中的比赛 → 点击编辑
**Then** 可修改比赛信息（名称、日期、等级、增删参赛马匹）

**Given** 比赛详情页（公开）
**When** 用户查看 `/races/:id`
**Then** 展示比赛名称、等级徽章、状态胶囊、参赛马匹列表（含完整 10 属性）

> 🟡 **[NFR-4/SM-4]** 此故事完成后，管理员应能在 2 分钟内完成一场 12 匹马的比赛创建流程（从点击「创建比赛」到确认提交）。
>
> 🟡 **[NOTE]** 自定义等级规则 UI（正序积分列表 + 扣分规则）为比赛创建表单的内嵌部分。实现时优先完成标准等级（G1/G2/2岁G1）的核心表单，自定义规则的展开控件作为自包含子任务在同一故事中完成。

### Story 2.4: 比赛删除与马匹详情展示

As a **管理员和用户**,
I want **管理员可删除未结算比赛，所有用户可查看比赛详情中的马匹完整属性**,
So that **数据可管理，信息可查阅**。

**Acceptance Criteria:**

**Given** 管理后台
**When** 管理员试图删除一场「投票中」或「已锁定」但未结算的比赛
**Then** 弹出二次确认：「确定删除「{比赛名}」？所有投票记录将被清除。」
**And** 确认后比赛及其投票记录被删除，API `DELETE /api/v1/races/{id}` 返回 204

**Given** 比赛已结算
**When** 管理员查看该比赛操作选项
**Then** 删除按钮置灰/隐藏
**And** 提示「已结算比赛不可删除，请修改结果」或仅显示「修改结果」按钮

**Given** 用户访问比赛详情页 `/races/:id`
**When** 页面加载
**Then** 每匹参赛马以 HorseDetailCard 展示，左侧马匹名（heading, primary），右侧列出 FR-5 定义的 10 项属性（body-sm 键值对）
**And** 数据来源为该场比赛创建时的马匹快照（非马匹库的实时数据）

### Story 2.5: 马匹属性自动更新框架

As a **管理员**,
I want **比赛结果录入时，系统按自动更新规则推送到马匹库**,
So that **我不必逐场手工追踪马匹数据变更**。

**Acceptance Criteria:**

**Given** 一场已结算比赛
**When** 结果确认后
**Then** 系统触发各马匹属性的自动更新逻辑，作用于比赛所在赛事的马匹记录
**And** 自动更新仅填充空字段或按规则覆盖旧值

**Given** 某字段已被管理员手动编辑过
**When** 自动更新触发
**Then** 该字段保持手动编辑值不变（手动优先）
**And** 自动更新仅作用于未被手动覆盖的字段

**Given** 自动更新的字段变更
**When** 用户查看马匹详情
**Then** 显示「自动更新」来源标记，变更可追溯

**Given** 马匹历史快照
**When** 自动更新作用于马匹库记录后
**Then** 过往比赛中的马匹快照数据不受影响

**IMPORTANT:** v1 仅搭建自动更新框架和触发机制，不定义每个字段的具体更新规则。规则由管理员在后续版本中逐步配置。

## Epic 3: Voting, Scoring Engine & Leaderboard

Deliver the complete vote-to-settlement cycle: users vote on races (modifiable before lock), admin locks voting and enters results via drag-drop, system auto-settles points using the 4-rule scoring engine, and the leaderboard reflects real-time standings. Public race details show full vote distribution and point breakdowns.

### Story 3.1: 积分规则引擎

As a **系统**,
I want **一个独立可测试的纯函数积分规则引擎，支持 4 种等级规则**,
So that **无论用户投中哪匹马，系统都能准确计算积分且零误差**。

**Acceptance Criteria:**

**Given** scoring_engine.py 作为纯函数模块实现
**When** 导入并使用
**Then** 模块零外部依赖，输入为（等级类型, 参赛马匹数, 用户投中名次），输出为整型积分值

**Given** G1 规则（FR-12）
**When** 正分：第1名+10、第2名+5、第3名+3、第4名+2、第5名+1
**And** ≥8匹：倒数第1名-10、倒数第2名-5、倒数第3名-1
**And** 7匹：倒数第1名-5、倒数第2名-1
**And** 6匹：仅倒数第1名-1
**And** ≤5匹：无扣分
**Then** 所有边界组合计算结果与手工计算 100% 一致

**Given** G2/JPN1 规则（FR-13）
**When** 正分：第1名+5、第2名+4、第3名+3、第4名+2、第5名+1
**Then** 无论参赛马匹数量，末位不扣分，投中第6名及以后得0分

**Given** 2岁G1 规则（FR-14）
**When** 正分同G1（+10/+5/+3/+2/+1）
**Then** 所有名次不扣分，投中末位不得负分

**Given** 自定义规则（FR-15）
**When** 输入自定义正序积分列表 [10,7,5,3,2,1] 和扣分规则 [{pos:-1, points:-5}, {pos:-2, points:-2}]
**Then** 按自定义列表和扣分档位正确计算

**Given** 退赛/DNF 马匹
**When** 用户投中该马
**Then** 得 0 分，不计入排名扣分计算的分母

### Story 3.2: 投票系统（后端）

As a **已登录用户**,
I want **能在一场开放的比赛中投票，并在锁定前修改选择**,
So that **我可以在比赛开始前自由决定支持哪匹马**。

**Acceptance Criteria:**

**Given** 赛事处于「投票中」状态
**When** 已登录用户提交 `POST /api/v1/races/{race_id}/votes` 带 `horse_id`
**Then** 创建投票记录，返回 201
**And** 每用户每场比赛仅一个有效投票（重复提交覆盖旧投票）

**Given** 用户修改投票
**When** 锁定前再次提交 `POST /api/v1/races/{race_id}/votes` 带不同 `horse_id`
**Then** 旧投票被覆盖，返回 200 + 更新后的投票信息
**And** 修改次数不限

**Given** 锁定后的比赛
**When** 用户尝试提交或修改投票
**Then** 返回 400 `{ "detail": { "code": "VOTE_LOCKED", "message": "投票已截止" } }`

**Given** 未登录用户
**When** 尝试提交投票
**Then** 返回 401 `{ "detail": { "code": "NOT_AUTHENTICATED", "message": "请先登录" } }`

**Given** 管理员锁定比赛
**When** `POST /api/v1/races/{race_id}/lock`
**Then** 比赛状态变为「已锁定」，所有投票冻结
**And** 锁定操作需二次确认

**Given** 投票数据查询
**When** `GET /api/v1/races/{race_id}/votes`
**Then** 返回所有用户的投票明细（用户 + 所选马匹），游客和登录用户均可查看
**And** 投票中比赛实时刷新，已结算比赛固定展示

### Story 3.3: 投票前端交互

As a **已登录用户**,
I want **在比赛详情页上通过直观的操作完成投票、看到实时投票分布**,
So that **我能在手机上快速完成投票并看到朋友们的选择**。

**Acceptance Criteria:**

**Given** 用户访问一场「投票中」比赛详情页
**When** 用户未投票
**Then** 页面底部显示金色 VoteButton（「投票」），马匹列表无标记
**And** VotingDetail 组件显示所有用户当前投票分布（「用户名 → 马匹名」）

**Given** 用户点击「投票」
**When** 弹出马匹选择面板，点击一匹
**Then** 该马卡片边框变金色 + 显示勾选标记
**And** 确认按钮在选中后激活

**Given** 用户确认投票
**When** 点击确认
**Then** VoteButton 变为绿底状态「✓ 已投：{马名}」
**And** 投票明细实时刷新显示该用户的投票

**Given** 用户想修改投票
**When** 点击「修改投票」
**Then** 重新进入选择界面
**And** 旧选择被覆盖

**Given** 比赛已锁定
**When** 用户访问详情页
**Then** 显示「投票已截止」
**And** 已投票用户可见自己的最终选择
**And** 未投票用户显示「投票已截止。你未参与本场竞猜。」

**Given** 游客访问
**When** 点击投票按钮
**Then** 跳转至 `/login?redirect=/races/{id}`

**Given** 移动端
**When** 用户完成整个投票流程
**Then** 核心操作不超过 3 次点击（选马 → 确认）

> 🟡 **[NFR-3/SM-3]** 迁移率 ≥90% 为上线后追踪指标，不在单个故事中验证。上线后通过分析 dashboard 追踪前 10 场比赛的参与情况。

### Story 3.4: 结果录入——拖拽排序

As a **管理员**,
I want **通过拖拽排序将参赛马匹按实际名次排列来录入比赛结果**,
So that **我可以直观、准确地完成结果录入**。

**Acceptance Criteria:**

**Given** 管理员登录并进入已锁定比赛的结果录入页（`/admin/races/{id}/results`）
**When** 页面加载
**Then** 所有参赛马匹以 DragCard 组件展示为可拖拽卡片
**And** 每张卡片左侧有六点网格拖拽手柄（⠿），右侧马匹名 + 关键属性摘要
**And** 底部有「弃权区」——退赛/DNF 马匹拖入此处

**Given** 管理员拖拽排序
**When** 桌面端鼠标拖拽一张卡片到新位置
**Then** 卡片随鼠标移动，插入位置显示绿色高亮条
**And** 移动端长按 300ms 激活拖拽（避免与滚动冲突）
**And** 拖拽中卡片半透明 + 轻微抬起阴影

**Given** 所有马匹尚未排完
**When** 尝试点击「确认结果」
**Then** 确认按钮置灰，提示「请排列所有马匹的名次（含弃权区）」

**Given** 所有马匹排列完成
**When** 点击「确认结果」
**Then** 触发 FR-21 的自动结算流程
**And** 页面跳转到比赛详情页，显示已结算结果

**Given** 管理员修改已结算结果
**When** 重新进入结果录入页
**Then** 预填上次的排列顺序，管理员可重新调整

### Story 3.5: 积分结算与排行榜

As a **管理员和用户**,
I want **比赛结果确认后系统自动结算所有用户的积分，排行榜即时更新**,
So that **所有排名和积分一目了然**。

**Acceptance Criteria:**

**Given** 管理确认结果后
**When** 系统触发结算
**Then** 按该比赛等级的积分规则引擎（FR-12~15），为所有已投票用户计算积分
**And** 退赛/DNF 马匹对应的用户得 0 分
**And** 结算完成后比赛状态变为「已结算」

**Given** 结算完成后
**When** 查看排行榜页（`/leaderboard`）
**Then** 所有已注册用户按累计积分降序排列
**And** 展示字段：排名（Barlow Condensed, 前三名金色数字）、用户名、累计积分（20px bold, 竞马绿色）、参与场数（body-sm）、场均得分
**And** 当前登录用户行有淡绿背景 `#F0F7F2` 标记
**And** 排行榜为空时显示「还没有人参与竞猜——成为第一个！」+ 跳转首页链接

**Given** 后端 API
**When** `GET /api/v1/leaderboard`
**Then** 返回所有用户排名列表（含积分、场数、场均）
**And** 排行榜在每次结算后即时刷新

### Story 3.6: 比赛详情公开查看

As a **所有用户（含游客）**,
I want **查看已结算比赛的完整结果——最终排名、每位用户的投票和所获积分**,
So that **我可以了解比赛全貌和朋友的竞猜表现**。

**Acceptance Criteria:**

**Given** 一场已结算比赛
**When** 任何人（登录或未登录）访问 `/races/:id`
**Then** 马匹按最终名次排列，名次标签显示（1st/2nd/3rd…）
**And** 每匹参赛马下方显示投票该马的用户列表
**And** 每位用户的投票旁边显示该场所获积分（「+10 / -10 / 0」等）

**Given** 投票中比赛
**When** 用户访问详情页
**Then** 实时展示每位用户的投票选择（格式：「用户名 → 马匹名」）
**And** 包含未登录用户的所有公开信息
**And** 用户提交或修改投票后展示即时刷新

**Given** 管理后台
**When** 管理员查看已结算比赛
**Then** 显示「修改结果」按钮入口

### Story 3.7: 结果修改——撤销重算

As a **管理员**,
I want **修改已结算比赛的结果时，系统自动撤销旧积分并重算**,
So that **即使录入错误也能快速纠正，不影响排名准确性**。

**Acceptance Criteria:**

**Given** 已结算比赛的结果被管理员修改
**When** 管理员重新进入结果录入页 → 调整拖拽排序 → 确认提交
**Then** 系统自动撤销该比赛原积分（从所有受影响用户的总分中扣除）
**And** 系统按新排名重新结算积分
**And** 排行榜即时反映变更

**Given** 积分变更
**When** 修改结果后
**Then** 所有受影响用户的积分即时更新
**And** 积分变更历史可追溯（记录每次修改的时间戳和变更内容）

**Given** 并发安全
**When** 管理员确认修改
**Then** 整个撤销+重算过程为原子操作（全部成功或全部失败）
**And** 关键操作失败显示错误提示，可重试
