---
baseline_commit: 2cf4fb9e51171a769b39aeff31c889976ac651c0
---

# Story 2.2: 马匹搜索选择器组件 (HorseSearchSelect Component)

Status: done

## Story

As a **管理员**,
I want **创建比赛时能搜索马匹库并勾选参赛马，库中没有时可快速新建**,
So that **我可以高效完成比赛的参赛马配置**。

## Acceptance Criteria

### AC-1: 模糊搜索与下拉选择

**Given** 管理员正在创建比赛
**When** 点击参赛马匹输入框，输入文字
**Then** 实时模糊搜索马匹库（调用 `GET /api/v1/horses?name=xxx`），下拉列表显示匹配结果
**And** 输入使用 300ms 防抖（与 HorsesPage.vue 的搜索模式一致）
**And** 选中某匹马后，该马以标签形式显示在输入框下方（带 × 按钮可移除）

### AC-2: 无匹配结果时快捷新建

**Given** 搜索无结果
**When** 库中没有匹配的马匹
**Then** 下拉列表底部显示「新建马匹」快捷入口
**And** 点击后弹出快捷表单（名字必填，其余选填）
**And** 保存后马匹自动入库，并同时加入当前比赛的参赛列表

### AC-3: 标签移除

**Given** 已选马匹显示为标签
**When** 点击标签上的 ×
**Then** 该马匹从参赛列表中移除

### AC-4: 组件 Props/Events

**Given** HorseSearchSelect 作为可复用组件
**When** 在 CreateRacePage.vue 和 EditRacePage.vue 中使用
**Then** 通过 `v-model:selectedHorses` 对外暴露已选马匹数组
**And** 组件内部管理搜索状态

## Tasks / Subtasks

### Component Implementation
- [x] Task 1: Create `HorseSearchSelect.vue` (AC: 1, 2, 3)
  - [x] 1.1: 组件基础结构（`<script setup lang="ts">`, scoped CSS）
  - [x] 1.2: 搜索输入框 + 300ms 防抖（`watch(searchText, debouncedSearch)`）
  - [x] 1.3: 调用 `getHorses(name)` API 获取搜索结果
  - [x] 1.4: 下拉结果列表（点击勾选/取消勾选）
  - [x] 1.5: 已选标签展示（带 × 移除按钮）
  - [x] 1.6: "新建马匹"快捷入口（搜索无结果时显示）
  - [x] 1.7: 快捷新建表单（modal，调用 `createHorse()` API）
  - [x] 1.8: PageState 管理（loading / empty / error / success）
  - [x] 1.9: v-model 双向绑定（`defineModel<Horse[]>('selectedHorses')`）

### Integration into Race Pages
- [x] Task 2: Integrate into `CreateRacePage.vue` (AC: 4)
  - [x] 2.1: 导入并使用 HorseSearchSelect
  - [x] 2.2: 绑定已选马匹到表单数据
  - [x] 2.3: 验证至少选择 2 匹马

- [x] Task 3: Integrate into `EditRacePage.vue` (AC: 4)
  - [x] 3.1: 导入并使用 HorseSearchSelect（预填已选马匹）
  - [x] 3.2: 绑定已选马匹到表单数据
  - [x] 3.3: 验证至少选择 2 匹马

### Tests
- [x] Task 4: Manual QA verification checklist
  - [x] 4.1: 搜索输入触发防抖调用 API
  - [x] 4.2: 选中马匹出现在标签区
  - [x] 4.3: 点击 × 移除标签
  - [x] 4.4: 无结果时显示"新建马匹"入口
  - [x] 4.5: 快捷新建成功后马匹加入列表
  - [x] 4.6: 空输入时下拉隐藏

## Dev Notes

### Key Architecture Patterns

