# Blind Hunter — Review Prompt (Diff Only)

You are a Blind Hunter reviewer. You receive ONLY the raw diff below — no project context, no spec, no architecture docs. Your task is to find bugs, vulnerabilities, logic errors, and code smells by examining the diff alone.

## Diff Content

```
diff --git a/_bmad-output/implementation-artifacts/sprint-status.yaml b/_bmad-output/implementation-artifacts/sprint-status.yaml
index 23bcc11..b0c3c5b 100644
--- a/_bmad-output/implementation-artifacts/sprint-status.yaml
+++ b/_bmad-output/implementation-artifacts/sprint-status.yaml
@@ -1,5 +1,5 @@
 # generated: 2026-06-09T17:36
-# last_updated: 2026-06-09T17:36
+# last_updated: 2026-06-12T16:27
 # project: guess
 # project_key: NOKEY
 # tracking_system: file-system
@@ -35,7 +35,7 @@
 # - Dev moves story to 'review', then runs code-review (fresh context, different LLM recommended)

 generated: 2026-06-09T17:36
-last_updated: 2026-06-11T18:12
+last_updated: 2026-06-12T16:27
 project: guess
 project_key: NOKEY
 tracking_system: file-system
@@ -59,7 +59,7 @@ development_status:
   2-1-horse-data-model-management: done
   2-2-horse-search-selector: done
   2-3-race-creation-management: done
-  2-4-race-deletion-horse-details: backlog
+  2-4-race-deletion-horse-details: review
   2-5-horse-auto-update-framework: backlog
   epic-2-retrospective: optional

diff --git a/backend/tests/test_races.py b/backend/tests/test_races.py
index 2ef5619..f01b45d 100644
--- a/backend/tests/test_races.py
+++ b/backend/tests/test_races.py
@@ -3,12 +3,14 @@
 from datetime import date, datetime

 import pytest
+from fastapi import HTTPException
 from httpx import ASGITransport, AsyncClient
 from sqlalchemy.ext.asyncio import AsyncSession

 from app.api.deps import get_db, get_current_admin
 from app.main import app
 from app.models.horse import Horse
+from app.models.race import RaceStatus
 from app.schemas.horse import HorseCreate


@@ -217,6 +219,41 @@ class TestRaceService:

         await db_session.rollback()

+    @pytest.mark.asyncio
+    async def test_delete_race_settled(self, db_session: AsyncSession):
+        from app.services.race_service import create_race, delete_race
+        from app.schemas.race import RaceCreate
+
+        h1 = await _create_horse(db_session, SAMPLE_HORSE)
+        h2 = await _create_horse(db_session, SAMPLE_HORSE_2)
+
+        created = await create_race(db_session, RaceCreate(
+            name="SettledRace", date=date(2026, 6, 15), grade="G1",
+            horse_ids=[h1.id, h2.id],
+        ), creator_id=1)
+
+        # Manually set status to SETTLED to simulate settled race
+        created.status = RaceStatus.SETTLED
+        await db_session.flush()
+
+        with pytest.raises(HTTPException) as exc_info:
+            await delete_race(db_session, created.id)
+        assert exc_info.value.status_code == 400
+        assert exc_info.value.detail["code"] == "RACE_SETTLED"
+
+        await db_session.rollback()
+
+    @pytest.mark.asyncio
+    async def test_delete_race_not_found(self, db_session: AsyncSession):
+        from app.services.race_service import delete_race
+
+        with pytest.raises(HTTPException) as exc_info:
+            await delete_race(db_session, 99999)
+        assert exc_info.value.status_code == 404
+        assert exc_info.value.detail["code"] == "NOT_FOUND"
+
+        await db_session.rollback()
+

 # --- API Tests ---

@@ -390,6 +426,101 @@ class TestRaceAPI:

         app.dependency_overrides.clear()

+    @pytest.mark.asyncio
+    async def test_delete_nonexistent_race_api(self, db_session: AsyncSession):
+        """DELETE non-existent race → 404."""
+        app.dependency_overrides[get_db] = lambda: db_session
+        app.dependency_overrides[get_current_admin] = override_get_admin
+
+        transport = ASGITransport(app=app)
+        async with AsyncClient(transport=transport, base_url="http://test") as client:
+            resp = await client.delete("/api/v1/races/99999")
+            assert resp.status_code == 404
+            data = resp.json()
+            assert data["detail"]["code"] == "NOT_FOUND"
+
+        app.dependency_overrides.clear()
+
+    @pytest.mark.asyncio
+    async def test_delete_settled_race_api(self, db_session: AsyncSession):
+        """DELETE settled race → 400."""
+        from app.services.race_service import create_race
+        from app.schemas.race import RaceCreate
+
+        h1 = await _create_horse(db_session, SAMPLE_HORSE)
+        h2 = await _create_horse(db_session, SAMPLE_HORSE_2)
+
+        created = await create_race(db_session, RaceCreate(
+            name="SettledDelete", date=date(2026, 6, 15), grade="G1",
+            horse_ids=[h1.id, h2.id],
+        ), creator_id=1)
+        created.status = RaceStatus.SETTLED
+        await db_session.flush()
+
+        app.dependency_overrides[get_db] = lambda: db_session
+        app.dependency_overrides[get_current_admin] = override_get_admin
+
+        transport = ASGITransport(app=app)
+        async with AsyncClient(transport=transport, base_url="http://test") as client:
+            resp = await client.delete(f"/api/v1/races/{created.id}")
+            assert resp.status_code == 400
+            data = resp.json()
+            assert data["detail"]["code"] == "RACE_SETTLED"
+
+        app.dependency_overrides.clear()
+
+    @pytest.mark.asyncio
+    async def test_delete_locked_race_api(self, db_session: AsyncSession):
+        """DELETE locked race → 204."""
+        from app.services.race_service import create_race
+        from app.schemas.race import RaceCreate
+
+        h1 = await _create_horse(db_session, SAMPLE_HORSE)
+        h2 = await _create_horse(db_session, SAMPLE_HORSE_2)
+
+        created = await create_race(db_session, RaceCreate(
+            name="LockedDelete", date=date(2026, 6, 15), grade="G1",
+            horse_ids=[h1.id, h2.id],
+        ), creator_id=1)
+        created.status = RaceStatus.LOCKED
+        await db_session.flush()
+
+        app.dependency_overrides[get_db] = lambda: db_session
+        app.dependency_overrides[get_current_admin] = override_get_admin
+
+        transport = ASGITransport(app=app)
+        async with AsyncClient(transport=transport, base_url="http://test") as client:
+            resp = await client.delete(f"/api/v1/races/{created.id}")
+            assert resp.status_code == 204
+
+            # Verify deleted
+            get_resp = await client.get(f"/api/v1/races/{created.id}")
+            assert get_resp.status_code == 404
+
+        app.dependency_overrides.clear()
+
+    @pytest.mark.asyncio
+    async def test_unauthenticated_delete_race_api(self, db_session: AsyncSession):
+        """DELETE without admin auth → 401."""
+        from app.services.race_service import create_race
+        from app.schemas.race import RaceCreate
+
+        h1 = await _create_horse(db_session, SAMPLE_HORSE)
+        h2 = await _create_horse(db_session, SAMPLE_HORSE_2)
+
+        created = await create_race(db_session, RaceCreate(
+            name="NoAuthDelete", date=date(2026, 6, 15), grade="G1",
+            horse_ids=[h1.id, h2.id],
+        ), creator_id=1)
+
+        app.dependency_overrides[get_db] = lambda: db_session
+        # No admin override → unauthenticated
+
+        transport = ASGITransport(app=app)
+        async with AsyncClient(transport=transport, base_url="http://test") as client:
+            resp = await client.delete(f"/api/v1/races/{created.id}")
+            assert resp.status_code == 401
+
+        app.dependency_overrides.clear()
+
     @pytest.mark.asyncio
     async def test_unauthenticated_create_race_api(self, db_session: AsyncSession):
         app.dependency_overrides[get_db] = lambda: db_session
@@ -447,3 +577,4 @@ class TestRaceAPI:

         app.dependency_overrides.clear()
+
```

