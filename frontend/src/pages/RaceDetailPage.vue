<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, shallowRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import StatusBadge from '@/components/StatusBadge.vue'
import HorseDetailCard from '@/components/HorseDetailCard.vue'
import AddHorseCard from '@/components/AddHorseCard.vue'
import RaceHeaderEditor from '@/components/RaceHeaderEditor.vue'
import VotingDetail from '@/components/VotingDetail.vue'
import HorseSearchSelect from '@/components/HorseSearchSelect.vue'
import ConfirmDeleteModal from '@/components/ConfirmDeleteModal.vue'

import {
  getRace,
  updateRace,
  addRaceHorse,
  updateRaceHorse,
  updateGateOrder,
  lockRace,
  removeRaceHorse,
  toggleRaceHidden,
  deleteRace,
} from '@/api/races'
import { submitResults } from '@/api/results'
import { updateBestWin, refreshRaceHorseSnapshot } from '@/api/horses'
import { useVote } from '@/composables/useVote'
import { useDragSort } from '@/composables/useDragSort'
import { useDragAutoScroll } from '@/composables/useDragAutoScroll'
import type { RaceDetail, ResultPosition } from '@/types/race'
import type { Horse } from '@/types/horse'

type PageState = 'loading' | 'error' | 'success'
type ResultMode = 'idle' | 'ranking'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const raceId = Number(route.params.id)

const pageState = ref<PageState>('loading')
const race = ref<RaceDetail | null>(null)
const errorMessage = ref('加载失败，请刷新重试')
const isJiggleMode = ref(false)

const {
  votedHorseName,
  votedRaceHorseId,
  isSubmitting,
  votes,
  votesLoading,
  errorMessage: voteError,
  toggleVote,
  loadVotes,
} = useVote()

function checkUserVote() {
  if (!authStore.isLoggedIn || !authStore.user) return
  const myVote = votes.value.find(v => v.user_id === authStore.user!.id)
  if (myVote) {
    votedHorseName.value = myVote.horse_name
    votedRaceHorseId.value = myVote.race_horse_id
  }
}

const isRaceVoting = computed(() => race.value?.status === 'voting')
const isRaceLocked = computed(() => race.value?.status === 'locked')
const isRaceSettled = computed(() => race.value?.status === 'settled')

const horsePositions = computed<Record<string, number> | undefined>(() => {
  if (!race.value || !isRaceSettled.value) return undefined
  const map: Record<string, number> = {}
  for (const h of race.value.horses) {
    if (h.position && h.position >= 1 && h.position <= 3) {
      map[h.snapshot_data.name ?? ''] = h.position
    }
  }
  return map
})

const isAdmin = computed(() => authStore.isAdmin)

const canEnterJiggleMode = computed(() =>
  isAdmin.value && (
    isRaceVoting.value ||
    ((isRaceLocked.value || isRaceSettled.value) && resultMode.value === 'ranking')
  ),
)

function toggleJiggleMode() {
  if (!canEnterJiggleMode.value) return
  if (isJiggleMode.value) {
    // Exit jiggle mode: reset all drag state
    isJiggleMode.value = false
    gateTouchIndex.value = -1
    gateDragOverIndex.value = -1
    gateDragSort.value?.endDrag()
    resultTouchIndex.value = -1
    resultDragOverIndex.value = -1
    resultDragSource.value = 'active'
    resultDragSort.value?.endDrag()
  } else {
    isJiggleMode.value = true
  }
}

const canVote = computed(() =>
  isRaceVoting.value && authStore.isLoggedIn && !authStore.isAdmin,
)
const cardsVotable = computed(() =>
  isRaceVoting.value && !authStore.isAdmin && authStore.isLoggedIn,
)

const isGuestVoting = computed(() =>
  isRaceVoting.value && !authStore.isLoggedIn,
)

function isHorseVoted(raceHorseId: number): boolean {
  return votedRaceHorseId.value === raceHorseId
}

function handleCardClick(horse: RaceDetail['horses'][0]) {
  if (!authStore.isLoggedIn) {
    router.push({ path: '/login', query: { redirect: `/races/${raceId}` } })
    return
  }
  if (authStore.isAdmin) return
  if (!isRaceVoting.value) return
  toggleVote(horse, raceId)
}

// Header editing
const headerSaveError = ref('')
const headerSaveSuccess = ref(false)
const dateEditing = ref(false)
const editDate = ref('')
const dateInputRef = ref<HTMLInputElement | null>(null)

function startDateEdit() {
  if (!isAdmin.value || !isRaceVoting.value || !race.value) return
  editDate.value = race.value.date.slice(0, 10)
  dateEditing.value = true
  nextTick(() => dateInputRef.value?.focus())
}

function saveDate() {
  if (!race.value || !editDate.value) return
  dateEditing.value = false
  handleHeaderSave({ name: race.value.name, date: editDate.value })
}

function cancelDateEdit() {
  dateEditing.value = false
}

async function handleHeaderSave({ name, date }: { name: string; date: string }) {
  if (!race.value || !isAdmin.value || !isRaceVoting.value) return
  headerSaveError.value = ''
  headerSaveSuccess.value = false

  const payload: { name?: string; date?: string } = {}
  if (name !== race.value.name) payload.name = name
  if (date !== race.value.date.slice(0, 10)) payload.date = date

  if (Object.keys(payload).length === 0) return

  try {
    race.value = await updateRace(raceId, payload)
    headerSaveSuccess.value = true
    setTimeout(() => { headerSaveSuccess.value = false }, 2000)
  } catch (err: any) {
    headerSaveError.value = err?.response?.data?.detail?.message || '保存失败'
  }
}

// Lock
const locking = ref(false)
const lockError = ref('')
const showLockConfirm = ref(false)

async function handleLock() {
  if (!race.value || !isAdmin.value || !isRaceVoting.value || locking.value) return
  locking.value = true
  lockError.value = ''
  try {
    await lockRace(raceId)
    showLockConfirm.value = false
    race.value = await getRace(raceId)
    await loadVotes(raceId)
    isJiggleMode.value = false
  } catch (err: any) {
    lockError.value = err?.response?.data?.detail?.message || '锁定失败'
  } finally {
    locking.value = false
  }
}

// Add horse modal
const showAddHorseModal = ref(false)
const selectedAddHorse = ref<Horse[]>([])
const addHorseError = ref('')
const addHorseSaving = ref(false)

// Delete horse via drag
const deleteHover = ref(false)
const deleteTarget = ref<{ raceHorseId: number; name: string } | null>(null)
const showDeleteConfirm = ref(false)
const deleting = ref(false)

function handleGateDragItemDragStart(e: DragEvent, horse: RaceDetail['horses'][0]) {
  if (!isAdmin.value || !isRaceVoting.value) return
  e.dataTransfer?.setData(
    'application/json',
    JSON.stringify({
      raceHorseId: horse.race_horse_id,
      name: horse.snapshot_data.name ?? '未知',
    }),
  )
}

function handleDeleteDragEnter() {
  deleteHover.value = true
}

