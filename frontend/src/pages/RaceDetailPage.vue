<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import GradeBadge from '@/components/GradeBadge.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import HorseDetailCard from '@/components/HorseDetailCard.vue'
import AddHorseCard from '@/components/AddHorseCard.vue'
import RaceHeaderEditor from '@/components/RaceHeaderEditor.vue'
import VotingDetail from '@/components/VotingDetail.vue'
import HorseSearchSelect from '@/components/HorseSearchSelect.vue'

import {
  getRace,
  updateRace,
  addRaceHorse,
  updateRaceHorse,
  updateGateOrder,
  lockRace,
} from '@/api/races'
import { submitResults } from '@/api/results'
import { updateBestWin } from '@/api/horses'
import { useVote } from '@/composables/useVote'
import { useDragSort } from '@/composables/useDragSort'
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

const {
  votedHorseName,
  votedRaceHorseId,
  isSubmitting,
  votes,
  votesLoading,
  errorMessage: voteError,
  toggleVote,
  loadVotes,
} = useVote(null)

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

const isAdmin = computed(() => authStore.isAdmin)

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

async function handleLock() {
  if (!race.value || !isAdmin.value || !isRaceVoting.value || locking.value) return
  locking.value = true
  lockError.value = ''
  try {
    await lockRace(raceId)
    race.value = await getRace(raceId)
    await loadVotes(raceId)
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

// Update horse jockey
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

// Mobile touch gate drag
const gateTouchIndex = ref(-1)
let gateLongPressTimer: ReturnType<typeof setTimeout> | null = null

function handleGateTouchStart(_event: TouchEvent, index: number) {
  if (gateLongPressTimer) clearTimeout(gateLongPressTimer)
  gateLongPressTimer = setTimeout(() => {
    gateTouchIndex.value = index
    gateDragSort.value?.startDrag(index)
    document.body.style.overflow = 'hidden'
  }, 300)
}

function handleGateTouchMove(event: TouchEvent) {
  if (gateTouchIndex.value < 0) {
    if (gateLongPressTimer) {
      clearTimeout(gateLongPressTimer)
      gateLongPressTimer = null
    }
    return
  }
  event.preventDefault()

  const cards = document.querySelectorAll('.gate-drag-item')
  const touchY = event.touches[0].clientY
  for (let i = 0; i < cards.length; i++) {
    const rect = cards[i].getBoundingClientRect()
    if (touchY >= rect.top && touchY <= rect.bottom) {
      if (i !== gateTouchIndex.value && gateDragSort.value) {
        const item = gateDragSort.value.activeList.value.splice(gateTouchIndex.value, 1)[0]
        if (item) {
          gateDragSort.value.activeList.value.splice(i, 0, item)
          gateTouchIndex.value = i
          gateDragOverIndex.value = i
        }
      }
      break
    }
  }
}

function handleGateTouchEnd() {
  if (gateLongPressTimer) {
    clearTimeout(gateLongPressTimer)
    gateLongPressTimer = null
  }
  if (gateTouchIndex.value >= 0) {
    submitGateOrder()
  }
  gateTouchIndex.value = -1
  gateDragOverIndex.value = -1
  document.body.style.overflow = ''
  gateDragSort.value?.endDrag()
}

// Result ranking mode
const resultMode = ref<ResultMode>('idle')
const existingPositions = ref<Map<number, number> | undefined>(undefined)
let resultDragSort: ReturnType<typeof useDragSort> | null = null
const resultDragOverIndex = ref(-1)
const resultSubmitting = ref(false)
const resultSubmitError = ref('')

const resultActiveList = computed(() => resultDragSort?.activeList.value ?? [])
const resultDnfList = computed(() => resultDragSort?.dnfList.value ?? [])
const isResultDragging = computed(() => resultDragSort?.isDragging.value ?? false)
const resultDragSource = ref<'active' | 'dnf'>('active')

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
  resultDragSort = useDragSort([...race.value.horses], existingPositions.value, { mode: 'result' })
}

function enterResultMode() {
  if (!isAdmin.value || (!isRaceLocked.value && !isRaceSettled.value)) return
  resultMode.value = 'ranking'
  resultSubmitError.value = ''
  initResultDragSort()
}

function exitResultMode() {
  resultMode.value = 'idle'
  resultDragSort = null
}

function handleResultDragStart(index: number, source: 'active' | 'dnf' = 'active') {
  resultDragSort?.startDrag(index)
  resultDragSource.value = source
  resultDragOverIndex.value = -1
}

function handleResultDrop(event: DragEvent) {
  event.preventDefault()
  if (!resultDragSort || resultDragSort.draggedIndex.value < 0) return

  if (resultDragSource.value === 'dnf') {
    resultDragSort.moveToActive(resultDragSort.draggedIndex.value)
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
    resultDragSort.commitReorder(resultDragSort.draggedIndex.value, targetIndex)
  }
  resultDragOverIndex.value = -1
}

function handleResultDragEnd() {
  resultDragSort?.endDrag()
  resultDragOverIndex.value = -1
}

function handleDnfDrop(event: DragEvent) {
  event.preventDefault()
  if (resultDragSort && resultDragSort.draggedIndex.value >= 0 && resultDragSource.value === 'active') {
    resultDragSort.moveToDnf(resultDragSort.draggedIndex.value)
  }
  resultDragSort?.endDrag()
  resultDragOverIndex.value = -1
}

function handleDnfClick(index: number) {
  resultDragSort?.moveToActive(index)
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
    race.value = await getRace(raceId)
    if (race.value.status === 'settled') {
      await loadVotes(raceId)
      checkUserVote()
    }
    exitResultMode()
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
  try {
    race.value = await getRace(raceId)
    pageState.value = 'success'
    if (race.value.status === 'voting' || race.value.status === 'locked') {
      await loadVotes(raceId)
      checkUserVote()
    }
  } catch {
    pageState.value = 'error'
  }
}

onMounted(loadRace)

onUnmounted(() => {
  if (gateLongPressTimer) clearTimeout(gateLongPressTimer)
})
</script>

<template>
  <div class="race-detail-page">
    <!-- Loading -->
    <div v-if="pageState === 'loading'" class="state-container">
      <p>加载中…</p>
    </div>

    <!-- Error -->
    <div v-else-if="pageState === 'error'" class="state-container">
      <p class="error-text">{{ errorMessage }}</p>
      <button
        class="refresh-btn"
        @click="router.go(0)"
      >
        刷新重试
      </button>
    </div>

    <!-- Race Detail -->
    <template v-else-if="race">
      <div class="race-header">
        <button class="back-btn" @click="router.push('/')" aria-label="返回首页">
          ← 返回
        </button>

        <div class="race-title-row">
          <GradeBadge :grade="race.grade as any" />
          <RaceHeaderEditor
            v-if="isAdmin && isRaceVoting"
            :name="race.name"
            :date="race.date"
            @save="handleHeaderSave"
          />
          <template v-else>
            <h1 class="race-name">{{ race.name }}</h1>
          </template>
          <StatusBadge :status="race.status as any" />
        </div>

        <p v-if="!(isAdmin && isRaceVoting)" class="race-date">{{ race.date }}</p>
        <p class="race-meta">{{ race.horses.length }} 匹参赛 · {{ race.vote_count }} 人已投</p>

        <p v-if="headerSaveError" class="header-message error">{{ headerSaveError }}</p>
        <p v-if="headerSaveSuccess" class="header-message success">保存成功</p>
      </div>

      <!-- Admin actions for voting state -->
      <div v-if="isAdmin && isRaceVoting" class="admin-actions-bar">
        <button
          class="admin-btn lock-btn"
          :disabled="locking"
          @click="handleLock"
        >
          {{ locking ? '锁定中…' : '锁定' }}
        </button>
        <p v-if="lockError" class="admin-error">{{ lockError }}</p>
      </div>

      <!-- Admin result mode entry -->
      <div v-if="isAdmin && isRaceLocked && resultMode === 'idle'" class="admin-actions-bar">
        <button class="admin-btn end-race-btn" @click="enterResultMode">
          比赛结束
        </button>
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
          <div
            v-for="(horse, index) in displayHorses"
            :key="horse.race_horse_id"
            class="gate-drag-item"
            :class="{ 'drag-over-top': gateDragOverIndex === index && isGateDragging }"
            @touchstart="(e: TouchEvent) => handleGateTouchStart(e, index)"
            @touchmove="handleGateTouchMove"
            @touchend="handleGateTouchEnd"
          >
            <HorseDetailCard
              :snapshot-data="horse.snapshot_data"
              :horse-id="horse.horse_id"
              :jockey="horse.jockey"
              :birth-year="horse.snapshot_data.birth_year ?? horse.snapshot_data.age"
              :hemisphere="horse.snapshot_data.hemisphere"
              :reference-date="race.date"
              :votable="cardsVotable"
              :voted="isHorseVoted(horse.race_horse_id)"
              :submitting="isSubmitting"
              :gate="horse.gate"
              :position="isRaceSettled ? (horse.position ?? null) : null"
              :editable="isAdmin && isRaceVoting"
              :draggable="isAdmin && isRaceVoting"
              :class="{ 'voted-horse-locked': (isRaceLocked || isRaceSettled) && votedHorseName && horse.snapshot_data.name === votedHorseName }"
              @vote-toggle="handleCardClick(horse)"
              @update-field="(payload) => handleUpdateJockey(horse, payload.value)"
              @drag-start="handleGateDragStart(index)"
              @drag-end="handleGateDragEnd"
            />
          </div>
          <AddHorseCard
            v-if="isAdmin && isRaceVoting"
            @click="openAddHorseModal"
          />
        </div>

        <!-- Result ranking mode -->
        <div v-else class="result-ranking-area">
          <div class="instructions">
            拖拽马匹卡片调整名次顺序。<span class="text-muted">第1名在顶部，弃权马匹拖入下方 DNF 区。</span>
          </div>

          <div class="drop-zone" @dragover.prevent @drop="handleResultDrop">
            <div
              v-for="(horse, index) in resultActiveList"
              :key="horse.race_horse_id"
              class="result-drag-item"
              :class="{ 'drag-over-top': resultDragOverIndex === index && isResultDragging }"
            >
              <HorseDetailCard
                :snapshot-data="horse.snapshot_data"
                :horse-id="horse.horse_id"
                :jockey="horse.jockey"
                :birth-year="horse.snapshot_data.birth_year ?? horse.snapshot_data.age"
                :hemisphere="horse.snapshot_data.hemisphere"
                :reference-date="race.date"
                :gate="horse.gate"
                :position="index + 1"
                :draggable="true"
                :is-dnf="false"
                @drag-start="handleResultDragStart(index, 'active')"
                @drag-end="handleResultDragEnd"
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
              :key="horse.race_horse_id"
              class="dnf-item"
              @click="handleDnfClick(index)"
            >
              <HorseDetailCard
                :snapshot-data="horse.snapshot_data"
                :horse-id="horse.horse_id"
                :jockey="horse.jockey"
                :birth-year="horse.snapshot_data.birth_year ?? horse.snapshot_data.age"
                :hemisphere="horse.snapshot_data.hemisphere"
                :reference-date="race.date"
                :gate="horse.gate"
                :draggable="true"
                :is-dnf="true"
                @drag-start="handleResultDragStart(index, 'dnf')"
                @drag-end="handleResultDragEnd"
              />
            </div>
          </div>

          <p v-if="resultSubmitError" class="submit-error" role="alert">{{ resultSubmitError }}</p>

          <div class="result-actions">
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
          </div>
        </div>
      </div>

      <p v-if="voteError" class="vote-error">{{ voteError }}</p>

      <VotingDetail
        v-if="(isRaceVoting || isRaceLocked) && resultMode !== 'ranking'"
        :votes="votes"
        :loading="votesLoading"
      />
    </template>

    <!-- Add Horse Modal -->
    <div v-if="showAddHorseModal" class="modal-backdrop" @click.self="closeAddHorseModal">
      <div class="modal-content">
        <h3 class="modal-title">添加马匹</h3>
        <HorseSearchSelect v-model:selected-horses="selectedAddHorse" />
        <p v-if="addHorseError" class="modal-error">{{ addHorseError }}</p>
        <div class="modal-actions">
          <button class="modal-btn modal-confirm" :disabled="addHorseSaving || selectedAddHorse.length === 0" @click="confirmAddHorse">
            {{ addHorseSaving ? '添加中…' : '添加' }}
          </button>
          <button class="modal-btn modal-cancel" @click="closeAddHorseModal">
            取消
          </button>
        </div>
      </div>
    </div>
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

.back-btn {
  background: none;
  border: none;
  color: var(--color-primary, #1A5632);
  font-size: var(--text-body, 16px);
  cursor: pointer;
  padding: 0;
  margin-bottom: var(--spacing-3, 12px);
  min-height: 44px;
  display: inline-flex;
  align-items: center;
}

.race-title-row {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-3, 12px);
  margin-bottom: var(--spacing-2, 8px);
  flex-wrap: wrap;
}

.race-name {
  font-family: var(--font-display, 'Barlow Condensed', system-ui, sans-serif);
  font-size: var(--text-heading, 24px);
  font-weight: 600;
  color: var(--color-ink-primary, #1A2E1A);
  margin: 0;
}

.race-date {
  font-size: var(--text-body, 16px);
  color: var(--color-ink-secondary, #4A5A4A);
  margin: 0 0 var(--spacing-1, 4px);
}

.race-meta {
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-secondary, #4A5A4A);
  margin: 0;
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
  gap: var(--spacing-4, 16px);
  min-height: 80px;
}

.gate-drag-item {
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

.drop-zone {
  display: flex;
  flex-direction: column;
  gap: 8px;
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

.submit-error {
  font-size: var(--text-body-sm, 14px);
  color: var(--color-destructive, #C53030);
  padding: 10px 12px;
  background: #FED7D7;
  border-radius: var(--rounded-md, 10px);
  margin-top: var(--spacing-3, 12px);
}

.result-actions {
  display: flex;
  gap: var(--spacing-3, 12px);
  margin-top: var(--spacing-6, 24px);
}

.confirm-result-btn {
  flex: 1;
  background: var(--color-accent, #B8960C);
  color: #FFFFFF;
  font-size: var(--text-subheading, 18px);
  padding: 14px 24px;
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
  max-width: 480px;
  max-height: 80vh;
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
  margin-top: var(--spacing-4, 16px);
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
    align-items: flex-start;
  }

  .result-actions {
    flex-direction: column;
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
</style>