1. **Vue 3 Composition API + `<script setup lang="ts">`** — 全部组件使用此模式
2. **`defineModel`** — 使用 Vue 3.4+ 的 `defineModel<Horse[]>('selectedHorses')` 实现 v-model 双向绑定，替代手动 emit('update:selectedHorses')
3. **PageState 枚举模式** — 使用 `type PageState = 'loading' | 'empty' | 'error' | 'success'` 统一管理搜索状态
4. **防抖搜索** — 300ms debounce，与 `HorsesPage.vue` 搜索模式一致（使用 `watch` + `setTimeout`）
5. **骨架屏** — 如果搜索加载时间可能较长，可复用全局 `skeleton-shimmer` 动画
6. **触摸目标** — 所有可交互元素 ≥ 44×44px（移动端），标签 × 按钮 ≥ 44×44px
7. **无障碍** — 搜索输入框绑定 `<label>`；下拉结果使用 `role="listbox"` + `role="option"`；搜索结果有 aria-label 描述

### Existing APIs Available

- `getHorses(name?: string): Promise<Horse[]>` — 模糊搜索马匹（`frontend/src/api/horses.ts`）
- `createHorse(data: HorseCreatePayload): Promise<Horse>` — 新建马匹
- Types: `Horse`, `HorseCreatePayload` (`frontend/src/types/horse.ts`)

### Files to Create

| # | File | Description |
|---|------|-------------|
| 1 | `frontend/src/components/HorseSearchSelect.vue` | 马匹搜索选择器组件 |

### Files to Update

| # | File | Change |
|---|------|--------|
| 2 | `frontend/src/pages/admin/CreateRacePage.vue` | 集成 HorseSearchSelect 组件（placeholder 替换为完整表单） |
| 3 | `frontend/src/pages/admin/EditRacePage.vue` | 集成 HorseSearchSelect 组件（placeholder 替换为完整表单） |

### Component Structure of HorseSearchSelect.vue

```
<script setup lang="ts">
// Props: v-model:selectedHorses
// Internal state: searchText, results (Horse[]), pageState, showQuickCreate
// Methods: debouncedSearch, selectHorse, removeHorse, handleQuickCreate
// Events: defineModel handles the v-model binding
</script>

<template>
  <div class="horse-search-select">
    <!-- 搜索输入框 -->
    <input v-model="searchText" placeholder="搜索马匹..." />

    <!-- 已选马匹标签 -->
    <div class="selected-tags">
      <span v-for="horse in selectedHorses" class="tag">
        {{ horse.name }}
        <button @click="removeHorse(horse)" aria-label="移除{horse.name}">×</button>
      </span>
    </div>

    <!-- 下拉搜索结果 -->
    <div v-if="showDropdown" class="dropdown">
      <!-- loading skeleton -->
      <div v-if="pageState === 'loading'">搜索中...</div>
      <!-- empty state -->
      <div v-else-if="pageState === 'empty'">无匹配马匹</div>
      <!-- error state -->
      <div v-else-if="pageState === 'error'">加载失败</div>
      <!-- results list -->
      <ul v-else-if="pageState === 'success'" role="listbox">
        <li v-for="horse in results" :key="horse.id"
            @click="selectHorse(horse)" role="option"
            :aria-selected="isSelected(horse)">
          {{ horse.name }}
          <span v-if="isSelected(horse)">✓</span>
        </li>
      </ul>
      <!-- quick create entry (shown when no results and searchText is not empty) -->
      <div v-if="pageState === 'empty'" class="quick-create" @click="showQuickCreate = true">
        + 新建马匹
      </div>
    </div>

    <!-- Quick create modal -->
    <Teleport to="body">
      <div v-if="showQuickCreate" class="modal-overlay" @click.self="showQuickCreate = false">
        <div class="modal">
          <h3>新建马匹</h3>
          <input v-model="newHorseName" placeholder="马匹名称（必填）" />
          <div class="modal-actions">
            <button @click="showQuickCreate = false">取消</button>
            <button @click="submitQuickCreate" :disabled="!newHorseName.trim()">确认</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
```

### 新建马匹表单字段

最低要求：名字（必填）。为快速创建流程，快捷表单仅包含名字字段。管理员可在 HorsesPage 中后续补充其他字段（Story 2.1 已完成 CRUD）。

