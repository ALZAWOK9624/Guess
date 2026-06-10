---
baseline_commit: d740f9b4e4a98654e186bbd346fcc550342e8c8f
---

# Story 1.2: Design Tokens & Navigation Layout

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **用户**,
I want **页面有统一的 JRA 品牌视觉风格和清晰的导航结构**,
So that **我在任何设备上都能流畅浏览和操作**。

## Acceptance Criteria

1. **Given** 前端 CSS 基础设施已搭建
   **When** 浏览器加载任意页面
   **Then** `:root` 中 CSS 自定义属性已定义：竞马绿/冠军金/暖白等 12 色、6 级排版字号、9 级间距值（4~64px）、4 级圆角值
   **And** `variables.css`, `base.css`, `utilities.css` 三个文件按约定分离

2. **Given** 用户访问网站
   **When** 在移动端（<768px）浏览器打开
   **Then** 底部固定导航栏显示「首页」「排行榜」（管理员额外显示「管理」）
   **And** 首页比赛列表为全宽单列布局，两侧 16px 边距
   **And** 底部导航适配 safe-area-inset-bottom（iOS 刘海屏）

3. **Given** 用户在桌面端（≥768px）访问
   **When** 打开首页
   **Then** 顶部固定导航栏显示 Logo + 「首页」「排行榜」+ 登录/用户信息
   **And** 内容区域居中，最大宽度 max-w-7xl (1280px)
   **And** 管理员访问 `/admin` 路径时显示左侧 240px 侧边栏 + 主内容区

4. **Given** 用户在任何设备浏览
   **When** 点击导航项
   **Then** Vue Router 4 按约定路由跳转，路由懒加载生效

## Tasks / Subtasks