function handleDeleteDragLeave() {
  deleteHover.value = false
}

function handleDeleteDrop(e: DragEvent) {
  e.preventDefault()
  deleteHover.value = false
  const raw = e.dataTransfer?.getData('application/json')
  if (!raw) return
  try {
    const data = JSON.parse(raw)
    deleteTarget.value = { raceHorseId: data.raceHorseId, name: data.name }
    showDeleteConfirm.value = true
  } catch {
    // ignore invalid data
  }
}

async function confirmDeleteHorse() {
  if (!race.value || !deleteTarget.value || deleting.value) return
  deleting.value = true
  try {
    await removeRaceHorse(raceId, deleteTarget.value.raceHorseId)
    race.value = await getRace(raceId)
    showDeleteConfirm.value = false
    deleteTarget.value = null
  } catch (err: any) {
    alert(err?.response?.data?.detail?.message || '删除马匹失败')
  } finally {
    deleting.value = false
  }
}

function openAddHorseModal() {
  if (!isAdmin.value || !isRaceVoting.value) return
  selectedAddHorse.value = []
  addHorseError.value = ''
  showAddHorseModal.value = true
}

function closeAddHorseModal() {
  showAddHorseModal.value = false
}

async function confirmAddHorse() {
  if (!race.value || selectedAddHorse.value.length === 0 || addHorseSaving.value) return
  addHorseSaving.value = true
  addHorseError.value = ''
  try {
    for (const horse of selectedAddHorse.value) {
      await addRaceHorse(raceId, { horse_id: horse.id })
    }
    race.value = await getRace(raceId)
    closeAddHorseModal()
  } catch (err: any) {
    addHorseError.value = err?.response?.data?.detail?.message || '添加马匹失败'
  } finally {
    addHorseSaving.value = false
  }
}

// Delete race
const showDeleteRaceModal = ref(false)
const deletingRace = ref(false)
const deleteRaceError = ref('')

async function handleDeleteRace() {
  if (!race.value || deletingRace.value) return
  deletingRace.value = true
  deleteRaceError.value = ''
  try {
    await deleteRace(raceId)
    router.push('/')
  } catch (err: any) {
    deleteRaceError.value = err?.response?.data?.detail?.message || '删除比赛失败'
  } finally {
    deletingRace.value = false
  }
}
async function handleUpdateJockey(
  horse: RaceDetail['horses'][0],
  value: string | null,
) {
  if (!isAdmin.value || !isRaceVoting.value) return
  try {
    await updateRaceHorse(raceId, horse.race_horse_id, { jockey: value })
    race.value = await getRace(raceId)
  } catch (err: any) {
    alert(err?.response?.data?.detail?.message || '保存失败')
  }
}

async function handleRefresh(horse: RaceDetail['horses'][0]) {
  if (!isAdmin.value || !race.value) return
  try {
    await refreshRaceHorseSnapshot(raceId, horse.race_horse_id)
    race.value = await getRace(raceId)
  } catch (err: any) {
    alert(err?.response?.data?.detail?.message || '刷新失败')
  }
}

// Gate drag mode
const gateDragSort = computed(() => {
  if (!race.value) return null
  return useDragSort(race.value.horses, undefined, { mode: 'gate' })
})

const gateHorses = computed(() => gateDragSort.value?.activeList.value ?? race.value?.horses ?? [])
const isGateDragging = computed(() => gateDragSort.value?.isDragging.value ?? false)

// For normal view (non-result mode): sort by gate (voting/locked) or position (settled)
const displayHorses = computed(() => {
  if (!race.value) return []
  if (isRaceSettled.value) {
    return [...race.value.horses].sort((a, b) => {
      const posA = a.position === 0 ? 999 : (a.position ?? 999)
      const posB = b.position === 0 ? 999 : (b.position ?? 999)
      if (posA !== posB) return posA - posB
      // For DNF horses (position 0), sort by gate to match DNF zone order
      return (a.gate ?? 999) - (b.gate ?? 999)
    })
  }
  return gateHorses.value
})

const gateDragOverIndex = ref(-1)

function handleGateDragStart(index: number) {
  gateDragSort.value?.startDrag(index)
  gateDragOverIndex.value = -1
}

function handleGateDrop(event: DragEvent) {
  event.preventDefault()
  const sort = gateDragSort.value
  if (!sort || sort.draggedIndex.value < 0) return

  const dropZone = event.currentTarget as HTMLElement
  const cards = dropZone.querySelectorAll('.gate-drag-item')
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
  sort.commitReorder(sort.draggedIndex.value, targetIndex)
  submitGateOrder()
  gateDragOverIndex.value = -1
}

function handleGateDragEnd() {
  gateDragSort.value?.endDrag()
  gateDragOverIndex.value = -1
  dragClientY.value = 0
}

async function submitGateOrder() {
  if (!race.value || !isAdmin.value || !isRaceVoting.value) return
  const order = gateHorses.value.map(h => h.race_horse_id)
  try {
    race.value = await updateGateOrder(raceId, { order })
  } catch (err: any) {
    alert(err?.response?.data?.detail?.message || '闸位排序保存失败')
    await loadRace()
  }
}

// Mobile touch gate drag (jiggle mode only)
const gateTouchIndex = ref(-1)

function handleGateTouchStart(_event: TouchEvent, index: number) {
  if (!authStore.isAdmin || !isRaceVoting.value || !isJiggleMode.value) return
  gateTouchIndex.value = index
  gateDragSort.value?.startDrag(index)
}

// Cache card positions to avoid getBoundingClientRect() on every touchmove
let cachedGateCardRects: { top: number; bottom: number }[] = []
let gateCardRectsCacheTime = 0
let cachedResultCardRects: { top: number; bottom: number }[] = []
let resultCardRectsCacheTime = 0

function handleGateTouchMove(event: TouchEvent) {
  if (gateTouchIndex.value < 0) return
  event.preventDefault()
  dragClientY.value = event.touches[0].clientY

  // Refresh card rect cache every 200ms
  const now = Date.now()
  if (now - gateCardRectsCacheTime > 200) {
    const cards = document.querySelectorAll('.gate-drag-item')
    cachedGateCardRects = []
    for (let i = 0; i < cards.length; i++) {
      const rect = cards[i].getBoundingClientRect()
      cachedGateCardRects.push({ top: rect.top, bottom: rect.bottom })
    }
    gateCardRectsCacheTime = now
  }

  const touchY = event.touches[0].clientY
  for (let i = 0; i < cachedGateCardRects.length; i++) {
    if (touchY >= cachedGateCardRects[i].top && touchY <= cachedGateCardRects[i].bottom) {
      if (i !== gateTouchIndex.value && gateDragSort.value) {
        const item = gateDragSort.value.activeList.value.splice(gateTouchIndex.value, 1)[0]
        if (item) {
          gateDragSort.value.activeList.value.splice(i, 0, item)
          gateTouchIndex.value = i
          gateDragOverIndex.value = i
          gateCardRectsCacheTime = 0
        }
      }
      break
    }
  }
}

