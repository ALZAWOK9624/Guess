---
baseline_commit: 53b093ff832f782cfa5c55b76cafe186d86896a8
---

# Story 2.5: 马匹属性自动更新框架 (Horse Auto-Update Framework)

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **管理员**,
I want **比赛结果录入结算时，系统按自动更新规则框架将结算信息推送到马匹库**,
So that **我不必逐场手工追踪马匹数据变更，并且手动编辑过的字段不受自动更新覆盖**。

## Acceptance Criteria

### AC-1: Horse 模型增加手动编辑追踪字段

**Given** Horse 模型已定义
**When** 查看 `models/horse.py`
**Then** Horse 模型增加 `manually_updated_fields` JSON 字段（可空，默认 `null`）
**And** 该字段存储已手动编辑过的字段名列表（例如 `["previous_result", "weight"]`），表示这些字段不可被自动更新覆盖

### AC-2: horse_service.update_horse 追踪手动编辑

**Given** `horse_service.update_horse` 已实现
**When** 管理员通过 PATCH API 手动编辑某字段
**Then** 该字段名自动追加到 Horse 的 `manually_updated_fields` 列表中（不重复）
**And** 不修改其他已有标记字段

**Given** `manually_updated_fields` 由系统维护但管理员也可以通过 API 清空
**When** 调用 `POST /api/v1/horses/{id}/reset-auto-protection`
**Then** 清空该马匹的 `manually_updated_fields` 列表
**And** 返回 200 状态码

### AC-3: HorseAutoUpdateLog 模型（追溯日志）

**Given** 系统模型已定义
**When** 查看 `models/auto_update.py`（新建）
**Then** `HorseAutoUpdateLog` 模型包含以下字段：
- `id`: int, 主键
- `horse_id`: int, FK → horses.id, 非空
- `race_id`: int, FK → races.id, 可空（对应触发自动更新的比赛）
- `field_name`: str, 被更新的字段名
- `old_value`: str | None, 更新前的值（JSON 序列化字符串）
- `new_value`: str | None, 更新后的值（JSON 序列化字符串）
- `trigger_source`: str, 触发来源（v1 固定为 `"settlement"`，预留扩展）
- `created_at`: datetime, 带时区的时间戳（server_default=func.now()）

**And** 表名为 `horse_auto_update_logs`（snake_case 复数）

### AC-4: AutoUpdateService — 自动更新框架核心

**Given** `services/auto_update_service.py`（新建）
**When** 导入并使用
**Then** 该模块公开以下接口：

```python
async def apply_auto_updates(
    db: AsyncSession,
    race_id: int,
    horse_updates: dict[int, dict[str, Any]]
) -> list[HorseAutoUpdateLog]:
```

**Given** `apply_auto_updates` 被调用
**When** 传入 `horse_updates`（key: horse_id, value: 建议更��的字段字典）
**Then** 对每匹马的每个建议字段执行以下逻辑：
1. 从 DB 加载 Horse 记录的 `manually_updated_fields`
2. 如果建议字段在 `manually_updated_fields` 中 → **跳过**该字段（手动优先）
3. 如果建议字段不在 `manually_updated_fields` 中 → 更新 Horse 记录的该字段
4. 记录每条变更到 `HorseAutoUpdateLog` 表
5. 返回所有创建的 `HorseAutoUpdateLog` 列表

**Given** `horse_updates` 为空
**When** 调用 `apply_auto_updates`
**Then** 不执行任何更新，返回空列表

### AC-5: 触发机制钩子（占位）

**Given** `auto_update_service.py` 已实现
**When** 查看 `services/race_service.py`（或 `result_service.py`，未来 Epic 3）
**Then** 在结算流程的关键位置存在 `auto_update_service.apply_auto_updates()` 的调用入口注释/占位代码
**And** 注释标明：`# TODO(Epic 3): 在结算完成后调用 auto_update_service.apply_auto_updates()`

**Given** v1 仅搭建框架
**When** 检查自动更新规则
**Then** 不定义任何具体的字段更新规则（无 `previous_result` 如何计算、无 `weight` 如何推导等）
**And** 注释标明各扩展点在何处添加具体规则
**And** `apply_auto_updates` 第一个参数的 `horse_updates` 由调用者（未来的结果结算逻辑）组装

### AC-6: Alembic 迁移

