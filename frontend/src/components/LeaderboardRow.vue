<script setup lang="ts">
import type { LeaderboardEntry } from '@/types/leaderboard'

const props = defineProps<{
  entry: LeaderboardEntry
  rank: number
  isCurrentUser: boolean
}>()
</script>

<template>
  <div
    class="leaderboard-row"
    :class="{ 'current-user': isCurrentUser }"
    role="row"
    :aria-label="`第${rank}名，${entry.username}，${entry.total_points}分`"
  >
    <span class="col-rank" :class="{ 'top-three': rank <= 3 }">
      {{ rank }}
    </span>
    <span class="col-name">{{ entry.username }}</span>
    <span class="col-points">{{ entry.total_points }}</span>
    <span class="col-races">{{ entry.races_participated }}</span>
    <span class="col-avg">{{ entry.avg_points.toFixed(1) }}</span>
  </div>
</template>

<style scoped>
.leaderboard-row {
  display: flex;
  gap: var(--spacing-12, 12px);
  padding: var(--spacing-3, 12px) var(--spacing-4, 16px);
  border-bottom: 1px solid var(--color-border-hairline, #D4DCD0);
  align-items: center;
  min-height: 44px;
}

.leaderboard-row.current-user {
  background: #F0F7F2;
}

.col-rank {
  width: 40px;
  flex-shrink: 0;
  font-family: 'Barlow Condensed', system-ui, sans-serif;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-ink-primary, #1A2E1A);
  text-align: center;
}

.col-rank.top-three {
  color: var(--color-accent, #B8960C);
}

.col-name {
  flex: 1;
  min-width: 0;
  font-size: var(--text-body, 16px);
  color: var(--color-ink-primary, #1A2E1A);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.col-points {
  width: 60px;
  flex-shrink: 0;
  font-family: 'Barlow Condensed', system-ui, sans-serif;
  font-size: 20px;
  font-weight: 700;
  color: var(--color-primary, #1A5632);
  text-align: right;
}

.col-races {
  width: 50px;
  flex-shrink: 0;
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-secondary, #4A5A4A);
  text-align: center;
}

.col-avg {
  width: 50px;
  flex-shrink: 0;
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-secondary, #4A5A4A);
  text-align: right;
}

@media (prefers-reduced-motion: reduce) {
  .leaderboard-row {
    transition: none;
  }
}
</style>
