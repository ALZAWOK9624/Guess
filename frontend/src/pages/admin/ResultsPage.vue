<script setup lang="ts">
/**
 * Result entry page — drag-sort horse cards to record finishing positions.
 * Supports locked → settled transition and re-settlement of already settled races.
 * Desktop: native HTML5 DnD. Mobile: touch events with 300ms long-press.
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DragCard from '@/components/DragCard.vue'
import { getRace } from '@/api/races'
import { submitResults } from '@/api/results'
import { useDragSort } from '@/composables/useDragSort'
import { useDragAutoScroll } from '@/composables/useDragAutoScroll'
import type { RaceDetail, ResultPosition } from '@/types/race'

type PageState = 'loading' | 'empty' | 'error' | 'success'

const route = useRoute()
const router = useRouter()
const raceId = Number(route.params.id)

const pageState = ref<PageState>('loading')
const race = ref<RaceDetail | null>(null)
const errorMessage = ref('')
const errorCode = ref('')

const isSubmitting = ref(false)
const submitError = ref('')

// Touch drag state
const touchDragIndex = ref(-1)
const touchStartY = ref(0)
const touchCurrentY = ref(0)
let longPressTimer: ReturnType<typeof setTimeout> | null = null

// Track which list the drag originated from
const dragSource = ref<'active' | 'dnf'>('active')

// Auto-scroll during drag
const dragClientY = ref(0)
const autoScrollEnabled = computed(() => isDragging.value || touchDragIndex.value >= 0)
const { autoScrollDirection } = useDragAutoScroll({ enabled: autoScrollEnabled, clientY: dragClientY })

let isMounted = true

// Initialize drag-sort composable
const existingPositions = ref<Map<number, number> | undefined>(undefined)
let dragSort: ReturnType<typeof useDragSort> | null = null

onMounted(async () => {
  await loadRace()
})
onUnmounted(() => {
  isMounted = false
  if (longPressTimer) clearTimeout(longPressTimer)
})

async function loadRace() {
  pageState.value = 'loading'
  try {
    const data = await getRace(raceId)
    if (!isMounted) return
    race.value = data

    if (data.horses.length === 0) {
      pageState.value = 'empty'
      return
    }

    // Build existing positions map for re-entry
    const hasPositions = data.horses.some(h => h.position !== null && h.position !== undefined)
    if (hasPositions) {
      existingPositions.value = new Map(
        data.horses.map(h => [h.race_horse_id, h.position ?? 0]),
      )
    }

    // Initialize drag sort with all horses
    const horses = [...data.horses]
    dragSort = useDragSort(horses, existingPositions.value)
    pageState.value = 'success'
  } catch (err: any) {
    if (!isMounted) return
    pageState.value = 'error'
    const detail = err?.response?.data?.detail
    errorCode.value = detail?.code || ''
    if (err?.response?.status === 404) {
      errorMessage.value = '比赛不存在'
    } else if (errorCode.value === 'RACE_NOT_LOCKED') {
      errorMessage.value = detail?.message || '比赛处于投票中状态，请先锁定'
    } else {
      errorMessage.value = '加载失败，请刷新重试'
    }
  }
}

// Get active list / dnf list from composable
const activeList = computed(() => dragSort?.activeList.value ?? [])
const dnfList = computed(() => dragSort?.dnfList.value ?? [])
const isDragging = computed(() => dragSort?.isDragging.value ?? false)
const draggedIndex = computed(() => dragSort?.draggedIndex.value ?? -1)

// Drag-over state for insertion highlight
const dragOverIndex = ref(-1)

// Desktop drag handlers using composable
function handleDragStart(index: number, source: 'active' | 'dnf' = 'active') {
  dragSort?.startDrag(index)
  dragSource.value = source
  dragOverIndex.value = -1
}

function handleDrop(event: DragEvent) {
  event.preventDefault()
  if (!dragSort || dragSort.draggedIndex.value < 0) return

  if (dragSource.value === 'dnf') {
    // Dragged from DNF → move back to active (append to end)
    dragSort.moveToActive(dragSort.draggedIndex.value)
  } else {
    // Dragged within active list → reorder
    const dropZone = event.currentTarget as HTMLElement
    const cards = dropZone.querySelectorAll('.drag-item-wrapper')
    let targetIndex = cards.length - 1
    const mouseY = event.clientY
    for (let i = 0; i < cards.length; i++) {
      const rect = cards[i].getBoundingClientRect()
      const midY = rect.top + rect.height / 2
      if (mouseY < midY) {
        targetIndex = i
        break
      }
    }
    dragSort.commitReorder(dragSort.draggedIndex.value, targetIndex)
  }
  dragOverIndex.value = -1
}

function handleDragEnd() {
  dragSort?.endDrag()
  dragOverIndex.value = -1
  dragClientY.value = 0
}

// DNF zone drop
function handleDnfDrop(event: DragEvent) {
  event.preventDefault()
  if (dragSort && dragSort.draggedIndex.value >= 0 && dragSource.value === 'active') {
    dragSort.moveToDnf(dragSort.draggedIndex.value)
  }
  dragSort?.endDrag()
  dragOverIndex.value = -1
}

// Move horse back from DNF to active (click on DNF item)
function handleDnfClick(index: number) {
  dragSort?.moveToActive(index)
}

// ===== Mobile Touch Support (AC-3) =====
function handleTouchStart(event: TouchEvent, index: number) {
  if (longPressTimer) clearTimeout(longPressTimer)

  longPressTimer = setTimeout(() => {
    if (!isMounted) return
    // Activate drag
    touchDragIndex.value = index
    touchStartY.value = event.touches[0].clientY
    touchCurrentY.value = event.touches[0].clientY
    dragSort?.startDrag(index)
  }, 300)
}

function handleTouchMove(event: TouchEvent) {
  if (touchDragIndex.value < 0) {
    // Cancel long-press if finger moved before activation
    if (longPressTimer) {
      clearTimeout(longPressTimer)
      longPressTimer = null
    }
    return
  }

  event.preventDefault()
  touchCurrentY.value = event.touches[0].clientY
  dragClientY.value = event.touches[0].clientY

  // Calculate which position the finger is over based on card positions
  const cards = document.querySelectorAll('.drag-item-wrapper')
  const touchY = event.touches[0].clientY
  for (let i = 0; i < cards.length; i++) {
    const rect = cards[i].getBoundingClientRect()
    if (touchY >= rect.top && touchY <= rect.bottom) {
      if (i !== touchDragIndex.value && dragSort) {
        const item = dragSort.activeList.value.splice(touchDragIndex.value, 1)[0]
        if (item) {
          dragSort.activeList.value.splice(i, 0, item)
          touchDragIndex.value = i
          dragOverIndex.value = i
        }
      }
      break
    }
  }
}

function handleTouchEnd(event: TouchEvent) {
  if (longPressTimer) {
    clearTimeout(longPressTimer)
    longPressTimer = null
  }

  if (touchDragIndex.value < 0) return

  // Check if dropped on DNF zone
  const touch = event.changedTouches[0]
  const dnfZone = document.querySelector('.dnf-zone')
  if (dnfZone) {
    const rect = dnfZone.getBoundingClientRect()
    if (touch.clientY >= rect.top && touch.clientY <= rect.bottom) {
      const horse = dragSort?.activeList.value[touchDragIndex.value]
      if (horse && dragSort) {
        dragSort.activeList.value = dragSort.activeList.value.filter((_, i) => i !== touchDragIndex.value)
        dragSort.dnfList.value.push(horse)
      }
    }
  }

  touchDragIndex.value = -1
  dragOverIndex.value = -1
  dragClientY.value = 0
}

// Validation
const allPositioned = computed(() => {
  return activeList.value.length + dnfList.value.length === (race.value?.horses.length ?? 0)
    && activeList.value.length > 0
})

const confirmDisabled = computed(() => {
  return !allPositioned.value || isSubmitting.value
})

const confirmText = computed(() => {
  if (isSubmitting.value) return '提交中…'
  if (!allPositioned.value) return '请排列所有马匹的名次（含弃权区）'
  return '确认结果'
})

const isReentry = computed(() => {
  return race.value?.status === 'settled'
})

// Submit results
async function handleSubmit() {
  if (!race.value || confirmDisabled.value) return

  isSubmitting.value = true
  submitError.value = ''

  const positions: ResultPosition[] = [
    ...activeList.value.map((horse, index) => ({
      race_horse_id: horse.race_horse_id,
      position: index + 1,
    })),
    ...dnfList.value.map(horse => ({
      race_horse_id: horse.race_horse_id,
      position: 0,
    })),
  ]

  try {
    await submitResults(raceId, positions)
    if (!isMounted) return
    router.push(`/races/${raceId}`)
  } catch (err: any) {
    if (!isMounted) return
    isSubmitting.value = false
    const code = err?.response?.data?.detail?.code
    if (code === 'RACE_NOT_LOCKED') {
      submitError.value = err?.response?.data?.detail?.message || '比赛处于投票中状态，请先锁定'
    } else if (err?.response?.status === 422) {
      const details = err?.response?.data?.detail
      if (Array.isArray(details)) {
        submitError.value = details.map((d: any) => d.msg || '').join('；') || '数据校验失败'
      } else {
        submitError.value = details?.message || '数据校验失败'
      }
    } else {
      submitError.value = err?.response?.data?.detail?.message || '提交失败，请重试'
    }
  }
}
</script>

<template>
  <div class="results-page">
    <!-- Auto-scroll hints -->
    <div class="scroll-hint scroll-hint-up" :class="{ active: autoScrollDirection === 'up' }">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"/></svg>
    </div>
    <div class="scroll-hint scroll-hint-down" :class="{ active: autoScrollDirection === 'down' }">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
    </div>
    <div class="page-header">
      <button class="btn btn-back" @click="router.push('/admin')">
        ← 返回
      </button>
      <h1 class="page-title">
        {{ isReentry ? '修改结果' : '结果录入' }}
        <span v-if="race" class="race-name-subtitle">— {{ race.name }}</span>
      </h1>
    </div>

    <!-- Loading state -->
    <div v-if="pageState === 'loading'" class="state-box">
      <div v-for="i in 5" :key="i" class="drag-card skeleton">
        <div class="skeleton-handle" />
        <div class="skeleton-content">
          <div class="skeleton-line skeleton-name" />
          <div class="skeleton-line skeleton-meta" />
        </div>
      </div>
    </div>

    <!-- Error state -->
    <div v-else-if="pageState === 'error'" class="state-box">
      <p class="state-message state-error">{{ errorMessage }}</p>
      <button class="btn btn-cancel" @click="errorCode === 'RACE_NOT_LOCKED' ? router.push('/admin') : loadRace()">
        {{ errorCode === 'RACE_NOT_LOCKED' ? '返回管理后台' : '刷新' }}
      </button>
    </div>

    <!-- Empty state -->
    <div v-else-if="pageState === 'empty'" class="state-box">
      <p class="state-message">该比赛没有参赛马匹</p>
    </div>

    <!-- Drag sort area -->
    <div v-else class="drag-area">
      <div class="instructions">
        拖拽马匹卡片调整名次顺序。<span class="text-muted">第1名在顶部，第{{ activeList.length }}名在底部。</span>
      </div>

      <!-- Active horses -->
      <div class="drop-zone" @dragover.prevent @drop="handleDrop">
        <div
          v-for="(horse, index) in activeList"
          :key="horse.race_horse_id"
          class="drag-item-wrapper"
          :class="{ 'drag-over-top': dragOverIndex === index && isDragging, 'touch-dragging': touchDragIndex >= 0 }"
        >
          <div class="position-badge">{{ index + 1 }}</div>
          <DragCard
            :horse="horse"
            :index="index"
            :is-dragging="isDragging && draggedIndex === index"
            @drag-start="handleDragStart"
            @drag-end="handleDragEnd"
            @touchstart="(e: TouchEvent) => handleTouchStart(e, index)"
            @touchmove="handleTouchMove"
            @touchend="handleTouchEnd"
          />
        </div>
      </div>

      <!-- DNF Zone -->
      <div
        class="dnf-zone"
        @dragover.prevent
        @drop="handleDnfDrop"
      >
        <div class="dnf-zone-header">
          <span class="dnf-label">DNF/弃权区</span>
          <span v-if="dnfList.length > 0" class="dnf-count">{{ dnfList.length }}匹</span>
        </div>
        <div v-if="dnfList.length === 0" class="dnf-empty-hint">
          将弃权马匹拖拽至此
        </div>
        <div
          v-for="(horse, index) in dnfList"
          :key="horse.race_horse_id"
          class="dnf-item"
          @click="handleDnfClick(index)"
        >
          <DragCard
            :horse="horse"
            :is-dnf="true"
            :index="index"
            @drag-start="(idx: number) => handleDragStart(idx, 'dnf')"
            @drag-end="handleDragEnd"
          />
        </div>
      </div>

      <!-- Submit error -->
      <p v-if="submitError" class="submit-error" role="alert">{{ submitError }}</p>

      <!-- Confirm button -->
      <button
        class="btn btn-confirm"
        :disabled="confirmDisabled"
        @click="handleSubmit"
      >
        {{ confirmText }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.results-page {
  padding: var(--spacing-4, 16px);
  max-width: 640px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-3, 12px);
  margin-bottom: var(--spacing-6, 24px);
}

.page-title {
  font-family: var(--font-display, 'Barlow Condensed', system-ui, sans-serif);
  font-size: var(--text-heading, 24px);
  font-weight: 600;
  color: var(--color-primary, #1A5632);
  margin: 0;
}

.race-name-subtitle {
  font-weight: 400;
  color: var(--color-ink-secondary, #4A5A4A);
}

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
  transition: opacity 0.15s ease;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-back {
  background: transparent;
  color: var(--color-primary, #1A5632);
  font-size: var(--text-body-sm, 14px);
  padding: 8px 12px;
  min-height: 36px;
}

.btn-cancel {
  background: var(--color-surface-raised, #FFFFFF);
  color: var(--color-ink-primary, #1A2E1A);
  border: 1px solid var(--color-border-strong, #A8B8A4);
}

.btn-confirm {
  width: 100%;
  margin-top: var(--spacing-6, 24px);
  background: var(--color-accent, #B8960C);
  color: #FFFFFF;
  font-size: var(--text-subheading, 18px);
  padding: 14px 24px;
}

.btn-confirm:hover:not(:disabled) {
  background: #a3840a;
}

.btn-confirm:disabled {
  background: #9CA3AF;
}

/* States */
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

