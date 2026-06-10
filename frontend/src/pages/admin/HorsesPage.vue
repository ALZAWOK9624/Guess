<script setup lang="ts">
import { ref, onMounted } from 'vue'

type PageState = 'loading' | 'empty' | 'error' | 'success'

const pageState = ref<PageState>('loading')
const errorMessage = ref('加载失败，请刷新重试')
const refreshing = ref(false)

async function loadData() {
  pageState.value = 'loading'
  errorMessage.value = '加载失败，请刷新重试'

  try {
    // Placeholder for future story — replace with actual API call
    // const horses = await getHorses()
    // if (horses.length === 0) {
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
  <div class="horses-page">
    <header class="page-header">
      <h1 class="page-title">马匹管理</h1>
    </header>

    <!-- Skeleton loading -->
    <template v-if="pageState === 'loading'">
      <div class="skeleton-container" role="status" aria-live="polite" aria-label="加载中">
        <div v-for="i in 5" :key="i" class="skeleton-row"></div>
      </div>
    </template>

    <!-- Empty state -->
    <template v-else-if="pageState === 'empty'">
      <div class="state-container" role="status" aria-live="polite">
        <p class="empty-text">
          马匹库为空——创建第一场比赛时，参赛马匹将自动入库。
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

    <!-- Content (placeholder for future stories) -->
    <template v-else>
      <div class="content-container">
        <p class="placeholder-text">马匹列表内容将在 Story 2.1 中实现</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
.horses-page {
  padding: var(--spacing-16);
  max-width: 1280px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: var(--spacing-20);
}

.page-title {
  font-family: 'Barlow Condensed', system-ui, sans-serif;
  font-size: 28px;
  font-weight: 600;
  color: var(--color-primary);
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
  min-height: 30vh;
  text-align: center;
  gap: var(--spacing-16);
  padding: var(--spacing-32) var(--spacing-16);
}

.empty-text {
  color: var(--color-ink-secondary);
  font-size: var(--text-body);
  max-width: 400px;
  line-height: 1.6;
}

.error-text {
  color: var(--color-destructive);
  font-size: var(--text-body);
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

.content-container {
  padding: var(--spacing-16) 0;
}

.placeholder-text {
  color: var(--color-ink-secondary);
  font-size: var(--text-body);
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
