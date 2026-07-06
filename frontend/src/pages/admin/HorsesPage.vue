<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { getHorses, getOriginsStats, getLocationsStats, createHorse, updateHorse, deleteHorse, toggleHemisphere } from '@/api/horses'
import type { Horse, HorseCreatePayload, HorseUpdatePayload } from '@/types/horse'

type PageState = 'loading' | 'empty' | 'error' | 'success'

const pageState = ref<PageState>('loading')
const errorMessage = ref('加载失败，请刷新重试')
const refreshing = ref(false)
const horses = ref<Horse[]>([])
const search = ref('')

// DB-sourced lists
const sortedCountries = ref<string[]>([])
const countryHemispheres = ref<Record<string, string>>({})  // origin → hemisphere
const sortedLocations = ref<string[]>([])

// Modal state
const showModal = ref(false)
const editingHorse = ref<Horse | null>(null)
const saving = ref(false)
const modalError = ref('')

// Sex options
const sexOptions = ['牡', '牝', '骟']

// Hemisphere options
const hemisphereOptions = [
  { value: 'north', label: '北半球' },
  { value: 'south', label: '南半球' },
]

// Country state: select or add-new mode
const isAddingCountry = ref(false)
const newCountryHemisphere = ref('north')

// Location state: select or add-new mode
const isAddingLocation = ref(false)

// Form fields
const formName = ref('')
const formSex = ref('')
const formBirthYear = ref<number | null>(null)
const formOrigin = ref('')
const formHemisphere = ref('')
const formNewCountry = ref('')
const formLocation = ref('')
const formNewLocation = ref('')
const formSire = ref('')
const formDamsire = ref('')
const formPreviousResult = ref('')
const formPreviousResultDate = ref('')
const formPreviousResultPosition = ref<number | null>(null)
const formBestWin = ref('')
const formBestWinDate = ref('')

let debounceTimer: ReturnType<typeof setTimeout> | null = null

// Origin-related
function handleOriginSelect(e: Event) {
  const val = (e.target as HTMLSelectElement).value
  if (val === '__new__') {
    isAddingCountry.value = true
    newCountryHemisphere.value = 'north'
    formOrigin.value = ''
    formHemisphere.value = ''
  } else {
    formOrigin.value = val
    formHemisphere.value = countryHemispheres.value[val] || ''
  }
}

const togglingHemisphere = ref(false)

async function handleToggleHemisphere() {
  if (!formOrigin.value || togglingHemisphere.value) return
  togglingHemisphere.value = true
  try {
    const result = await toggleHemisphere(formOrigin.value)
    formHemisphere.value = result.new_hemisphere
    countryHemispheres.value[formOrigin.value] = result.new_hemisphere
  } catch {
    // silent
  } finally {
    togglingHemisphere.value = false
  }
}

function confirmNewCountry() {
  const name = formNewCountry.value.trim()
  if (!name) return
  formOrigin.value = name
  formHemisphere.value = newCountryHemisphere.value
  isAddingCountry.value = false
  countryHemispheres.value[name] = newCountryHemisphere.value
  // Note: sortedCountries is NOT modified here — the new country only
  // appears as a temporary option in the select until the form is saved.
  // After save, refreshCountryList() adds it to sortedCountries.
}

function cancelNewCountry() {
  isAddingCountry.value = false
  formOrigin.value = ''
  formHemisphere.value = ''
}

function handleLocationSelect(e: Event) {
  const val = (e.target as HTMLSelectElement).value
  if (val === '__new__') {
    isAddingLocation.value = true
    formLocation.value = ''
  } else {
    formLocation.value = val
  }
}

function confirmNewLocation() {
  const name = formNewLocation.value.trim()
  if (!name) return
  formLocation.value = name
  isAddingLocation.value = false
  // Not added to sortedLocations until saved. Shows as temporary option.
}

function cancelNewLocation() {
  isAddingLocation.value = false
  formLocation.value = ''
}

async function loadHorses() {
  pageState.value = 'loading'
  errorMessage.value = '加载失败，请刷新重试'

  try {
    const [data, stats, locStats] = await Promise.all([
      getHorses(search.value || undefined),
      getOriginsStats(),
      getLocationsStats(),
    ])
    horses.value = data
    // Build country list and hemisphere map
    const sorted = [...stats].sort((a, b) => {
      if (a.count !== b.count) return b.count - a.count
      return a.origin.localeCompare(b.origin)
    })
    sortedCountries.value = sorted.map(s => s.origin)
    const hMap: Record<string, string> = {}
    for (const s of sorted) {
      if (s.hemisphere) hMap[s.origin] = s.hemisphere
    }
    countryHemispheres.value = hMap
    // Build location list
    sortedLocations.value = [...locStats]
      .sort((a, b) => {
        if (a.count !== b.count) return b.count - a.count
        return a.location.localeCompare(b.location)
      })
      .map(s => s.location)
    pageState.value = data.length === 0 ? 'empty' : 'success'
  } catch {
    pageState.value = 'error'
  }
}

