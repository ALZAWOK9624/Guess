<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { getHorses, createHorse, updateHorse, deleteHorse } from '@/api/horses'
import type { Horse, HorseCreatePayload, HorseUpdatePayload } from '@/types/horse'

type PageState = 'loading' | 'empty' | 'error' | 'success'

const pageState = ref<PageState>('loading')
const errorMessage = ref('加载失败，请刷新重试')
const refreshing = ref(false)
const horses = ref<Horse[]>([])
const search = ref('')

// Modal state
const showModal = ref(false)
const editingHorse = ref<Horse | null>(null)
const saving = ref(false)
const modalError = ref('')

// Form fields
const formName = ref('')
const formSex = ref('')
const formAge = ref<number | null>(null)
const formOrigin = ref('')
const formSire = ref('')
const formDamsire = ref('')
const formWeight = ref('')
const formJockey = ref('')
const formPreviousResult = ref('')
const formBestWin = ref('')

let debounceTimer: ReturnType<typeof setTimeout> | null = null

async function loadHorses() {
  pageState.value = 'loading'
  errorMessage.value = '加载失败，请刷新重试'

  try {
    const data = await getHorses(search.value || undefined)
    horses.value = data
    pageState.value = data.length === 0 ? 'empty' : 'success'
  } catch {
    pageState.value = 'error'
  }
}

async function handleRefresh() {
  refreshing.value = true
  await loadHorses()
  refreshing.value = false
}

function debouncedSearch() {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    loadHorses()
  }, 300)
}

watch(search, debouncedSearch)

function resetForm() {
  formName.value = ''
  formSex.value = ''
  formAge.value = null
  formOrigin.value = ''
  formSire.value = ''
  formDamsire.value = ''
  formWeight.value = ''
  formJockey.value = ''
  formPreviousResult.value = ''
  formBestWin.value = ''
  modalError.value = ''
}

function openCreateModal() {
  editingHorse.value = null
  resetForm()
  showModal.value = true
}

function openEditModal(horse: Horse) {
  editingHorse.value = horse
  formName.value = horse.name
  formSex.value = horse.sex || ''
  formAge.value = horse.age
  formOrigin.value = horse.origin || ''
  formSire.value = horse.sire || ''
  formDamsire.value = horse.damsire || ''
  formWeight.value = horse.weight || ''
  formJockey.value = horse.jockey || ''
  formPreviousResult.value = horse.previous_result || ''
  formBestWin.value = horse.best_win || ''
  modalError.value = ''
  showModal.value = true
}

async function handleSave() {
  const name = formName.value.trim()
  if (!name) {
    modalError.value = '马匹名称不能为空'
    return
  }

  saving.value = true
  modalError.value = ''

  try {
    if (editingHorse.value) {
      // Only send changed fields for PATCH
      const payload: HorseUpdatePayload = {}
      if (name !== editingHorse.value.name) payload.name = name
      if (formSex.value !== (editingHorse.value.sex || '')) payload.sex = formSex.value || null
      if (formAge.value !== editingHorse.value.age) payload.age = formAge.value
      if (formOrigin.value !== (editingHorse.value.origin || '')) payload.origin = formOrigin.value || null
      if (formSire.value !== (editingHorse.value.sire || '')) payload.sire = formSire.value || null
      if (formDamsire.value !== (editingHorse.value.damsire || '')) payload.damsire = formDamsire.value || null
      if (formWeight.value !== (editingHorse.value.weight || '')) payload.weight = formWeight.value || null
      if (formJockey.value !== (editingHorse.value.jockey || '')) payload.jockey = formJockey.value || null
      if (formPreviousResult.value !== (editingHorse.value.previous_result || '')) payload.previous_result = formPreviousResult.value || null
      if (formBestWin.value !== (editingHorse.value.best_win || '')) payload.best_win = formBestWin.value || null

      const updated = await updateHorse(editingHorse.value.id, payload)
      const idx = horses.value.findIndex((h) => h.id === updated.id)
      if (idx !== -1) horses.value[idx] = updated
    } else {
      const payload: HorseCreatePayload = {
        name,
        sex: formSex.value || null,
        age: formAge.value,
        origin: formOrigin.value || null,
        sire: formSire.value || null,
        damsire: formDamsire.value || null,
        weight: formWeight.value || null,
        jockey: formJockey.value || null,
        previous_result: formPreviousResult.value || null,
        best_win: formBestWin.value || null,
      }
      const created = await createHorse(payload)
      // Insert in sorted position to match backend ordering
      horses.value.push(created)
      horses.value.sort((a, b) => a.name.localeCompare(b.name))
      pageState.value = 'success'
    }

    showModal.value = false
  } catch (err: unknown) {
    const response = (err as Record<string, unknown>)?.response as Record<string, unknown> | undefined
    const detail = response?.data as Record<string, unknown> | undefined
    const message = ((detail?.detail as Record<string, unknown> | undefined)?.message as string) || '保存失败，请重试'
    modalError.value = message
  } finally {
    saving.value = false
  }
}