## New Files (not in diff, full content below):

### frontend/src/components/ConfirmDeleteModal.vue
```vue
<script setup lang="ts">
/**
 * ConfirmDeleteModal — Reusable destructive confirmation dialog.
 *
 * Usage:
 *   <ConfirmDeleteModal
 *     v-if="showModal"
 *     title="删除比赛"
 *     :item-name="raceName"
 *     :loading="isDeleting"
 *     @confirm="handleDelete"
 *     @cancel="showModal = false"
 *   />
 */

const props = withDefaults(defineProps<{
  title?: string
  itemName: string
  message?: string
  loading?: boolean
}>(), {
  title: '确认删除',
  message: '确定删除「{name}」？此操作不可撤销。',
  loading: false,
})

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

function displayMessage(): string {
  return props.message.replace('{name}', props.itemName)
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && !props.loading) {
    emit('cancel')
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      class="modal-overlay"
      role="dialog"
      aria-modal="true"
      :aria-labelledby="titleId"
      @keydown="onKeydown"
      @click.self
    >
      <div class="modal-content">
        <h2 :id="titleId" class="modal-title">{{ title }}</h2>

        <p class="modal-message">
          {{ displayMessage() }}
        </p>

        <div class="modal-actions">
          <button
            class="btn btn-cancel"
            :disabled="loading"
            @click="emit('cancel')"
          >
            取消
          </button>
          <button
            class="btn btn-destructive"
            :disabled="loading"
            @click="emit('confirm')"
          >
            {{ loading ? '删除中…' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(26, 46, 26, 0.5);
  padding: var(--spacing-4, 16px);
}

.modal-content {
  background: var(--color-surface-raised, #FFFFFF);
  border-radius: var(--rounded-lg, 14px);
  padding: var(--spacing-6, 24px);
  max-width: 400px;
  width: 100%;
  box-shadow: 0 4px 12px rgba(26, 86, 50, 0.15);
}

.modal-title {
  font-family: var(--font-display, 'Barlow Condensed', system-ui, sans-serif);
  font-size: var(--text-heading, 24px);
  font-weight: 600;
  color: var(--color-ink-primary, #1A2E1A);
  margin: 0 0 var(--spacing-4, 16px);
}

.modal-message {
  font-size: var(--text-body, 16px);
  color: var(--color-ink-primary, #1A2E1A);
  line-height: var(--text-body-line-height, 1.6);
  margin: 0 0 var(--spacing-6, 24px);
}

.modal-actions {
  display: flex;
  gap: var(--spacing-3, 12px);
  justify-content: flex-end;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 24px;
  border: none;
  border-radius: var(--rounded-md, 10px);
  font-size: var(--text-body, 16px);
  font-weight: 600;
  cursor: pointer;
  min-height: 44px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-cancel {
  background: var(--color-surface-raised, #FFFFFF);
  color: var(--color-ink-primary, #1A2E1A);
  border: 1px solid var(--color-border-strong, #A8B8A4);
}

.btn-destructive {
  background: var(--color-destructive, #C53030);
  color: #FFFFFF;
}

.btn-destructive:hover:not(:disabled) {
  opacity: 0.9;
}
</style>
```