**Given** 数据模型变更
**When** 运行 `alembic revision --autogenerate -m "add auto-update framework"`
**Then** 自动生成迁移文件，包含：
- `horses` 表新增 `manually_updated_fields` 列（JSON, nullable）
- 新建 `horse_auto_update_logs` 表
**And** 迁移脚本经过人工审查后应用

**Given** 迁移已应用
**When** 数据库检查
**Then** 所有现有 Horse 记录的 `manually_updated_fields` 为 `null`（不丢失数据）

## Tasks / Subtasks

### Backend: Horse 模型扩展
- [x] Task 1 (AC-1): 扩展 Horse 模型添加 `manually_updated_fields` 字段
  - [x] 在 `models/horse.py` 的 Horse 类中添加 `manually_updated_fields: Mapped[dict | None] = mapped_column(JSON, nullable=True)`
  - [x] 更新 `schemas/horse.py` 中 HorseCreate、HorseUpdate、HorseResponse 不直接暴露此字段（系统维护）

### Backend: HorseAutoUpdateLog 模型
- [x] Task 2 (AC-3): 新建 `models/auto_update.py`
  - [x] 定义 `HorseAutoUpdateLog` 模型（参照 `models/horse.py` 和 `models/race.py` 的 SQLAlchemy 模式）
  - [x] 在 `models/__init__.py` 注册 `HorseAutoUpdateLog` 导入
  - [x] HorseAutoUpdateLog 的 `horse_id` 和 `race_id` 外键参照现有模型

### Backend: Horse Service 扩展
- [x] Task 3 (AC-2): 修改 `horse_service.update_horse` 追踪手动编辑
  - [x] 在 `update_horse` 方法中，对每个实际更新的字段，追加到 `horse.manually_updated_fields`
  - [x] 对于空值更新（设置为 None），也视为手动编辑并标记
  - [x] 确保 `manually_updated_fields` 是 set-like 去重（Python list 手动去重）
  - [x] 新增 `reset_auto_protection()` 服务方法：清空指定马匹的 `manually_updated_fields`

### Backend: AutoUpdateService 框架
- [x] Task 4 (AC-4): 新建 `services/auto_update_service.py`
  - [x] 实现 `apply_auto_updates(db, race_id, horse_updates) -> list[HorseAutoUpdateLog]`
  - [x] 核心逻辑：遍历每条建议更新 → 检查 manual_updated_fields → 更新或跳过 → 记录日志
  - [x] 使用 `db.flush()` + `db.refresh()` 模式（遵循项目规范）
  - [x] 在文件顶部和关键位置添加扩展点注释：

### Backend: 触发钩子注释
- [x] Task 5 (AC-5): 在结算相关位置添加触发入口
  - [x] 在 `services/race_service.py` 中合适位置添加 TODO 注释（在 `delete_race` 之后）
  - [x] 注释格式遵循 TODO 规范，标明 Epic 3 触发点

### Backend: 管理员 API 扩展
- [x] Task 6 (AC-2, AC-1): 新增重置手动保护 API
  - [x] 在 `endpoints/horses.py` 添加 `POST /api/v1/horses/{id}/reset-auto-protection`
  - [x] 需要 `get_current_admin` 权限
  - [x] 返回 `{"data": HorseResponse}`
  - [x] 响应 schema 复用 `HorseResponse`（不暴露 `manually_updated_fields`）

### Database: Alembic 迁移
- [x] Task 7 (AC-6): 创建迁移文件
  - [x] 编写迁移脚本 (005_add_auto_update_framework.py)，包含 horses 表新增列 + 新建 horse_auto_update_logs 表
  - [x] 审查迁移脚本：manually_updated_fields 列类型为 JSON 且 nullable
  - [x] 确认 horse_auto_update_logs 表结构与 AC-3 一致（含索引）
  - [ ] 运行 `alembic upgrade head` 应用迁移（需 PostgreSQL 运行中，注意：当前 Docker 未启动）

