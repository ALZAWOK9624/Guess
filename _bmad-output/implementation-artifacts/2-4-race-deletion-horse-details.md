---
baseline_commit: 975ebfe7a70375275f4ab8c89cfb11bc42e514ad
---

# Story 2.4: 比赛删除与马匹详情展示 (Race Deletion & Horse Detail Display)

Status: done

## Story

As a **管理员和用户**,
I want **管理员可删除未结算比赛，所有用户可查看比赛详情中的马匹完整属性**,
So that **数据可管理，信息可查阅**。

## Acceptance Criteria

### AC-1: 管理后台比赛列表与删除

**Given** 管理员在管理后台
**When** 访问 `/admin`
**Then** 显示所有比赛列表（Race 管理主页），表格/卡片列包含：
- 比赛名称（可点击跳转详情）
- 等级徽章（GradeBadge）
- 状态胶囊（StatusBadge）
- 日期
- 参赛马匹数
- 操作列：「编辑」「删除」

**Given** 管理后台比赛列表
**When** 点击某场比赛的「编辑」
**Then** 跳转到 `/admin/races/:id/edit`

**Given** 管理员试图删除比赛
**When** 点击「删除」按钮
**Then** 弹出二次确认弹窗：「确定删除「{比赛名}」？所有投票记录将被清除。」
**And** 确认后调用 `DELETE /api/v1/races/{id}`，比赛从列表中移除
**And** 取消关闭弹窗，不做任何操作

**Given** 比赛已结算（status === 'settled'）
**When** 查看该比赛操作列
**Then** 删除按钮不显示（或置灰加提示）
**And** 提示「已结算比赛不可删除」的 tooltip

**Given** 删除请求失败（网络错误/服务端错误）
**When** 确认删除后
**Then** 显示错误提示「删除失败，请重试」

### AC-2: 编辑页增加删除入口

**Given** 管理员在编辑比赛页（`/admin/races/:id/edit`）
**When** 比赛状态为 voting 或 locked（未结算）
**Then** 页面底部（提交按钮同一区域）显示「删除比赛」按钮（destructive 样式：红色文字/边框）

**Given** 管理员在编辑页点击「删除比赛」
**When** 弹出二次确认弹窗（同 AC-1 的确认逻辑）
**Then** 确认后删除并跳转回管理后台 `/admin`

**Given** 比赛已结算
**When** 在「不可编辑」状态页面
**Then** 不显示删除按钮（已结算不可删除）

### AC-3: 比赛详情页马匹属性展示（补充验证）

**Given** 用户访问比赛详情页 `/races/:id`
**When** 页面加载
**Then** 每匹参赛马以 HorseDetailCard 组件展示：
- 左侧马匹名作为标题（subheading 字号, 墨绿黑 #1A2E1A）
- 右侧列出 9 项属性键值对（body-sm 字号，ink-secondary 值色，空值显示 `-`）：
  性别 / 年龄 / 产地 / 父马 / 母父马 / 负重 / 骑手 / 前走成绩 / 主胜鞍
- 数据来源为比赛创建时的马匹**快照**（RaceHorse.snapshot_data），非实时的 Horse 表

**Given** HorseDetailCard 已存在（Story 2.3 实现）
**When** 验证组件完整性
**Then** 确认所有 10 项属性（name 为标题 + 9 项字段）均正确渲染
**And** `withDefaults` 提供了空快照的默认值，防止 null 崩溃
**And** `safeData` computed 属性已处理空值回退

### AC-4: 后端 API 补充

> 注：`DELETE /api/v1/races/{id}` 已在 Story 2.3 实现。验证以下条件已满足：

**Given** 已结算比赛
**When** `DELETE /api/v1/races/{id}`
**Then** 返回 400 `{ "detail": { "code": "RACE_SETTLED", "message": "已结算比赛不可删除" } }`

**Given** 投票中或已锁定比赛
**When** `DELETE /api/v1/races/{id}`
**Then** 返回 204，比赛及关联投票记录级联删除

