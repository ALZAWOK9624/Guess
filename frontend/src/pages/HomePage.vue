<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import RaceCard from '@/components/RaceCard.vue'
import GradeBadge from '@/components/GradeBadge.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import { getRaces, createRace, toggleRaceHidden } from '@/api/races'
import type { RaceListItem } from '@/types/race'
import type { Grade } from '@/types/race'

type PageState = 'loading' | 'empty' | 'error' | 'success'

const authStore = useAuthStore()
const router = useRouter()
const pageState = ref<PageState>('loading')
const races = ref<RaceListItem[]>([])
const errorMessage = ref('加载失败，请刷新重试')
const refreshing = ref(false)

// Client-side filter: non-admin users should not see hidden races
// This ensures immediate effect when logging out without a re-fetch
const visibleRaces = computed(() => {
  if (authStore.isAdmin) return races.value
  return races.value.filter(r => !r.is_hidden)
})

// Create race modal
const showCreateModal = ref(false)
const createForm = ref({
  name: '',
  date: '',
  grade: 'G1' as Grade,
})
const creating = ref(false)
const createError = ref('')

const gradeOptions: { value: Grade; label: string }[] = [
  { value: 'G1', label: 'G1' },
  { value: 'G2_JPN1', label: 'G2·JPN1' },
  { value: 'YOUNG_G1', label: '2岁G1' },
  { value: 'CUSTOM', label: '自定义' },
]

// Toggle hidden state
const togglingHiddenId = ref<number | null>(null)

async function handleToggleHidden(raceId: number) {
  if (togglingHiddenId.value !== null) return
  togglingHiddenId.value = raceId
  try {
    const result = await toggleRaceHidden(raceId)
    const race = races.value.find(r => r.id === raceId)
    if (race) race.is_hidden = result.is_hidden
  } catch {
    // silently fail
  } finally {
    togglingHiddenId.value = null
  }
}

async function loadData() {
  pageState.value = 'loading'
  errorMessage.value = '加载失败，请刷新重试'

  try {
    const data = await getRaces()
    races.value = data
    if (data.length === 0) {
      pageState.value = 'empty'
    } else {
      pageState.value = 'success'
    }
  } catch {
    pageState.value = 'error'
  }
}

async function handleRefresh() {
  refreshing.value = true
  await loadData()
  refreshing.value = false
}

function goToRaceDetail(raceId: number) {
  router.push(`/races/${raceId}`)
}

function openCreateModal() {
  createForm.value = { name: '', date: '', grade: 'G1' }
  createError.value = ''
  showCreateModal.value = true
}

function closeCreateModal() {
  showCreateModal.value = false
}

