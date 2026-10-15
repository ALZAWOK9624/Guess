<script setup lang="ts">
import { computed, ref, nextTick, onMounted } from 'vue'
import type { HorseSnapshotData } from '@/types/race'
import { gateBracketColor } from '@/utils/gateBracket'

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
  showDeleteButton?: boolean
  isJiggling?: boolean
  /** Runner count; when set, the gate badge uses JRA bracket (枠) colours. */
  fieldSize?: number | null
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
  showDeleteButton: false,
  isJiggling: false,
  fieldSize: null,
})

// The template has two roots (card + Teleport), so attrs such as the
// parent's `voted-horse-locked` class must be forwarded to the card by hand.
defineOptions({ inheritAttrs: false })

const emit = defineEmits<{
  voteToggle: []
  updateField: [{ field: 'jockey'; value: string | null }]
  dragStart: []
  dragEnd: []
  refresh: []
  deleteClick: []
}>()

const isMobile = ref(false)

onMounted(() => {
  isMobile.value = window.matchMedia('(max-width: 767px)').matches
})

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
function startEdit() {
  if (!props.editable) return
  editingField.value = true
  editValue.value = displayJockey.value || ''
  nextTick(() => {
    const input = document.querySelector<HTMLInputElement>('.inline-input')
    input?.focus()
  })
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

const gateStyle = computed(() => {
  if (props.gate == null || !props.fieldSize) return undefined
  const color = gateBracketColor(props.gate, props.fieldSize)
  return color ? { background: color.bg, color: color.fg } : undefined
})

const positionClass = computed(() => {
  if (props.position === 0) return 'badge-dnf'
  if (props.position === 1) return 'badge-p1'
  if (props.position === 2) return 'badge-p2'
  if (props.position === 3) return 'badge-p3'
  return ''
})

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

function handleContextMenu(e: MouseEvent) {
  if (window.matchMedia('(max-width: 767px)').matches) {
    e.preventDefault()
  }
}
</script>

<template>
  <div
    v-bind="$attrs"
    class="horse-detail-card"
    :class="{
      votable,
      voted,
      'submitting': submitting && voted,
      'draggable-card': draggable,
      'dnf-card': isDnf,
      'is-jiggling': isJiggling,
    }"
    :role="votable ? 'button' : undefined"
    :tabindex="votable ? 0 : undefined"
    :aria-pressed="votable ? voted : undefined"
    :draggable="draggable && !isMobile ? true : undefined"
    @click="handleClick"
    @keydown.enter="handleClick"
    @keydown.space.prevent="handleClick"
    @dragstart="handleDragStart"
    @dragend="handleDragEnd"
    @contextmenu="handleContextMenu"
  >
    <div v-if="position != null" class="side-badge left-badge" :class="positionClass">
      {{ position === 0 ? 'DNF' : position }}
    </div>

    <div class="card-body">
      <div v-if="editable" class="refresh-btn" @click.stop="openRefreshConfirm" :title="`刷新「${safeData.name}」数据`" aria-label="刷新马匹数据">
        <svg class="refresh-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <polyline points="23 4 23 10 17 10" /><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
        </svg>
      </div>

      <!-- Desktop table layout (≥768px) -->
      <table class="horse-table desktop-table">
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

      <!-- Mobile 4-row layout (<768px) -->
      <div class="mobile-card-layout">
        <div class="mobile-name-section">
          <div class="horse-name">{{ safeData.name }}</div>
          <div class="horse-suffix">{{ sexAgeStr }}</div>
          <div v-if="votable && voted" class="vote-badge" aria-hidden="true">
            <span class="vote-checkmark">✓</span>
            <span class="vote-label">已投</span>
          </div>
          <div v-if="submitting && voted" class="vote-spinner" aria-hidden="true" />
        </div>
        <div class="mobile-info-rows">
          <div class="mobile-row">
            <span class="m-lbl">骑手</span>
            <span class="m-val" :class="{ editable: editable }" @click.stop="startEdit()">
              <input
                v-if="editingField"
                v-model="editValue"
                class="inline-input"
                type="text"
                @blur="submitEdit"
                @keydown="handleEditKeydown"
              />
              <span v-else>{{ displayJockey || '-' }}</span>
            </span>
            <span class="m-lbl">属地</span>
            <span class="m-val">{{ safeData.location || '-' }}</span>
          </div>
          <div class="mobile-row">
            <span class="m-lbl">父</span>
            <span class="m-val">{{ safeData.sire || '-' }}</span>
            <span class="m-lbl">母父</span>
            <span class="m-val">{{ safeData.damsire || '-' }}</span>
          </div>
          <div class="mobile-row">
            <span class="m-lbl">前走</span>
            <span class="m-val-wide">{{ formatPrevResult(safeData) }}</span>
          </div>
          <div class="mobile-row">
            <span class="m-lbl">主胜</span>
            <span class="m-val-wide">{{ formatBestWin(safeData) }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="gate != null" class="side-badge right-badge" :class="{ 'is-bracket': gateStyle }" :style="gateStyle">
      {{ gate }}
    </div>

    <button
      v-if="showDeleteButton && !isDnf"
      class="delete-card-btn"
      aria-label="删除此马匹"
      @click.stop="emit('deleteClick')"
    >✕</button>
  </div>

  <!-- Refresh Confirm Modal -->
  <Teleport to="body">
    <div
      v-if="showRefreshConfirm"
      class="refresh-confirm-overlay ui-anim-overlay"
      @mousedown.self="closeRefreshConfirm"
      @keydown="handleConfirmKeydown"
    >
      <div class="refresh-confirm-content ui-anim-dialog" role="dialog" aria-label="确认刷新">
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
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-hairline);
  border-radius: var(--rounded-lg);
  padding: 4px;
  box-shadow: var(--shadow-sm);
  transition:
    border-color var(--duration-fast) ease,
    box-shadow var(--duration-base) var(--ease-out),
    background-color var(--duration-base) ease,
    transform var(--duration-base) var(--ease-out);
  overflow: hidden;
}

