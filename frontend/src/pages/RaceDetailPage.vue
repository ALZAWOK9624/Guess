<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GradeBadge from '@/components/GradeBadge.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import HorseDetailCard from '@/components/HorseDetailCard.vue'
import { getRace } from '@/api/races'
import type { RaceDetail } from '@/types/race'

type PageState = 'loading' | 'error' | 'success'

const route = useRoute()
const router = useRouter()
const raceId = Number(route.params.id)

const pageState = ref<PageState>('loading')
const race = ref<RaceDetail | null>(null)
const errorMessage = ref('加载失败，请刷新重试')

onMounted(async () => {
  try {
    race.value = await getRace(raceId)
    pageState.value = 'success'
  } catch {
    pageState.value = 'error'
  }
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
          <h1 class="race-name">{{ race.name }}</h1>
          <StatusBadge :status="race.status as any" />
        </div>

        <p class="race-date">{{ race.date }}</p>
        <p class="race-meta">{{ race.horses.length }} 匹参赛 · {{ race.vote_count }} 人已投</p>
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

      <!-- Horse list -->
      <div class="horse-list">
        <h2 class="section-title">参赛马匹</h2>
        <HorseDetailCard
          v-for="horse in race.horses"
          :key="horse.horse_id"
          :snapshot-data="horse.snapshot_data"
          :horse-id="horse.horse_id"
        />
      </div>
    </template>
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
  align-items: center;
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
</style>