async function handleCreateRace() {
  if (!createForm.value.name.trim() || !createForm.value.date || creating.value) return
  creating.value = true
  createError.value = ''
  try {
    const data = await createRace({
      name: createForm.value.name.trim(),
      date: createForm.value.date,
      grade: createForm.value.grade,
      horse_ids: [],
    })
    closeCreateModal()
    router.push(`/races/${data.id}`)
  } catch (err: any) {
    createError.value = err?.response?.data?.detail?.message || '创建失败'
  } finally {
    creating.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <div class="home-page">
    <!-- Skeleton loading -->
    <template v-if="pageState === 'loading'">
      <div class="race-list" role="status" aria-live="polite" aria-label="加载中">
        <RaceCard v-for="i in 4" :key="i" skeleton />
      </div>
    </template>

    <!-- Empty state -->
    <template v-else-if="pageState === 'empty'">
      <div class="state-container" role="status" aria-live="polite">
        <p v-if="authStore.isLoggedIn" class="empty-text">
          还没有比赛。管理员正在筹备中——
        </p>
        <p v-else class="empty-text">
          还没有比赛。
        </p>
      </div>
    </template>

    <!-- Error state -->
    <template v-else-if="pageState === 'error'">
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

    <!-- Race list -->
    <template v-else>
      <div class="race-list">
        <div
          v-for="race in visibleRaces"
          :key="race.id"
          class="race-card-wrapper"
          :class="{ 'race-hidden': race.is_hidden }"
          @click="goToRaceDetail(race.id)"
        >
          <div class="race-card">
            <div class="card-header">
              <GradeBadge :grade="race.grade as any" />
              <h2 class="race-name">{{ race.name }}</h2>
              <StatusBadge :status="race.status as any" />
              <span
                v-if="race.status === 'voting' && authStore.isLoggedIn && !authStore.isAdmin"
                class="vote-status"
                :class="{ voted: race.has_voted }"
              >
                {{ race.has_voted ? '已投票' : '未投票' }}
              </span>
              <button
                v-if="authStore.isAdmin"
                class="eye-btn"
                :class="{ 'eye-hidden': race.is_hidden }"
                :disabled="togglingHiddenId === race.id"
                :title="race.is_hidden ? '已隐藏，点击取消隐藏' : '点击隐藏比赛'"
                :aria-label="race.is_hidden ? '取消隐藏' : '隐藏'"
                @click.stop="handleToggleHidden(race.id)"
              >
                <span v-if="togglingHiddenId === race.id" class="eye-spinner"></span>
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
            <div class="card-body">
              <span class="race-date">{{ race.date }}</span>
              <span class="race-meta">
                {{ race.horse_count }} 匹参赛 · {{ race.vote_count }} 人已投
              </span>
            </div>
          </div>
        </div>
      </div>

      <button
        v-if="authStore.isAdmin"
        class="create-race-fab"
        type="button"
        aria-label="创建比赛"
        @click="openCreateModal"
      >
        + 创建比赛
      </button>
    </template>

    <!-- Create race modal -->
    <div v-if="showCreateModal" class="modal-backdrop" @click.self="closeCreateModal">
      <div class="modal-content">
        <h3 class="modal-title">创建比赛</h3>
        <div class="form-group">
          <label for="race-name">比赛名称</label>
          <input
            id="race-name"
            v-model="createForm.name"
            type="text"
            placeholder="输入比赛名称"
          />
        </div>
        <div class="form-group">
          <label for="race-date">比赛日期</label>
          <input id="race-date" v-model="createForm.date" type="date" :class="{ 'is-empty': !createForm.date }" />
        </div>
        <div class="form-group">
          <label>比赛等级</label>
          <div class="grade-options">
            <label
              v-for="option in gradeOptions"
              :key="option.value"
              class="grade-option"
              :class="{ active: createForm.grade === option.value }"
            >
              <input
                v-model="createForm.grade"
                type="radio"
                :value="option.value"
              />
              <span>{{ option.label }}</span>
            </label>
          </div>
        </div>
        <p v-if="createError" class="modal-error">{{ createError }}</p>
        <div class="modal-actions">
          <button
            class="modal-btn modal-confirm"
            :disabled="creating || !createForm.name.trim() || !createForm.date"
            @click="handleCreateRace"
          >
            {{ creating ? '创建中…' : '创建' }}
          </button>
          <button class="modal-btn modal-cancel" @click="closeCreateModal">
            取消
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-page {
  padding: var(--spacing-4, 16px);
  max-width: 1280px;
  margin: 0 auto;
  padding-bottom: calc(var(--spacing-4, 16px) + env(safe-area-inset-bottom, 0px));
}

.race-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4, 16px);
}

.race-card-wrapper {
  cursor: pointer;
}

.race-card {
  background: var(--color-surface-raised, #FFFFFF);
  border: 1px solid var(--color-border-hairline, #D4DCD0);
  border-radius: var(--rounded-md, 10px);
  padding: var(--spacing-5, 20px);
  transition: box-shadow 0.15s;
}

.race-card:hover {
  box-shadow: 0 2px 8px rgba(26, 86, 50, 0.08);
}

.card-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-3, 12px);
  margin-bottom: var(--spacing-3, 12px);
}