### Backend: 测试
- [x] Task 8: 编写 `tests/test_auto_update.py`
  - [x] 测试 `auto_update_service.apply_auto_updates` 核心逻辑：
    - [x] 正常更新：字段不在 manual_updated_fields → 更新成功 + 日志记录
    - [x] 跳过手动编辑字段：字段在 manual_updated_fields → 跳过更新 + 不记录日志
    - [x] 混合情况：同一马匹部分字段可更新、部分被跳过
    - [x] 空更新输入：horse_updates 为空 → 空返回
    - [x] 不存在的 horse_id → 404 处理
  - [x] 测试 `horse_service.update_horse` 手动编辑追踪：
    - [x] 编辑单字段 → 该字段名出现在 manually_updated_fields
    - [x] 编辑多字段 → 所有字段名出现在 manually_updated_fields
    - [x] 重复编辑同一字段 → 不重复添加标记
    - [x] 编辑后查看 Horse 记录 → manually_updated_fields 正确存储
  - [x] 测试 `reset_auto_protection`：
    - [x] 清空后 manually_updated_fields = null
    - [x] 不存在的 horse_id → 404
  - [x] 测试 API 端点 `POST /api/v1/horses/{id}/reset-auto-protection`：
    - [x] 管理员调用 → 200 + manually_updated_fields = null
    - [x] 非管理员调用 → 401/403
    - [x] 不存在的 horse_id → 404
    - [x] 无标记的马匹调用 → 200（幂等）

## Dev Notes

### Senior Developer Review (AI) — 2026-06-12

**Review Outcome:** Changes Requested
**Action Items:** 1 decision-needed, 7 patch, 4 defer, 4 dismiss

#### Action Items

**Decision Needed (Resolved):**
- [x] [Review][Decision] D1: HorseResponse 暴露 manually_updated_fields — 选择选项B，在 HorseResponse 中添加 `manually_updated_fields: list[str] | None` 字段，让前端可查询保护列表状态。更新了 `schemas/horse.py` 和测试断言。

**Patch (Resolved):**
- [x] [Review][Patch] P1: manually_updated_fields 类型不一致 — 修复：标注改为 `list | None`，统一使用 list 语义，修复空值 falsy 陷阱。 [models/horse.py:27, auto_update_service.py:41-44, horse_service.py:94-96]
- [x] [Review][Patch] P2: tracked_fields 排除 manually_updated_fields 自身 — 修复：在 exclude 列表中添加 `"manually_updated_fields"`。 [horse_service.py:92]
- [x] [Review][Patch] P3: apply_auto_updates 事务原子性 + 字段校验 — 修复：先全部验证 horse_id 存在再批量更新 + 添加字段名校验（无效字段返回 400）。 [auto_update_service.py]
- [x] [Review][Patch] P4: old_value/new_value 日志截断 — 修复：从 String(500) 改为 Text 类型。 [models/auto_update.py:24-25]
- [x] [Review][Patch] P5: TODO 注释添加事务边界说明 + 函数签名 — 修复。 [race_service.py:350-359]
- [x] [Review][Patch] P6: 无效字段名静默忽略 — 使用 `inspect(Horse).columns` 验证字段名。 [auto_update_service.py:78]
- [x] [Review][Patch] P7: apply_auto_updates 添加 refresh — flush 后 refresh。 [auto_update_service.py:69]

**Deferred (pre-existing / v1 scope):**
- [x] [Review][Defer] W1: 并发竞态条件 (TOCTOU / FOR UPDATE) — deferred, v1 框架不考虑并发安全，后续版本添加行级锁
- [x] [Review][Defer] W2: trigger_source 硬编码 "settlement" — deferred, v1 仅一个触发来源，后续扩展为 Enum
- [x] [Review][Defer] W3: 测试缺少并发/None→None/混合 horse_id 场景 — deferred, v1 框架，后续版本补充
- [x] [Review][Defer] W4: race_id ondelete SET NULL 导致审计上下文丢失 — deferred, 设计选择以允许比赛删除

**Dismissed:**
- id 缺少 autoincrement 显式声明 — SQLAlchemy 默认行为，无需修改
- 返回类型不完整 — 返回完整 log list 是 API 设计选择
- isinstance 极端失败场景 — tuple 驱动的极端假设
- 路由冲突路径 — GET 和 POST 不冲突

### Current Implementation State (Story 2.4 Complete)

| Component/File | Status | Notes |
|---------------|--------|-------|
| `models/horse.py` & `Horse` model | ✅ Done | 10 attributes, no manual tracking yet |
| `schemas/horse.py` | ✅ Done | HorseCreate/HorseUpdate/HorseResponse |
| `services/horse_service.py` & `update_horse` | ✅ Done | Uses `exclude_unset=True`, needs manual tracking |
| `endpoints/horses.py` | ✅ Done | CRUD endpoints complete |
| `services/race_service.py` | ✅ Done | Race CRUD, snapshot mechanism, no auto-update hook |
| `models/race.py` / `RaceHorse` | ✅ Done | snapshot_data for race horse display |
| `models/auto_update.py` | ❌ New | Needs creation |
| `services/auto_update_service.py` | ❌ New | Framework needs creation |
| `tests/test_auto_update.py` | ❌ New | Needs creation |
| Alembic migration | ❌ New | Needs create-and-rev |