function handleGateTouchEnd() {
  if (gateTouchIndex.value >= 0) {
    submitGateOrder()
  }
  gateTouchIndex.value = -1
  gateDragOverIndex.value = -1
  dragClientY.value = 0
  gateDragSort.value?.endDrag()
}

// Result ranking mode
const resultMode = ref<ResultMode>('idle')
const resultEntryVersion = ref(0)
const existingPositions = ref<Map<number, number> | undefined>(undefined)
const resultDragSort = shallowRef<ReturnType<typeof useDragSort> | null>(null)
const resultDragOverIndex = ref(-1)
const resultSubmitting = ref(false)
const resultSubmitError = ref('')

const resultActiveList = computed(() => resultDragSort.value?.activeList.value ?? [])
const resultDnfList = computed(() => resultDragSort.value?.dnfList.value ?? [])
const isResultDragging = computed(() => resultDragSort.value?.isDragging.value ?? false)
const resultDragSource = ref<'active' | 'dnf'>('active')
const resultTouchIndex = ref(-1)

// Auto-scroll during drag
const dragClientY = ref(0)
const autoScrollEnabled = computed(() =>
  gateDragSort.value?.isDragging.value ||
  resultDragSort.value?.isDragging.value ||
  gateTouchIndex.value >= 0 ||
  resultTouchIndex.value >= 0,
)
const { autoScrollDirection } = useDragAutoScroll({ enabled: autoScrollEnabled, clientY: dragClientY })

function initResultDragSort() {
  if (!race.value) return
  const hasPositions = race.value.horses.some(h => h.position !== null && h.position !== undefined)
  if (hasPositions) {
    existingPositions.value = new Map(
      race.value.horses.map(h => [h.race_horse_id, h.position ?? 0]),
    )
  } else {
    existingPositions.value = undefined
  }
  resultDragSort.value = useDragSort([...race.value.horses], existingPositions.value, { mode: 'result' })
}

function enterResultMode() {
  if (!isAdmin.value || (!isRaceLocked.value && !isRaceSettled.value)) return
  resultMode.value = 'ranking'
  resultEntryVersion.value++
  resultSubmitError.value = ''
  resultDragOverIndex.value = -1
  resultTouchIndex.value = -1
  resultDragSource.value = 'active'
  initResultDragSort()
  isJiggleMode.value = true
}

function exitResultMode() {
  resultMode.value = 'idle'
  resultDragSort.value = null
  isJiggleMode.value = false
  resultDragOverIndex.value = -1
  resultTouchIndex.value = -1
  resultDragSource.value = 'active'
}

function handleResultDragStart(index: number, source: 'active' | 'dnf' = 'active') {
  resultDragSort.value?.startDrag(index)
  resultDragSource.value = source
  resultDragOverIndex.value = -1
}

function handleResultDrop(event: DragEvent) {
  event.preventDefault()
  if (!resultDragSort.value || resultDragSort.value.draggedIndex.value < 0) return

  if (resultDragSource.value === 'dnf') {
    resultDragSort.value.moveToActive(resultDragSort.value.draggedIndex.value)
  } else {
    const dropZone = event.currentTarget as HTMLElement
    const cards = dropZone.querySelectorAll('.result-drag-item')
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
    resultDragSort.value.commitReorder(resultDragSort.value.draggedIndex.value, targetIndex)
  }
  resultDragOverIndex.value = -1
}

function handleResultDragEnd() {
  resultDragSort.value?.endDrag()
  resultDragOverIndex.value = -1
  dragClientY.value = 0
}

function handleDnfDrop(event: DragEvent) {
  event.preventDefault()
  if (resultDragSort.value && resultDragSort.value.draggedIndex.value >= 0 && resultDragSource.value === 'active') {
    resultDragSort.value.moveToDnf(resultDragSort.value.draggedIndex.value)
  }
  resultDragSort.value?.endDrag()
  resultDragOverIndex.value = -1
}

function handleDnfClick(index: number) {
  resultDragSort.value?.moveToActive(index)
}

// Mobile touch result ranking (jiggle mode)
function handleResultTouchStart(index: number, source: 'active' | 'dnf') {
  if (!isJiggleMode.value) return
  resultTouchIndex.value = index
  resultDragSource.value = source
  resultDragSort.value?.startDrag(index)
}

function handleResultTouchMove(event: TouchEvent) {
  if (resultTouchIndex.value < 0 || !resultDragSort.value) return
  event.preventDefault()
  dragClientY.value = event.touches[0].clientY

  // Refresh card rect cache every 200ms
  const now = Date.now()
  if (now - resultCardRectsCacheTime > 200) {
    const cards = document.querySelectorAll('.result-drag-item')
    cachedResultCardRects = []
    for (let i = 0; i < cards.length; i++) {
      const rect = cards[i].getBoundingClientRect()
      cachedResultCardRects.push({ top: rect.top, bottom: rect.bottom })
    }
    resultCardRectsCacheTime = now
  }

  const touch = event.touches[0]
  for (let i = 0; i < cachedResultCardRects.length; i++) {
    if (touch.clientY >= cachedResultCardRects[i].top && touch.clientY <= cachedResultCardRects[i].bottom) {
      if (i !== resultTouchIndex.value && resultDragSource.value === 'active') {
        const item = resultDragSort.value.activeList.value.splice(resultTouchIndex.value, 1)[0]
        if (item) {
          resultDragSort.value.activeList.value.splice(i, 0, item)
          resultTouchIndex.value = i
          resultDragOverIndex.value = i
          resultCardRectsCacheTime = 0
        }
      }
      break
    }
  }
}

function handleResultTouchEnd(event: TouchEvent) {
  if (resultTouchIndex.value < 0) return

  // Check if released over DNF zone
  if (resultDragSource.value === 'active') {
    const dnfZone = document.querySelector('.dnf-zone')
    if (dnfZone) {
      const dnfRect = dnfZone.getBoundingClientRect()
      const touchY = event.changedTouches[0].clientY
      if (touchY >= dnfRect.top && touchY <= dnfRect.bottom) {
        resultDragSort.value?.moveToDnf(resultTouchIndex.value)
      }
    }
  } else if (resultDragSource.value === 'dnf') {
    // DNF card tap → move back to active
    const activeZone = document.querySelector('.drop-zone')
    if (activeZone) {
      const activeRect = activeZone.getBoundingClientRect()
      const touchY = event.changedTouches[0].clientY
      if (touchY < activeRect.bottom) {
        resultDragSort.value?.moveToActive(resultTouchIndex.value)
      }
    }
  }

  resultTouchIndex.value = -1
  resultDragOverIndex.value = -1
  dragClientY.value = 0
  resultDragSort.value?.endDrag()
}

function handleResultTouchCancel() {
  resultTouchIndex.value = -1
  resultDragOverIndex.value = -1
  dragClientY.value = 0
  resultDragSort.value?.endDrag()
}

const allPositioned = computed(() => {
  return resultActiveList.value.length + resultDnfList.value.length === (race.value?.horses.length ?? 0)
    && resultActiveList.value.length > 0
})

