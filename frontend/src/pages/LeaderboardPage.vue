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
      <div class="leaderboard-container" role="status" aria-live="polite" aria-label="加载中">
        <div class="skeleton-table">
          <div class="skeleton-header-row">
            <div class="skeleton-block col-rank"></div>
            <div class="skeleton-block col-name"></div>
            <div class="skeleton-block col-points"></div>
            <div class="skeleton-block col-races"></div>
            <div class="skeleton-block col-avg"></div>
          </div>
          <div v-for="i in 5" :key="i" class="skeleton-row">
            <div class="skeleton-block col-rank"></div>
            <div class="skeleton-block col-name"></div>
            <div class="skeleton-block col-points"></div>
            <div class="skeleton-block col-races"></div>
            <div class="skeleton-block col-avg"></div>
          </div>
        </div>
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
      <div class="leaderboard-container">
        <div class="leaderboard-table" role="table" aria-label="排行榜">
          <div class="leaderboard-header" role="row">
            <span class="col-rank" role="columnheader">排名</span>
            <span class="col-name" role="columnheader">用户名</span>
            <span class="col-points" role="columnheader">积分</span>
            <span class="col-races" role="columnheader">场数</span>
            <span class="col-avg" role="columnheader">场均</span>
          </div>
          <LeaderboardRow
            v-for="(entry, index) in leaderboard"
            :key="entry.username"
            :entry="entry"
            :rank="index + 1"
            :is-current-user="entry.username === authStore.user?.username"
          />
        </div>
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

.leaderboard-container {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

/* Skeleton table */
.skeleton-table {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-8, 8px);
  min-width: 320px;
}

.skeleton-header-row,
.skeleton-row {
  display: flex;
  gap: var(--spacing-12, 12px);
  padding: var(--spacing-12, 12px) var(--spacing-8, 8px);
  border-bottom: 1px solid var(--color-border-hairline, #D4DCD0);
}

.skeleton-header-row {
  border-bottom: 2px solid var(--color-border-hairline, #D4DCD0);
}

.skeleton-block {
  background: linear-gradient(
    90deg,
    var(--color-surface-base, #F8FAF7) 25%,
    var(--color-border-hairline, #D4DCD0) 50%,
    var(--color-surface-base, #F8FAF7) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
  border-radius: var(--rounded-sm, 6px);
  height: 16px;
}

.col-rank { width: 40px; flex-shrink: 0; }
.col-name { flex: 1; max-width: 120px; }
.col-points { width: 60px; flex-shrink: 0; }
.col-races { width: 50px; flex-shrink: 0; }
.col-avg { width: 50px; flex-shrink: 0; }

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

/* Leaderboard table */
.leaderboard-table {
  min-width: 320px;
  background: var(--color-surface-raised, #FFFFFF);
  border-radius: var(--rounded-md, 10px);
  overflow: hidden;
}

.leaderboard-header {
  display: flex;
  gap: var(--spacing-12, 12px);
  padding: var(--spacing-3, 12px) var(--spacing-4, 16px);
  border-bottom: 2px solid var(--color-border-hairline, #D4DCD0);
  font-size: var(--text-body-sm, 14px);
  font-weight: 600;
  color: var(--color-ink-secondary, #4A5A4A);
  position: sticky;
  top: 0;
  background: var(--color-surface-raised, #FFFFFF);
  z-index: 1;
}

.updated-hint {
  text-align: center;
  font-size: var(--text-caption, 12px);
  color: var(--color-ink-secondary, #4A5A4A);
  margin-top: var(--spacing-8, 8px);
}

@media (prefers-reduced-motion: reduce) {
  .skeleton-block {
    animation: none;
    background: var(--color-surface-base, #F8FAF7);
  }
  .refresh-btn {
    transition: none;
  }
}
</style>