### Architecture Design

#### manually_updated_fields 设计

Horse 模型新增 `manually_updated_fields` 列为 JSON 字段（存储字符串列表）：

```json
["previous_result", "weight", "jockey"]
```

- **非 `manually_updated_fields` 中的字段**：允许自动更新覆盖（遵循具体规则）
- **`manually_updated_fields` 中的字段**：自动更新时跳过，保持手动编辑值
- **管理员可重置**：通过 `POST /api/v1/horses/{id}/reset-auto-protection` 清空列表
- **不可通过直接编辑 `manually_updated_fields` 添加字段到保护列表**：保护列表仅由 `update_horse` 自动维护，确保"编辑即保护"

#### HorseAutoUpdateLog 日志表

```
horse_auto_update_logs
├── id: int (PK)
├── horse_id: int (FK → horses.id, ON DELETE CASCADE)
├── race_id: int | null (FK → races.id, ON DELETE SET NULL)
├── field_name: str (e.g., "previous_result")
├── old_value: str | null (JSON serialized)
├── new_value: str | null (JSON serialized)
├── trigger_source: str (v1: "settlement")
└── created_at: datetime (server_default)
```

索引建议：`horse_id`、`race_id`、`(horse_id, field_name)` —— 后查和可追溯性查询。

#### auto_update_service.apply_auto_updates 流程图

```
输入: horse_updates = {horse_id: {field: value, ...}}
  │
  ├─ 遍历每个 horse_id
  │   ├─ DB 查询 Horse + manually_updated_fields
  │   ├─ 遍历每个建议字段
  │   │   ├─ 字段在 manually_updated_fields? → 跳过
  │   │   └─ 字段不在 → 更新 Horse.字段 + 创建 HorseAutoUpdateLog
  │   └─ db.flush() 批量提交
  │
  └─ 返回所有 HorseAutoUpdateLog 列表
```

#### v1 框架边界（易超范围提醒）

| 属于 v1 | 不属于 v1（推迟到后续版本） |
|---------|--------------------------|
| manually_updated_fields 追踪机制 | 具体字段的自动更新规则逻辑 |
| HorseAutoUpdateLog 模型和日志记录 | 前端查看自动更新历史界面 |
| apply_auto_updates 核心框架 | 自定义规则配置界面 |
| 手动编辑追踪（update_horse 修改） | 自动更新结果的前端展示 |
| 触发钩子占位注释 | 实际从结算流程调用 |
| 清空保护 API | 按字段精细管理保护列表 |

### Architectural Patterns

1. **手动优先模式** — `manually_updated_fields` 作为"保护名单"：编辑即标记自动保护，无需手动管理保护状态。重置 API 用于管理员需要"重新授权自动更新覆盖此字段"的场景。

2. **纯框架模式** — `apply_auto_updates` 只做"更新 or 跳过"的判断和日志记录，不做字段值计算。具体规则由调用者（结算逻辑）提供，确保单一职责。

3. **扩展点注释** — 在 `auto_update_service.py` 的关键位置添加 `# EXTENSION POINT` 注释，明确标注后续版本可在何处添加规则、如何注册新的触发来源。

4. **JSON serialized 旧值/新值** — 因为 Horse 字段类型多样（str、int、None），`HorseAutoUpdateLog.old_value` 和 `new_value` 设计为 `str | None`，使用 `str()` 序列化存储。不回存对象形的 Python repr。

5. **触发钩子位置** — 钩子不放在本故事创建的代码中（因为结算逻辑在 Epic 3 实现），而是在 `race_service.py` 中添加 TODO 注释占位，标明：
   - 在哪个函数后调用（`settle_race` 或类似函数，未来创建）
   - 传入参数格式（`horse_updates` 的 schema）
   - 调用时机（结算完成后，排行榜更新前）

### File Structure