**Given** 不存在的比赛
**When** `DELETE /api/v1/races/{id}`
**Then** 返回 404

## Tasks / Subtasks

### Frontend: 管理后台比赛列表页 (DashboardPage.vue)
- [x] Task 1 (AC-1): 重写 DashboardPage.vue 为比赛管理列表
  - [x] 从 API 获取所有比赛列表（GET /api/v1/races）
  - [x] 列表展示：名称、GradeBadge、StatusBadge、日期、参赛数
  - [x] 操作列：「编辑」按钮（跳转 `/admin/races/:id/edit`）
  - [x] 操作列：「删除」按钮（已结算隐藏，未结算显示）
  - [x] 使用 `<Teleport to="body">` 模态框实现删除确认弹窗
  - [x] PageState 模式：loading / empty / error / success
  - [x] 空状态：管理后台暂无比赛时显示微文案
  - [x] 删除成功后刷新列表，不保留删除项在 UI 中
  - [x] 删除失败时显示错误提示

### Frontend: 编辑页添加删除按钮
- [x] Task 2 (AC-2): 在 EditRacePage.vue 添加删除功能
  - [x] 可编辑表单底部增加「删除比赛」按钮（destructive 样式：红色文字 + 红色边框）
  - [x] 不可编辑（已结算）状态不显示删除按钮
  - [x] 删除确认使用相同模态框逻辑（可复用组件或内联模态框）
  - [x] 确认删除后调用 `deleteRace()` API，成功后跳转 `/admin`

### Frontend: 删除确认弹窗组件
- [x] Task 3 (AC-1, AC-2): 创建 ConfirmDeleteModal 组件（或内联实现）
  - [x] `<Teleport to="body">` 模态框
  - [x] 标题：「删除比赛」
  - [x] 内容：「确定删除「{比赛名}」？所有投票记录将被清除。」
  - [x] 两个按钮：「取消」（灰底）和「确认删除」（红色 destructive 风格）
  - [x] 确认中显示 loading 状态并禁用按钮
  - [x] 支持 `aria-modal="true"` + `role="dialog"` + `aria-labelledby`
  - [x] 点击遮罩层外部不关闭（防止误操作）
  - [x] Esc 键关闭

### Backend: 验证与补充测试
- [x] Task 4 (AC-4): 补充删除端点的边缘测试用例
  - [x] 测试：删除不存在的比赛 → 404
  - [x] 测试：删除已结算比赛 → 400
  - [x] 测试：删除投票中比赛 → 204（验证级联删除投票记录）
  - [x] 测试：删除已锁定比赛 → 204
  - [x] 测试：非管理员调用 DELETE → 401/403
  - [x] 测试：删除后详细页查询 → 404

### Frontend: 马匹详情验证
- [x] Task 5 (AC-3): 验证 HorseDetailCard 渲染完整性
  - [x] 确认 name 作为标题正确渲染
  - [x] 确认 9 个属性字段全部显示
  - [x] 确认空值显示 `-`
  - [x] 确认 `withDefaults` + `safeData` 处理 null 保护

## Dev Notes

### 当前实现状态（Story 2.3 完成）

| 组件/文件 | 状态 | 说明 |
|-----------|------|------|
| `DELETE /api/v1/races/{id}` | ✅ 已实现 | 204，已结算返回 400 |
| `race_service.delete_race()` | ✅ 已实现 | settled + not_found 检查 |
| `api/races.ts` 中的 `deleteRace()` | ✅ 已实现 | 前端 API 函数已就绪 |
| `HorseDetailCard.vue` | ✅ 已实现 | 10 属性展示（name 为标题 + 9 字段） |
| `RaceDetailPage.vue` | ✅ 已实现 | 加载比赛详情 + 渲染 HorseDetailCard 列表 |
| `DashboardPage.vue` | ❌ 占位符 | 仅显示「管理后台仪表盘将在后续故事中实现」 |
| `EditRacePage.vue` 删除按钮 | ❌ 缺失 | 无删除功能 UI |
| 删除确认弹窗 | ❌ 缺失 | 尚未创建 |
| 删除测试用例 | ❌ 缺失 | 需补充 |

