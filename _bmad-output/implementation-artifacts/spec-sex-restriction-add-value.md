---
title: 'sex_restriction 新增「牡牝限」选项'
type: 'feature'
created: '2026-07-10'
status: 'done'
baseline_commit: 'ae586bc8860dffd47b2c954236f42b523b2e683f'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 当前 `sex_restriction` 仅支持三种值（无、牝限、牡限），缺少"牡牝限"选项，无法满足混合性别限制场景。

**Approach:** 在 sex_restriction 的合法值集合中新增「牡牝限」，涉及后端 Pydantic 校验器、前端三个页面的选项常量，以及 project-context.md 文档。数据库列无需变更（已是 `String(20)` 自由文本）。

## Boundaries & Constraints

**Always:**
- 新值顺序保持：无 / 牝限 / 牡牝限 / 牡限
- 「无」仍然在前端标签渲染时隐藏（`v-if !== '无'`）
- 后端 schema 校验器必须包含新值
- 排行榜筛选器支持新值多选

**Ask First:**
- 无 — 变更路径明确，无需人工决策

**Never:**
- 不修改数据库 schema（无需新迁移）
- 不修改现有数据的 `sex_restriction` 值
- 不改变 tag 显示/隐藏逻辑

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 创建比赛选牡牝限 | 表单选择「牡牝限」提交 | 创建成功，sex_restriction='牡牝限' | N/A |
| 编辑比赛改选牡牝限 | PATCH 传 `sex_restriction: "牡牝限"` | 更新成功 | N/A |
| 后端非法值校验 | 传 `sex_restriction: "invalid"` | 422 校验错误 | 返回 allowed values 提示 |
| 牡牝限标签显示 | race.sex_restriction='牡牝限' | 卡片渲染「牡牝限」tag | N/A |
| 排行榜按牡牝限筛选 | filters.sex_restriction=['牡牝限'] | 只返回匹配比赛 | N/A |
| 投票后锁定标签 | race 有投票，改 sex_restriction | 被 lockable_tags 拦截，返回错误 | 返回 HORSE_HAS_VOTES 相关错误 |

</frozen-after-approval>

## Code Map

- `backend/app/schemas/race.py:65-71` -- `RaceCreate.validate_sex_restriction` allowed 集合
- `backend/app/schemas/race.py:147-154` -- `RaceUpdate.validate_sex_restriction` allowed 集合
- `frontend/src/pages/HomePage.vue:46` -- `sexRestrictionOptions` 常量
- `frontend/src/pages/admin/EditRacePage.vue:33` -- `sexRestrictionOptions` 常量
- `frontend/src/pages/LeaderboardPage.vue:20` -- `sexRestrictionOptions` 常量
- `_bmad-output/project-context.md:212` -- 文档中的 6-tag 说明

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/schemas/race.py` -- 在 `RaceCreate` 和 `RaceUpdate` 的 `validate_sex_restriction` 校验器中添加 "牡牝限" 到 allowed 集合
- [x] `frontend/src/pages/HomePage.vue` -- 在 `sexRestrictionOptions` 数组中添加 '牡牝限'（在 '牝限' 和 '牡限' 之间）
- [x] `frontend/src/pages/admin/EditRacePage.vue` -- 在 `sexRestrictionOptions` 数组中添加 '牡牝限'（在 '牝限' 和 '牡限' 之间）
- [x] `frontend/src/pages/LeaderboardPage.vue` -- 在 `sexRestrictionOptions` 数组中添加 '牡牝限'（在 '牝限' 和 '牡限' 之间）
- [x] `_bmad-output/project-context.md` -- 更新第 212 行文档为：`sex_restriction（无/牝限/牡牝限/牡限）`

**Acceptance Criteria:**
- Given 管理员创建比赛，when 选择「牡牝限」提交，then 比赛成功创建且 sex_restriction='牡牝限'
- Given 管理员编辑比赛，when 将 sex_restriction 改为「牡牝限」保存，then 更新成功
- Given 后端接收非法 sex_restriction 值，when 传入 "invalid"，then 返回 422 校验错误
- Given 前端任意 sex_restriction 选择场景，when 遍历选项列表，then 显示顺序为 无 → 牝限 → 牡牝限 → 牡限

## Spec Change Log

## Verification

**Commands:**
- `cd backend && python -m pytest tests/ -x -q` -- 后端测试全部通过
- `cd frontend && pnpm build` -- 前端构建成功（若环境可用）

**Manual checks (if no CLI):**
- 检查 HomePage.vue、EditRacePage.vue、LeaderboardPage.vue 中 sexRestrictionOptions 数组顺序是否为 ['无', '牝限', '牡牝限', '牡限']
- 检查 race.py 中两处 validator allowed 集合是否包含 '牡牝限'

## Suggested Review Order

**后端校验 — 合法性入口**

- RaceCreate validator：新值被接受的权威定义点
  [`race.py:68`](../../backend/app/schemas/race.py#L68)

- RaceUpdate validator：与 RaceCreate 必须保持一致的镜像校验
  [`race.py:151`](../../backend/app/schemas/race.py#L151)

**前端选项 — 三个渲染点同步**

- 首页创建比赛弹窗：用户首次暴露新选项的位置
  [`HomePage.vue:46`](../../frontend/src/pages/HomePage.vue#L46)

- 编辑比赛页：修改已有比赛时可切换为牡牝限
  [`EditRacePage.vue:33`](../../frontend/src/pages/admin/EditRacePage.vue#L33)

- 排行榜筛选：多选筛选器支持按牡牝限过滤
  [`LeaderboardPage.vue:20`](../../frontend/src/pages/LeaderboardPage.vue#L20)

**文档**

- 6-tag 系统说明文档更新
  [`project-context.md:212`](../../_bmad-output/project-context.md#L212)