.horse-detail-card.votable {
  cursor: pointer;
  user-select: none;
}

.horse-detail-card.votable:hover {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 1px var(--color-primary), var(--shadow-lg);
  transform: translateY(-2px);
}

.horse-detail-card.votable:active {
  transform: translateY(0) scale(0.99);
}

.horse-detail-card.votable:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.horse-detail-card.voted {
  border-color: var(--color-accent);
  background: linear-gradient(100deg, var(--color-accent-tint) 0%, #FFFFFF 70%);
  box-shadow: var(--shadow-glow-gold);
}

/* One-off shine sweep when a card becomes the user's pick */
.horse-detail-card.voted::after {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(105deg, transparent 35%, rgba(255, 255, 255, 0.85) 50%, transparent 65%);
  transform: translateX(-110%);
  animation: vote-shine 0.9s var(--ease-out) 0.1s 1 forwards;
}

@keyframes vote-shine {
  to { transform: translateX(110%); }
}

.horse-detail-card.voted-horse-locked {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-gold);
}

.horse-detail-card.votable.voted:hover {
  border-color: var(--color-destructive);
  box-shadow: 0 0 0 1px var(--color-destructive), 0 10px 24px -12px rgba(197, 48, 48, 0.4);
}

.horse-detail-card.submitting {
  opacity: 0.7;
  pointer-events: none;
}

.horse-detail-card.draggable-card {
  cursor: grab;
}

.horse-detail-card.draggable-card:hover {
  border-color: var(--color-border-strong);
  box-shadow: var(--shadow-md);
}

.horse-detail-card.draggable-card:active {
  cursor: grabbing;
}

.horse-detail-card.dnf-card {
  opacity: 0.55;
  background: var(--color-surface-sunken);
  box-shadow: none;
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
  color: var(--color-ink-secondary);
  cursor: pointer;
  user-select: none;
  min-width: 36px;
  transition: color var(--duration-fast) ease, background var(--duration-fast) ease;
  border-radius: var(--rounded-sm);
  margin: 2px;
}

.refresh-btn:hover {
  color: var(--color-primary);
  background: var(--color-primary-tint);
}

.refresh-icon {
  display: block;
  width: 16px;
  height: 16px;
}

.refresh-btn:hover .refresh-icon {
  animation: refresh-hover-spin 0.6s var(--ease-out);
}

@keyframes refresh-hover-spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.side-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 38px;
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 700;
  color: #FFFFFF;
  background: var(--color-primary);
  margin: -4px;
}

.left-badge {
  border-radius: var(--rounded-lg) 0 0 var(--rounded-lg);
  margin-right: 4px;
}

.right-badge {
  border-radius: 0 var(--rounded-lg) var(--rounded-lg) 0;
  margin-left: 4px;
  background: var(--gradient-gold);
}

/* JRA bracket colour: white bracket 1 needs an edge to stay visible */
.right-badge.is-bracket {
  box-shadow: inset 1px 0 0 rgba(0, 0, 0, 0.08);
}