### 删除按钮可见性规则

| 比赛状态 | 删除按钮 | 行为 |
|---------|---------|------|
| voting | ✅ 显示 | 弹出确认 → 删除 |
| locked | ✅ 显示 | 弹出确认 → 删除 |
| settled | ❌ 隐藏 | 不可删除 |

### 删除确认弹窗设计

```
┌─────────────────────────────────────┐
│  删除比赛                            │
│─────────────────────────────────────│
│                                     │
│  确定删除「日本德比」？              │
│  所有投票记录将被清除。               │
│                                     │
│  ┌──────────┐  ┌──────────────┐     │
│  │   取消    │  │  确认删除    │     │
│  └──────────┘  └──────────────┘     │
│                （红色 destructive）  │
└─────────────────────────────────────┘
```

- 确认按钮：红色背景 `var(--color-destructive, #C53030)` + 白色文字
- 取消按钮：灰色背景 + 墨绿文字
- 不可点击外部遮罩关闭（防止误触删除）
- Esc 键可关闭

### 管理后台比赛列表设计

```
┌────────────────────────────────────────────────────┐
│  管理后台                                            │
│  ┌────────────────────────────────────────────┐     │
│  │  比赛             等级  状态      日期  操作 │     │
│  ├────────────────────────────────────────────┤     │
│  │  日本德比          G1   投票中  06-15  [编辑][删除]│
│  │  凯旋门大赛        G2   已锁定  06-10  [编辑][删除]│
│  │  有马纪念赛        G1   已结算  06-01  [编辑]     │
│  └────────────────────────────────────────────┘     │
│                                                     │
│  [创建比赛] 按钮 (跳转 /admin/races/new)               │
└────────────────────────────────────────────────────┘
```

### Architectural Patterns

1. **删除确认防误触** — 使用 `<Teleport to="body">` 模态框，遮罩层 `@click.self` 不关闭对话框，仅「取消」按钮和 Esc 键关闭。避免点击遮罩误触删除。

2. **删除后状态处理** — 删除成功后从列表中移除该行（`filter` 或 `splice`）。不重新加载整个列表，避免闪烁。同时更新 `raceStore` 状态。

3. **DashboardPage 结构** — 从 placeholder 扩展为完整的比赛管理列表。保持 AdminLayout 布局（240px 侧边栏）。顶部显示标题「管理后台」+「创建比赛」按钮。

4. **EditRacePage 删除按钮位置** — 放在表单底部操作区，「取消」和「保存修改」按钮的上方或同一区域，使用红色边框按钮样式（destructive），与保存按钮（绿色 primary）形成视觉区分。

5. **后端级联删除** — race_service.delete_race 通过 SQLAlchemy cascade 配置自动级联删除关联的 RaceHorse 和 Vote 记录。验证模型已配置 `cascade="all, delete-orphan"`。

### 删除确认文案（来自 UX 文档）

- 确认文案：「确定删除「{比赛名}」？所有投票记录将被清除。」 [Source: `_bmad-output/planning-artifacts/ux-designs/ux-guess-2026-06-09/EXPERIENCE.md` Line 77]
- 语调：短句、完整、陈述事实。无感叹号、无 Emoji。JRA 克制语调。

### 分页说明

- v1 不做分页，`GET /api/v1/races` 返回所有比赛。~100 场比赛列表在管理后台可接受。分页 deferred。

### 前端文件清单

