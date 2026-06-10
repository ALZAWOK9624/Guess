<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import RaceCard from '@/components/RaceCard.vue'

type PageState = 'loading' | 'empty' | 'error' | 'success'

const authStore = useAuthStore()
const pageState = ref<PageState>('loading')
const errorMessage = ref('加载失败，请刷新重试')
const refreshing = ref(false)

async function loadData() {
  pageState.value = 'loading'
  errorMessage.value = '加载失败，请刷新重试'

  try {
    // Placeholder for future story — replace with actual API call
    // const races = await getRaces()
    // if (races.length === 0) {
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

    <!-- Content (placeholder for future stories) -->
    <template v-else>
      <div class="race-list">
        <p>比赛列表内容将在后续故事中展示</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
.home-page {
  padding: var(--spacing-16);
  max-width: 1280px;
  margin: 0 auto;
}

.race-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-12);
}

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
  .refresh-btn {
    transition: none;
  }
}
</style>