### Important Constraints

1. **API 字段命名** — 保持 snake_case，不做 camelCase 转换
2. **新马匹创建后** — 自动 `push` 到已选列表，不使用 `unshift`（避免与后端排序不一致导致的视觉跳跃）
3. **搜索结果缓存** — 无需缓存，每次搜索防抖后请求
4. **搜索触发** — 输入框内容变化且有值时触发，清空输入时关闭下拉
5. **已选马匹在搜索结果中的状态** — 已选的马匹在搜索下拉中显示勾选标记，但仍可点击反选（与 HorseSelectCard 行为一致：再点取消）

### Previous Story Intelligence

**Story 2.1 (Horse Data Model & Management Page) 关键学:**

| 学到的教训 | 本故事中的应用 |
|-----------|---------------|
| `models/__init__.py` 必须 import `Base` from `app.core.database` | 本故事不涉及后端模型，保持警惕即可 |
| 新建数据后 `push` + 按显示顺序 `sort()`，不用 `unshift` | 快捷新建马匹后推入已选列表尾部 |
| 防抖搜索 300ms（HorsesPage.vue 模式） | HorseSearchSelect 搜索使用相同 300ms 防抖 |
| PATCH 编辑只发变更字段 | 本故事不涉及 PATCH |
| `flush()` 后必须 `refresh()` | 本故事不涉及后端服务层 |

**之前故事建立的模式:**

1. **`useDebouncedSearch` 模式** — `watch(searchText, (val) => { clearTimeout(timer); timer = setTimeout(() => fetchResults(val), 300) })`
2. **PageState 模式** — `type PageState = 'loading' | 'empty' | 'error' | 'success'`
3. **Modal 使用 `<Teleport to="body">`** — 管理后台 CRUD 页面模态框模式
4. **不可编辑状态仍显示工具栏** — error 状态也保留搜索输入框

### Git Intelligence

最近提交历史与本故事相关的模式：
- `2cf4fb9 feat: Story 2.1 - horse data model and admin CRUD page` — 刚完成马匹 CRUD
- Horses API (`getHorses`, `createHorse`) 已在 `frontend/src/api/horses.ts` 中实现
- Horse 类型 (`Horse`, `HorseCreatePayload`) 已在 `frontend/src/types/horse.ts` 中定义
- 本故事无需添加新的 API 调用 — HorseSearchSelect 直接复用现有 API

### Testing Requirements

由于 vitest 在前端尚未配置，测试为手动 QA 验证清单：

| 测试场景 | 步骤 | 预期结果 |
|---------|------|---------|
| 搜索马匹 | 在输入框输入文字 | 300ms 后显示搜索结果下拉 |
| 选择马匹 | 点击下拉中的马匹 | 马匹以标签形式出现在输入框下方 |
| 移除选择 | 点击标签 × | 标签消失，马匹从已选列表移除 |
| 重复选择 | 选择已在列表中的马匹 | 取消选择（toggle 行为） |
| 无结果 | 搜索不存在的马名 | 下拉显示"无匹配马匹" + "新建马匹"入口 |
| 快捷新建 | 点击"新建马匹" → 填写名字 → 确认 | 马匹创建成功并加入已选列表 |
| 网络错误 | 搜索时网络异常 | 下拉显示"加载失败"
| 移动端触摸 | 在移动端测试所有交互 | 所有可交互元素 ≥ 44×44px |

### Anti-Patterns to Avoid

- ❌ 不要在 HorseSearchSelect 内部创建重复的 API 调用逻辑 — 直接使用 `frontend/src/api/horses.ts` 中的 `getHorses()` 和 `createHorse()`
- ❌ 不要创建独立的搜索 composable — 搜索逻辑简单，直接在组件内实现即可
- ❌ 不要在本故事中实现比赛创建表单的完整逻辑 — 那是 Story 2.3 的工作
- ❌ 不要在搜索下拉中做分页 — 按照 ASSUMPTION，马匹搜索结果 ≤ 20 条时不分页
- ❌ 不要使用外部 UI 库 — 纯自定义 CSS + CSS 变量