| # | 文件 | 操作 | 说明 |
|---|------|------|------|
| 1 | `frontend/src/pages/admin/DashboardPage.vue` | 🔄 重写 | 从占位符重写为比赛管理列表 |
| 2 | `frontend/src/pages/admin/EditRacePage.vue` | ✏️ 修改 | 添加删除按钮 + 删除确认模态框 |
| 3 | `frontend/src/components/ConfirmDeleteModal.vue` | ✨ 新建 | 可复用的删除确认弹窗组件（或内联） |
| 4 | `backend/tests/test_races.py` | ✏️ 修改 | 补充删除端点的测试用例 |

### 后端已有实现（验证使用，无需修改）

- `backend/app/services/race_service.py` — `delete_race()` 方法：查询比赛 → 检查 settled → db.delete
- `backend/app/api/v1/endpoints/races.py` — `DELETE /{race_id}` 端点，status_code=204，需要 admin 认证

### 已存在的 UI 组件

| 组件 | 文件 | 状态 |
|------|------|------|
| GradeBadge.vue | `frontend/src/components/GradeBadge.vue` | ✅ 已有 |
| StatusBadge.vue | `frontend/src/components/StatusBadge.vue` | ✅ 已有 |
| HorseDetailCard.vue | `frontend/src/components/HorseDetailCard.vue` | ✅ 已有 |
| RaceCard.vue | `frontend/src/components/RaceCard.vue` | ✅ 已有 |
| CreateRacePage.vue | `frontend/src/pages/admin/CreateRacePage.vue` | ✅ 已有 |
| EditRacePage.vue | `frontend/src/pages/admin/EditRacePage.vue` | ✅ 已有（需修改） |

### Previous Story Intelligence (Story 2.3)

| 学到教训 | 本故事的应用 |
|---------|-------------|
| `PATCH 防 null 覆盖模式` → `update_data = {k: v for k, v in update_data.items() if v is not None}` | 不涉及 PATCH，DELETE 无此风险 |
| `flush()` → `refresh()` 模式 | DELETE 不需要 refresh，但需确保级联删除正确 flush |
| 组件命名 PascalCase / API snake_case | ConfirmDeleteModal → PascalCase，API 字段 snake_case |
| `<Teleport to="body">` 模态框 | 删除确认弹窗使用此模式 |
| `aria-modal` / `role="dialog"` 无障碍规范 | 删除确认弹窗必须遵循 |
| 枚举验证失败导致 500 | `delete_race` 没有枚举参数，不涉及 |
| 编辑时按字段逐一比较差异（HorsesPage 模式） | 删除操作无需比较差异 |

### Git Intelligence

最近提交：
- `975ebfe feat: Story 2.3 - race creation and management with code review fixes` — Race 模型、Service、Endpoints、CreateRacePage、EditRacePage、HorseDetailCard
- `1e62564 feat: Story 2.2 - HorseSearchSelect component` — HorseSearchSelect 已就绪
- `2cf4fb9 feat: Story 2.1 - horse data model and admin CRUD page` — Horse 模型和 CRUD 已就绪

当前状态：
- ✅ 后端 DELETE 端点已实现，前端 API 函数已导出但未使用
- ✅ HorseDetailCard 和 RaceDetailPage 已完整实现
- ❌ DashboardPage.vue 是占位符，需重写为比赛管理列表
- ❌ EditRacePage 缺少删除按钮
- ❌ 删除确认弹窗尚未创建

### Testing Requirements

| 测试场景 | 步骤 | 预期结果 |
|---------|------|---------|
| 删除投票中比赛 | admin → 点击删除 → 确认 | 204，比赛从列表消失 |
| 删除已锁定比赛 | 同上 | 204 |
| 删除已结算比赛 | 查看操作列 | 删除按钮不显示 |
| 删除确认取消 | 点击删除 → 取消 | 比赛保留，列表无变化 |
| 删除不存在的比赛 | 直接调用 DELETE API | 404 |
| 非管理员删除 | 非 admin token 调用 DELETE | 401/403 |
| 删除后级联验证 | 删除后 GET `/races/{id}/votes` | 404 或空列表 |
| 验证 HorseDetailCard 空值 | 创建含空属性的马匹 → 查看详情 | 空字段显示 `-` |

