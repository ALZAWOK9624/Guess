<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { getLeaderboard } from '@/api/leaderboard'
import type { LeaderboardEntry } from '@/types/leaderboard'
import LeaderboardRow from '@/components/LeaderboardRow.vue'

type PageState = 'loading' | 'empty' | 'error' | 'success'

const authStore = useAuthStore()
const pageState = ref<PageState>('loading')
const leaderboard = ref<LeaderboardEntry[]>([])
const errorMessage = ref('加载失败，请刷新重试')
const refreshing = ref(false)

async function loadData() {
  pageState.value = 'loading'
  errorMessage.value = '加载失败，请刷新重试'

  try {
    const data = await getLeaderboard()
    leaderboard.value = data
    // Check if any user has points — empty means no settled races with votes
    const hasActivity = data.length > 0 && data.some(e => e.races_participated > 0)
    if (hasActivity) {
      pageState.value = 'success'
    } else {
      pageState.value = 'empty'
    }
  } catch (err) {
    console.error('Leaderboard load failed:', err)
    pageState.value = 'error'
  }
}

async function handleRefresh() {
  refreshing.value = true
  await loadData()
  refreshing.value = false
}

onMounted(loadData)
</script>

<template>
  <div class="leaderboard-page">
    <!-- Loading skeleton -->
    <template v-if="pageState === 'loading'">
      <div class="skeleton-container" role="status" aria-live="polite" aria-label="加载中">
        <div v-for="i in 5" :key="i" class="skeleton-row"></div>
      </div>
    </template>

    <!-- Empty state -->
    <template v-else-if="pageState === 'empty'">
      <div class="state-container" role="status" aria-live="polite">
        <p class="empty-text">还没有人参与竞猜——成为第一个！</p>
        <router-link to="/" class="home-link">去首页看看</router-link>
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

    <!-- Leaderboard data -->
    <template v-else>
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th scope="col" class="col-rank">排名</th>
              <th scope="col" class="col-name">用户名</th>
              <th scope="col" class="col-points">积分</th>
              <th scope="col" class="col-races">场数</th>
              <th scope="col" class="col-avg">场均</th>
            </tr>
          </thead>
          <tbody>
            <LeaderboardRow
              v-for="(entry, index) in leaderboard"
              :key="entry.username"
              :entry="entry"
              :rank="index + 1"
              :is-current-user="entry.username === authStore.user?.username"
            />
          </tbody>
        </table>
      </div>
      <p class="updated-hint">积分在每次比赛结算后自动更新</p>
    </template>
  </div>
</template>

<style scoped>
.leaderboard-page {
  padding: var(--spacing-16, 16px);
  max-width: 1280px;
  margin: 0 auto;
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
  min-height: 50vh;
  text-align: center;
  gap: var(--spacing-16, 16px);
}

.empty-text {
  color: var(--color-ink-secondary, #4A5A4A);
  font-size: var(--text-body, 16px);
}

.error-text {
  color: var(--color-destructive, #C53030);
  font-size: var(--text-body, 16px);
}

.home-link {
  color: var(--color-primary, #1A5632);
  font-weight: 600;
  font-size: var(--text-body, 16px);
  text-decoration: underline;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
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
  transition: background 0.2s;
}

.refresh-btn:hover {
  background: var(--color-primary-light, #2D7A4F);
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

thead tr {
  border-bottom: 2px solid var(--color-border-hairline, #D4DCD0);
}

th {
  padding: var(--spacing-3, 12px) var(--spacing-2, 8px);
  font-weight: 600;
  color: var(--color-ink-secondary, #4A5A4A);
  white-space: nowrap;
  text-align: left;
}

th.col-rank { text-align: center; }
th.col-points { text-align: right; }
th.col-races { text-align: center; }
th.col-avg { text-align: right; }

.updated-hint {
  text-align: center;
  font-size: var(--text-caption, 12px);
  color: var(--color-ink-secondary, #4A5A4A);
  margin-top: var(--spacing-8, 8px);
}

@media (prefers-reduced-motion: reduce) {
  .skeleton-row {
    animation: none;
    background: var(--color-surface-base);
  }
  .refresh-btn {
    transition: none;
  }
}
</style>
