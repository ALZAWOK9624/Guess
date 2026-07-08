<script setup lang="ts">
import { computed, ref, nextTick } from 'vue'
import type { HorseSnapshotData } from '@/types/race'

function formatPrevResult(snap: HorseSnapshotData): string {
  if (!snap.previous_result) return '-'
  const parts: string[] = []
  if (snap.previous_result_date) parts.push(snap.previous_result_date)
  parts.push(snap.previous_result)
  return parts.join(' ')
}

function formatBestWin(snap: HorseSnapshotData): string {
  if (!snap.best_win) return '-'
  if (snap.best_win_date) return `${snap.best_win_date} ${snap.best_win}`
  return snap.best_win
}

function computeAge(birthYear: number, hemisphere: string, onDate: Date): number {
  const cutoffMonth = hemisphere === 'south' ? 8 : 1
  const thisYear = onDate.getFullYear()
  const cutoff = new Date(thisYear, cutoffMonth - 1, 1)
  const effectiveYear = onDate >= cutoff ? thisYear : thisYear - 1
  return effectiveYear - birthYear
}

const props = withDefaults(defineProps<{
  snapshotData?: HorseSnapshotData | null
  horseId: number
  jockey?: string | null
  birthYear?: number | null
  hemisphere?: string | null
  referenceDate?: string | null
  votable?: boolean
  voted?: boolean
  submitting?: boolean
  gate?: number | null
  position?: number | null
  editable?: boolean
  draggable?: boolean
  isDnf?: boolean
}>(), {
  snapshotData: () => ({
    name: '',
    sex: null,
    birth_year: null,
    hemisphere: null,
    location: null,
    origin: null,
    sire: null,
    damsire: null,
    previous_result: null,
    previous_result_date: null,
    previous_result_position: null,
    best_win: null,
    best_win_date: null,
  }),
  jockey: null,
  birthYear: null,
  hemisphere: null,
  referenceDate: null,
  votable: false,
  voted: false,
  submitting: false,
  gate: null,
  position: null,
  editable: false,
  draggable: false,
  isDnf: false,
})

const emit = defineEmits<{
  voteToggle: []
  updateField: [{ field: 'jockey'; value: string | null }]
  dragStart: []
  dragEnd: []
  refresh: []
}>()

const showRefreshConfirm = ref(false)
const refreshLoading = ref(false)

function openRefreshConfirm() {
  showRefreshConfirm.value = true
}

function closeRefreshConfirm() {
  if (refreshLoading.value) return
  showRefreshConfirm.value = false
}

function confirmRefresh() {
  emit('refresh')
  showRefreshConfirm.value = false
}

const safeData = computed(() => props.snapshotData ?? {
  name: '',
  sex: null,
  birth_year: null,
  hemisphere: null,
  location: null,
  origin: null,
  sire: null,
  damsire: null,
  previous_result: null,
  previous_result_date: null,
  previous_result_position: null,
  best_win: null,
  best_win_date: null,
})

const rawBirthYear = computed(() => props.birthYear ?? props.snapshotData?.birth_year ?? null)
const rawHemisphere = computed(() => props.hemisphere ?? props.snapshotData?.hemisphere ?? null)

const displayAge = computed(() => {
  if (rawBirthYear.value === null || rawBirthYear.value === undefined) return null
  const refDate = props.referenceDate ? new Date(props.referenceDate) : new Date()
  const hs = rawHemisphere.value || 'north'
  return computeAge(rawBirthYear.value, hs, refDate)
})

const displayJockey = computed(() => props.jockey ?? null)

const editingField = ref(false)
const editValue = ref('')
const jockeyInput = ref<HTMLInputElement | null>(null)

function startEdit() {
  if (!props.editable) return
  editingField.value = true
  editValue.value = displayJockey.value || ''
  nextTick(() => jockeyInput.value?.focus())
}

function submitEdit() {
  if (!editingField.value) return
  const trimmed = editValue.value.trim()
  const value = trimmed === '' ? null : trimmed
  if (value !== displayJockey.value) {
    emit('updateField', { field: 'jockey', value })
  }
  editingField.value = false
}

function cancelEdit() {
  editingField.value = false
}

function handleEditKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter') {
    e.preventDefault()
    submitEdit()
  } else if (e.key === 'Escape') {
    cancelEdit()
  }
}

function handleDragStart(e: DragEvent) {
  if (!props.draggable) {
    e.preventDefault()
    return
  }
  emit('dragStart')
}

function handleDragEnd() {
  emit('dragEnd')
}

function handleClick() {
  if (props.editable && editingField.value) return
  if (props.submitting || !props.votable) return
  emit('voteToggle')
}

const sexAgeStr = computed(() => {
  const sex = safeData.value.sex || '-'
  const age = displayAge.value !== null ? `${displayAge.value}` : '-'
  return `${sex}${age}`
})

function handleConfirmKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && !refreshLoading.value) {
    closeRefreshConfirm()
  }
}
</script>

<template>
  <div
    class="horse-detail-card"
    :class="{
      votable,
      voted,
      'submitting': submitting && voted,
      'draggable-card': draggable,
      'dnf-card': isDnf,
    }"
    :role="votable ? 'button' : undefined"
    :tabindex="votable ? 0 : undefined"
    :aria-pressed="votable ? voted : undefined"
    :draggable="draggable"
    @click="handleClick"
    @keydown.enter="handleClick"
    @keydown.space.prevent="handleClick"
    @dragstart="handleDragStart"
    @dragend="handleDragEnd"
  >
    <div v-if="position != null" class="side-badge left-badge" :class="{ 'badge-dnf': position === 0 }">
      {{ position === 0 ? 'DNF' : position }}
    </div>

    <div class="card-body">
      <div v-if="editable" class="refresh-btn" @click.stop="openRefreshConfirm" :title="`刷新「${safeData.name}」数据`" aria-label="刷新马匹数据">
        <span class="refresh-icon">↻</span>
      </div>

      <table class="horse-table">
        <colgroup>
          <col style="width:18%" />
          <col style="width:6%" />
          <col style="width:16.5%" />
          <col style="width:6%" />
          <col style="width:8.5%" />
          <col style="width:6%" />
          <col style="width:6%" />
          <col style="width:10.5%" />
          <col style="width:6%" />
          <col style="width:16.5%" />
        </colgroup>
        <tbody>
          <tr>
            <td class="name-cell" rowspan="2">
              <div class="horse-name">{{ safeData.name }}</div>
              <div class="horse-suffix">{{ sexAgeStr }}</div>
              <div v-if="votable && voted" class="vote-badge" aria-hidden="true">
                <span class="vote-checkmark">✓</span>
                <span class="vote-label">已投</span>
              </div>
              <div v-if="submitting && voted" class="vote-spinner" aria-hidden="true" />
            </td>
            <th class="cl-lbl">骑手</th>
            <td class="cl-val" :class="{ editable: editable }" @dblclick.stop="startEdit()">
              <input
                v-if="editingField"
                ref="jockeyInput"
                v-model="editValue"
                class="inline-input"
                type="text"
                @blur="submitEdit"
                @keydown="handleEditKeydown"
              />
              <span v-else>{{ displayJockey || '-' }}</span>
            </td>
            <th class="cl-lbl">属地</th>
            <td class="cl-val">{{ safeData.location || '-' }}</td>
            <th class="cl-lbl">父</th>
            <td class="cl-val" colspan="2">{{ safeData.sire || '-' }}</td>
            <th class="cl-lbl">母父</th>
            <td class="cl-val">{{ safeData.damsire || '-' }}</td>
          </tr>
          <tr>
            <th class="cl-lbl">前走</th>
            <td class="cl-val-wide" colspan="4">{{ formatPrevResult(safeData) }}</td>
            <th class="cl-lbl">主胜</th>
            <td class="cl-val-wide" colspan="3">{{ formatBestWin(safeData) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="gate != null" class="side-badge right-badge">
      {{ gate }}
    </div>
  </div>

  <!-- Refresh Confirm Modal -->
  <Teleport to="body">
    <div
      v-if="showRefreshConfirm"
      class="refresh-confirm-overlay"
      @mousedown.self="closeRefreshConfirm"
      @keydown="handleConfirmKeydown"
    >
      <div class="refresh-confirm-content" role="dialog" aria-label="确认刷新">
        <h3 class="refresh-confirm-title">确认更新</h3>
        <p class="refresh-confirm-message">确定刷新「{{ safeData.name }}」的数据为后台最新信息？</p>
        <div class="refresh-confirm-actions">
          <button class="refresh-confirm-btn cancel" :disabled="refreshLoading" @click="closeRefreshConfirm">
            取消
          </button>
          <button class="refresh-confirm-btn confirm" :disabled="refreshLoading" @click="confirmRefresh">
            更新
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.horse-detail-card {
  position: relative;
  display: flex;
  align-items: stretch;
  background: var(--color-surface-raised, #FFFFFF);
  border: 2px solid var(--color-border-hairline, #D4DCD0);
  border-radius: var(--rounded-md, 10px);
  padding: 4px;
  transition: border-color 0.15s, box-shadow 0.15s, background-color 0.15s;
  overflow: hidden;
}

.horse-detail-card.votable {
  cursor: pointer;
  user-select: none;
}

.horse-detail-card.votable:hover {
  border-color: var(--color-primary, #1A5632);
  box-shadow: 0 2px 8px rgba(26, 86, 50, 0.12);
}

.horse-detail-card.votable:focus-visible {
  outline: 2px solid var(--color-primary, #1A5632);
  outline-offset: 2px;
}

.horse-detail-card.voted {
  border-color: var(--color-accent, #B8960C);
  background: #FFFDF0;
}

.horse-detail-card.votable.voted:hover {
  border-color: var(--color-destructive, #C53030);
  box-shadow: 0 2px 8px rgba(197, 48, 48, 0.12);
}

.horse-detail-card.submitting {
  opacity: 0.7;
  pointer-events: none;
}

.horse-detail-card.draggable-card {
  cursor: grab;
}

.horse-detail-card.draggable-card:active {
  cursor: grabbing;
}

.horse-detail-card.dnf-card {
  opacity: 0.5;
  background: #F9FAFB;
}

.card-body {
  flex: 1;
  display: flex;
  align-items: stretch;
  min-width: 0;
}

.refresh-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 8px;
  color: var(--color-ink-secondary, #4A5A4A);
  font-size: 16px;
  cursor: pointer;
  user-select: none;
  min-width: 36px;
  transition: color 0.15s, background 0.15s;
  border-radius: var(--rounded-sm, 6px);
  margin: 2px;
}

.refresh-btn:hover {
  color: var(--color-primary, #1A5632);
  background: var(--color-surface-base, #F8FAF7);
}

.refresh-icon {
  display: inline-block;
  font-size: 18px;
  line-height: 1;
}

.refresh-btn:hover .refresh-icon {
  animation: refresh-hover-spin 0.6s ease-in-out;
}

@keyframes refresh-hover-spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.side-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  font-family: var(--font-display, 'Barlow Condensed', system-ui, sans-serif);
  font-size: 20px;
  font-weight: 700;
  color: #FFFFFF;
  background: var(--color-primary, #1A5632);
  margin: -4px;
}

.left-badge {
  border-radius: var(--rounded-md, 10px) 0 0 var(--rounded-md, 10px);
  margin-right: 4px;
}

.right-badge {
  border-radius: 0 var(--rounded-md, 10px) var(--rounded-md, 10px) 0;
  margin-left: 4px;
  background: var(--color-accent, #B8960C);
}

.badge-dnf {
  background: var(--color-destructive, #C53030);
  font-size: var(--text-caption, 11px);
  letter-spacing: 0.5px;
}

/* ===== HTML Table Layout ===== */
.horse-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.horse-table th,
.horse-table td {
  border: 1px solid var(--color-border-hairline, #D4DCD0);
  padding: 8px 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Name cell spans 2 rows */
.name-cell {
  position: relative;
  text-align: left;
  vertical-align: middle;
  min-width: 80px;
}

.horse-name {
  font-family: var(--font-display, 'Barlow Condensed', system-ui, sans-serif);
  font-size: 20px;
  font-weight: 600;
  color: var(--color-ink-primary, #1A2E1A);
}

.horse-suffix {
  font-size: 13px;
  color: var(--color-ink-secondary, #4A5A4A);
}

/* Label cells */
.cl-lbl {
  font-size: 11px;
  line-height: 1.2;
  color: var(--color-ink-secondary, #4A5A4A);
  font-weight: 600;
  text-align: center;
  background: var(--color-surface-base, #F8FAF7);
}

/* Value cells */
.cl-val {
  font-size: 13px;
  line-height: 1.2;
  color: var(--color-ink-primary, #1A2E1A);
  text-align: center;
}

.cl-val.editable {
  cursor: text;
  background: #FAFDFB;
}

.cl-val.editable:hover {
  background: #F0F7F2;
}

.cl-val-wide {
  font-size: 13px;
  line-height: 1.2;
  color: var(--color-ink-primary, #1A2E1A);
  text-align: center;
}

.inline-input {
  width: 100%;
  padding: 2px 4px;
  border: 1px solid var(--color-primary, #1A5632);
  border-radius: 4px;
  font-size: var(--text-body-sm, 14px);
  text-align: center;
  background: #FFFFFF;
}

.inline-input:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(26, 86, 50, 0.2);
}

/* Vote badge & spinner */
.vote-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  display: flex;
  align-items: center;
  gap: 4px;
  background: var(--color-accent, #B8960C);
  color: #ffffff;
  border-radius: 20px;
  padding: 1px 8px;
  font-size: var(--text-caption, 11px);
  font-weight: 600;
  white-space: nowrap;
}

.vote-checkmark {
  font-size: 12px;
  line-height: 1;
}

.vote-label {
  line-height: 1;
}

.vote-spinner {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  border: 2px solid rgba(185, 150, 12, 0.3);
  border-top-color: var(--color-accent, #B8960C);
  border-radius: 50%;
  animation: horse-spin 0.6s linear infinite;
}

@keyframes horse-spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 767px) {
  .horse-detail-card {
    padding: 2px;
  }

  .horse-name {
    font-size: var(--text-subheading, 18px);
  }

  .cl-lbl {
    font-size: 11px;
  }

  .cl-val,
  .cl-val-wide {
    font-size: 11px;
  }

  .side-badge {
    min-width: 28px;
    font-size: var(--text-body, 16px);
  }

  .refresh-btn {
    padding: 0 2px;
    font-size: 14px;
    min-width: 28px;
  }
}

/* Refresh confirm modal */
.refresh-confirm-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(26, 46, 26, 0.5);
  padding: var(--spacing-4, 16px);
}

.refresh-confirm-content {
  background: var(--color-surface-raised, #FFFFFF);
  border-radius: var(--rounded-lg, 14px);
  padding: var(--spacing-6, 24px);
  max-width: 380px;
  width: 100%;
  box-shadow: 0 4px 12px rgba(26, 86, 50, 0.15);
}

.refresh-confirm-title {
  font-family: var(--font-display, 'Barlow Condensed', system-ui, sans-serif);
  font-size: var(--text-heading, 24px);
  font-weight: 600;
  color: var(--color-ink-primary, #1A2E1A);
  margin: 0 0 var(--spacing-3, 12px);
}

.refresh-confirm-message {
  font-size: var(--text-body, 16px);
  color: var(--color-ink-primary, #1A2E1A);
  line-height: var(--text-body-line-height, 1.6);
  margin: 0 0 var(--spacing-5, 20px);
}

.refresh-confirm-actions {
  display: flex;
  gap: var(--spacing-3, 12px);
  justify-content: flex-end;
}

.refresh-confirm-btn {
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

.refresh-confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-confirm-btn.cancel {
  background: var(--color-surface-raised, #FFFFFF);
  color: var(--color-ink-primary, #1A2E1A);
  border: 1px solid var(--color-border-strong, #A8B8A4);
}

.refresh-confirm-btn.confirm {
  background: var(--color-primary, #1A5632);
  color: #FFFFFF;
}

.refresh-confirm-btn.confirm:hover:not(:disabled) {
  background: var(--color-primary-light, #2D7A4F);
}

@media (prefers-reduced-motion: reduce) {
  .horse-detail-card,
  .vote-spinner {
    transition: none;
    animation: none;
  }
}
</style>