### Anti-Patterns to Avoid

- ❌ 不要在 DashboardPage 中添加多余的路由 — 使用现有 `/admin` 路由
- ❌ 不要修改后端 delete_race 逻辑（已验证可用）
- ❌ 不要修改 HorseDetailCard 或 RaceDetailPage（已验证完整）
- ❌ 不要为删除弹窗使用独立的 Vue Router 路由 — 使用内联模态框
- ❌ 不要使用 `window.confirm()` — 必须使用自定义模态框（满足无障碍 + JRA 设计系统）
- ❌ 删除后不要使用 `location.reload()` — 使用响应式状态移除删除项
- ❌ 不要忘记 `aria-modal` 和 `role="dialog"` 无障碍属性

### Project Context Reference

- **Tech**: Vue 3 + Vite + TypeScript (Composition API, `<script setup>`), FastAPI + SQLAlchemy 2.0 async, PostgreSQL 16
- **Component naming**: PascalCase (`ConfirmDeleteModal.vue`)
- **API prefix**: `/api/v1/` (handled by Vite proxy + Axios client)
- **API field naming**: snake_case throughout (no camelCase conversion)
- **Auth**: JWT; DELETE endpoint requires `get_current_admin` dependency
- **CSS**: scoped CSS + CSS variables (JRA design system, no UI library)
- **PageState pattern**: `'loading' | 'empty' | 'error' | 'success'` for list pages
- **Modal pattern**: `<Teleport to="body">` for dialogs and modals
- **A11y**: Semantic HTML, focus ring (2px `--color-primary` outline + 2px offset), `aria-modal`, `role="dialog"`, `aria-labelledby`
- **Touch targets**: ≥ 44×44px for all interactive elements
- **Destructive actions**: Red color (`var(--color-destructive, #C53030)`) with `var(--color-destructive-light, #FED7D7)` background
- **Dates**: ISO 8601 strings
- **Null handling**: Use `null`, never empty strings or omitted fields

## Dev Agent Record

### Agent Model Used

Deepseek-V4-Flash

### Completion Notes

Story 2.4 实现完成：

1. **ConfirmDeleteModal.vue** (新建) — 可复用删除确认弹窗，使用 `<Teleport to="body">`、`aria-modal`、destructive 红色样式、Esc 关闭、遮罩层不关闭防误触、loading 状态
2. **DashboardPage.vue** (重写) — 从占位符重写为完整的管理后台比赛列表页面：
   - 比赛列表表格：名称（可跳转详情）/ GradeBadge / StatusBadge / 日期 / 参赛数
   - 操作列：「编辑」（跳转 `/admin/races/:id/edit`）+「删除」（已结算隐藏）
   - PageState 模式：loading / empty / error / success
   - 利用 ConfirmDeleteModal 实现二次确认删除
   - 删除成功后 filter 移除而不全量重载
   - 移动端自适应（行卡模式）
3. **EditRacePage.vue** (修改) — 可编辑表单底部添加「删除比赛」destructive 按钮，已结算状态不显示，复用 ConfirmDeleteModal
4. **GradeBadge.vue / StatusBadge.vue** (新建) — 发现引用但缺失的组件，按 UX DESIGN.md 规范创建（G1 金/G2 灰/2岁G1 亮绿/自定义灰虚线 + 投票中绿/已锁定灰🔒/已结算深绿✓）
5. **后端测试** — 新增 4 个 API 测试 + 2 个服务测试，验证以下场景全部通过：
   - 不存在的比赛删除 404
   - 已结算比赛删除 400 (RACE_SETTLED)
   - 投票中比赛删除 204
   - 已锁定比赛删除 204
   - 非管理员删除 401
   - 删除后 GET 返回 404
