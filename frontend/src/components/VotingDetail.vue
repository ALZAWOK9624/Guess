<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
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
  /** horse_name → position (1=winner, 2=second, 3=third). Only applicable for settled races. */
  horsePositions?: Record<string, number>
}>()

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

// Medal config
const MEDAL_ICONS: Record<number, string> = {
  1: '🥇',
  2: '🥈',
  3: '🥉',
}

const MEDAL_BORDERS: Record<number, string> = {
  1: '#B8960C',
  2: '#A0A0A0',
  3: '#CD7F32',
}

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
  return Object.entries(groups).map(([horseName, data]) => {
    const pos = props.horsePositions?.[horseName]
    return {
      horseName,
      count: data.count,
      percentage: totalVotes.value > 0 ? Math.round((data.count / totalVotes.value) * 100) : 0,
      voters: data.voters,
      position: (pos && pos >= 1 && pos <= 3) ? pos : null,
    }
  })
})

const COLORS = [
  '#1A5632', '#B8960C', '#2B6CB0', '#C53030',
  '#6B46C1', '#319795', '#D69E2E', '#38A169',
  '#DD6B20', '#4FD1C5', '#805AD5', '#E53E3E',
]

const chartData = computed(() => {
  const groups = horseGroups.value
  return {
    labels: groups.map(g =>
      g.position ? `${MEDAL_ICONS[g.position]} ${g.horseName}` : g.horseName,
    ),
    datasets: [
      {
        data: groups.map(g => g.count),
        backgroundColor: groups.map((_, i) => COLORS[i % COLORS.length]),
        borderWidth: groups.map(g => (g.position ? 4 : 2)),
        borderColor: groups.map(g =>
          g.position ? MEDAL_BORDERS[g.position] : '#FFFFFF',
        ),
        hoverOffset: groups.map(g => (g.position ? 12 : 8)),
        offset: groups.map(g => (g.position ? 8 : 0)),
      },
    ],
  }
})

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
    </div>

    <!-- Empty state -->
    <div v-else-if="votes.length === 0" class="empty-state">
      暂无投票
    </div>

    <!-- Chart -->
    <div v-else class="chart-wrapper">
      <Doughnut :data="chartData" :options="chartOptions" />
    </div>
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

.empty-state {
  font-size: var(--text-body, 16px);
  color: var(--color-ink-secondary, #4A5A4A);
  padding: var(--spacing-4, 16px) 0;
}

.chart-wrapper {
  max-width: 360px;
  margin: 0 auto;
}
</style>