### frontend/src/components/GradeBadge.vue
```vue
<script setup lang="ts">
defineProps<{
  grade: string
}>()

const labelMap: Record<string, string> = {
  G1: 'G1',
  G2_JPN1: 'G2·JPN1',
  YOUNG_G1: '2岁G1',
  CUSTOM: '自定义',
}
</script>

<template>
  <span
    class="grade-badge"
    :class="`grade-${grade.toLowerCase()}`"
  >
    {{ labelMap[grade] || grade }}
  </span>
</template>

<style scoped>
.grade-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: var(--rounded-sm, 6px);
  font-size: 12px;
  font-weight: 700;
  font-family: 'Barlow Condensed', 'system-ui', sans-serif;
  line-height: 1.4;
  white-space: nowrap;
}

.grade-g1 {
  background: var(--color-accent, #B8960C);
  color: #FFFFFF;
}

.grade-g2_jpn1 {
  background: #6B7280;
  color: #FFFFFF;
}

.grade-young_g1 {
  background: var(--color-primary-light, #2D7A4F);
  color: #FFFFFF;
}

.grade-custom {
  background: #6B7280;
  color: #FFFFFF;
  border: 1px dashed var(--color-border-strong, #A8B8A4);
}
</style>
```

### frontend/src/components/StatusBadge.vue
```vue
<script setup lang="ts">
defineProps<{
  status: string
}>()

const labelMap: Record<string, string> = {
  voting: '投票中',
  locked: '已锁定',
  settled: '已结算',
}

const iconMap: Record<string, string> = {
  locked: ' 🔒',
  settled: ' ✓',
}
</script>

<template>
  <span class="status-badge" :class="`status-${status}`">
    {{ labelMap[status] || status }}{{ iconMap[status] || '' }}
  </span>
</template>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
  line-height: 1.4;
  white-space: nowrap;
}

.status-voting {
  background: var(--color-primary-light, #2D7A4F);
  color: #FFFFFF;
}

.status-locked {
  background: #6B7280;
  color: #FFFFFF;
}

.status-settled {
  background: var(--color-primary-dark, #0D3A1F);
  color: #FFFFFF;
}
</style>
```