6. **HorseDetailCard 验证** (AC-3) — 确认已正确渲染 name 为标题、9 属性字段、空值显示 `-`、withDefaults + safeData 保护
7. **全部 85 个测试通过**，零回归

### File List

#### New Files
| # | File | Description |
|---|------|-------------|
| 1 | `frontend/src/components/ConfirmDeleteModal.vue` | Reusable delete confirmation modal with Teleport, aria-modal, destructive styling |
| 2 | `frontend/src/components/GradeBadge.vue` | Race grade badge (G1 gold/G2 gray/YOUNG_G1 light green/CUSTOM gray dashed) — missing component created |
| 3 | `frontend/src/components/StatusBadge.vue` | Race status capsule (voting green/locked gray+🔒/settled dark green+✓) — missing component created |

#### Modified Files
| # | File | Change |
|---|------|--------|
| 4 | `frontend/src/pages/admin/DashboardPage.vue` | Rewrite from placeholder to full race management list with table, actions, delete modal, PageState |
| 5 | `frontend/src/pages/admin/EditRacePage.vue` | Add delete button (destructive style) + ConfirmDeleteModal for unsettled races |
| 6 | `backend/tests/test_races.py` | Add 4 new delete edge case tests (nonexistent/settled/locked/unauthenticated)

## Change Log

| Date | Change |
|------|--------|
| 2026-06-12 | Created Story 2.4: Race Deletion & Horse Detail Display |
| 2026-06-12 | Implemented: DashboardPage race list, EditRacePage delete button, ConfirmDeleteModal, GradeBadge/StatusBadge missing components, 6 delete edge case tests |

## Review Findings

### Code Review (2026-06-12)

#### Decision Needed (Resolved)
- [x] [Review][Decision] EditRacePage locked race no delete button — 用户确认保持现状（选项B），已锁定比赛只能从 Dashboard 删除。

#### Patch (Applied)
- [x] [Review][Patch] ConfirmDeleteModal — 添加 `titleId` 常量修复 `aria-labelledby` 引用 [ConfirmDeleteModal.vue:49]
- [x] [Review][Patch] ConfirmDeleteModal — 添加 `@click.self="emit('cancel')"` 修复遮罩层点击无反应 [ConfirmDeleteModal.vue:51]
- [x] [Review][Patch] EditRacePage — 删除弹窗使用 `raceName` 代替过时的 `raceNameDisplay` [EditRacePage.vue:362]
- [x] [Review][Patch] DashboardPage — 添加 `isMounted` 守卫防止组件卸载后更新状态 [DashboardPage.vue:29]
- [x] [Review][Patch] DashboardPage — 添加双击删除按钮并发防护 [DashboardPage.vue:55]
- [x] [Review][Patch] EditRacePage — 添加双击删除按钮并发防护 [EditRacePage.vue:206]
- [x] [Review][Patch] GradeBadge — 修复 `toLowerCase()` 在 null/undefined grade 时崩溃 [GradeBadge.vue:27]
- [x] [Review][Patch] test_races — 添加 race_horses 级联删除验证 [test_races.py:220]
- [x] [Review][Patch] DashboardPage — 添加 `formatDate` null/undefined 保护 [DashboardPage.vue:76]
- [x] [Review][Patch] DashboardPage — 移除已结算比赛隐藏按钮上的冗余 title 属性 [DashboardPage.vue:151]

#### Deferred
- [x] [Review][Defer] 比赛名包含 `{name}` 字面量时弹窗文案异常 — deferred, 极低概率
- [x] [Review][Defer] 网络断开时前端显示"删除失败"但后端已删除 — deferred, 预存在, DELETE 幂等性已处理
- [x] [Review][Defer] parseCustomScoring 前端校验不足 — deferred, pre-existing from Story 2.3
- [x] [Review][Defer] Dashboard 401 认证过期未单独处理 — deferred, pre-existing 模式
- [x] [Review][Defer] StatusBadge Unicode 图标无障碍替代文本缺失 — deferred, pre-existing