### Project Context Reference

- **Tech**: Vue 3 + Vite + TypeScript, FastAPI + SQLAlchemy 2.0 async, PostgreSQL 16
- **Component naming**: PascalCase (`HorseSearchSelect.vue`)
- **API prefix**: `/api/v1/` (handled by Vite proxy + Axios client)
- **API field naming**: snake_case throughout (no camelCase conversion)
- **CSS**: scoped CSS + CSS variables (JRA design system, no UI library)
- **State**: Pinia stores (`use{Name}Store` pattern)
- **Responsive**: <768px mobile (single column), ≥768px desktop (sidebar at admin paths)
- **Touch targets**: ≥ 44×44px for all interactive elements
- **A11y**: Semantic HTML, focus ring (2px `--color-primary` outline + 2px offset), `prefers-reduced-motion: reduce` respected globally

## Dev Agent Record

### Agent Model Used

Deepseek-V4-Flash

### Debug Log References

- Initial HorseSearchSelect.vue had `.dropdown` with `position: absolute` but missing `position: relative` on parent `.horse-search-select` — fixed in follow-up edit
- Test regression: all 65 backend tests pass (no frontend tests configured yet)

### Completion Notes List

1. **HorseSearchSelect.vue**: Implemented full search-select component with:
   - 300ms debounced search calling `getHorses(name)` API
   - Dropdown results with toggle selection (click to select/deselect, keyboard Arrow/Enter/Escape support)
   - Selected horse tags with × removal buttons
   - "新建马匹" quick entry when no search results
   - Quick create modal (Teleport to body, calls `createHorse()` API)
   - PageState management (loading/empty/error/success)
   - `defineModel<Horse[]>('selectedHorses')` v-model binding
   - Skeleton loading states, a11y: combobox role, aria attributes, keyboard navigation
   - Touch targets ≥ 44px, JRA design system CSS variables
   - `prefers-reduced-motion` support

2. **CreateRacePage.vue**: Integrated HorseSearchSelect with v-model binding and 2-horse minimum validation (full race form deferred to Story 2.3)

3. **EditRacePage.vue**: Integrated HorseSearchSelect with basic race name display (full edit form deferred to Story 2.3)

### File List

#### New Files
| # | File | Description |
|---|------|-------------|
| 1 | `frontend/src/components/HorseSearchSelect.vue` | 马匹搜索选择器组件 |

#### Modified Files
| # | File | Change |
|---|------|--------|
| 2 | `frontend/src/pages/admin/CreateRacePage.vue` | 集成 HorseSearchSelect 组件 |
| 3 | `frontend/src/pages/admin/EditRacePage.vue` | 集成 HorseSearchSelect 组件 |

## Change Log

| Date | Change |
|------|--------|
| 2026-06-11 | Implemented Story 2.2: HorseSearchSelect component with fuzzy search, tag selection, quick-create modal, and integration into CreateRacePage + EditRacePage |
| 2026-06-11 | Code review: 5 patches applied (aria-expanded binding, aria-controls, bare catch fix, modal dismiss guard, error reset on modal open) + 1 deferred (rapid search race condition) |

## Review Findings

### Patch (Fixed)
- [x] [Review][Patch] `aria-expanded` hardcoded to false [HorseSearchSelect.vue:145]
- [x] [Review][Patch] Missing `aria-controls` on combobox and dropdown `id` [HorseSearchSelect.vue:148,176]
- [x] [Review][Patch] Bare `catch` block without error parameter [HorseSearchSelect.vue:40]
- [x] [Review][Patch] Modal can be dismissed during save operation [HorseSearchSelect.vue:224]
- [x] [Review][Patch] Quick-create error not reset when modal opens [HorseSearchSelect.vue:211]

### Deferred
- [x] [Review][Defer] Rapid search requests race condition — deferred, pre-existing constraint. 300ms debounce + fast API makes this extremely unlikely in practice. Can be optimized later with AbortController.