/* Drag area */
.drag-area {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2, 8px);
}

.instructions {
  font-size: var(--text-body-sm, 13px);
  color: var(--color-ink-primary, #1A2E1A);
  margin-bottom: var(--spacing-3, 12px);
  padding: 8px 12px;
  background: #F0F7F2;
  border-radius: var(--radius-md, 10px);
}

.text-muted {
  color: var(--color-text-muted, #6B7280);
}

/* Drop zone for active horses */
.drop-zone {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 80px;
}

.drag-item-wrapper {
  display: flex;
  align-items: stretch;
  gap: 8px;
}

.drag-item-wrapper.touch-dragging {
  touch-action: none;
}

/* Green insertion highlight (AC-2) */
.drag-item-wrapper.drag-over-top {
  position: relative;
}

.drag-item-wrapper.drag-over-top::before {
  content: '';
  position: absolute;
  top: -6px;
  left: 40px;
  right: 0;
  height: 3px;
  background: var(--color-primary, #1A5632);
  border-radius: 2px;
  z-index: 1;
}

.position-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  font-family: var(--font-display, 'Barlow Condensed', system-ui, sans-serif);
  font-size: var(--text-body-sm, 13px);
  font-weight: 700;
  color: var(--color-text-muted, #6B7280);
  background: #F3F4F6;
  border-radius: var(--radius-sm, 6px) 0 0 var(--radius-sm, 6px);
}

/* DNF Zone */
.dnf-zone {
  margin-top: var(--spacing-4, 16px);
  border: 2px dashed var(--color-text-muted, #9CA3AF);
  border-radius: var(--radius-md, 10px);
  padding: var(--spacing-3, 12px);
  min-height: 80px;
  background: #F9FAFB;
  transition: border-color 0.15s ease;
}

.dnf-zone-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-2, 8px);
}

.dnf-label {
  font-size: var(--text-body-sm, 13px);
  font-weight: 600;
  color: var(--color-text-muted, #6B7280);
}

.dnf-count {
  font-size: var(--text-body-sm, 13px);
  color: var(--color-text-muted, #6B7280);
  background: #E5E7EB;
  padding: 2px 8px;
  border-radius: 9999px;
}

.dnf-empty-hint {
  font-size: var(--text-body-sm, 13px);
  color: #9CA3AF;
  text-align: center;
  padding: 20px 0;
}

.dnf-item {
  cursor: pointer;
  margin-bottom: 8px;
}

.dnf-item:last-child {
  margin-bottom: 0;
}

/* Skeleton */
.drag-card.skeleton {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  min-height: 56px;
  background: #fff;
  border: 1px solid var(--border-hairline, #d4dcd0);
  border-radius: var(--radius-md, 10px);
}

.skeleton-handle {
  width: 32px;
  height: 16px;
  background: #E5E7EB;
  border-radius: 4px;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
}

.skeleton-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.skeleton-line {
  height: 12px;
  background: #E5E7EB;
  border-radius: 4px;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
}

.skeleton-name {
  width: 60%;
}

.skeleton-meta {
  width: 40%;
}

/* Submit error */
.submit-error {
  font-size: var(--text-body-sm, 14px);
  color: var(--color-destructive, #C53030);
  padding: 10px 12px;
  background: #FED7D7;
  border-radius: var(--rounded-md, 10px);
  margin-top: var(--spacing-3, 12px);
}

/* Auto-scroll hints */
.scroll-hint {
  position: fixed;
  left: 0;
  right: 0;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  z-index: 50;
  opacity: 0;
  transition: opacity 0.2s ease;
  color: var(--color-primary, #1A5632);
}

.scroll-hint.active {
  opacity: 1;
}

.scroll-hint-up {
  top: var(--header-height, 0px);
  background: linear-gradient(to bottom, rgba(26, 86, 50, 0.12), transparent);
}

.scroll-hint-down {
  bottom: calc(var(--bottom-nav-height, 0px) + env(safe-area-inset-bottom, 0px));
  background: linear-gradient(to top, rgba(26, 86, 50, 0.12), transparent);
}

@media (min-width: 768px) {
  .scroll-hint-down {
    bottom: 0;
  }
}

@media (max-width: 767px) {
  .scroll-hint-up {
    top: 0;
  }
}

.scroll-hint svg {
  animation: scroll-bounce 0.6s ease-in-out alternate infinite;
}

@keyframes scroll-bounce {
  from { transform: translateY(-4px); }
  to   { transform: translateY(4px); }
}

@media (prefers-reduced-motion: reduce) {
  .scroll-hint svg {
    animation: none;
  }
}

/* Mobile */
@media (max-width: 767px) {
  .page-header {
    flex-wrap: wrap;
  }

  .page-title {
    font-size: var(--text-subheading, 18px);
  }

  .position-badge {
    min-width: 24px;
    font-size: var(--text-caption, 11px);
  }
}
</style>
