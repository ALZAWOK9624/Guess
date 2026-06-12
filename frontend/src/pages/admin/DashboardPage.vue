<script setup lang="ts">
/**
 * Admin dashboard — race management list.
 * Shows all races with GradeBadge, StatusBadge, and action buttons.
 */
import { ref, onMounted, onUnmounted } from 'vue'
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

// Guard against async operations after unmount
let isMounted = true
onMounted(async () => {
  await loadRaces()
})
onUnmounted(() => {
  isMounted = false
})

async function loadRaces() {
  pageState.value = 'loading'
  try {
    const data = await getRaces()
    if (!isMounted) return
    races.value = data
    pageState.value = data.length === 0 ? 'empty' : 'success'
  } catch (err: any) {
    if (!isMounted) return
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
  if (!raceToDelete.value || isDeleting.value) return
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
  if (!dateStr) return ''
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
.dashboard-page {
  padding: var(--spacing-4, 16px);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-6, 24px);
}

.page-title {
  font-family: var(--font-display, 'Barlow Condensed', system-ui, sans-serif);
  font-size: var(--text-heading, 24px);
  font-weight: 600;
  color: var(--color-primary, #1A5632);
  margin: 0;
}

.state-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-4, 16px);
  padding: var(--spacing-12, 48px);
  text-align: center;
}

.state-message {
  font-size: var(--text-body, 16px);
  color: var(--color-ink-secondary, #4A5A4A);
  margin: 0;
}

.state-error {
  color: var(--color-destructive, #C53030);
}

/* Table */
.race-table-wrapper {
  overflow-x: auto;
}

.race-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-body-sm, 14px);
}

.race-table thead th {
  text-align: left;
  padding: var(--spacing-3, 12px) var(--spacing-2, 8px);
  font-weight: 600;
  color: var(--color-ink-secondary, #4A5A4A);
  border-bottom: 1px solid var(--color-border-hairline, #D4DCD0);
  white-space: nowrap;
}

.race-table tbody td {
  padding: var(--spacing-3, 12px) var(--spacing-2, 8px);
  border-bottom: 1px solid var(--color-border-hairline, #D4DCD0);
  vertical-align: middle;
}

.col-name { min-width: 140px; }
.col-grade { width: 80px; }
.col-status { width: 100px; }
.col-date { width: 100px; white-space: nowrap; }
.col-horses { width: 60px; text-align: center; }
.col-actions { width: 140px; white-space: nowrap; }

.race-name-link {
  color: var(--color-primary, #1A5632);
  font-weight: 600;
  text-decoration: none;
}

.race-name-link:hover {
  text-decoration: underline;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: var(--rounded-md, 10px);
  font-size: var(--text-body, 16px);
  font-weight: 600;
  cursor: pointer;
  min-height: 44px;
  padding: 10px 24px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-sm {
  font-size: var(--text-body-sm, 14px);
  padding: 6px 14px;
  min-height: 36px;
}

.btn-primary {
  background: var(--color-primary, #1A5632);
  color: #FFFFFF;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-light, #2D7A4F);
}

.btn-cancel {
  background: var(--color-surface-raised, #FFFFFF);
  color: var(--color-ink-primary, #1A2E1A);
  border: 1px solid var(--color-border-strong, #A8B8A4);
}

.btn-outline {
  background: var(--color-surface-raised, #FFFFFF);
  color: var(--color-primary, #1A5632);
  border: 1px solid var(--color-border-hairline, #D4DCD0);
  margin-right: var(--spacing-2, 8px);
}

.btn-outline:hover {
  border-color: var(--color-primary, #1A5632);
}

.btn-destructive-outline {
  background: var(--color-surface-raised, #FFFFFF);
  color: var(--color-destructive, #C53030);
  border: 1px solid var(--color-destructive, #C53030);
}

.btn-destructive-outline:hover {
  background: var(--color-destructive-light, #FED7D7);
}

.delete-error {
  font-size: var(--text-body-sm, 14px);
  color: var(--color-destructive, #C53030);
  padding: 10px 12px;
  background: var(--color-destructive-light, #FED7D7);
  border-radius: var(--rounded-md, 10px);
  margin-top: var(--spacing-4, 16px);
}

/* Mobile: stack rows as cards */
@media (max-width: 767px) {
  .race-table thead {
    display: none;
  }

  .race-table,
  .race-table tbody,
  .race-table tr,
  .race-table td {
    display: block;
  }

  .race-table tbody tr {
    background: var(--color-surface-raised, #FFFFFF);
    border: 1px solid var(--color-border-hairline, #D4DCD0);
    border-radius: var(--rounded-md, 10px);
    padding: var(--spacing-4, 16px);
    margin-bottom: var(--spacing-3, 12px);
  }

  .race-table tbody td {
    border: none;
    padding: var(--spacing-1, 4px) 0;
  }

  .col-name {
    font-size: var(--text-subheading, 18px);
  }

  .col-grade,
  .col-status {
    display: inline-block;
    margin-right: var(--spacing-2, 8px);
  }

  .col-actions {
    padding-top: var(--spacing-2, 8px);
  }
}
</style>