### frontend/src/pages/admin/DashboardPage.vue (full rewrite — old was placeholder)
```vue
<script setup lang="ts">
/**
 * Admin dashboard — race management list.
 * Shows all races with GradeBadge, StatusBadge, and action buttons.
 */
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import GradeBadge from '@/components/GradeBadge.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import ConfirmDeleteModal from '@/components/ConfirmDeleteModal.vue'
import { getRaces, deleteRace } from '@/api/races'
import type { RaceListItem } from '@/types/race'

type PageState = 'loading' | 'empty' | 'error' | 'success'

const router = useRouter()
const pageState = ref<PageState>('loading')
const races = ref<RaceListItem[]>([])
const errorMessage = ref('')

// Delete modal state
const showDeleteModal = ref(false)
const raceToDelete = ref<RaceListItem | null>(null)
const isDeleting = ref(false)
const deleteError = ref('')

onMounted(async () => {
  await loadRaces()
})

async function loadRaces() {
  pageState.value = 'loading'
  try {
    const data = await getRaces()
    races.value = data
    pageState.value = data.length === 0 ? 'empty' : 'success'
  } catch (err: any) {
    pageState.value = 'error'
    errorMessage.value = '加载失败，请刷新重试'
  }
}

function promptDelete(race: RaceListItem) {
  raceToDelete.value = race
  deleteError.value = ''
  showDeleteModal.value = true
}

function cancelDelete() {
  showDeleteModal.value = false
  raceToDelete.value = null
  deleteError.value = ''
}

async function handleDelete() {
  if (!raceToDelete.value) return
  isDeleting.value = true
  deleteError.value = ''
  try {
    await deleteRace(raceToDelete.value.id)
    // Remove from list without full reload
    races.value = races.value.filter(r => r.id !== raceToDelete.value!.id)
    showDeleteModal.value = false
    raceToDelete.value = null
    // If list becomes empty, show empty state
    if (races.value.length === 0) {
      pageState.value = 'empty'
    }
  } catch (err: any) {
    deleteError.value = err?.response?.data?.detail?.message || '删除失败，请重试'
  } finally {
    isDeleting.value = false
  }
}

function formatDate(dateStr: string): string {
  return dateStr.split('T')[0] || dateStr
}

const canDelete = (race: RaceListItem): boolean => {
  return race.status !== 'settled'
}
</script>

<template>
  <div class="dashboard-page">
    <div class="page-header">
      <h1 class="page-title">管理后台</h1>
      <button class="btn btn-primary" @click="router.push('/admin/races/new')">
        创建比赛
      </button>
    </div>

    <!-- Loading state -->
    <div v-if="pageState === 'loading'" class="state-box">
      <p class="state-message">加载中…</p>
    </div>

    <!-- Error state -->
    <div v-else-if="pageState === 'error'" class="state-box">
      <p class="state-message state-error">{{ errorMessage }}</p>
      <button class="btn btn-cancel" @click="loadRaces">刷新</button>
    </div>

    <!-- Empty state -->
    <div v-else-if="pageState === 'empty'" class="state-box">
      <p class="state-message">还没有比赛。管理员正在筹备中——</p>
    </div>

    <!-- Race list -->
    <div v-else class="race-table-wrapper">
      <table class="race-table">
        <thead>
          <tr>
            <th class="col-name">比赛</th>
            <th class="col-grade">等级</th>
            <th class="col-status">状态</th>
            <th class="col-date">日期</th>
            <th class="col-horses">参赛</th>
            <th class="col-actions">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="race in races" :key="race.id">
            <td class="col-name">
              <router-link
                :to="`/races/${race.id}`"
                class="race-name-link"
              >
                {{ race.name }}
              </router-link>
            </td>
            <td class="col-grade">
              <GradeBadge :grade="race.grade" />
            </td>
            <td class="col-status">
              <StatusBadge :status="race.status" />
            </td>
            <td class="col-date">{{ formatDate(race.date) }}</td>
            <td class="col-horses">{{ race.horse_count }}匹</td>
            <td class="col-actions">
              <button
                class="btn btn-sm btn-outline"
                @click="router.push(`/admin/races/${race.id}/edit`)"
              >
                编辑
              </button>
              <button
                v-if="canDelete(race)"
                class="btn btn-sm btn-destructive-outline"
                :title="race.status === 'settled' ? '已结算比赛不可删除' : '删除此比赛'"
                @click="promptDelete(race)"
              >
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Delete error inline -->
    <p v-if="deleteError" class="delete-error" role="alert">{{ deleteError }}</p>

    <!-- Delete confirmation modal -->
    <ConfirmDeleteModal
      v-if="showDeleteModal && raceToDelete"
      title="删除比赛"
      :item-name="raceToDelete.name"
      message="确定删除「{name}」？所有投票记录将被清除。"
      :loading="isDeleting"
      @confirm="handleDelete"
      @cancel="cancelDelete"
    />
  </div>
</template>

<style scoped>
/* ... full styles including mobile responsive ... */
</style>
```

### frontend/src/pages/admin/EditRacePage.vue (changes)
Key additions:
- Import `ConfirmDeleteModal` and `deleteRace`
- Added `raceNameDisplay`, `showDeleteModal`, `isDeleting`, `deleteError` refs
- `promptDelete()`, `cancelDelete()`, `handleDelete()` functions
- Delete button in form-actions (destructive style)
- ConfirmDeleteModal in template
- `.btn-destructive` CSS class

## Task

Examine this diff and all new file contents. Report findings as a Markdown list. Each finding: severity (High/Med/Low), category (Bug/Security/Logic/CodeSmell/MissingEdgeCase), description with line references, and suggested fix.