| # | File | Operation | Description |
|---|------|-----------|-------------|
| 1 | `backend/app/models/horse.py` | ✏️ Modify | Add `manually_updated_fields` JSON column to Horse |
| 2 | `backend/app/models/auto_update.py` | ✨ New | HorseAutoUpdateLog model |
| 3 | `backend/app/models/__init__.py` | ✏️ Modify | Import HorseAutoUpdateLog |
| 4 | `backend/app/services/horse_service.py` | ✏️ Modify | Update `update_horse` to track manual edits + add `reset_auto_protection` |
| 5 | `backend/app/services/auto_update_service.py` | ✨ New | AutoUpdateService framework |
| 6 | `backend/app/services/race_service.py` | ✏️ Modify | Add TODO hook comment for auto-update trigger |
| 7 | `backend/app/api/v1/endpoints/horses.py` | ✏️ Modify | Add reset-auto-protection endpoint |
| 8 | `backend/tests/test_auto_update.py` | ✨ New | Tests for auto-update framework |
| 9 | `backend/alembic/versions/xxx_add_auto_update_framework.py` | ✨ New | Alembic migration (auto-generated) |

### Alembic Migration Strategy

```bash
cd backend
alembic revision --autogenerate -m "add auto-update framework"
```

Review generated migration for:
- `op.add_column('horses', sa.Column('manually_updated_fields', sa.JSON(), nullable=True))`
- `op.create_table('horse_auto_update_logs', ...)`
- Indexes on `horse_id` and `race_id` columns

### Testing Requirements

| Test Scenario | Steps | Expected |
|--------------|-------|----------|
| apply_auto_updates: normal update | Call with unmarked field | Field updated, log created |
| apply_auto_updates: skip manual field | Call with marked field | Field skipped, no log |
| apply_auto_updates: mixed scenario | Call with mix of marked/unmarked | Only unmarked updated |
| apply_auto_updates: empty input | Call with empty dict | Empty list returned |
| update_horse tracks manual edits | Edit a field via PATCH | Field appears in manually_updated_fields |
| update_horse no duplicate marks | Edit same field twice | Single entry in list |
| reset_auto_protection success | Call reset API | manually_updated_fields = null |
| reset_auto_protection nonexistent | Call on invalid horse_id | 404 |
| reset_auto_protection unauthorized | Call without admin | 401/403 |
| Alembic migration | Create and apply | Tables created without existing data loss |

### Project Context Reference

- **Tech**: Vue 3 + Vite + TypeScript (Composition API), FastAPI + SQLAlchemy 2.0 async, PostgreSQL 16
- **Python naming**: snake_case files and variables, snake_case table/column names
- **SQLAlchemy**: `mapped_column` type annotations, `relationship` for relations
- **Api prefix**: `/api/v1/` for all endpoints
- **Response format**: Success `{"data": ...}`, Error `{"detail": {"code": "...", "message": "..."}}`
- **Auth**: JWT; admin endpoints require `get_current_admin` dependency
- **Service pattern**: `flush()` → `refresh()` for CRUD methods to read server_default fields
- **Dates**: ISO 8601 strings (`2026-06-09T15:00:00Z`)
- **Null handling**: Use `null`, never empty strings or omitted fields
- **Testing**: pytest + pytest-asyncio (asyncio_mode=auto), in-memory SQLite with StaticPool

### Previous Story Intelligence (Story 2.4)

| Learning | Application to This Story |
|---------|--------------------------|
| `PATCH 防 null 覆盖模式` → `exclude_unset=True` + `filter out None` | `update_horse` 已有该模式，修改后需保留此行为 |
| `flush()` → `refresh()` 模式 | `apply_auto_updates` 需在每个 horse 更新后 `flush()` → `refresh()` |
| 组件命名 PascalCase / API snake_case | Model 类和表名遵循相同规范 |
| 删除确认防误触模式 | 本故事无前端 UI，不涉及 |
| 枚举验证失败处理 | 本故事无新枚举类型 |
| `_build_snapshot` 函数模式 | 可参考此函数设计 auto-update 的数据提取模式 |
| cascade delete 模式 | HorseAutoUpdateLog 的 `horse_id` FK 应设置 CASCADE |

### Git Intelligence

最近提交：
- `53b093f` feat: Story 2.4 - race deletion UI and horse detail display
- `975ebfe` feat: Story 2.3 - race creation and management
- `1e62564` feat: Story 2.2 - HorseSearchSelect component
- `2cf4fb9` feat: Story 2.1 - horse data model and admin CRUD page

当前状态：
- ✅ Horse 模型完整（10 属性 + timestamps）
- ✅ 马匹 CRUD 后端+前端完整
- ✅ 比赛 CRUD（含快照机制）完整
- ✅ 85 个测试全部通过，零回归
- ❌ Auto-update 框架未实现（本次故事）

### Anti-Patterns to Avoid

