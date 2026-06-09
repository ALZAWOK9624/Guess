---
name: Guess
description: 赛马爱好者圈子的专属竞猜投票平台。JRA 精密仪器美学——沉稳竞马绿、冠军金点缀、留白驱动的信息清晰度。
status: final
updated: 2026-06-09
colors:
  primary: '#1A5632'
  primary-light: '#2D7A4F'
  primary-dark: '#0D3A1F'
  accent: '#B8960C'
  accent-light: '#D4B84A'
  surface-base: '#F8FAF7'
  surface-raised: '#FFFFFF'
  ink-primary: '#1A2E1A'
  ink-secondary: '#4A5A4A'
  ink-disabled: '#9CAA9C'
  border-hairline: '#D4DCD0'
  border-strong: '#A8B8A4'
  success: '#2D7A4F'
  destructive: '#C53030'
  destructive-light: '#FED7D7'
typography:
  display:
    fontFamily: 'Barlow Condensed, system-ui, sans-serif'
    fontSize: 36px
    fontWeight: '600'
    lineHeight: '1.15'
  heading:
    fontFamily: 'Barlow Condensed, system-ui, sans-serif'
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.25'
  subheading:
    fontFamily: '-apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif'
    fontSize: 18px
    fontWeight: '600'
    lineHeight: '1.35'
  body:
    fontFamily: '-apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif'
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  body-sm:
    fontFamily: '-apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif'
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  caption:
    fontFamily: '-apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif'
    fontSize: 12px
    fontWeight: '400'
    lineHeight: '1.4'
  number:
    note: 'For tabular data (leaderboard scores, race dates) — Barlow Condensed with tabular-nums feature. Latin numerals render in Barlow Condensed; CJK context inherits body font.'
rounded:
  sm: 6px
  md: 10px
  lg: 14px
  full: 9999px
spacing:
  '1': 4px
  '2': 8px
  '3': 12px
  '4': 16px
  '5': 20px
  '6': 24px
  '8': 32px
  '10': 40px
  '12': 48px
  '16': 64px
components:
  race-card:
    background: '{colors.surface-raised}'
    border: '1px solid {colors.border-hairline}'
    radius: '{rounded.md}'
    padding: '{spacing.5}'
  grade-badge-g1:
    background: '{colors.accent}'
    foreground: '#FFFFFF'
    radius: '{rounded.sm}'
    fontSize: 12px
    fontWeight: '700'
  grade-badge-g2:
    background: '#6B7280'
    foreground: '#FFFFFF'
    radius: '{rounded.sm}'
    fontSize: 12px
    fontWeight: '700'
  grade-badge-2yog1:
    background: '{colors.primary-light}'
    foreground: '#FFFFFF'
    radius: '{rounded.sm}'
    fontSize: 12px
    fontWeight: '700'
  vote-button:
    background: '{colors.accent}'
    foreground: '#FFFFFF'
    radius: '{rounded.md}'
    hover-background: '{colors.accent-light}'
  vote-confirmed:
    background: '{colors.primary}'
    foreground: '#FFFFFF'
    radius: '{rounded.md}'
  leaderboard-row:
    background: '{colors.surface-raised}'
    border-bottom: '1px solid {colors.border-hairline}'
    padding: '{spacing.3} {spacing.4}'
  drag-card:
    background: '{colors.surface-raised}'
    border: '1px solid {colors.border-strong}'
    radius: '{rounded.md}'
    shadow: '0 2px 4px rgba(26,86,50,0.08)'
  status-badge:
    radius: '{rounded.full}'
    fontSize: 12px
    padding: '2px 10px'
---
---

## Brand & Style

Guess 是一个赛马爱好者圈子的专属竞猜平台——不是博彩产品，是朋友间的荣誉积分游戏。用户群体约 100 人，管理员 1-2 人，移动端为主要使用场景。

视觉语言直接参考 **JRA（日本中央競馬会）** 官网的设计 DNA：1987 年 GK Graphics 为 JRA 重塑品牌时提出"马是美丽的"——将赛马从赌博形象重新定义为健康、智性的体育娱乐。这一理念完美契合 Guess 的定位。