async function refreshCountryList() {
  try {
    const [stats, locStats] = await Promise.all([
      getOriginsStats(),
      getLocationsStats(),
    ])
    const sorted = [...stats].sort((a, b) => {
      if (a.count !== b.count) return b.count - a.count
      return a.origin.localeCompare(b.origin)
    })
    sortedCountries.value = sorted.map(s => s.origin)
    const hMap: Record<string, string> = {}
    for (const s of sorted) {
      if (s.hemisphere) hMap[s.origin] = s.hemisphere
    }
    countryHemispheres.value = hMap
    sortedLocations.value = [...locStats]
      .sort((a, b) => {
        if (a.count !== b.count) return b.count - a.count
        return a.location.localeCompare(b.location)
      })
      .map(s => s.location)
  } catch {
    // silently ignore
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
  formBirthYear.value = null
  formOrigin.value = ''
  formHemisphere.value = ''
  formNewCountry.value = ''
  isAddingCountry.value = false
  newCountryHemisphere.value = 'north'
  formLocation.value = ''
  formNewLocation.value = ''
  isAddingLocation.value = false
  formSire.value = ''
  formDamsire.value = ''
  formPreviousResult.value = ''
  formPreviousResultDate.value = ''
  formPreviousResultPosition.value = null
  formBestWin.value = ''
  formBestWinDate.value = ''
  modalError.value = ''
}

function openCreateModal() {
  editingHorse.value = null
  resetForm()
  showModal.value = true
}

function openEditModal(horse: Horse) {
  editingHorse.value = horse
  isAddingCountry.value = false
  isAddingLocation.value = false
  formNewCountry.value = ''
  formNewLocation.value = ''
  formName.value = horse.name
  formSex.value = horse.sex || ''
  formBirthYear.value = horse.birth_year
  formOrigin.value = horse.origin || ''
  formHemisphere.value = horse.hemisphere || countryHemispheres.value[horse.origin || ''] || ''
  formLocation.value = horse.location || ''
  formSire.value = horse.sire || ''
  formDamsire.value = horse.damsire || ''
  formPreviousResult.value = horse.previous_result || ''
  formPreviousResultDate.value = horse.previous_result_date || ''
  formPreviousResultPosition.value = horse.previous_result_position
  formBestWin.value = horse.best_win || ''
  formBestWinDate.value = horse.best_win_date || ''
  modalError.value = ''
  showModal.value = true
}

function handleSave() {
  const name = formName.value.trim()
  if (!name) {
    modalError.value = '马匹名称不能为空'
    return
  }

  // Validate previous_result fields: if any is provided, all must be
  const hasPrevResult = !!formPreviousResult.value
  const hasPrevDate = !!formPreviousResultDate.value
  const hasPrevPos = formPreviousResultPosition.value !== null
  if (hasPrevResult || hasPrevDate || hasPrevPos) {
    if (!hasPrevResult || !hasPrevDate || !hasPrevPos) {
      modalError.value = '前走成绩必须同时填写比赛名称、日期和名次'
      return
    }
  }

  // Validate best_win fields
  const hasBestWin = !!formBestWin.value
  const hasBestDate = !!formBestWinDate.value
  if (hasBestWin !== hasBestDate) {
    modalError.value = '主要胜鞍必须同时填写比赛名称和日期'
    return
  }

  saving.value = true
  modalError.value = ''

  // Wrap in async to use await
  ;(async () => {
    try {
      if (editingHorse.value) {
        const payload: HorseUpdatePayload = {}
        if (name !== editingHorse.value.name) payload.name = name
        if (formSex.value !== (editingHorse.value.sex || '')) payload.sex = formSex.value || null
        if (formBirthYear.value !== editingHorse.value.birth_year) payload.birth_year = formBirthYear.value
        if (formOrigin.value !== (editingHorse.value.origin || '')) payload.origin = formOrigin.value || null
        if (formHemisphere.value !== (editingHorse.value.hemisphere || '')) payload.hemisphere = formHemisphere.value || null
        if (formLocation.value !== (editingHorse.value.location || '')) payload.location = formLocation.value || null
        if (formSire.value !== (editingHorse.value.sire || '')) payload.sire = formSire.value || null
        if (formDamsire.value !== (editingHorse.value.damsire || '')) payload.damsire = formDamsire.value || null
        if (formPreviousResult.value !== (editingHorse.value.previous_result || '')) payload.previous_result = formPreviousResult.value || null
        if (formPreviousResultDate.value !== (editingHorse.value.previous_result_date || '')) payload.previous_result_date = formPreviousResultDate.value || null
        if (formPreviousResultPosition.value !== editingHorse.value.previous_result_position) payload.previous_result_position = formPreviousResultPosition.value
        if (formBestWin.value !== (editingHorse.value.best_win || '')) payload.best_win = formBestWin.value || null
        if (formBestWinDate.value !== (editingHorse.value.best_win_date || '')) payload.best_win_date = formBestWinDate.value || null

        const updated = await updateHorse(editingHorse.value.id, payload)
        const idx = horses.value.findIndex((h) => h.id === updated.id)
        if (idx !== -1) horses.value[idx] = updated
      } else {
        const payload: HorseCreatePayload = {
          name,
          sex: formSex.value || null,
          birth_year: formBirthYear.value,
          origin: formOrigin.value || null,
          hemisphere: formHemisphere.value || null,
          location: formLocation.value || null,
          sire: formSire.value || null,
          damsire: formDamsire.value || null,
          previous_result: formPreviousResult.value || null,
          previous_result_date: formPreviousResultDate.value || null,
          previous_result_position: formPreviousResultPosition.value,
          best_win: formBestWin.value || null,
          best_win_date: formBestWinDate.value || null,
        }
        const created = await createHorse(payload)
        horses.value.push(created)
        horses.value.sort((a, b) => a.name.localeCompare(b.name))
        pageState.value = 'success'
      }

      // Refresh country list to include any newly added country
      await refreshCountryList()

      showModal.value = false
    } catch (err: unknown) {
      const response = (err as Record<string, unknown>)?.response as Record<string, unknown> | undefined
      const detail = response?.data as Record<string, unknown> | undefined
      const message = ((detail?.detail as Record<string, unknown> | undefined)?.message as string) || '保存失败，请重试'
      modalError.value = message
    } finally {
      saving.value = false
    }
  })()
}

async function handleDelete(horse: Horse) {
  const confirmed = confirm(`确定删除马匹「${horse.name}」？此操作不可撤销。`)
  if (!confirmed) return
  try {
    await deleteHorse(horse.id)
    horses.value = horses.value.filter((h) => h.id !== horse.id)
    if (horses.value.length === 0) pageState.value = 'empty'
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
        <p class="empty-text">马匹库为空——创建第一场比赛时，参赛马匹将自动入库。</p>
        <button class="btn btn-primary" @click="openCreateModal">新建马匹</button>
      </div>
    </template>

    <!-- Error state -->
    <template v-else-if="pageState === 'error'">
      <div class="toolbar">
        <input v-model="search" type="text" class="search-input" placeholder="搜索马匹名称..." aria-label="搜索马匹名称" />
        <button class="btn btn-primary" @click="openCreateModal">新建马匹</button>
      </div>
      <div class="state-container" role="alert" aria-live="polite">
        <p class="error-text">{{ errorMessage }}</p>
        <button class="refresh-btn" :disabled="refreshing" @click="handleRefresh">
          {{ refreshing ? '刷新中…' : '刷新重试' }}
        </button>
      </div>
    </template>

    <!-- Content: horse table -->
    <template v-else>
      <div class="toolbar">
        <input v-model="search" type="text" class="search-input" placeholder="搜索马匹名称..." aria-label="搜索马匹名称" />
        <button class="btn btn-primary" @click="openCreateModal">新建马匹</button>
      </div>

      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th scope="col">名称</th>
              <th scope="col">性别</th>
              <th scope="col">年龄</th>
              <th scope="col">出生国</th>
              <th scope="col">所属地</th>
              <th scope="col">父系</th>
              <th scope="col">母父</th>
              <th scope="col">前走</th>
              <th scope="col">主要胜鞍</th>
              <th scope="col">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="horse in horses" :key="horse.id">
              <td><strong>{{ horse.name }}</strong></td>
              <td>{{ horse.sex || '-' }}</td>
              <td>{{ horse.birth_year ?? '-' }}</td>
              <td>{{ horse.origin || '-' }}{{ horse.hemisphere === 'south' ? ' (南)' : horse.hemisphere === 'north' ? ' (北)' : '' }}</td>
              <td>{{ horse.location || '-' }}</td>
              <td>{{ horse.sire || '-' }}</td>
              <td>{{ horse.damsire || '-' }}</td>
              <td>
                <template v-if="horse.previous_result">
                  <template v-if="horse.previous_result_date">{{ horse.previous_result_date }} </template>
                  {{ horse.previous_result }}
                </template>
                <span v-else>-</span>
              </td>
              <td>
                <template v-if="horse.best_win">
                  <template v-if="horse.best_win_date">{{ horse.best_win_date }} </template>
                  {{ horse.best_win }}
                </template>
                <span v-else>-</span>
              </td>
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
                <select v-model="formSex" class="form-input">
                  <option value="" disabled>选择性别</option>
                  <option v-for="s in sexOptions" :key="s" :value="s">{{ s }}</option>
                </select>
              </label>
              <label class="form-label">
                出生年
                <input v-model.number="formBirthYear" type="number" class="form-input" min="1900" :max="new Date().getFullYear()" placeholder="如 2022" />
              </label>
              <label class="form-label">
                出生国
                <template v-if="!isAddingCountry">
                  <select class="form-input" v-model="formOrigin" @change="handleOriginSelect">
                    <option value="" disabled>选择国家或新增</option>
                    <option value="__new__">＋ 新增国家</option>
                    <!-- Pending new country (confirmed but not yet saved) -->
                    <option v-if="formOrigin && !sortedCountries.includes(formOrigin)" :value="formOrigin">{{ formOrigin }} (未保存)</option>
                    <option v-for="c in sortedCountries" :key="c" :value="c">{{ c }}</option>
                  </select>
                  <template v-if="formHemisphere">
                    <span class="hemisphere-badge">{{ formHemisphere === 'north' ? '北半球' : '南半球' }}</span>
                    <button
                      v-if="sortedCountries.includes(formOrigin)"
                      type="button"
                      class="btn btn-hemisphere-toggle"
                      :disabled="togglingHemisphere"
                      @click="handleToggleHemisphere"
                    >
                      {{ togglingHemisphere ? '切换中…' : '切换半球' }}
                    </button>
                  </template>
                </template>
                <template v-else>
                  <input
                    v-model="formNewCountry"
                    type="text"
                    class="form-input"
                    maxlength="100"
                    placeholder="输入新增国家名称"
                    autofocus
                  />
                  <div class="hemisphere-select-row">
                    <label v-for="h in hemisphereOptions" :key="h.value" class="radio-label">
                      <input type="radio" v-model="newCountryHemisphere" :value="h.value" />
                      {{ h.label }}
                    </label>
                  </div>
                  <div class="add-cancel-row">
                    <button type="button" class="btn btn-sm btn-primary" :disabled="!formNewCountry.trim()" @click="confirmNewCountry">确认</button>
                    <button type="button" class="btn btn-sm" @click="cancelNewCountry">取消</button>
                  </div>
                </template>
              </label>
              <label class="form-label">
                所属地
                <template v-if="!isAddingLocation">
                  <select class="form-input" v-model="formLocation" @change="handleLocationSelect">
                    <option value="" disabled>选择所属地或新增</option>
                    <option value="__new__">＋ 新增所属地</option>
                    <!-- Pending new location (confirmed but not yet saved) -->
                    <option v-if="formLocation && !sortedLocations.includes(formLocation)" :value="formLocation">{{ formLocation }} (未保存)</option>
                    <option v-for="l in sortedLocations" :key="l" :value="l">{{ l }}</option>
                  </select>
                </template>
                <template v-else>
                  <input
                    v-model="formNewLocation"
                    type="text"
                    class="form-input"
                    maxlength="100"
                    placeholder="输入新增所属地名"
                    autofocus
                  />
                  <div class="add-cancel-row">
                    <button type="button" class="btn btn-sm btn-primary" :disabled="!formNewLocation.trim()" @click="confirmNewLocation">确认</button>
                    <button type="button" class="btn btn-sm" @click="cancelNewLocation">取消</button>
                  </div>
                </template>
              </label>
              <label class="form-label">
                父系
                <input v-model="formSire" type="text" class="form-input" maxlength="100" placeholder="父马名称" />
              </label>
              <label class="form-label">
                母父
                <input v-model="formDamsire" type="text" class="form-input" maxlength="100" placeholder="母父名称" />
              </label>
            </div>

            <!-- 前走成绩 box (3 sub-fields) -->
            <div class="field-box">
              <div class="field-box-header">前走成绩</div>
              <div class="field-box-body field-box-col-3">
                <label class="form-label">
                  比赛名称
                  <input v-model="formPreviousResult" type="text" class="form-input" maxlength="100" placeholder="如 东京优骏 1着" />
                </label>
                <label class="form-label">
                  日期
                  <input v-model="formPreviousResultDate" type="date" class="form-input" :class="{ 'is-empty': !formPreviousResultDate }" />
                </label>
                <label class="form-label">
                  名次
                  <input v-model.number="formPreviousResultPosition" type="number" class="form-input" min="0" max="99" placeholder="如 1" />
                </label>
              </div>
            </div>

            <!-- 主要胜鞍 box (2 sub-fields) -->
            <div class="field-box">
              <div class="field-box-header">主要胜鞍</div>
              <div class="field-box-body field-box-col-2">
                <label class="form-label">
                  比赛名称
                  <input v-model="formBestWin" type="text" class="form-input" maxlength="100" placeholder="如 有马纪念(G1)" />
                </label>
                <label class="form-label">
                  日期
                  <input v-model="formBestWinDate" type="date" class="form-input" :class="{ 'is-empty': !formBestWinDate }" />
                </label>
              </div>
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
  padding: var(--spacing-4, 16px);
  max-width: 1280px;
  margin: 0 auto;
}
.page-header { margin-bottom: var(--spacing-4, 16px); }
.page-title {
  font-family: 'Barlow Condensed', system-ui, sans-serif;
  font-size: var(--text-heading, 24px);
  font-weight: 600;
  color: var(--color-primary, #1A5632);
  margin: 0;
}
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
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: var(--color-primary, #1A5632); color: #FFFFFF; }
.btn-primary:hover:not(:disabled) { background: var(--color-primary-light, #2D7A4F); }
.btn-sm {
  padding: 4px 12px;
  font-size: var(--text-caption, 12px);
  min-height: 44px;
  background: var(--color-surface-raised, #FFFFFF);
  border: 1px solid var(--color-border-hairline, #D4DCD0);
  color: var(--color-ink-primary, #1A2E1A);
}
.btn-sm:hover { background: var(--color-surface-base, #F8FAF7); }
.btn-danger { color: var(--color-destructive, #C53030); border-color: var(--color-destructive, #C53030); }
.btn-danger:hover { background: var(--color-destructive-light, #FED7D7); }
.btn-cancel { background: var(--color-surface-base, #F8FAF7); border: 1px solid var(--color-border-hairline, #D4DCD0); color: var(--color-ink-primary, #1A2E1A); }
.text-muted { font-size: var(--text-caption, 12px); color: var(--color-ink-secondary, #4A5A4A); }
.skeleton-container { display: flex; flex-direction: column; gap: var(--spacing-8); }
.skeleton-row {
  height: 40px;
  background: linear-gradient(90deg, var(--color-surface-base) 25%, var(--color-border-hairline) 50%, var(--color-surface-base) 75%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
  border-radius: var(--rounded-sm);
}
.state-container { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 30vh; text-align: center; gap: var(--spacing-4, 16px); padding: var(--spacing-8, 32px) var(--spacing-4, 16px); }
.empty-text { color: var(--color-ink-secondary); font-size: var(--text-body); max-width: 400px; line-height: 1.6; }
.error-text { color: var(--color-destructive); font-size: var(--text-body); }
.refresh-btn { padding: 10px 24px; font-size: var(--text-body); font-weight: 600; color: #ffffff; background: var(--color-primary); border: none; border-radius: var(--rounded-md); cursor: pointer; min-height: 44px; transition: background 0.2s; }
.refresh-btn:hover { background: var(--color-primary-light); }
.refresh-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.table-wrapper { overflow-x: auto; -webkit-overflow-scrolling: touch; }
table { width: 100%; border-collapse: collapse; font-size: var(--text-body-sm, 14px); }
th { text-align: left; padding: var(--spacing-3, 12px) var(--spacing-2, 8px); font-weight: 600; color: var(--color-ink-secondary, #4A5A4A); border-bottom: 2px solid var(--color-border-hairline, #D4DCD0); white-space: nowrap; }
td { padding: var(--spacing-3, 12px) var(--spacing-2, 8px); border-bottom: 1px solid var(--color-border-hairline, #D4DCD0); white-space: nowrap; }
.actions-cell { display: flex; gap: var(--spacing-2, 8px); }
.modal-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: var(--spacing-16); }
.modal-content { background: var(--color-surface-raised, #FFFFFF); border-radius: var(--rounded-lg, 14px); padding: var(--spacing-20, 24px); width: 100%; max-width: 640px; max-height: 90vh; overflow-y: auto; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12); }
.modal-title { font-family: 'Barlow Condensed', system-ui, sans-serif; font-size: 22px; font-weight: 600; color: var(--color-primary, #1A5632); margin-bottom: var(--spacing-16, 20px); }
.horse-form { display: flex; flex-direction: column; gap: var(--spacing-12, 16px); }
.form-row { width: 100%; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-12, 16px); }
@media (max-width: 768px) { .form-grid { grid-template-columns: 1fr; } }
.form-label { display: flex; flex-direction: column; gap: var(--spacing-1, 4px); font-size: var(--text-body-sm, 14px); font-weight: 500; color: var(--color-ink-primary, #1A2E1A); }
.required { color: var(--color-destructive, #C53030); }
.form-input { padding: 8px 12px; border: 1px solid var(--color-border-hairline, #D4DCD0); border-radius: var(--rounded-sm, 6px); font-size: var(--text-body, 16px); font-family: var(--font-body); color: var(--color-ink-primary, #1A2E1A); background: var(--color-surface-base, #F8FAF7); }
.form-input:focus { outline: 2px solid var(--color-primary, #1A5632); outline-offset: 2px; }
select.form-input { cursor: pointer; appearance: auto; }
.hemisphere-badge { display: inline-block; margin-top: 4px; padding: 2px 8px; font-size: var(--text-caption, 12px); border-radius: var(--rounded-sm, 6px); background: var(--color-surface-base, #F8FAF7); color: var(--color-ink-secondary); }
.hemisphere-select-row { display: flex; gap: 16px; margin-top: 8px; }
.radio-label { display: flex; align-items: center; gap: 4px; font-size: var(--text-body-sm, 14px); cursor: pointer; }
.add-cancel-row { display: flex; gap: 8px; margin-top: 8px; }
.btn-sm.btn-primary { background: var(--color-primary, #1A5632); color: #fff; border: none; }
.btn-hemisphere-toggle { margin-top: 4px; margin-left: 8px; padding: 2px 8px; font-size: var(--text-caption, 12px); border: 1px solid var(--color-border-strong); border-radius: var(--rounded-sm, 6px); background: transparent; cursor: pointer; min-height: 28px; color: var(--color-primary); }
.btn-hemisphere-toggle:hover:not(:disabled) { background: var(--color-surface-base); }
.btn-hemisphere-toggle:disabled { opacity: 0.5; cursor: not-allowed; }

/* Field boxes for grouped form sections */
.field-box {
  border: 1px solid var(--color-border-hairline, #D4DCD0);
  border-radius: var(--rounded-md, 10px);
  background: var(--color-surface-base, #F8FAF7);
  padding: var(--spacing-3, 12px);
}
.field-box-header {
  font-size: var(--text-body-sm, 14px);
  font-weight: 600;
  color: var(--color-ink-secondary, #4A5A4A);
  margin-bottom: var(--spacing-2, 8px);
  padding-bottom: var(--spacing-1, 4px);
  border-bottom: 1px solid var(--color-border-hairline, #D4DCD0);
}
.field-box-body {
  display: grid;
  gap: var(--spacing-3, 12px);
}
.field-box-col-3 {
  grid-template-columns: 1fr 1fr 1fr;
}
.field-box-col-2 {
  grid-template-columns: 1fr 1fr;
}
@media (max-width: 768px) {
  .field-box-col-3,
  .field-box-col-2 {
    grid-template-columns: 1fr;
  }
}

.form-actions { display: flex; gap: var(--spacing-3, 12px); justify-content: flex-end; margin-top: var(--spacing-8, 12px); }
.error-banner { padding: var(--spacing-3, 12px); margin-bottom: var(--spacing-3, 12px); background: var(--color-destructive-light, #FED7D7); color: var(--color-destructive, #C53030); border-radius: var(--rounded-sm, 6px); font-size: var(--text-body-sm, 14px); }

@media (prefers-reduced-motion: reduce) {
  .skeleton-row { animation: none; background: var(--color-surface-base); }
  .refresh-btn, .btn { transition: none; }
}
</style>