const confirmResultDisabled = computed(() => {
  return !allPositioned.value || resultSubmitting.value
})

const confirmResultText = computed(() => {
  if (resultSubmitting.value) return '提交中…'
  if (!allPositioned.value) return '请排列所有马匹的名次（含弃权区）'
  return '确认结果'
})

async function handleConfirmResult() {
  if (!race.value || confirmResultDisabled.value) return

  resultSubmitting.value = true
  resultSubmitError.value = ''

  const positions: ResultPosition[] = [
    ...resultActiveList.value.map((horse, index) => ({
      race_horse_id: horse.race_horse_id,
      position: index + 1,
    })),
    ...resultDnfList.value.map(horse => ({
      race_horse_id: horse.race_horse_id,
      position: 0,
    })),
  ]

  try {
    await submitResults(raceId, positions)
    // Exit result mode first, then refresh data to prevent stale rendering state
    exitResultMode()
    await nextTick()
    race.value = await getRace(raceId)
    if (race.value.status === 'settled') {
      await loadVotes(raceId)
      checkUserVote()
    }
  } catch (err: any) {
    const code = err?.response?.data?.detail?.code
    if (code === 'RACE_NOT_LOCKED') {
      resultSubmitError.value = err?.response?.data?.detail?.message || '比赛处于投票中状态，请先锁定'
    } else if (err?.response?.status === 422) {
      const details = err?.response?.data?.detail
      if (Array.isArray(details)) {
        resultSubmitError.value = details.map((d: any) => d.msg || '').join('；') || '数据校验失败'
      } else {
        resultSubmitError.value = details?.message || '数据校验失败'
      }
    } else {
      resultSubmitError.value = err?.response?.data?.detail?.message || '提交失败，请重试'
    }
  } finally {
    resultSubmitting.value = false
  }
}

// Toggle hidden
const togglingHidden = ref(false)

async function handleToggleHidden() {
  if (!race.value || togglingHidden.value) return
  togglingHidden.value = true
  try {
    const result = await toggleRaceHidden(race.value.id)
    race.value.is_hidden = result.is_hidden
  } catch {
    // silently fail
  } finally {
    togglingHidden.value = false
  }
}

// Best win update
const updatingBestWin = ref(false)
const bestWinUpdateError = ref('')
const bestWinUpdateSuccess = ref(false)

const winnerHorse = computed(() => {
  if (!race.value || !isRaceSettled.value) return null
  return race.value.horses.find(h => h.position === 1) ?? null
})

const canUpdateBestWin = computed(() => {
  if (!winnerHorse.value || !race.value) return false
  if (winnerHorse.value.snapshot_data.best_win === race.value.name) return false
  return true
})

async function handleUpdateBestWin() {
  if (!winnerHorse.value || !race.value || updatingBestWin.value) return
  updatingBestWin.value = true
  bestWinUpdateError.value = ''
  bestWinUpdateSuccess.value = false
  try {
    await updateBestWin(winnerHorse.value.horse_id, race.value.id)
    bestWinUpdateSuccess.value = true
  } catch (err: any) {
    bestWinUpdateError.value = err?.response?.data?.detail?.message || '更新主胜鞍失败'
  } finally {
    updatingBestWin.value = false
  }
}

async function loadRace() {
  pageState.value = 'loading'
  errorMessage.value = '加载失败，请刷新重试'
  try {
    race.value = await getRace(raceId)
    pageState.value = 'success'
    await loadVotes(raceId)
    checkUserVote()
  } catch (err: any) {
    pageState.value = 'error'
    const code = err?.response?.data?.detail?.code
    if (code === 'RACE_HIDDEN') {
      errorMessage.value = '当前比赛已隐藏'
    }
  }
}

onMounted(loadRace)

onUnmounted(() => {
  isJiggleMode.value = false
})
</script>

