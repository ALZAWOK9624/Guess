<script setup lang="ts">

import HorseDetailCard from '@/components/HorseDetailCard.vue'
import type { RaceHorseResult } from '@/types/race'
import { refreshRaceHorseSnapshot } from '@/api/horses'

const props = defineProps<{
  horses: RaceHorseResult[]
  raceId: number
}>()

const emit = defineEmits<{
  refresh: []
}>()

async function handleRefresh(horse: RaceHorseResult) {
  try {
    await refreshRaceHorseSnapshot(props.raceId, horse.race_horse_id)
    emit('refresh')
  } catch (err: any) {
    alert(err?.response?.data?.detail?.message || '刷新失败')
  }
}

function getPositionLabel(position: number | null): string {
  if (position === null) return '-'
  if (position === 0) return 'DNF'
  if (position === 1) return '1st'
  if (position === 2) return '2nd'
  if (position === 3) return '3rd'
  return `${position}th`
}

function getPositionAriaLabel(position: number | null): string {
  if (position === null) return ''
  if (position === 0) return '弃权'
  if (position === 1) return '第一名'
  if (position === 2) return '第二名'
  if (position === 3) return '第三名'
  return `第${position}名`
}

function formatPoints(points: number | null): string {
  if (points === null) return ''
  if (points === 0) return '0'
  return points > 0 ? `+${points}` : `${points}`
}

const isTop3 = (position: number | null) => position !== null && position > 0 && position <= 3
const isDnf = (position: number | null) => position === 0
</script>

<template>
  <div class="race-result-view">
    <h2 v-if="horses.length > 0" class="section-title">比赛结果</h2>

    <div
      v-for="horse in horses"
      :key="horse.race_horse_id"
      class="result-horse-wrapper"
      :class="{ 'dnf-horse': isDnf(horse.position) }"
    >
      <div class="position-section">
        <span
          class="position-badge"
          :class="{
            'pos-gold': isTop3(horse.position),
            'pos-gray': !isTop3(horse.position) && !isDnf(horse.position),
            'pos-dnf': isDnf(horse.position),
          }"
          :aria-label="getPositionAriaLabel(horse.position)"
        >
          {{ getPositionLabel(horse.position) }}
        </span>

        <div class="horse-card-area">
          <HorseDetailCard
            :snapshot-data="horse.snapshot_data as any"
            :horse-id="horse.horse_id"
            @refresh="handleRefresh(horse)"
          />
        </div>
      </div>

      <!-- Vote list under this horse -->
      <div v-if="horse.votes.length > 0" class="vote-list-container">
        <div
          v-for="(vote, idx) in horse.votes"
          :key="idx"
          class="vote-entry"
          :aria-label="`${vote.username}，${vote.points ?? 0}分`"
        >
          <span class="vote-username">{{ vote.username }}</span>
          <span
            v-if="!isDnf(horse.position)"
            class="vote-points"
            :class="{
              'points-positive': vote.points !== null && vote.points > 0,
              'points-negative': vote.points !== null && vote.points < 0,
              'points-zero': vote.points === null || vote.points === 0,
            }"
          >
            <template v-if="vote.points !== null">· {{ formatPoints(vote.points) }}</template>
          </span>
          <span
            v-else
            class="vote-points points-zero"
          >
            · 0
          </span>
        </div>
      </div>
      <div v-else class="no-votes">
        — 无人投给此马
      </div>
    </div>
  </div>
</template>

<style scoped>
.race-result-view {
  margin-top: var(--spacing-6, 24px);
}

.section-title {
  font-size: var(--text-subheading, 18px);
  font-weight: 600;
  color: var(--color-ink-primary, #1A2E1A);
  margin: 0 0 var(--spacing-4, 16px);
}

.result-horse-wrapper {
  margin-bottom: var(--spacing-5, 20px);
  padding: var(--spacing-3, 12px);
  background: var(--color-surface-base, #F8FAF7);
  border-radius: var(--rounded-md, 10px);
}

.result-horse-wrapper.dnf-horse {
  opacity: 0.5;
}

.result-horse-wrapper.dnf-horse .no-votes {
  opacity: 1;
}

.position-section {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-3, 12px);
}

.position-badge {
  font-family: var(--font-display, 'Barlow Condensed', system-ui, sans-serif);
  font-size: var(--text-body, 16px);
  font-weight: 700;
  padding: 4px 8px;
  border-radius: var(--rounded-sm, 6px);
  min-width: 44px;
  text-align: center;
  flex-shrink: 0;
  margin-top: 4px;
}

.pos-gold {
  background: var(--color-accent, #B8960C);
  color: #FFFFFF;
}

.pos-gray {
  background: var(--color-ink-disabled, #9CAA9C);
  color: #FFFFFF;
}

.pos-dnf {
  background: var(--color-ink-disabled, #9CAA9C);
  color: #FFFFFF;
  font-style: italic;
}

.horse-card-area {
  flex: 1;
  min-width: 0;
}

.vote-list-container {
  margin-top: var(--spacing-2, 8px);
  margin-left: calc(44px + var(--spacing-3, 12px));
  padding: var(--spacing-3, 12px);
  background: var(--color-surface-raised, #FFFFFF);
  border-radius: var(--rounded-sm, 6px);
  border: 1px solid var(--color-border-hairline, #D4DCD0);
}

.vote-entry {
  display: flex;
  align-items: center;
  gap: var(--spacing-2, 8px);
  font-size: var(--text-body-sm, 14px);
  padding: 4px 0;
}

.vote-entry + .vote-entry {
  border-top: 1px solid var(--color-border-hairline, #D4DCD0);
}

.vote-username {
  color: var(--color-ink-secondary, #4A5A4A);
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.vote-points {
  font-family: var(--font-display, 'Barlow Condensed', system-ui, sans-serif);
  font-size: var(--text-body-sm, 14px);
  font-weight: 700;
  flex-shrink: 0;
}

.points-positive {
  color: var(--color-primary, #1A5632);
}

.points-negative {
  color: var(--color-destructive, #C53030);
}

.points-zero {
  color: var(--color-ink-disabled, #9CAA9C);
}

.no-votes {
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-disabled, #9CAA9C);
  font-style: italic;
  margin-top: var(--spacing-2, 8px);
  margin-left: calc(44px + var(--spacing-3, 12px));
  padding: var(--spacing-2, 8px) var(--spacing-3, 12px);
}

/* Responsive: full width on mobile */
@media (max-width: 767px) {
  .vote-list-container {
    margin-left: 0;
  }

  .no-votes {
    margin-left: 0;
  }
}
</style>
