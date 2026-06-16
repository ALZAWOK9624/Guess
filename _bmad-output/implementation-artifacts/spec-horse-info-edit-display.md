---
title: '马匹信息编辑与显示增强'
type: 'feature'
created: '2026-06-16'
baseline_commit: '372dcc6fb99b81160f8e6154c50cd1579ff2b9de'
status: 'in-review'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 当前马匹管理页面包含"体重"和"骑手"这两个每场比赛都可能不同的字段，混在马匹数据中不合理；性别需要手动输入容易出错；出生国没有标准化管理；前走成绩和主要胜鞍的自动更新逻辑缺失。

**Approach:** (1) 将体重和骑手从马匹模型移到比赛编辑中（RaceHorse级别），(2) 性别改为固定下拉选项，(3) 出生国改为带国旗emoji的可搜索下拉列表并按使用频率排序，(4) 实现比赛结算后的前走成绩自动更新，以及胜马主胜鞍手动更新功能。

## Boundaries & Constraints

**Always:**
- 遵循现有项目架构（FastAPI + Vue 3 + SQLAlchemy + SQLite/PostgreSQL）
- 所有API字段使用snake_case
- 前端使用`<script setup lang="ts">` Composition API
- 马匹快照机制不变——比赛编辑时weight/jockey写入RaceHorse.snapshot_data
- 性别下拉选项固定：牡（去势前雄性）、牝（雌性）、骟（去势后雄性）
- 出生国下拉列表包含所有能找到的有国旗emoji的国家，按库中使用频率排序
- 自动更新使用现有`auto_update_service.apply_auto_updates()`框架
- 所有编辑操作遵循现有的PATCH差异检测模式

**Ask First:** 无

**Never:** 不要修改现有比赛已创建的RaceHorse数据（仅新编辑/创建时影响）；不要引入新的UI库；不要修改非马匹相关的事务逻辑。

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 创建马匹时前走/主胜鞍为空 | 只填名称保存 | 创建成功，前走相关字段为NULL | N/A |
| 手动编辑前走成绩 | 提供日期和名次 | 保存成功，自动更新标记保护 | 缺日期或名次时提示错误 |
| 比赛结算后前走自动更新 | 马匹原前走日期 <= 比赛日期 | 自动更新前走日期/比赛名/名次 | 跳过手动保护字段 |
| 更新主胜鞍 | 胜马当前主胜鞍不是该比赛 | 按钮可点击，点击后更新 | 非胜马不显示按钮 |
| 多次录入同一场比赛 | 第二次提交相同结果 | 由于 race.date == previous_result_date，触发更新覆盖 | N/A |
| 出生国搜索 | 输入"日" | 过滤出日本等相关国家 | 无匹配显示空态 |

</frozen-after-approval>

## Code Map

