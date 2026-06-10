<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

type PageState = 'loading' | 'empty' | 'error' | 'success'

const router = useRouter()
const pageState = ref<PageState>('loading')
const errorMessage = ref('加载失败，请刷新重试')
const refreshing = ref(false)

async function loadData() {
  pageState.value = 'loading'
  errorMessage.value = '加载失败，请刷新重试'

  try {
    // Placeholder for future story — replace with actual API call
    // const data = await getLeaderboard()
    // if (data.length === 0) {
    //   pageState.value = 'empty'
    // } else {
    //   pageState.value = 'success'
    // }
    // Temporary: simulate empty state for now
    pageState.value = 'empty'
  } catch {
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
    <!-- Skeleton loading -->
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

    <!-- Content (placeholder for future stories) -->
    <template v-else>
      <div class="leaderboard-container">
        <p>排行榜内容将在 Story 3.5 中实现</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
.leaderboard-page {
  padding: var(--spacing-16);
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
  gap: var(--spacing-8);
  min-width: 320px;
}

.skeleton-header-row,
.skeleton-row {
  display: flex;
  gap: var(--spacing-12);
  padding: var(--spacing-12) var(--spacing-8);
  border-bottom: 1px solid var(--color-border-hairline);
}

.skeleton-header-row {
  border-bottom: 2px solid var(--color-border-hairline);
}

.skeleton-block {
  background: linear-gradient(
    90deg,
    var(--color-surface-base) 25%,
    var(--color-border-hairline) 50%,
    var(--color-surface-base) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
  border-radius: var(--rounded-sm);
  height: 16px;
}

.col-rank {
  width: 40px;
  flex-shrink: 0;
}

.col-name {
  flex: 1;
  max-width: 120px;
}

.col-points {
  width: 60px;
  flex-shrink: 0;
}

.col-races {
  width: 50px;
  flex-shrink: 0;
}

.col-avg {
  width: 50px;
  flex-shrink: 0;
}

/* State patterns */
.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  text-align: center;
  gap: var(--spacing-16);
}

.empty-text {
  color: var(--color-ink-secondary);
  font-size: var(--text-body);
}

.error-text {
  color: var(--color-destructive);
  font-size: var(--text-body);
}

.home-link {
  color: var(--color-primary);
  font-weight: 600;
  font-size: var(--text-body);
  text-decoration: underline;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
}

.refresh-btn {
  padding: 10px 24px;
  font-size: var(--text-body);
  font-weight: 600;
  color: #ffffff;
  background: var(--color-primary);
  border: none;
  border-radius: var(--rounded-md);
  cursor: pointer;
  min-height: 44px;
  transition: background 0.2s;
}

.refresh-btn:hover {
  background: var(--color-primary-light);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (prefers-reduced-motion: reduce) {
  .skeleton-block {
    animation: none;
    background: var(--color-surface-base);
  }
  .refresh-btn {
    transition: none;
  }
}
</style>
