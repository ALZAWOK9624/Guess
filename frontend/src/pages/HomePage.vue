<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import RaceCard from '@/components/RaceCard.vue'
import GradeBadge from '@/components/GradeBadge.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import { getRaces } from '@/api/races'
import type { RaceListItem } from '@/types/race'

type PageState = 'loading' | 'empty' | 'error' | 'success'

const authStore = useAuthStore()
const router = useRouter()
const pageState = ref<PageState>('loading')
const races = ref<RaceListItem[]>([])
const errorMessage = ref('加载失败，请刷新重试')
const refreshing = ref(false)

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
          v-for="race in races"
          :key="race.id"
          class="race-card-wrapper"
          @click="goToRaceDetail(race.id)"
        >
          <div class="race-card">
            <div class="card-header">
              <GradeBadge :grade="race.grade as any" />
              <h2 class="race-name">{{ race.name }}</h2>
              <StatusBadge :status="race.status as any" />
              <span
                v-if="race.status === 'voting'"
                class="vote-entry"
                @click.stop="goToRaceDetail(race.id)"
                aria-label="前往投票"
              >
                投票
              </span>
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
    </template>
  </div>
</template>

<style scoped>
.home-page {
  padding: var(--spacing-4, 16px);
  max-width: 1280px;
  margin: 0 auto;
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

.vote-entry {
  background: var(--color-accent, #B8960C);
  color: #FFFFFF;
  padding: 4px 12px;
  border-radius: var(--rounded-sm, 6px);
  font-size: var(--text-caption, 12px);
  font-weight: 700;
  white-space: nowrap;
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
  .refresh-btn {
    transition: none;
  }
}
</style>