- `backend/app/models/horse.py` -- Horse模型（去weight/jockey/+前走日期/名次/+主胜鞍日期）
- `backend/app/models/race.py` -- RaceHorse模型（+weight/+jockey字段）
- `backend/app/schemas/horse.py` -- Horse相关Pydantic schema更新
- `backend/app/schemas/race.py` -- Race相关schema更新（weight/jockey per horse）
- `backend/app/services/horse_service.py` -- 新增前走/主胜鞍校验、出生国频率统计
- `backend/app/services/race_service.py` -- 修改快照构建逻辑
- `backend/app/services/result_service.py` -- 结算后触发自动更新
- `backend/app/api/v1/endpoints/horses.py` -- 新增origins/stats端点
- `backend/app/api/v1/endpoints/races.py` -- 更新创建/编辑端点支持per-horse weight/jockey
- `frontend/src/types/horse.ts` -- Horse类型更新
- `frontend/src/types/race.ts` -- Race类型更新
- `frontend/src/api/horses.ts` -- 新增origin统计API
- `frontend/src/api/races.ts` -- Race API类型更新
- `frontend/src/pages/admin/HorsesPage.vue` -- 马匹管理页面UI大改
- `frontend/src/pages/admin/CreateRacePage.vue` -- 创建比赛页面加weight/jockey输入
- `frontend/src/pages/admin/EditRacePage.vue` -- 编辑比赛页面加weight/jockey输入
- `frontend/src/pages/admin/ResultsPage.vue` -- 结算后显示"更新主胜鞍"按钮
- `frontend/src/components/HorseSearchSelect.vue` -- 不修改（仅展示时显示origin

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/models/horse.py` -- 移除weight/jockey，新增previous_result_date/previous_result_position/best_win_date字段
- [x] `backend/app/models/race.py` -- RaceHorse新增weight/jockey列
- [x] `backend/app/schemas/horse.py` -- 移除weight/jockey，新增previous_result_date/previous_result_position/best_win_date/sex validator
- [x] `backend/app/schemas/race.py` -- HorseSnapshot移除weight/jockey；RaceHorseResponse新增weight/jockey；RaceCreate/Update新增horse_weights/horse_jockeys
- [x] `backend/app/services/horse_service.py` -- 前走/主胜鞍校验、get_origins_stats()、update_best_win()
- [x] `backend/app/services/race_service.py` -- _build_snapshot接受weight/jockey参数；create/update支持per-horse weight/jockey
- [x] `backend/app/services/result_service.py` -- submit_results后自动更新前走成绩
- [x] `backend/app/services/vote_service.py` -- get_race_results_grouped_by_horse 返回 weight/jockey
- [x] `backend/app/api/v1/endpoints/horses.py` -- 新增origins/stats、update-best-win端点
- [x] `backend/app/api/v1/endpoints/races.py` -- 响应包含weight/jockey
- [x] `frontend/src/utils/countries.ts` -- 创建带国旗emoji的完整国家列表
- [x] `frontend/src/types/horse.ts` -- Horse接口更新
- [x] `frontend/src/types/race.ts` -- Race类型更新
- [x] `frontend/src/api/horses.ts` -- 新增getOriginsStats/updateBestWin
- [x] `frontend/src/pages/admin/HorsesPage.vue` -- 完整重写
- [x] `frontend/src/pages/admin/CreateRacePage.vue` -- 添加per-horse weight/jockey输入
- [x] `frontend/src/pages/admin/EditRacePage.vue` -- 添加per-horse weight/jockey输入
- [x] `frontend/src/pages/RaceDetailPage.vue` -- 传递weight/jockey、添加"更新主胜鞍"按钮
- [x] `frontend/src/components/HorseDetailCard.vue` -- 添加weight/jockey props
- [x] `frontend/src/components/DragCard.vue` -- 优先从顶层读取weight/jockey

**Acceptance Criteria:**
- Given 管理员进入马匹管理页面，when 创建/编辑马匹，then 性别只能从"牡"、"牝"、"骟"中选择
- Given 管理员创建比赛时选择了马匹，when 填写参赛信息，then 每匹马都有独立的体重和骑手输入框
- Given 管理员在出生国下拉框输入文字，when 搜索，then 显示带国旗emoji的匹配国家列表
- Given 比赛结算完成，when 某马匹的前走日期<=比赛日期，then 前走成绩自动更新
- Given 比赛结算完成且胜马的主胜鞍不是该比赛，when 点击"更新主胜鞍"按钮，then 该马的主胜鞍更新为该比赛
- Given 管理员手动编辑前走成绩，when 未提供日期或名次，then 保存被拒绝并提示错误

## Design Notes

**出生国国旗列表实现方案：**
前端维护一个静态的`countries`列表，包含`{code: 'JP', name: '日本', emoji: '🇯🇵'}`格式。从后端`GET /api/v1/horses/origins/stats`获取各国家的出现次数，在前端对列表排序（频率降序→emoji升序）。搜索时过滤name和emoji字段。emoji的排序使用`String.prototype.localeCompare()`进行比较。

**前走成绩自动更新逻辑：**
在`result_service.submit_results()`中，结算后构建`horse_updates`字典：
- 对所有参赛马匹：`previous_result = f"{position}着"`（position=0时为"除外/取消"），`previous_result_date = race.date`
- 对胜者（position=1）：不做自动更新（由手动按钮触发）
- 调用`auto_update_service.apply_auto_updates()`，它会自动跳过手动保护的字段

**更新主胜鞍端点：**
`POST /api/v1/horses/{id}/update-best-win` 接收`{"race_id": int}`。校验该马在指定比赛中position=1。如果是，更新`best_win`为该比赛名称，`best_win_date`为比赛日期。

## Verification

**Commands:**
- `cd backend && python -m pytest tests/` -- 所有测试通过
- `cd frontend && pnpm build` -- 构建成功

**Manual checks:**
- 检查马匹管理页面中weight/jockey列消失，性别变为下拉选择，出生国变为带emoji的下拉选择
- 检查创建/编辑比赛页面中每匹马都有weight和jockey输入框
- 检查比赛结算后前走成绩自动更新
- 检查已结算比赛详情页胜马显示"更新主胜鞍"按钮