.race-name {
  font-size: var(--text-subheading, 18px);
  font-weight: 600;
  color: var(--color-ink-primary, #1A2E1A);
  margin: 0;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.vote-status {
  font-size: var(--text-caption, 12px);
  font-weight: 600;
  padding: 4px 12px;
  border-radius: var(--rounded-sm, 6px);
  white-space: nowrap;
  color: var(--color-ink-secondary, #4A5A4A);
  background: var(--color-surface-base, #F8FAF7);
  border: 1px solid var(--color-border-hairline, #D4DCD0);
}

.vote-status.voted {
  color: var(--color-primary, #1A5632);
  background: #EDF5EF;
  border-color: var(--color-primary, #1A5632);
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

.race-hidden .race-card {
  opacity: 0.5;
}

.card-body {
  display: flex;
  align-items: center;
  gap: var(--spacing-4, 16px);
}

.race-date {
  font-size: var(--text-caption, 12px);
  color: var(--color-ink-secondary, #4A5A4A);
  font-family: 'Barlow Condensed', system-ui, sans-serif;
}

.race-meta {
  font-size: var(--text-caption, 12px);
  color: var(--color-ink-secondary, #4A5A4A);
}

.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  text-align: center;
  gap: var(--spacing-4, 16px);
}

.empty-text {
  color: var(--color-ink-secondary);
  font-size: var(--text-body, 16px);
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

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (prefers-reduced-motion: reduce) {
  .race-card,
  .refresh-btn,
  .create-race-fab {
    transition: none;
  }
}

.create-race-fab {
  position: fixed;
  right: var(--spacing-4, 16px);
  bottom: calc(var(--spacing-4, 16px) + env(safe-area-inset-bottom, 0px));
  padding: 14px 24px;
  background: var(--color-primary, #1A5632);
  color: #FFFFFF;
  border: none;
  border-radius: var(--rounded-md, 10px);
  font-size: var(--text-body, 16px);
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(26, 86, 50, 0.25);
  min-height: 52px;
  z-index: 50;
}

.create-race-fab:hover {
  background: var(--color-primary-light, #2D7A4F);
}

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

.form-group {
  margin-bottom: var(--spacing-4, 16px);
}

.form-group label {
  display: block;
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-secondary, #4A5A4A);
  margin-bottom: var(--spacing-2, 8px);
  font-weight: 600;
}

.form-group input[type="text"],
.form-group input[type="date"] {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border-strong, #A8B8A4);
  border-radius: var(--rounded-sm, 6px);
  font-size: var(--text-body, 16px);
  color: var(--color-ink-primary, #1A2E1A);
  background: var(--color-surface-raised, #FFFFFF);
}

.form-group input:focus {
  outline: 2px solid var(--color-primary, #1A5632);
  outline-offset: 2px;
}

.grade-options {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-2, 8px);
}

.grade-option {
  flex: 1;
  min-width: 80px;
  padding: 10px 12px;
  border: 1px solid var(--color-border-strong, #A8B8A4);
  border-radius: var(--rounded-sm, 6px);
  text-align: center;
  cursor: pointer;
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-primary, #1A2E1A);
  background: var(--color-surface-raised, #FFFFFF);
  transition: border-color 0.15s, background-color 0.15s;
}

.grade-option.active {
  border-color: var(--color-primary, #1A5632);
  background: #F0F7F2;
  color: var(--color-primary, #1A5632);
  font-weight: 600;
}

.grade-option input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.modal-error {
  color: var(--color-destructive, #C53030);
  font-size: var(--text-body-sm, 14px);
  margin: 0 0 var(--spacing-3, 12px);
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
  .create-race-fab {
    left: var(--spacing-4, 16px);
    right: var(--spacing-4, 16px);
    width: auto;
  }

  .modal-actions {
    flex-direction: column;
  }
}

</style>