<template>
  <div class="race-detail-page">
    <!-- Auto-scroll hints -->
    <div class="scroll-hint scroll-hint-up" :class="{ active: autoScrollDirection === 'up' }">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"/></svg>
    </div>
    <div class="scroll-hint scroll-hint-down" :class="{ active: autoScrollDirection === 'down' }">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
    </div>
    <!-- Loading -->
    <div v-if="pageState === 'loading'" class="state-container">
      <p>加载中…</p>
    </div>

    <!-- Error -->
    <div v-else-if="pageState === 'error'" class="state-container">
      <p class="error-text">{{ errorMessage }}</p>
      <button
        v-if="errorMessage !== '当前比赛已隐藏'"
        class="refresh-btn"
        @click="router.go(0)"
      >
        刷新重试
      </button>
      <button
        v-if="errorMessage === '当前比赛已隐藏'"
        class="refresh-btn"
        @click="router.push('/')"
      >
        返回首页
      </button>
    </div>

    <!-- Race Detail -->
    <template v-else-if="race">
      <div class="race-header">
        <div class="race-header-top">
          <button class="back-btn" @click="router.push('/')" aria-label="返回首页">
            ← 返回
          </button>
        </div>

        <div class="race-title-row">
          <RaceHeaderEditor
            v-if="isAdmin && isRaceVoting"
            :name="race.name"
            :date="race.date"
            @save="handleHeaderSave"
          />
          <template v-else>
            <h1 class="race-name">{{ race.name }}</h1>
          </template>
          <div class="title-row-right">
            <div class="race-tags">
              <span class="race-tag">{{ race.race_grade }}</span>
              <span class="race-tag">{{ race.age_range }}</span>
              <span v-if="race.sex_restriction !== '无'" class="race-tag">{{ race.sex_restriction }}</span>
              <span class="race-tag">{{ race.country }}</span>
              <span class="race-tag">{{ race.distance }}</span>
              <span class="race-tag">{{ race.surface }}</span>
            </div>
            <StatusBadge :status="race.status as any" />
            <button
              v-if="isAdmin"
              class="eye-btn"
              :class="{ 'eye-hidden': race.is_hidden }"
              :disabled="togglingHidden"
              :title="race.is_hidden ? '已隐藏，点击取消隐藏' : '点击隐藏比赛'"
              :aria-label="race.is_hidden ? '取消隐藏' : '隐藏'"
              @click="handleToggleHidden"
            >
              <span v-if="togglingHidden" class="eye-spinner"></span>
              <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <template v-if="race.is_hidden">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
                  <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
                  <line x1="1" y1="1" x2="23" y2="23"/>
                </template>
                <template v-else>
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </template>
              </svg>
            </button>
          </div>
        </div>

        <div class="race-subinfo">
          <div class="date-row">
            <template v-if="isAdmin && isRaceVoting && dateEditing">
              <input
                ref="dateInputRef"
                v-model="editDate"
                type="date"
                class="date-input"
                @blur="saveDate"
                @keydown.enter.prevent="saveDate"
                @keydown.escape.prevent="cancelDateEdit"
              />
            </template>
            <p
              v-else
              class="race-date"
              :class="{ 'date-editable': isAdmin && isRaceVoting }"
              @dblclick="startDateEdit"
            >{{ race.date }}</p>
          </div>
          <p class="race-meta">{{ race.horses.length }} 匹参赛 · {{ race.vote_count }} 人已投</p>
        </div>

        <p v-if="headerSaveError" class="header-message error">{{ headerSaveError }}</p>
        <p v-if="headerSaveSuccess" class="header-message success">保存成功</p>
      </div>

      <!-- Admin actions for voting state -->
      <div v-if="isAdmin && isRaceVoting && resultMode === 'idle'" class="admin-actions-bar">
        <button
          class="admin-btn lock-btn"
          :disabled="locking"
          @click="showLockConfirm = true; lockError = ''"
        >
          锁定
        </button>
        <button
          v-if="canEnterJiggleMode"
          class="jiggle-toggle-btn mobile-only"
          :class="{ active: isJiggleMode }"
          :aria-label="isJiggleMode ? '退出编辑闸位模式' : '进入编辑闸位模式'"
          :aria-pressed="isJiggleMode"
          @click="toggleJiggleMode"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
          <span>{{ isJiggleMode ? '完成' : '编辑闸位' }}</span>
        </button>
        <button
          class="admin-btn delete-btn"
          @click="showDeleteRaceModal = true; deleteRaceError = ''"
        >
          删除比赛
        </button>
        <p v-if="lockError" class="admin-error">{{ lockError }}</p>
        <p v-if="deleteRaceError" class="admin-error">{{ deleteRaceError }}</p>
      </div>

      <!-- Admin result mode entry -->
      <div v-if="isAdmin && isRaceLocked && resultMode === 'idle'" class="admin-actions-bar">
        <button class="admin-btn end-race-btn" @click="enterResultMode">
          比赛结束
        </button>
        <button
          class="admin-btn delete-btn"
          @click="showDeleteRaceModal = true; deleteRaceError = ''"
        >
          删除比赛
        </button>
        <p v-if="deleteRaceError" class="admin-error">{{ deleteRaceError }}</p>
      </div>

      <div v-if="isAdmin && isRaceSettled && resultMode === 'idle'" class="admin-actions-bar">
        <button class="admin-btn modify-result-btn" @click="enterResultMode">
          修改结果
        </button>
        <button
          v-if="canUpdateBestWin"
          class="admin-btn modify-result-btn"
          :disabled="updatingBestWin"
          @click="handleUpdateBestWin"
        >
          {{ updatingBestWin ? '更新中…' : '更新主胜鞍' }}
        </button>
        <p v-if="bestWinUpdateSuccess" class="admin-success">主胜鞍已更新为「{{ race.name }}」</p>
        <p v-if="bestWinUpdateError" class="admin-error">{{ bestWinUpdateError }}</p>
      </div>

      <!-- Admin result confirmation / cancel in ranking mode (at top, same position as 修改结果) -->
      <div v-if="isAdmin && resultMode === 'ranking'" class="admin-actions-bar ranking-actions-bar">
        <button
          class="admin-btn confirm-result-btn"
          :disabled="confirmResultDisabled"
          @click="handleConfirmResult"
        >
          {{ confirmResultText }}
        </button>
        <button class="admin-btn cancel-result-btn" @click="exitResultMode">
          取消
        </button>
        <p v-if="resultSubmitError" class="admin-error">{{ resultSubmitError }}</p>
      </div>


      <!-- Custom scoring info -->
      <div v-if="race.custom_scoring" class="custom-scoring-info">
        <p class="scoring-title">自定义积分规则</p>
        <p class="scoring-detail">
          正序积分：{{ race.custom_scoring.positive_scores.join(', ') }}
        </p>
        <p
          v-if="race.custom_scoring.penalty_rules?.length"
          class="scoring-detail"
        >
          扣分规则：{{ race.custom_scoring.penalty_rules.map(r => `倒数第${Math.abs(r.position)}名扣${Math.abs(r.points)}分`).join('，') }}
        </p>
      </div>

      <!-- Vote hints -->
      <div v-if="canVote && !votedHorseName" class="vote-hint">
        点击马匹卡片进行投票，再次点击取消投票
      </div>
      <div v-if="canVote && votedHorseName" class="vote-hint voted">
        已投 <strong>{{ votedHorseName }}</strong>，点击该马匹可取消投票，点击其他马匹可更换选择
      </div>
      <div v-if="isGuestVoting" class="vote-hint">
        点击马匹卡片，登录后即可投票
      </div>

      <!-- Horse list -->
      <div class="horse-list">
        <h2 class="section-title">参赛马匹</h2>

        <!-- Normal / gate drag view -->
        <div
          v-if="resultMode !== 'ranking'"
          class="horse-list-content"
          :class="{ 'gate-dragging': isGateDragging }"
          @dragover.prevent
          @drop="handleGateDrop"
        >
          <!-- Admin voting: with touch/drag handlers for gate reorder -->
          <template v-if="isAdmin && isRaceVoting">
            <div
              v-for="(horse, index) in displayHorses"
              :key="horse.race_horse_id"
              class="gate-drag-item"
              :class="{ 'drag-over-top': gateDragOverIndex === index && isGateDragging, 'touch-dragging': gateTouchIndex >= 0 }"
              @dragstart="(e: DragEvent) => handleGateDragItemDragStart(e, horse)"
              @touchstart="(e: TouchEvent) => handleGateTouchStart(e, index)"
              @touchmove="handleGateTouchMove"
              @touchend="handleGateTouchEnd"
              @touchcancel="handleGateTouchEnd"
            >
              <HorseDetailCard
                :snapshot-data="horse.snapshot_data"
                :horse-id="horse.horse_id"
                :jockey="horse.jockey"
                :birth-year="horse.snapshot_data.birth_year"
                :hemisphere="horse.snapshot_data.hemisphere"
                :reference-date="race.date"
                :votable="cardsVotable"
                :voted="isHorseVoted(horse.race_horse_id)"
                :submitting="isSubmitting"
                :gate="horse.gate"
                :position="isRaceSettled ? (horse.position ?? null) : null"
                :editable="isAdmin && isRaceVoting"
                :draggable="(isAdmin && isRaceVoting) ? true : undefined"
                :show-delete-button="isJiggleMode"
                :is-jiggling="isJiggleMode"
                :class="{ 'voted-horse-locked': (isRaceLocked || isRaceSettled) && votedHorseName && horse.snapshot_data.name === votedHorseName }"
                @vote-toggle="handleCardClick(horse)"
                @update-field="(payload) => handleUpdateJockey(horse, payload.value)"
                @drag-start="handleGateDragStart(index)"
                @drag-end="handleGateDragEnd"
                @refresh="handleRefresh(horse)"
                @delete-click="deleteTarget = { raceHorseId: horse.race_horse_id, name: horse.snapshot_data.name ?? '未知' }; showDeleteConfirm = true"
              />
            </div>
          </template>
          <!-- Regular users / non-voting: NO touch/drag handlers to avoid mobile freeze -->
          <template v-else>
            <div
              v-for="horse in displayHorses"
              :key="horse.race_horse_id"
              class="gate-drag-item"
            >
              <HorseDetailCard
                :snapshot-data="horse.snapshot_data"
                :horse-id="horse.horse_id"
                :jockey="horse.jockey"
                :birth-year="horse.snapshot_data.birth_year"
                :hemisphere="horse.snapshot_data.hemisphere"
                :reference-date="race.date"
                :votable="cardsVotable"
                :voted="isHorseVoted(horse.race_horse_id)"
                :submitting="isSubmitting"
                :gate="horse.gate"
                :position="isRaceSettled ? (horse.position ?? null) : null"
                :editable="isAdmin && isRaceVoting"
                :class="{ 'voted-horse-locked': (isRaceLocked || isRaceSettled) && votedHorseName && horse.snapshot_data.name === votedHorseName }"
                @vote-toggle="handleCardClick(horse)"
                @refresh="handleRefresh(horse)"
              />
            </div>
          </template>
          <div v-if="isAdmin && isRaceVoting && !isJiggleMode" class="add-delete-row">
            <AddHorseCard @click="openAddHorseModal" />
            <div
              class="delete-zone"
              :class="{ 'delete-hover': deleteHover }"
              @dragenter.prevent="handleDeleteDragEnter"
              @dragover.prevent="handleDeleteDragEnter"
              @dragleave="handleDeleteDragLeave"
              @drop="handleDeleteDrop"
            >
              <span class="delete-icon">✕</span>
              <span class="delete-label">拖拽至此删除</span>
            </div>
          </div>
        </div>

        <!-- Result ranking mode -->
        <div v-else class="result-ranking-area" :key="'ranking-' + resultEntryVersion">
          <div class="instructions">
            拖拽马匹卡片调整名次顺序。<span class="text-muted">第1名在顶部，弃权马匹拖入下方 DNF 区。</span>
          </div>

          <div class="drop-zone" @dragover.prevent @drop="handleResultDrop">
            <div
              v-for="(horse, index) in resultActiveList"
              :key="'result-active-' + horse.race_horse_id"
              class="result-drag-item"
              :class="{ 'drag-over-top': resultDragOverIndex === index && isResultDragging, 'touch-dragging': resultTouchIndex >= 0 }"
              @touchstart="handleResultTouchStart(index, 'active')"
              @touchmove="handleResultTouchMove"
              @touchend="handleResultTouchEnd"
              @touchcancel="handleResultTouchCancel"
            >
              <HorseDetailCard
                :snapshot-data="horse.snapshot_data"
                :horse-id="horse.horse_id"
                :jockey="horse.jockey"
                :birth-year="horse.snapshot_data.birth_year"
                :hemisphere="horse.snapshot_data.hemisphere"
                :reference-date="race.date"
                :gate="horse.gate"
                :position="index + 1"
                :draggable="true"
                :is-dnf="false"
                :show-delete-button="isJiggleMode"
                :is-jiggling="isJiggleMode"
                @drag-start="handleResultDragStart(index, 'active')"
                @drag-end="handleResultDragEnd"
                @refresh="handleRefresh(horse)"
                @delete-click="deleteTarget = { raceHorseId: horse.race_horse_id, name: horse.snapshot_data.name ?? '未知' }; showDeleteConfirm = true"
              />
            </div>
          </div>

          <div
            class="dnf-zone"
            @dragover.prevent
            @drop="handleDnfDrop"
          >
            <div class="dnf-zone-header">
              <span class="dnf-label">DNF/弃权区</span>
              <span v-if="resultDnfList.length > 0" class="dnf-count">{{ resultDnfList.length }}匹</span>
            </div>
            <div v-if="resultDnfList.length === 0" class="dnf-empty-hint">
              将弃权马匹拖拽至此
            </div>
            <div
              v-for="(horse, index) in resultDnfList"
              :key="'result-dnf-' + horse.race_horse_id"
              class="dnf-item"
              @click="handleDnfClick(index)"
              @touchstart="handleResultTouchStart(index, 'dnf')"
              @touchmove="handleResultTouchMove"
              @touchend="handleResultTouchEnd"
              @touchcancel="handleResultTouchCancel"
            >
              <HorseDetailCard
                :snapshot-data="horse.snapshot_data"
                :horse-id="horse.horse_id"
                :jockey="horse.jockey"
                :birth-year="horse.snapshot_data.birth_year"
                :hemisphere="horse.snapshot_data.hemisphere"
                :reference-date="race.date"
                :gate="horse.gate"
                :draggable="true"
                :is-dnf="true"
                :show-delete-button="isJiggleMode"
                :is-jiggling="isJiggleMode"
                @drag-start="handleResultDragStart(index, 'dnf')"
                @drag-end="handleResultDragEnd"
                @refresh="handleRefresh(horse)"
                @delete-click="deleteTarget = { raceHorseId: horse.race_horse_id, name: horse.snapshot_data.name ?? '未知' }; showDeleteConfirm = true"
              />
            </div>
          </div>

        </div>
      </div>

      <p v-if="voteError" class="vote-error">{{ voteError }}</p>

      <VotingDetail
        v-if="resultMode !== 'ranking'"
        :votes="votes"
        :loading="votesLoading"
        :horse-positions="horsePositions"
      />
    </template>

    <!-- Add Horse Modal -->
    <div v-if="showAddHorseModal" class="modal-backdrop">
      <div class="modal-content">
        <h3 class="modal-title">添加马匹</h3>
        <div class="modal-actions">
          <button class="modal-btn modal-confirm" :disabled="addHorseSaving || selectedAddHorse.length === 0" @click="confirmAddHorse">
            {{ addHorseSaving ? '添加中…' : '添加' }}
          </button>
          <button class="modal-btn modal-cancel" @click="closeAddHorseModal">
            取消
          </button>
        </div>
        <HorseSearchSelect v-model:selected-horses="selectedAddHorse" />
        <p v-if="addHorseError" class="modal-error">{{ addHorseError }}</p>
      </div>
    </div>

    <!-- Delete Horse Confirm Modal -->
    <ConfirmDeleteModal
      v-if="showDeleteConfirm && deleteTarget"
      title="从比赛中移除"
      :item-name="deleteTarget.name"
      message="确定将「{name}」从本场比赛中移除？此操作不可撤销。"
      :loading="deleting"
      @confirm="confirmDeleteHorse"
      @cancel="showDeleteConfirm = false"
    />

    <!-- Lock Race Confirm Modal -->
    <ConfirmDeleteModal
      v-if="showLockConfirm && race"
      title="锁定比赛"
      :item-name="race.name"
      message="确定锁定比赛「{name}」？锁定后不可再修改闸位与马匹信息。"
      :loading="locking"
      confirm-text="确认锁定"
      loading-text="锁定中…"
      @confirm="handleLock"
      @cancel="showLockConfirm = false"
    />

    <!-- Delete Race Confirm Modal -->
    <ConfirmDeleteModal
      v-if="showDeleteRaceModal && race"
      title="删除比赛"
      :item-name="race.name"
      message="确定删除比赛「{name}」？此操作不可撤销，所有相关数据将被清除。"
      :loading="deletingRace"
      @confirm="handleDeleteRace"
      @cancel="showDeleteRaceModal = false"
    />
  </div>