- ❌ **不要在 v1 实现任何具体的字段更新规则** — Story 2.5 仅搭建框架。具体规则（如"前走成绩=最新比赛名称"）在后续版本定义
- ❌ **不要在前端添加自动更新相关 UI** — v1 仅后端框架，前端相关展示推迟
- ❌ **不要在 `manually_updated_fields` 字段上添加前端可编辑的 API** — 该字段由系统自动维护，仅可通过 `reset-auto-protection` 整体清空
- ❌ **不要在结算端点中实际调用 `apply_auto_updates`** — 结算端点在 Epic 3 实现，本故事仅添加 TODO 注释占位
- ❌ **不要修改 `models/race.py` 或 `RaceHorse` 模型** — 快照机制不变
- ❌ **不要对外暴露 `manually_updated_fields` 在 HorseResponse 中** — 该字段为系统内部字段，不在 API 响应中暴露
- ❌ **不要在 HorseAutoUpdateLog 的 `old_value`/`new_value` 中存储 ORM 对象或 dict** — 序列化为 str
- ❌ **不要忘记在 `models/__init__.py` 注册新模型** — 否则 Alembic 自动迁移无法检测到新表

## Dev Agent Record

### Agent Model Used

Deepseek-V4-Flash

### Completion Notes

Story 2.5 horse-auto-update-framework 实现完成（2026-06-12）：

**实现内容：**
1. **models/horse.py** — Horse 模型新增 `manually_updated_fields` JSON 列（nullable），用于追踪手动编辑过的字段
2. **models/auto_update.py** (新建) — HorseAutoUpdateLog 模型，记录自动更新的完整变更历史（含旧值/新值/触发比赛/来源）
3. **models/__init__.py** — 注册 HorseAutoUpdateLog 导入
4. **services/horse_service.py** — `update_horse` 方法自动追踪手动编辑字段（空值更新也标记）；新增 `reset_auto_protection()` 方法清空保护列表
5. **services/auto_update_service.py** (新建) — `apply_auto_updates()` 核心框架：手动优先模式（跳过 protected 字段）+ 变更日志记录 + EXTENSION POINT 注释
6. **services/race_service.py** — 末尾添加 Auto-Update Hook TODO 注释，标明 Epic 3 触发位置
7. **api/v1/endpoints/horses.py** — 新增 `POST /{id}/reset-auto-protection` 端点（admin only）
8. **alembic/versions/005_add_auto_update_framework.py** — 手动编写迁移：horses 表新增列 + horse_auto_update_logs 表创建（含索引）
9. **tests/test_auto_update.py** (新建) — 21 个测试用例：6 个 apply_auto_updates（正常/保护/混合/空/404/null）、6 个手动编辑追踪（单字段/多字段/去重/name不追踪/追加/null）、3 个 reset（清空/幂等/404）、4 个 API（admin/401/404/幂等）、2 个模型测试

**测试结果：106/106 全部通过，零回归**

**注意：** 迁移文件 `005_add_auto_update_framework.py` 已创建但未应用（需 PostgreSQL 运行后执行 `alembic upgrade head`）

### File List

#### New Files
| # | File | Description |
|---|------|-------------|
| 1 | `backend/app/models/auto_update.py` | HorseAutoUpdateLog model for change traceability |
| 2 | `backend/app/services/auto_update_service.py` | Auto-update framework with apply_auto_updates |
| 3 | `backend/tests/test_auto_update.py` | Comprehensive tests for auto-update framework |

#### Modified Files
| # | File | Change |
|---|------|--------|
| 4 | `backend/app/models/horse.py` | Add manually_updated_fields JSON column |
| 5 | `backend/app/models/__init__.py` | Register HorseAutoUpdateLog import |
| 6 | `backend/app/services/horse_service.py` | Track manual edits in update_horse + reset_auto_protection |
| 7 | `backend/app/services/race_service.py` | Add TODO hook comment for settlement trigger |
| 8 | `backend/app/api/v1/endpoints/horses.py` | Add reset-auto-protection endpoint |
| 9 | `backend/alembic/versions/005_add_auto_update_framework.py` | Manually written migration (review before apply) |

## Change Log

| Date | Change |
|------|--------|
| 2026-06-12 | Created Story 2.5: Horse Auto-Update Framework |
| 2026-06-12 | Implemented: Horse model extension, HorseAutoUpdateLog model, auto_update_service framework, manual edit tracking, reset protection API, TODO hook, migration, 21 tests (106 total, 0 regression) |