Guess 的视觉系统遵循 JRA 的核心原则：**像精密仪器一样**——每个元素都有其确切功用。不追求花哨动画，不堆砌装饰元素。信赖感来自秩序，而非炫技。

- **沉稳竞马绿**是唯一的品牌色，象征草地赛道、英国赛马传统的优雅。
- **冠军金**是仅用于行动召唤和 G1 等级徽章的点缀色——出现即意味"重要的东西"。
- **大面积留白**是 JRA 式信息密度的解药——排行榜、比赛列表等高密度数据页通过白色呼吸感保持可读。
- **无衬线数字优先**——比赛中日期、积分、排名用 Barlow Condensed 的等宽数字特性确保对齐；中文正文走系统 UI 字体栈，不引入额外 web font 加载。

## Colors

- **竞马绿 (`#1A5632`)** 是主品牌色。用于导航、页头、主按钮（投票确认后状态）、链接下划线、活跃标签指示器。
- **冠军金 (`#B8960C`)** 是唯一的强调色。仅用于 CTA 按钮（"投票"主操作）、G1 等级徽章、排行榜第一名高亮。从不用于装饰，从不用于状态标签。金色意味着"行动"或"最高等级"。
- **暖白 (`#F8FAF7`)** 是页面底色。微微偏暖，带极淡绿调，避免纯白冷感。JRA 式大面积留白。
- **纯白 (`#FFFFFF`)** 用于卡片和浮层表面。
- **墨绿黑 (`#1A2E1A`)** 是正文色。非纯黑——比纯黑柔和，适合长时间阅读数据。
- **中灰绿 (`#4A5A4A`)** 用于辅助文字、标签、时间戳。
- **细线 (`#D4DCD0`)** 用于列表分隔线和卡片边框——最低可辨识对比度。任何更重的边框都会像 UI 框架而非数据页面。

禁用：渐变填充、彩色阴影、色块背景（卡片即白底绿描边，不加色块）、超过两种品牌色（一绿一金，其余灰度）。

## Typography

**Barlow Condensed** 承担"赛马数字感"——等级徽章（G1/G2）、积分数字、比赛日期、排行榜数值。自带等宽数字特性 (`tabular-nums`)，确保积分列在排行榜中对齐。

**系统 UI 字体栈** 承担所有中文正文：`-apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif`。v1 不加载中文字体 web font，避免首次访问延迟。

字号层级严格：
- `display` (36px) — 仅用于首页大标题和排行榜页面头
- `heading` (24px) — 比赛名称、管理后台标题
- `subheading` (18px) — 卡片内标题、马匹名称
- `body` (16px) — 正文、列表项、表单标签
- `body-sm` (14px) — 辅助说明、面包屑
- `caption` (12px) — 时间戳、徽章文字、表格脚注

数字在中文语境中保持 Barlow Condensed 渲染——比赛结果 1st/2nd/3rd、积分 +10/-5 等。

## Layout & Spacing

间距比例：4 / 8 / 12 / 16 / 20 / 24 / 32 / 40 / 48 / 64 px。最大间距用于页头与内容区之间；最小间距用于紧密关联元素（标签与值、图标与文字）。

内容最大宽度 `max-w-7xl` (1280px)——足够宽以承载排行榜全列，但不撑满超宽屏幕。移动端全宽自适应，两侧 16px 边距。

移动端单列布局；桌面端管理后台使用左侧边栏（240px）+ 主内容区的双列结构。移动端管理功能通过顶部 Tab 切换或汉堡菜单承载。

JRA 风格日历网格：首页比赛列表优先展示"即将开始"的比赛，以时间线布局排列。每场比赛独立卡片，包含等级徽章、比赛名、日期、状态标签。

## Elevation & Depth

Guess 不将阴影用作层级手段。卡片与背景之间仅靠边框颜色区隔（`surface-raised` vs `surface-base`）。信息层级由排版（字号粗细）和间距（留白大小）驱动，而非 z 轴深度。