</template>

<style scoped>
.race-detail-page {
  padding: var(--spacing-4, 16px);
  max-width: 960px;
  margin: 0 auto;
}

.race-header {
  margin-bottom: var(--spacing-6, 24px);
}

.race-header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-3, 12px);
}

.back-btn {
  background: none;
  border: none;
  color: var(--color-primary, #1A5632);
  font-size: var(--text-body, 16px);
  cursor: pointer;
  padding: 0;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
}

.back-btn:hover {
  opacity: 0.8;
}

/* Jiggle mode toggle button (mobile only) */
.jiggle-toggle-btn {
  display: none;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid var(--color-border-strong, #A8B8A4);
  border-radius: var(--rounded-md, 10px);
  background: var(--color-surface-raised, #FFFFFF);
  color: var(--color-ink-primary, #1A2E1A);
  font-size: var(--text-body, 16px);
  font-weight: 600;
  cursor: pointer;
  min-height: 44px;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}

.jiggle-toggle-btn:hover {
  background: var(--color-surface-base, #F8FAF7);
  border-color: var(--color-primary, #1A5632);
}

.jiggle-toggle-btn.active {
  background: var(--color-primary, #1A5632);
  color: #FFFFFF;
  border-color: var(--color-primary, #1A5632);
}

.jiggle-toggle-btn.active:hover {
  background: var(--color-primary-light, #2D7A4F);
}

@media (max-width: 767px) {
  .jiggle-toggle-btn {
    display: inline-flex;
  }
}

.race-title-row {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-3, 12px);
  row-gap: var(--spacing-2, 8px);
  margin-bottom: var(--spacing-2, 8px);
  flex-wrap: wrap;
}

.title-row-right {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-left: auto;
  flex-shrink: 0;
}

.race-name {
  font-family: var(--font-display, 'Barlow Condensed', system-ui, sans-serif);
  font-size: var(--text-heading, 24px);
  font-weight: 600;
  color: var(--color-ink-primary, #1A2E1A);
  margin: 0;
  line-height: 1.25;
}

/* Eye toggle button */
.eye-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--color-border-hairline, #D4DCD0);
  border-radius: var(--rounded-sm, 6px);
  background: var(--color-surface-raised, #FFFFFF);
  color: var(--color-ink-secondary, #4A5A4A);
  cursor: pointer;
  flex-shrink: 0;
  transition: color 0.15s, border-color 0.15s, background-color 0.15s;
  padding: 0;
}

.eye-btn:hover:not(:disabled) {
  border-color: var(--color-primary, #1A5632);
  color: var(--color-primary, #1A5632);
}

.eye-btn.eye-hidden {
  color: var(--color-destructive, #C53030);
  border-color: var(--color-destructive, #C53030);
  background: #FFF5F5;
}

.eye-btn.eye-hidden:hover:not(:disabled) {
  background: #FED7D7;
}

.eye-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.eye-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-border-hairline, #D4DCD0);
  border-top-color: var(--color-primary, #1A5632);
  border-radius: 50%;
  animation: eye-spin 0.6s linear infinite;
}

@keyframes eye-spin {
  to { transform: rotate(360deg); }
}

.race-subinfo {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-2, 8px);
  align-items: baseline;
}

.race-date {
  font-size: var(--text-body, 16px);
  color: var(--color-ink-secondary, #4A5A4A);
  margin: 0;
}

.date-editable {
  cursor: pointer;
  padding: 2px 6px;
  margin-left: -6px;
  margin-right: -6px;
  border-radius: var(--rounded-sm, 6px);
  transition: background 0.15s;
}

.date-editable:hover {
  background: var(--color-surface-base, #F8FAF7);
}

.date-input {
  padding: 4px 8px;
  border: 1px solid var(--color-border-strong, #A8B8A4);
  border-radius: var(--rounded-sm, 6px);
  font-size: var(--text-body, 16px);
  color: var(--color-ink-primary, #1A2E1A);
  background: var(--color-surface-raised, #FFFFFF);
}

.date-input:focus {
  outline: 2px solid var(--color-primary, #1A5632);
  outline-offset: 2px;
}

.race-meta {
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-secondary, #4A5A4A);
  margin: 0;
}

.race-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.race-tag {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: var(--rounded-sm, 6px);
  font-size: 11px;
  font-weight: 600;
  font-family: 'Barlow Condensed', 'system-ui', sans-serif;
  background: var(--color-surface-base, #F8FAF7);
  color: var(--color-ink-secondary, #4A5A4A);
  border: 1px solid var(--color-border-hairline, #D4DCD0);
}

.header-message {
  font-size: var(--text-body-sm, 14px);
  margin: var(--spacing-2, 8px) 0 0;
  padding: 6px 10px;
  border-radius: var(--rounded-sm, 6px);
}

.header-message.error {
  color: var(--color-destructive, #C53030);
  background: #FED7D7;
}

.header-message.success {
  color: var(--color-primary, #1A5632);
  background: #F0F7F2;
}

.admin-actions-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--spacing-3, 12px);
  margin-bottom: var(--spacing-6, 24px);
}

.admin-btn {
  padding: 10px 24px;
  border-radius: var(--rounded-md, 10px);
  font-size: var(--text-body, 16px);
  font-weight: 600;
  cursor: pointer;
  min-height: 44px;
  border: none;
  transition: background 0.15s, color 0.15s;
}

.admin-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.lock-btn {
  background: var(--color-primary, #1A5632);
  color: #FFFFFF;
}

.lock-btn:hover:not(:disabled) {
  background: var(--color-primary-light, #2D7A4F);
}

.end-race-btn {
  background: var(--color-accent, #B8960C);
  color: #FFFFFF;
}

.end-race-btn:hover {
  background: #a3840a;
}

.modify-result-btn {
  background: transparent;
  color: var(--color-primary, #1A5632);
  border: 1px solid var(--color-primary, #1A5632);
}

.modify-result-btn:hover:not(:disabled) {
  background: var(--color-primary, #1A5632);
  color: #FFFFFF;
}

.delete-btn {
  background: transparent;
  color: var(--color-destructive, #C53030);
  border: 1px solid var(--color-destructive, #C53030);
}

.delete-btn:hover {
  background: var(--color-destructive, #C53030);
  color: #FFFFFF;
}

.admin-error {
  color: var(--color-destructive, #C53030);
  font-size: var(--text-body-sm, 14px);
  margin: 0;
}

.admin-success {
  color: var(--color-primary, #1A5632);
  font-size: var(--text-body-sm, 14px);
  margin: 0;
}

.custom-scoring-info {
  background: var(--color-surface-base, #F8FAF7);
  border-radius: var(--rounded-md, 10px);
  padding: var(--spacing-4, 16px);
  margin-bottom: var(--spacing-6, 24px);
}

.scoring-title {
  font-weight: 600;
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-primary, #1A2E1A);
  margin: 0 0 var(--spacing-2, 8px);
}

.scoring-detail {
  font-size: var(--text-caption, 12px);
  color: var(--color-ink-secondary, #4A5A4A);
  margin: 0;
}

.vote-hint {
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-secondary, #4A5A4A);
  margin-bottom: var(--spacing-4, 16px);
  padding: var(--spacing-3, 12px);
  background: var(--color-surface-base, #F8FAF7);
  border-radius: var(--rounded-md, 10px);
  text-align: center;
}

.vote-hint.voted {
  border: 1px solid var(--color-accent, #B8960C);
  background: #FFFDF0;
  color: var(--color-ink-primary, #1A2E1A);
}

.section-title {
  font-size: var(--text-subheading, 18px);
  font-weight: 600;
  color: var(--color-ink-primary, #1A2E1A);
  margin: 0 0 var(--spacing-4, 16px);
}

.horse-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4, 16px);
  margin-top: var(--spacing-4, 16px);
}

.horse-list-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3, 12px);
  min-height: 80px;
}

.gate-drag-item {
  width: 100%;
  transition: transform 0.15s;
}

.gate-drag-item.drag-over-top {
  position: relative;
}

.gate-drag-item.drag-over-top::before {
  content: '';
  position: absolute;
  top: -6px;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--color-primary, #1A5632);
  border-radius: 2px;
  z-index: 1;
}

/* Add / Delete row */
.add-delete-row {
  display: flex;
  gap: var(--spacing-3, 12px);
}

.add-delete-row > .add-horse-card {
  flex: 1;
  min-width: 0;
}

.delete-zone {
  flex-shrink: 0;
  width: 100px;
  min-height: 96px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2, 8px);
  background: var(--color-surface-raised, #FFFFFF);
  border: 2px dashed var(--color-border-strong, #A8B8A4);
  border-radius: var(--rounded-md, 10px);
  padding: var(--spacing-2, 8px);
  transition: border-color 0.15s, background-color 0.15s;
  cursor: default;
  user-select: none;
}

.delete-zone.delete-hover {
  border-color: var(--color-destructive, #C53030);
  background: #FFF5F5;
}

.delete-icon {
  font-size: 24px;
  font-weight: 300;
  color: var(--color-ink-secondary, #4A5A4A);
  line-height: 1;
}

.delete-zone.delete-hover .delete-icon {
  color: var(--color-destructive, #C53030);
}

.delete-label {
  font-size: var(--text-caption, 12px);
  color: var(--color-ink-secondary, #4A5A4A);
  font-weight: 600;
  text-align: center;
  line-height: 1.3;
}

.delete-zone.delete-hover .delete-label {
  color: var(--color-destructive, #C53030);
}

@media (max-width: 767px) {
  .delete-zone {
    display: none;
  }
}

.voted-horse-locked {
  border-color: var(--color-accent, #B8960C) !important;
}

.vote-error {
  color: var(--color-destructive, #C53030);
  font-size: var(--text-body-sm, 14px);
  margin: var(--spacing-2, 8px) 0;
  text-align: center;
}

.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 40vh;
  text-align: center;
  gap: var(--spacing-4, 16px);
}

.error-text {
  color: var(--color-destructive, #C53030);
  font-size: var(--text-body, 16px);
}

.refresh-btn {
  padding: 10px 24px;
  font-size: var(--text-body, 16px);
  font-weight: 600;
  color: #ffffff;
  background: var(--color-primary, #1A5632);
  border: none;
  border-radius: var(--rounded-md, 10px);
  cursor: pointer;
  min-height: 44px;
}

.refresh-btn:hover {
  background: var(--color-primary-light, #2D7A4F);
}

/* Result ranking mode */
.result-ranking-area {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3, 12px);
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

.drop-zone {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3, 12px);
  min-height: 80px;
}

.result-drag-item {
  display: flex;
  align-items: stretch;
  gap: 8px;
}

.result-drag-item.drag-over-top {
  position: relative;
}

.result-drag-item.drag-over-top::before {
  content: '';
  position: absolute;
  top: -6px;
  left: 0;
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
  margin-bottom: var(--spacing-3, 12px);
}

.dnf-item:last-child {
  margin-bottom: 0;
}

.ranking-actions-bar {
  /* Confirm / cancel buttons in the admin-actions-bar at top;
     buttons inherit admin-btn sizing naturally, side by side on one line */
}

.confirm-result-btn {
  background: var(--color-accent, #B8960C);
  color: #FFFFFF;
  padding: 10px 24px;
}

.confirm-result-btn:hover:not(:disabled) {
  background: #a3840a;
}

.confirm-result-btn:disabled {
  background: #9CA3AF;
}

.cancel-result-btn {
  background: var(--color-surface-raised, #FFFFFF);
  color: var(--color-ink-primary, #1A2E1A);
  border: 1px solid var(--color-border-strong, #A8B8A4);
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: var(--spacing-4, 16px);
}

.modal-content {
  background: var(--color-surface-raised, #FFFFFF);
  border-radius: var(--rounded-md, 10px);
  padding: var(--spacing-6, 24px);
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-title {
  font-size: var(--text-subheading, 18px);
  font-weight: 600;
  margin: 0 0 var(--spacing-4, 16px);
  color: var(--color-ink-primary, #1A2E1A);
}

.modal-error {
  color: var(--color-destructive, #C53030);
  font-size: var(--text-body-sm, 14px);
  margin: var(--spacing-2, 8px) 0 0;
}

.modal-actions {
  display: flex;
  gap: var(--spacing-3, 12px);
  margin-bottom: var(--spacing-3, 12px);
}

.modal-btn {
  flex: 1;
  padding: 10px 20px;
  border-radius: var(--rounded-md, 10px);
  font-size: var(--text-body, 16px);
  font-weight: 600;
  cursor: pointer;
  min-height: 44px;
  border: none;
}

.modal-confirm {
  background: var(--color-primary, #1A5632);
  color: #FFFFFF;
}

.modal-confirm:hover:not(:disabled) {
  background: var(--color-primary-light, #2D7A4F);
}

.modal-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-cancel {
  background: var(--color-surface-base, #F8FAF7);
  color: var(--color-ink-primary, #1A2E1A);
  border: 1px solid var(--color-border-strong, #A8B8A4);
}

@media (max-width: 767px) {
  .race-title-row {
    flex-direction: column;
    align-items: stretch;
  }

  .title-row-right {
    margin-left: 0;
    width: 100%;
  }

  .race-name {
    font-size: var(--text-subheading, 18px);
    white-space: normal;
    word-break: break-word;
  }

  .race-tags {
    width: 100%;
  }

  .ranking-actions-bar {
    flex-wrap: nowrap;
    width: 100%;
  }

  .gate-drag-item,
  .result-drag-item {
    touch-action: manipulation;
  }

  .gate-drag-item.touch-dragging,
  .result-drag-item.touch-dragging {
    touch-action: none;
  }

  .position-badge {
    min-width: 24px;
    font-size: var(--text-caption, 11px);
  }
}

@media (prefers-reduced-motion: reduce) {
  .horse-detail-card,
  .gate-drag-item,
  .result-drag-item {
    transition: none;
  }
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
</style>