.badge-p1 {
  background: var(--gradient-gold);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.badge-p2 {
  background: var(--gradient-silver);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.badge-p3 {
  background: var(--gradient-bronze);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.badge-dnf {
  background: var(--color-destructive);
  font-size: var(--text-caption);
  letter-spacing: 0.5px;
}

/* ===== HTML Table Layout ===== */
.horse-table {
  width: 100%;
  border-collapse: collapse;
  border-style: hidden;
  table-layout: fixed;
}

.desktop-table {
  display: table;
}

.mobile-card-layout {
  display: none;
}

.horse-table th,
.horse-table td {
  border: 1px solid #E6ECE3;
  padding: 8px 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Name cell spans 2 rows */
.horse-table .name-cell {
  position: relative;
  text-align: left;
  vertical-align: middle;
  min-width: 80px;
  padding-left: 10px;
}

.horse-name {
  font-family: var(--font-display);
  font-size: 21px;
  font-weight: 700;
  line-height: 1.15;
  color: var(--color-ink-primary);
  overflow: hidden;
  text-overflow: ellipsis;
}

.horse-suffix {
  display: inline-block;
  margin-top: 3px;
  padding: 0 7px;
  border-radius: var(--rounded-full);
  font-size: 12px;
  font-weight: 600;
  color: var(--color-ink-secondary);
  background: var(--color-surface-sunken);
}

/* Label cells */
.cl-lbl {
  font-size: 11px;
  line-height: 1.2;
  color: var(--color-ink-secondary);
  font-weight: 600;
  text-align: center;
  background: var(--color-surface-base);
}

/* Value cells */
.cl-val {
  font-size: 13px;
  line-height: 1.2;
  color: var(--color-ink-primary);
  text-align: center;
}

.cl-val.editable {
  cursor: text;
  background: #FAFDFB;
  transition: background var(--duration-fast) ease;
}

.cl-val.editable:hover {
  background: var(--color-primary-tint);
}

.cl-val-wide {
  font-size: 13px;
  line-height: 1.2;
  color: var(--color-ink-primary);
  text-align: center;
}

.inline-input {
  width: 100%;
  padding: 2px 4px;
  border: 1px solid var(--color-primary);
  border-radius: 4px;
  font-size: var(--text-body-sm);
  text-align: center;
  background: #FFFFFF;
}

.inline-input:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(26, 86, 50, 0.18);
}

/* Vote badge & spinner */
.vote-badge {
  position: absolute;
  top: 3px;
  right: 3px;
  display: flex;
  align-items: center;
  gap: 4px;
  background: var(--gradient-gold);
  color: #ffffff;
  border-radius: 20px;
  padding: 1px 8px;
  font-size: var(--text-caption);
  font-weight: 700;
  white-space: nowrap;
  box-shadow: 0 3px 8px -3px rgba(143, 116, 6, 0.8);
  animation: pop-in var(--duration-slow) var(--ease-spring);
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
  top: 3px;
  right: 3px;
  width: 12px;
  height: 12px;
  border: 2px solid rgba(185, 150, 12, 0.3);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: horse-spin 0.6s linear infinite;
}

@keyframes horse-spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 767px) {
  .horse-detail-card {
    padding: 2px;
    width: 100%;
    touch-action: manipulation;
    -webkit-touch-callout: none;
    -webkit-user-drag: none;
    user-select: none;
  }

  .horse-detail-card.votable:hover {
    transform: none;
  }

  .horse-name {
    font-size: var(--text-subheading);
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
    font-size: var(--text-body);
    margin: -2px;
  }

  .left-badge {
    margin-right: 2px;
  }

  .right-badge {
    margin-left: 2px;
  }

  .badge-dnf {
    font-size: 10px;
    letter-spacing: 0.3px;
    min-width: 26px;
  }

  .refresh-btn {
    padding: 0 2px;
    min-width: 28px;
  }

  /* Hide desktop table on mobile */
  .desktop-table {
    display: none;
  }

  /* Show mobile layout on mobile */
  .mobile-card-layout {
    display: flex;
    flex: 1;
    min-width: 0;
    gap: 4px;
    padding: 2px;
  }

  .mobile-name-section {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-width: 84px;
    max-width: 40%;
    padding: 6px;
    position: relative;
    text-align: center;
    border-radius: var(--rounded-md);
    background: var(--color-surface-base);
  }

  .mobile-name-section .horse-name {
    max-width: 100%;
    white-space: normal;
    word-break: break-word;
  }

  .horse-detail-card.voted .mobile-name-section {
    background: rgba(255, 255, 255, 0.7);
  }

  .mobile-name-section .vote-badge {
    position: static;
    margin-top: 4px;
  }

  .mobile-info-rows {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-width: 0;
    gap: 0;
    border: 1px solid #E6ECE3;
    border-radius: var(--rounded-md);
    overflow: hidden;
    background: var(--color-surface-raised);
  }

  .mobile-row {
    display: flex;
    align-items: center;
    min-height: 28px;
  }

  .mobile-row + .mobile-row {
    border-top: 1px solid #E6ECE3;
  }

  .m-lbl {
    align-self: stretch;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: 600;
    color: var(--color-ink-secondary);
    background: var(--color-surface-base);
    text-align: center;
    padding: 4px 4px;
    min-width: 30px;
    flex-shrink: 0;
    line-height: 1.2;
  }

  .m-val {
    font-size: 11px;
    color: var(--color-ink-primary);
    text-align: center;
    padding: 4px 4px;
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    line-height: 1.2;
  }

  .m-val.editable {
    cursor: text;
    background: #FAFDFB;
  }

  .m-val-wide {
    font-size: 11px;
    color: var(--color-ink-primary);
    text-align: center;
    padding: 4px 4px;
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    line-height: 1.2;
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
  background: rgba(13, 30, 18, 0.5);
  padding: var(--spacing-4);
}

.refresh-confirm-content {
  background: var(--color-surface-raised);
  border-radius: var(--rounded-xl);
  padding: var(--spacing-6);
  max-width: 380px;
  width: 100%;
}

.refresh-confirm-title {
  font-family: var(--font-display);
  font-size: var(--text-heading);
  font-weight: 700;
  color: var(--color-ink-primary);
  margin: 0 0 var(--spacing-3);
}

.refresh-confirm-message {
  font-size: var(--text-body);
  color: var(--color-ink-primary);
  line-height: 1.6;
  margin: 0 0 var(--spacing-5);
}

.refresh-confirm-actions {
  display: flex;
  gap: var(--spacing-3);
  justify-content: flex-end;
}

.refresh-confirm-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 24px;
  border: none;
  border-radius: var(--rounded-md);
  font-size: var(--text-body);
  font-weight: 600;
  cursor: pointer;
  min-height: 44px;
  transition: transform var(--duration-fast) var(--ease-out), filter var(--duration-fast) ease, background var(--duration-fast) ease;
}

.refresh-confirm-btn:active:not(:disabled) {
  transform: scale(0.97);
}

.refresh-confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-confirm-btn.cancel {
  background: var(--color-surface-raised);
  color: var(--color-ink-primary);
  border: 1px solid var(--color-border-strong);
}

.refresh-confirm-btn.cancel:hover:not(:disabled) {
  background: var(--color-surface-base);
}

.refresh-confirm-btn.confirm {
  background: var(--gradient-brand-soft);
  color: #FFFFFF;
}

.refresh-confirm-btn.confirm:hover:not(:disabled) {
  filter: brightness(1.08);
}

@media (prefers-reduced-motion: reduce) {
  .horse-detail-card,
  .vote-spinner {
    transition: none;
    animation: none;
  }

  .horse-detail-card.voted::after {
    display: none;
  }
}

/* Jiggle animation for edit mode (mobile only) */
@keyframes jiggle {
  0% { transform: rotate(0deg) translate(0, 0); }
  25% { transform: rotate(-0.8deg) translate(-1px, 0); }
  75% { transform: rotate(0.8deg) translate(1px, 1px); }
  100% { transform: rotate(0deg) translate(0, 0); }
}

.horse-detail-card.is-jiggling {
  touch-action: none;
  overflow: visible;
}

@media (max-width: 767px) {
  .horse-detail-card.is-jiggling {
    animation: jiggle 0.3s ease-in-out infinite alternate;
  }
}

/* Delete X button (mobile jiggle mode, positioned at card top-right) */
.delete-card-btn {
  position: absolute;
  top: -12px;
  right: -12px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid #FFFFFF;
  background: var(--color-destructive);
  color: #FFFFFF;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 2;
  padding: 0;
  line-height: 1;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
  animation: pop-in var(--duration-base) var(--ease-spring);
  transition: transform 0.12s, background 0.12s;
}

.delete-card-btn:hover {
  transform: scale(1.15);
  background: var(--color-destructive-dark);
}

.delete-card-btn:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

@media (prefers-reduced-motion: reduce) {
  .horse-detail-card.is-jiggling {
    animation: none;
  }
}
</style>