- [x] Task 1: 完善 CSS 设计令牌系统 (AC: #1)
  - [x] 更新 `variables.css` — 映射 JRA 完整色板（14 色含 border/ink/surface）、6 级排版、10 级间距、4 级圆角
  - [x] 更新 `base.css` — 完整 reset + 全局样式（body 底色 warm-white、字体栈、scrollbar 样式）
  - [x] 更新 `utilities.css` — 响应式断点工具类、文本排版工具类、间距工具类
  - [x] 在 `index.html` 引入 Barlow Condensed 字体（Google Fonts `wght@400;600;700`）

- [x] Task 2: 实现 AppLayout 公共布局 (AC: #2, #3, #4)
  - [x] 移动端（<768px）：底部固定导航栏，包含首页、排行榜图标+文字、管理员可见管理图标
  - [x] 桌面端（≥768px）：顶部固定导航栏，包含 Logo、首页、排行榜、登录/用户信息
  - [x] 响应式断点：768px 切换移动/桌面布局
  - [x] 底部导航适配 safe-area-inset-bottom（`env(safe-area-inset-bottom)`）
  - [x] 内容区域居中，最大宽度 max-w-7xl (1280px)
  - [x] 使用 Pinia authStore.isAdmin 控制管理入口可见性（占位，Story 1.5b 实现完整认证）
  - [x] 导航项当前路由自动高亮（router-link-active）

- [x] Task 3: 完善 AdminLayout 管理后台布局 (AC: #3, #4)
  - [x] 桌面端：左侧 240px 固定侧边栏，包含仪表盘、比赛管理、马匹库、邀请码导航
  - [x] 移动端（<768px）：隐藏侧边栏，改为汉堡菜单触发的侧栏
  - [x] 侧边栏使用竞马绿背景色，当前导航项高亮
  - [x] 主内容区随容器独立滚动

## Dev Notes

### 要修改的文件（非新建——全部是 UPDATE）

| 文件 | 当前状态 | 修改内容 |
|------|---------|---------|
| `frontend/index.html` | 基础 HTML，无字体引入 | 添加 Barlow Condensed Google Fonts link |
| `frontend/src/assets/styles/variables.css` | 占位令牌，颜色不精确 | 替换为准确 JRA 色板（12+ 色）、添加组件令牌变量 |
| `frontend/src/assets/styles/base.css` | 基础 reset | 完善全局样式：warm-white 底色、字体栈、滚动条、prefers-reduced-motion |
| `frontend/src/assets/styles/utilities.css` | 只有 .sr-only | 添加排版/间距/响应式工具类 |
| `frontend/src/layouts/AppLayout.vue` | `<div><slot/></div>` 占位 | 完整实现响应式导航布局 |
| `frontend/src/layouts/AdminLayout.vue` | 基础侧边栏，无移动端响应 | 完善侧边栏 + 移动端适配 |

### JRA 设计令牌参考（必须精确匹配）

**色板（12 色）：**

```
--color-primary: #1A5632          /* 竞马绿 — 主品牌色 */
--color-primary-light: #2D7A4F   /* 亮绿 — 2岁G1 徽章、success */
--color-primary-dark: #0D3A1F    /* 深绿 — 已结算状态 */
--color-accent: #B8960C           /* 冠军金 — CTA + G1 徽章 */
--color-accent-light: #D4B84A     /* 亮金 — hover */
--color-surface-base: #F8FAF7     /* 暖白 — 页面底色 */
--color-surface-raised: #FFFFFF   /* 纯白 — 卡片/浮层 */
--color-ink-primary: #1A2E1A      /* 墨绿黑 — 正文 */
--color-ink-secondary: #4A5A4A    /* 中灰绿 — 辅助文字 */
--color-ink-disabled: #9CAA9C     /* 禁用文字 */
--color-border-hairline: #D4DCD0  /* 细线 — 分隔线、卡片边框 */
--color-border-strong: #A8B8A4    /* 强边框 — 拖拽卡片 */
--color-destructive: #C53030      /* 红色 — 错误、删除 */
--color-destructive-light: #FED7D7 /* 浅红 — 错误背景 */
```

**排版：**

```
--font-display: 'Barlow Condensed', system-ui, sans-serif  /* 数字/等级 */
--font-body: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif

/* 字号层级 */
--text-display: 36px    /* 600 weight, 1.15 line-height */
--text-heading: 24px    /* 600 weight, 1.25 line-height */
--text-subheading: 18px /* 600 weight, 1.35 line-height */
--text-body: 16px       /* 400 weight, 1.6 line-height */
--text-body-sm: 14px    /* 400 weight, 1.5 line-height */
--text-caption: 12px    /* 400 weight, 1.4 line-height */
```

**间距：** `--spacing-{1|2|3|4|5|6|8|10|12|16}` → 4/8/12/16/20/24/32/40/48/64 px

**圆角：** `--rounded-sm: 6px; --rounded-md: 10px; --rounded-lg: 14px; --rounded-full: 9999px`

**组件令牌（可选，用于后续故事引用的 CSS 变量模式）：**
- `--card-radius: var(--rounded-md)` 等组件级变量可先在 variables.css 中定义注释，由后续组件实现填充

### 导航布局规范

**移动端（<768px）：**
- 底部固定导航栏，`position: fixed; bottom: 0;`
- 使用 `padding-bottom: env(safe-area-inset-bottom)` 适配 iOS 刘海屏
- 导航项：首页图标+文字 / 排行榜图标+文字 / 管理图标+文字（仅管理员）
- 激活项高亮（竞马绿文字色 + 细条指示器）
- 内容区域有 `padding-bottom: 64px` 防止被导航遮挡

**桌面端（≥768px）：**
- 顶部固定导航栏，竞马绿背景，白色文字
- 左侧显示 Logo 文字（"Guess" + 赛马图标）
- 中间：首页、排行榜链接（白色）
- 右侧：未登录显示"登录"按钮，已登录显示用户名
- 内容区域 `max-width: 1280px; margin: 0 auto; padding: 0 16px`
- 导航栏高度 ~ 56px

**管理后台：**
- 桌面端：左侧 240px 固定侧边栏（竞马绿背景）
- 导航项：仪表盘 / 比赛管理 / 马匹库 / 邀请码
- 当前项白色背景高亮
- 移动端：侧边栏隐藏，改为独立页面或顶部按钮触发侧栏

### AppLayout.vue 实现要点

```vue
<script setup lang="ts">
// 使用 authStore 获取登录状态和管理员标记
// 使用 useRoute() 获取当前路由名称以高亮导航项
// 响应式断点通过 CSS media query 控制，无需 JS
// 移动端导航项：home, leaderboard, admin（条件显示）
</script>

<template>
  <div class="app-layout">
    <!-- 桌面端顶部导航 -->
    <header class="desktop-header">
      <div class="header-inner">
        <router-link to="/" class="logo">Guess</router-link>
        <nav class="nav-links">
          <router-link to="/">首页</router-link>
          <router-link to="/leaderboard">排行榜</router-link>
          <router-link v-if="isAdmin" to="/admin">管理</router-link>
        </nav>
        <div class="user-area">
          <!-- 登录/用户信息（占位，完整实现在 1.5b） -->
        </div>
      </div>
    </header>

    <!-- 主内容 -->
    <main class="main-content">
      <slot />
    </main>

    <!-- 移动端底部导航 -->
    <nav class="mobile-bottom-nav">
      <router-link to="/" class="nav-item">首页</router-link>
      <router-link to="/leaderboard" class="nav-item">排行榜</router-link>
      <router-link v-if="isAdmin" to="/admin" class="nav-item">管理</router-link>
    </nav>
  </div>
</template>
```

### AdminLayout.vue 实现要点

```vue
<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="sidebar-header">管理后台</div>
      <nav>
        <router-link to="/admin">仪表盘</router-link>
        <router-link to="/admin/races/new">创建比赛</router-link>
        <router-link to="/admin/horses">马匹管理</router-link>
        <router-link to="/admin/invite-codes">邀请码</router-link>
      </nav>
    </aside>
    <div class="admin-content">
      <slot />
    </div>
  </div>
</template>
```

### 路由配置（维持 Story 1.1 已有配置）

路由定义无需修改。但注意：
- AppLayout.vue 应与 router view 搭配使用（在 App.vue 中包裹 `<router-view>`）
- AdminLayout.vue 用于 admin 路由的子路由（可在页面内部使用布局）
- 当前项目可能尚未在 App.vue 中集成布局组件——AppLayout 应作为全局布局包裹 router-view

### 无障碍要求

- 导航 `<nav>` 标签，底部导航添加 `aria-label="主导航"`
- 导航链接使用语义化 `<router-link>`——Vue Router 自动处理焦点管理
- 字体大小符合 4.5:1 对比度（色板中 `--color-ink-secondary: #4A5A4A` 在暖白背景上 ≥ 4.5:1）
- `prefers-reduced-motion` media query：骨架屏脉冲动画等应被媒体查询禁用

### 测试标准

- **视觉验证（手动）**：在不同视口宽度（375px / 768px / 1280px）下验证导航渲染
- **无单元测试要求**：此故事主要是 CSS + 模板工作

### 重要实现提示

1. **Barlow Condensed 字体**：Google Fonts 链接 → `https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700&display=swap`，在 `index.html` 的 `<head>` 中引入
2. **路由器链接类**：Vue Router 自动添加 `router-link-active` 和 `router-link-exact-active` 类——使用这些类实现导航高亮
3. **safe-area-inset-bottom**：需要 `viewport-fit=cover` 在 meta viewport 中：`<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">` （确认 Story 1.1 已有 `initial-scale=1.0`，需要追加 `viewport-fit=cover`）
4. **用户区域占位**：Story 1.5b 实现完整认证前，用户区域显示静态文本（如"登录"按钮）。使用 `data-is-logged-in` 等 CSS 控制显示/隐藏
5. **manager/admin 权限占位**：使用 `authStore.isAdmin`（将在 Story 1.5a 实现）控制管理入口——当前可硬编码为 `false` 或使用 `import.meta.env.DEV` 用于开发调试
6. **不与 1.5b 冲突**：布局导航中的登录态部分保持骨架/占位状态，不实现完整的 JWT 拦截器或登录跳转逻辑——那些属于 Story 1.5b
7. **样式文件分离**：布局相关的样式使用 `<style scoped>`，CSS 变量放在 `variables.css`（全局可访问）

### References

- [Source: `epics.md` — Story 1.2 验收条件] — 全部 4 条 AC 的 Given/When/Then
- [Source: `DESIGN.md` — 完整色板、排版、间距、圆角定义] — 12 色、6 级字号、9 级间距、4 级圆角
- [Source: `DESIGN.md` — 组件设计规范] — RaceCard、GradeBadge、VoteButton、StatusBadge 等组件视觉规范
- [Source: `EXPERIENCE.md` — 导航模式] — 移动端底部导航 vs 桌面端顶部导航
- [Source: `EXPERIENCE.md` — 响应式断点] — 768px 断点策略
- [Source: `EXPERIENCE.md` — 无障碍] — 触摸目标 ≥ 44px、focus ring、aria 标签
- [Source: `architecture.md` — 目录结构] — frontend/src/layouts/AppLayout.vue, variables.css, base.css, utilities.css
- [Source: `Story 1.1` — Dev Notes] — 项目已建立、Vite API 代理配置、CSS 文件占位状态

## Review Findings

### Decision Needed

- [x] [Review][Decision] AppLayout 与 AdminLayout 在管理后台页面布局冲突 — **已修复**：AppLayout 通过 `useRoute()` 检测 admin 路由，隐藏桌面端顶部导航和移动端底部导航

### Patch

- [x] [Review][Patch] 移动端侧边栏打开时未锁定 body 滚动 [AdminLayout.vue] — **已修复**：添加 `watch(sidebarOpen)` 控制 `document.body.style.overflow`
- [x] [Review][Patch] 桌面端/移动端缩放跨越 768px 时侧边栏状态不一致 [AdminLayout.vue] — **已修复**：添加 `resize` 事件监听，跨 768px 时重置 sidebar 状态
- [x] [Review][Patch] safe-area-inset-bottom 未计入 main-content 底部 padding 补偿 [AppLayout.vue] — **已修复**：`padding-bottom: calc(var(--bottom-nav-height) + env(safe-area-inset-bottom, 0))`
- [x] [Review][Patch] 添加 Firefox scrollbar 样式兼容 [base.css] — **已修复**：添加 `scrollbar-width: thin` 和 `scrollbar-color`
- [x] [Review][Patch] Windows High Contrast Mode focus ring 适配 [base.css] — **已修复**：添加 `@media (forced-colors: active)` 将 outline color 改为 `Highlight`
- [x] [Review][Patch] 添加 Google Fonts dns-prefetch 降级 [index.html] — **已修复**：添加 `<link rel="dns-prefetch" href="//fonts.googleapis.com">`
- [x] [Review][Patch] 100dvh 浏览器兼容回退 [base.css] — **已修复**：添加 `min-height: 100vh` 前置回退
- [x] [Review][Patch] .hidden 工具类缺少 !important [utilities.css] — **已修复**：`display: none !important`
- [x] [Review][Patch] AdminLayout closeSidebar 桌面端无意义调用 [AdminLayout.vue] — **已修复**：`if (window.innerWidth >= 768) return`

### Defer

- [x] [Review][Defer] 路由守卫空函数（auth guard TODO）[router/index.ts] — deferred, pre-existing, 明确标注在 Story 1.5b 实现
- [x] [Review][Defer] 管理入口 UI 隐藏 vs 路由未拦截不匹配 — deferred, depends on auth guard in Story 1.5b
- [x] [Review][Defer] Token 过期刷新与持久化逻辑缺失 [authStore.ts] — deferred, 明确留给 Story 1.5a/1.5b 实现

## Dev Agent Record

### Agent Model Used

Deepseek-V4-Flash

### Debug Log References

- Story 1.1 创建了 12 条路由配置、CSS 文件占位（variables.css/ base.css/ utilities.css）、布局组件占位（AppLayout.vue 仅 `<div><slot/></div>`，AdminLayout.vue 有基础侧边栏）
- variables.css 已有部分颜色定义但不完全匹配 DESIGN.md 规格（缺少 primary-light, primary-dark, accent-light, surface-base, ink-primary, ink-secondary, ink-disabled, border-hairline, border-strong, destructive, destructive-light）
- AppLayout.vue 目前是空容器——需要完全重新实现
- AdminLayout.vue 已有基础侧边栏结构（桌面端），需要增加移动端响应式逻辑
- index.html 需要添加 font-display:swap 和 viewport-fit=cover

### Completion Notes List

- [x] 更新 variables.css 到准确 JRA 色板（14 色含 primary/accent/surface/ink/border/destructive 系列）
- [x] 更新 base.css 完善全局样式（warm-white 底色、系统字体栈、scrollbar、prefers-reduced-motion）
- [x] 更新 utilities.css 添加响应式断点工具类、排版工具类、间距工具类
- [x] 更新 index.html 添加 Barlow Condensed 字体 Google Fonts + viewport-fit=cover
- [x] 实现 AppLayout.vue 完整导航布局（桌面端顶部导航 + 移动端底部导航 + 768px 断点）
- [x] 完善 AdminLayout.vue 侧边栏 + 移动端汉堡菜单适配
- [x] 创建 authStore.ts 占位（供导航组件引用 isAdmin/computed）
- [x] 更新 App.vue 集成 AppLayout 作为全局布局
- [x] 修复 tsconfig.app.json 添加 @/ 路径别名（baseUrl + paths）
- [x] 构建验证：51 modules，150ms，所有路由懒加载正常

### File List

**UPDATE:**
- `frontend/index.html` — 添加 Barlow Condensed Google Fonts + viewport-fit=cover
- `frontend/src/assets/styles/variables.css` — 完整 JRA 设计令牌（14 色 + 排版 + 间距 + 圆角）
- `frontend/src/assets/styles/base.css` — 完善全局样式（reset + warm-white + scrollbar + reduced-motion）
- `frontend/src/assets/styles/utilities.css` — 排版/间距/响应式工具类
- `frontend/src/layouts/AppLayout.vue` — 完整响应式导航布局实现
- `frontend/src/layouts/AdminLayout.vue` — 侧边栏 + 移动端汉堡菜单适配
- `frontend/src/App.vue` — 集成 AppLayout 包裹 RouterView
- `frontend/tsconfig.app.json` — 添加 @/ 路径别名配置

**NEW:**
- `frontend/src/stores/authStore.ts` — 占位 auth store（isAdmin 供导航使用）