async function handleDelete(horse: Horse) {
  const confirmed = confirm(`确定删除马匹「${horse.name}」？此操作不可撤销。`)
  if (!confirmed) return

  try {
    await deleteHorse(horse.id)
    horses.value = horses.value.filter((h) => h.id !== horse.id)
    if (horses.value.length === 0) {
      pageState.value = 'empty'
    }
  } catch (err: unknown) {
    const response = (err as Record<string, unknown>)?.response as Record<string, unknown> | undefined
    const detail = response?.data as Record<string, unknown> | undefined
    const message = ((detail?.detail as Record<string, unknown> | undefined)?.message as string) || '删除失败，请重试'
    errorMessage.value = message
    setTimeout(() => { errorMessage.value = '加载失败，请刷新重试' }, 3000)
  }
}

onMounted(loadHorses)
onUnmounted(() => {
  if (debounceTimer) clearTimeout(debounceTimer)
})
</script>

<template>
  <div class="horses-page">
    <header class="page-header">
      <h1 class="page-title">马匹管理</h1>
    </header>

    <!-- Skeleton loading -->
    <template v-if="pageState === 'loading'">
      <div class="skeleton-container" role="status" aria-live="polite" aria-label="加载中">
        <div v-for="i in 5" :key="i" class="skeleton-row"></div>
      </div>
    </template>

    <!-- Empty state -->
    <template v-else-if="pageState === 'empty'">
      <div class="state-container" role="status" aria-live="polite">
        <p class="empty-text">
          马匹库为空——创建第一场比赛时，参赛马匹将自动入库。
        </p>
        <button class="btn btn-primary" @click="openCreateModal">新建马匹</button>
      </div>
    </template>

    <!-- Error state (with search bar) -->
    <template v-else-if="pageState === 'error'">
      <div class="toolbar">
        <input
          v-model="search"
          type="text"
          class="search-input"
          placeholder="搜索马匹名称..."
          aria-label="搜索马匹名称"
        />
        <button class="btn btn-primary" @click="openCreateModal">新建马匹</button>
      </div>
      <div class="state-container" role="alert" aria-live="polite">
        <p class="error-text">{{ errorMessage }}</p>
        <button
          class="refresh-btn"
          :disabled="refreshing"
          @click="handleRefresh"
        >
          {{ refreshing ? '刷新中…' : '刷新重试' }}
        </button>
      </div>
    </template>

    <!-- Content: horse table -->
    <template v-else>
      <div class="toolbar">
        <input
          v-model="search"
          type="text"
          class="search-input"
          placeholder="搜索马匹名称..."
          aria-label="搜索马匹名称"
        />
        <button class="btn btn-primary" @click="openCreateModal">新建马匹</button>
      </div>

      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th scope="col">名称</th>
              <th scope="col">性别</th>
              <th scope="col">年龄</th>
              <th scope="col">产地</th>
              <th scope="col">父系</th>
              <th scope="col">母父</th>
              <th scope="col">体重</th>
              <th scope="col">骑手</th>
              <th scope="col">前走</th>
              <th scope="col">最佳胜马</th>
              <th scope="col">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="horse in horses" :key="horse.id">
              <td><strong>{{ horse.name }}</strong></td>
              <td>{{ horse.sex || '-' }}</td>
              <td>{{ horse.age ?? '-' }}</td>
              <td>{{ horse.origin || '-' }}</td>
              <td>{{ horse.sire || '-' }}</td>
              <td>{{ horse.damsire || '-' }}</td>
              <td>{{ horse.weight || '-' }}</td>
              <td>{{ horse.jockey || '-' }}</td>
              <td>{{ horse.previous_result || '-' }}</td>
              <td>{{ horse.best_win || '-' }}</td>
              <td class="actions-cell">
                <button class="btn btn-sm" @click="openEditModal(horse)">编辑</button>
                <button class="btn btn-sm btn-danger" @click="handleDelete(horse)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <!-- Create/Edit Modal -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-content" role="dialog" :aria-label="editingHorse ? '编辑马匹' : '新建马匹'">
          <h2 class="modal-title">{{ editingHorse ? '编辑马匹' : '新建马匹' }}</h2>

          <div v-if="modalError" class="error-banner">{{ modalError }}</div>

          <form @submit.prevent="handleSave" class="horse-form">
            <div class="form-row">
              <label class="form-label">
                名称 <span class="required">*</span>
                <input v-model="formName" type="text" class="form-input" required maxlength="100" placeholder="马匹名称" />
              </label>
            </div>
            <div class="form-grid">
              <label class="form-label">
                性别
                <input v-model="formSex" type="text" class="form-input" maxlength="10" placeholder="牡/牝/騸" />
              </label>
              <label class="form-label">
                年龄
                <input v-model.number="formAge" type="number" class="form-input" min="1" max="99" placeholder="年龄" />
              </label>
              <label class="form-label">
                产地
                <input v-model="formOrigin" type="text" class="form-input" maxlength="100" placeholder="日本/美国..." />
              </label>
              <label class="form-label">
                父系
                <input v-model="formSire" type="text" class="form-input" maxlength="100" placeholder="父马名称" />
              </label>
              <label class="form-label">
                母父
                <input v-model="formDamsire" type="text" class="form-input" maxlength="100" placeholder="母父名称" />
              </label>
              <label class="form-label">
                体重
                <input v-model="formWeight" type="text" class="form-input" maxlength="20" placeholder="如 520kg" />
              </label>
              <label class="form-label">
                骑手
                <input v-model="formJockey" type="text" class="form-input" maxlength="50" placeholder="骑手名" />
              </label>
              <label class="form-label">
                前走成绩
                <input v-model="formPreviousResult" type="text" class="form-input" maxlength="100" placeholder="如 1着" />
              </label>
              <label class="form-label">
                最佳胜马
                <input v-model="formBestWin" type="text" class="form-input" maxlength="100" placeholder="如 有马纪念(G1)" />
              </label>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-cancel" @click="showModal = false">取消</button>
              <button type="submit" class="btn btn-primary" :disabled="saving">
                {{ saving ? '保存中...' : (editingHorse ? '保存修改' : '确认创建') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.horses-page {
  padding: var(--spacing-16);
  max-width: 1280px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: var(--spacing-20);
}

.page-title {
  font-family: 'Barlow Condensed', system-ui, sans-serif;
  font-size: 28px;
  font-weight: 600;
  color: var(--color-primary);
}

/* Toolbar */
.toolbar {
  display: flex;
  gap: var(--spacing-3, 12px);
  margin-bottom: var(--spacing-4, 16px);
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 200px;
  padding: 8px 12px;
  border: 1px solid var(--color-border-hairline, #D4DCD0);
  border-radius: var(--rounded-sm, 6px);
  font-size: var(--text-body, 16px);
  font-family: var(--font-body);
  color: var(--color-ink-primary, #1A2E1A);
  background: var(--color-surface-raised, #FFFFFF);
}

.search-input:focus {
  outline: 2px solid var(--color-primary, #1A5632);
  outline-offset: 2px;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  border: none;
  border-radius: var(--rounded-sm, 6px);
  font-size: var(--text-body-sm, 14px);
  cursor: pointer;
  min-height: 44px;
  white-space: nowrap;
  transition: opacity 0.15s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--color-primary, #1A5632);
  color: #FFFFFF;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-light, #2D7A4F);
}

.btn-sm {
  padding: 4px 12px;
  font-size: var(--text-caption, 12px);
  min-height: 44px;
  background: var(--color-surface-raised, #FFFFFF);
  border: 1px solid var(--color-border-hairline, #D4DCD0);
  color: var(--color-ink-primary, #1A2E1A);
}

.btn-sm:hover {
  background: var(--color-surface-base, #F8FAF7);
}

.btn-danger {
  color: var(--color-destructive, #C53030);
  border-color: var(--color-destructive, #C53030);
}

.btn-danger:hover {
  background: var(--color-destructive-light, #FED7D7);
}

.btn-cancel {
  background: var(--color-surface-base, #F8FAF7);
  border: 1px solid var(--color-border-hairline, #D4DCD0);
  color: var(--color-ink-primary, #1A2E1A);
}

/* Skeleton */
.skeleton-container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-8);
}

.skeleton-row {
  height: 40px;
  background: linear-gradient(90deg, var(--color-surface-base) 25%, var(--color-border-hairline) 50%, var(--color-surface-base) 75%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
  border-radius: var(--rounded-sm);
}

/* State patterns */
.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 30vh;
  text-align: center;
  gap: var(--spacing-16);
  padding: var(--spacing-32) var(--spacing-16);
}

.empty-text {
  color: var(--color-ink-secondary);
  font-size: var(--text-body);
  max-width: 400px;
  line-height: 1.6;
}

.error-text {
  color: var(--color-destructive);
  font-size: var(--text-body);
}

.refresh-btn {
  padding: 10px 24px;
  font-size: var(--text-body);
  font-weight: 600;
  color: #ffffff;
  background: var(--color-primary);
  border: none;
  border-radius: var(--rounded-md);
  cursor: pointer;
  min-height: 44px;
  transition: background 0.2s;
}

.refresh-btn:hover {
  background: var(--color-primary-light);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Table */
.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-body-sm, 14px);
}

th {
  text-align: left;
  padding: var(--spacing-3, 12px) var(--spacing-2, 8px);
  font-weight: 600;
  color: var(--color-ink-secondary, #4A5A4A);
  border-bottom: 2px solid var(--color-border-hairline, #D4DCD0);
  white-space: nowrap;
}

td {
  padding: var(--spacing-3, 12px) var(--spacing-2, 8px);
  border-bottom: 1px solid var(--color-border-hairline, #D4DCD0);
  white-space: nowrap;
}

.actions-cell {
  display: flex;
  gap: var(--spacing-2, 8px);
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--spacing-16);
}

.modal-content {
  background: var(--color-surface-raised, #FFFFFF);
  border-radius: var(--rounded-lg, 14px);
  padding: var(--spacing-20, 24px);
  width: 100%;
  max-width: 640px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}

.modal-title {
  font-family: 'Barlow Condensed', system-ui, sans-serif;
  font-size: 22px;
  font-weight: 600;
  color: var(--color-primary, #1A5632);
  margin-bottom: var(--spacing-16, 20px);
}

/* Form */
.horse-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-12, 16px);
}

.form-row {
  width: 100%;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-12, 16px);
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}

.form-label {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1, 4px);
  font-size: var(--text-body-sm, 14px);
  font-weight: 500;
  color: var(--color-ink-primary, #1A2E1A);
}

.required {
  color: var(--color-destructive, #C53030);
}

.form-input {
  padding: 8px 12px;
  border: 1px solid var(--color-border-hairline, #D4DCD0);
  border-radius: var(--rounded-sm, 6px);
  font-size: var(--text-body, 16px);
  font-family: var(--font-body);
  color: var(--color-ink-primary, #1A2E1A);
  background: var(--color-surface-base, #F8FAF7);
}

.form-input:focus {
  outline: 2px solid var(--color-primary, #1A5632);
  outline-offset: 2px;
}

.form-actions {
  display: flex;
  gap: var(--spacing-3, 12px);
  justify-content: flex-end;
  margin-top: var(--spacing-8, 12px);
}

.error-banner {
  padding: var(--spacing-3, 12px);
  margin-bottom: var(--spacing-3, 12px);
  background: var(--color-destructive-light, #FED7D7);
  color: var(--color-destructive, #C53030);
  border-radius: var(--rounded-sm, 6px);
  font-size: var(--text-body-sm, 14px);
}

@media (prefers-reduced-motion: reduce) {
  .skeleton-row {
    animation: none;
    background: var(--color-surface-base);
  }
  .refresh-btn,
  .btn {
    transition: none;
  }
}
</style>
