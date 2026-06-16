<script setup lang="ts">
import type { LeaderboardEntry } from '@/types/leaderboard'

const props = defineProps<{
  entry: LeaderboardEntry
  rank: number
  isCurrentUser: boolean
}>()
</script>

<template>
  <tr
    class="leaderboard-row"
    :class="{ 'current-user': isCurrentUser }"
    :aria-label="`第${rank}名，${entry.username}，${entry.total_points}分`"
  >
    <td class="col-rank" :class="{ 'top-three': rank <= 3 }">
      {{ rank }}
    </td>
    <td class="col-name">{{ entry.username }}</td>
    <td class="col-points">{{ entry.total_points }}</td>
    <td class="col-races">{{ entry.races_participated }}</td>
    <td class="col-avg">{{ entry.avg_points.toFixed(1) }}</td>
  </tr>
</template>

<style scoped>
.leaderboard-row {
  border-bottom: 1px solid var(--color-border-hairline, #D4DCD0);
}

.leaderboard-row.current-user {
  background: #F0F7F2;
}

td {
  padding: var(--spacing-3, 12px) var(--spacing-2, 8px);
  vertical-align: middle;
  white-space: nowrap;
}

.col-rank {
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
  font-size: var(--text-body, 16px);
  color: var(--color-ink-primary, #1A2E1A);
  overflow: hidden;
  text-overflow: ellipsis;
}

.col-points {
  font-family: 'Barlow Condensed', system-ui, sans-serif;
  font-size: 20px;
  font-weight: 700;
  color: var(--color-primary, #1A5632);
  text-align: right;
}

.col-races {
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-secondary, #4A5A4A);
  text-align: center;
}

.col-avg {
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