唯一例外：拖拽排序界面中的拖拽卡片使用轻微阴影（`0 2px 4px rgba(26,86,50,0.08)`）——因为拖拽操作本质上是"拿起-放下"的物理隐喻。

## Shapes

`rounded/sm` (6px) 用于徽章、标签、小型输入框。`rounded/md` (10px) 用于卡片、按钮、表格行。`rounded/lg` (14px) 用于弹窗和抽屉面板。`rounded/full` (9999px) 仅用于状态胶囊标签（"投票中""已锁定""已结算"）。

整体偏锐利——读作"工具"而非"消费品"。无大圆角卡片，无气泡式 UI。

## Components

### 比赛卡片 (Race Card)
`{components.race-card}`。白色表面，1px 细绿灰边框。顶部行：等级徽章 + 状态标签；中部：比赛名称（`subheading`）+ 日期（`caption`）；底部：参赛马匹数 + 已投票人数。投票中比赛卡片右上角有金色"投票"入口。

### 等级徽章 (Grade Badge)
- G1: `{components.grade-badge-g1}` — 金色底，白色字，赛事最高等级
- G2/JPN1: `{components.grade-badge-g2}` — 灰色底
- 2岁G1: `{components.grade-badge-2yog1}` — 亮绿底
- 自定义: 灰色底 + 虚线边框

### 投票按钮 (Vote Button)
`{components.vote-button}`。金色底色，白色文字，10px 圆角。悬停时变亮金色。点击后切换为 `{components.vote-confirmed}` 竞马绿底 + 显示"✓ 已投：{马名}"。移动端全宽，桌面端自适应宽度。

### 排行榜行 (Leaderboard Row)
`{components.leaderboard-row}`。白色行，细底部分割线。排名数字（Barlow Condensed, 18px bold）、用户名（body）、积分（Barlow Condensed, 20px bold, primary color）、参与场数（body-sm, ink-secondary）、场均得分（body-sm）。前三名排名数字用金色高亮。当前登录用户行用极淡绿背景 `#F0F7F2` 标记。

### 拖拽排序卡片 (Drag Card)
`{components.drag-card}`。用于管理员录入比赛结果。白色卡片，强边框，轻微阴影。左侧拖拽手柄（六点网格图标），右侧马匹名 + 属性摘要。触摸设备上卡片高度 ≥ 56px 确保可拖拽。

### 状态指示器 (Status Badge)
`{components.status-badge}`。胶囊形，12px 字号。
- 投票中：绿底 `#2D7A4F` 白字
- 已锁定：灰底 `#6B7280` 白字 + 🔒 图标
- 已结算：深绿底 `#0D3A1F` 白字 + ✓ 图标

### 马匹属性卡片 (Horse Detail Card)
比赛详情页中展示每匹参赛马。左侧马匹名（subheading, primary），右侧列出 FR-5 定义的 10 项属性（body-sm 键值对）。已投票用户在该马匹卡片上方有金色小标记"你选了这匹"。

## Do's and Don'ts

| Do | Don't |
|---|---|
| 竞马绿 + 冠军金，两色到底 | 引入第三种品牌色或装饰色 |
| 大面积留白，让数据呼吸 | 压缩间距以塞入更多信息 |
| Barlow Condensed 渲染数字和等级 | 用系统字体渲染积分数字 |
| 细线分隔（`border-hairline`） | 粗边框、彩色分割线、卡阴影 |
| 状态靠文字 + 颜色双重表达 | 仅靠颜色区分状态（无障碍要求） |
| 移动端全宽单列，表格水平滚动 | 移动端缩小字号以强行适配表格 |
| 拖拽排序仅管理员可见 | 普通用户界面出现拖拽手柄 |
| 比赛卡片列表按时间线排列 | 用网格或瀑布流排列比赛 |
| 金徽章仅用于 G1 和 CTA | 金色用于装饰或非关键信息 |
