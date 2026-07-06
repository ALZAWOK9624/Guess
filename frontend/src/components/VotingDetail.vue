<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js'
import type { VoteListEntry } from '@/types/vote'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps<{
  votes: VoteListEntry[]
  loading?: boolean
}>()

const showList = ref(false)

// Prefers reduced motion
const prefersReducedMotion = ref(false)
let motionMedia: MediaQueryList | null = null
const reducedMotionHandler = (e: MediaQueryListEvent) => {
  prefersReducedMotion.value = e.matches
}

onMounted(() => {
  motionMedia = window.matchMedia('(prefers-reduced-motion: reduce)')
  prefersReducedMotion.value = motionMedia.matches
  motionMedia.addEventListener('change', reducedMotionHandler)
})

onUnmounted(() => {
  if (motionMedia) {
    motionMedia.removeEventListener('change', reducedMotionHandler)
  }
})

// Group votes by horse
const totalVotes = computed(() => props.votes.length)

const horseGroups = computed(() => {
  const groups: Record<string, { count: number; voters: string[] }> = {}
  for (const vote of props.votes) {
    if (!groups[vote.horse_name]) {
      groups[vote.horse_name] = { count: 0, voters: [] }
    }
    groups[vote.horse_name].count++
    groups[vote.horse_name].voters.push(vote.username)
  }
  return Object.entries(groups).map(([horseName, data]) => ({
    horseName,
    count: data.count,
    percentage: totalVotes.value > 0 ? Math.round((data.count / totalVotes.value) * 100) : 0,
    voters: data.voters,
  }))
})

const COLORS = [
  '#1A5632', '#B8960C', '#2B6CB0', '#C53030',
  '#6B46C1', '#319795', '#D69E2E', '#38A169',
  '#DD6B20', '#4FD1C5', '#805AD5', '#E53E3E',
]

const chartData = computed(() => ({
  labels: horseGroups.value.map(g => g.horseName),
  datasets: [
    {
      data: horseGroups.value.map(g => g.count),
      backgroundColor: horseGroups.value.map((_, i) => COLORS[i % COLORS.length]),
      borderWidth: 2,
      borderColor: '#FFFFFF',
      hoverOffset: 8,
    },
  ],
}))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: true,
  cutout: '55%',
  plugins: {
    legend: {
      display: true,
      position: 'bottom' as const,
      labels: {
        padding: 16,
        usePointStyle: true,
        font: { size: 13 },
      },
    },
    tooltip: {
      enabled: true,
      backgroundColor: 'rgba(26, 44, 26, 0.92)',
      titleFont: { size: 14, weight: 'bold' as const },
      bodyFont: { size: 13 },
      padding: 12,
      cornerRadius: 8,
      displayColors: true,
      callbacks: {
        label(ctx: any) {
          const group = horseGroups.value[ctx.dataIndex]
          if (!group) return ''
          return ` ${group.count}/${totalVotes.value} 票 (${group.percentage}%)`
        },
        afterLabel(ctx: any) {
          const group = horseGroups.value[ctx.dataIndex]
          if (!group) return ''
          const names = group.voters.join('、')
          return `投票人: ${names}`
        },
      },
    },
  },
  animation: prefersReducedMotion.value
    ? false
    : { animateRotate: true },
}))
</script>

<template>
  <div class="voting-detail">
    <h3 class="section-title">投票分布</h3>

    <!-- Loading state -->
    <div v-if="loading" class="skeleton-list">
      <div class="skeleton-chart">
        <div class="skeleton-circle" />
      </div>
      <div v-for="n in 2" :key="n" class="skeleton-row" />
    </div>

    <!-- Empty state -->
    <div v-else-if="votes.length === 0" class="empty-state">
      暂无投票
    </div>

    <!-- Chart -->
    <template v-else>
      <div class="chart-wrapper">
        <Doughnut :data="chartData" :options="chartOptions" />
      </div>

      <!-- Toggle text list -->
      <button
        class="toggle-list-btn"
        @click="showList = !showList"
      >
        <span v-if="!showList">查看投票明细 ({{ totalVotes }} 人)</span>
        <span v-else>收起明细</span>
        <span class="toggle-arrow" :class="{ expanded: showList }">▸</span>
      </button>

      <div v-if="showList" class="vote-list">
        <div
          v-for="vote in votes"
          :key="vote.user_id"
          class="vote-item"
        >
          <span class="vote-user">{{ vote.username }}</span>
          <span class="vote-arrow">→</span>
          <span class="vote-horse">{{ vote.horse_name }}</span>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.voting-detail {
  margin-top: var(--spacing-6, 24px);
}

.section-title {
  font-size: var(--text-subheading, 18px);
  font-weight: 600;
  color: var(--color-ink-primary, #1A2E1A);
  margin: 0 0 var(--spacing-3, 12px);
}

.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-chart {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.skeleton-circle {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: var(--border-hairline, #D4DCD0);
  animation: skeleton-shimmer 1.5s infinite ease-in-out;
}

.skeleton-row {
  height: 36px;
  background: var(--border-hairline, #D4DCD0);
  border-radius: var(--rounded-sm, 6px);
  animation: skeleton-shimmer 1.5s infinite ease-in-out;
}

.empty-state {
  font-size: var(--text-body, 16px);
  color: var(--color-ink-secondary, #4A5A4A);
  padding: var(--spacing-4, 16px) 0;
}

.chart-wrapper {
  max-width: 360px;
  margin: 0 auto var(--spacing-3, 12px);
}

.toggle-list-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  padding: 10px var(--spacing-3, 12px);
  background: var(--color-surface-base, #F8FAF7);
  border: 1px solid var(--border-hairline, #D4DCD0);
  border-radius: var(--rounded-sm, 6px);
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-secondary, #4A5A4A);
  cursor: pointer;
  transition: background 0.15s;
  min-height: 44px;
  text-align: left;
}

.toggle-list-btn:hover {
  background: var(--color-surface-hover, #F0F7F2);
}

.toggle-arrow {
  margin-left: auto;
  transition: transform 0.15s;
  font-size: 12px;
}

.toggle-arrow.expanded {
  transform: rotate(90deg);
}

.vote-list {
  list-style: none;
  padding: 0;
  margin: var(--spacing-2, 8px) 0 0;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2, 8px);
  border: 1px solid var(--border-hairline, #D4DCD0);
  border-radius: var(--rounded-sm, 6px);
  padding: var(--spacing-2, 8px);
  background: var(--color-surface-raised, #FFFFFF);
}

.vote-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-2, 8px);
  font-size: var(--text-body, 16px);
  padding: var(--spacing-2, 8px) 0;
  border-bottom: 1px solid var(--border-hairline, #D4DCD0);
}

.vote-item:last-child {
  border-bottom: none;
}

.vote-user {
  font-weight: 500;
  color: var(--color-ink-primary, #1A2E1A);
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.vote-arrow {
  color: var(--color-ink-disabled, #9CAA9C);
  flex-shrink: 0;
}

.vote-horse {
  color: var(--color-ink-primary, #1A2E1A);
  font-weight: 500;
}

@media (prefers-reduced-motion: reduce) {
  .toggle-list-btn {
    transition: none;
  }

  .toggle-arrow {
    transition: none;
  }
}
</style>
