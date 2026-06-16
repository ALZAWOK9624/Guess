<script setup lang="ts">
import { computed } from 'vue'
import type { HorseSnapshotData } from '@/types/race'

function computeAge(birthYear: number, hemisphere: string, onDate: Date): number {
  const cutoffMonth = hemisphere === 'south' ? 8 : 1
  const thisYear = onDate.getFullYear()
  const cutoff = new Date(thisYear, cutoffMonth - 1, 1)
  const effectiveYear = onDate >= cutoff ? thisYear : thisYear - 1
  return effectiveYear - birthYear
}

const props = withDefaults(defineProps<{
  snapshotData?: HorseSnapshotData | null
  horseId: number
  weight?: string | null
  jockey?: string | null
  birthYear?: number | null
  hemisphere?: string | null
  referenceDate?: string | null
  votable?: boolean
  voted?: boolean
  submitting?: boolean
}>(), {
  snapshotData: () => ({
    name: '',
    sex: null,
    birth_year: null,
    hemisphere: null,
    origin: null,
    sire: null,
    damsire: null,
    previous_result: null,
    best_win: null,
  }),
  weight: null,
  jockey: null,
  birthYear: null,
  hemisphere: null,
  referenceDate: null,
  votable: false,
  voted: false,
  submitting: false,
})

const emit = defineEmits<{
  voteToggle: []
}>()

const safeData = computed(() => props.snapshotData ?? {
  name: '',
  sex: null,
  birth_year: null,
  hemisphere: null,
  origin: null,
  sire: null,
  damsire: null,
  previous_result: null,
  best_win: null,
})

// Compute age: from props (new) → snapshotData.birth_year (new snap) → snapshotData.age (legacy snap)
const rawBirthYear = computed(() => props.birthYear ?? props.snapshotData?.birth_year ?? props.snapshotData?.age ?? null)
const rawHemisphere = computed(() => props.hemisphere ?? props.snapshotData?.hemisphere ?? null)

const displayAge = computed(() => {
  if (rawBirthYear.value === null || rawBirthYear.value === undefined) return null
  const refDate = props.referenceDate ? new Date(props.referenceDate) : new Date()
  const hs = rawHemisphere.value || 'north'
  return computeAge(rawBirthYear.value, hs, refDate)
})

const infoLine = computed(() => {
  const parts: string[] = []
  const sex = safeData.value.sex || '-'
  const age = displayAge.value !== null ? `${displayAge.value}` : '-'
  parts.push(`${sex}${age}`)
  parts.push(`产:${safeData.value.origin || '-'}`)
  parts.push(`父:${safeData.value.sire || '-'}`)
  parts.push(`母父:${safeData.value.damsire || '-'}`)
  parts.push(`前走:${safeData.value.previous_result || '-'}`)
  parts.push(`主胜鞍:${safeData.value.best_win || '-'}`)
  return parts.join(' ')
})

function handleClick() {
  if (props.submitting || !props.votable) return
  emit('voteToggle')
}
</script>

<template>
  <div
    class="horse-detail-card"
    :class="{ votable, voted, submitting: submitting && voted }"
    :role="votable ? 'button' : undefined"
    :tabindex="votable ? 0 : undefined"
    :aria-pressed="votable ? voted : undefined"
    @click="handleClick"
    @keydown.enter="handleClick"
    @keydown.space.prevent="handleClick"
  >
    <div class="card-inner">
      <span class="horse-name">{{ safeData.name }}</span>
      <span class="info-line">{{ infoLine }}</span>
      <div v-if="votable && voted" class="vote-badge" aria-hidden="true">
        <span class="vote-checkmark">✓</span>
        <span class="vote-label">已投</span>
      </div>
      <div v-if="submitting && voted" class="vote-spinner" aria-hidden="true" />
    </div>
  </div>
</template>

<style scoped>
.horse-detail-card {
  position: relative;
  background: var(--color-surface-raised, #FFFFFF);
  border: 2px solid var(--color-border-hairline, #D4DCD0);
  border-radius: var(--rounded-md, 10px);
  padding: var(--spacing-3, 12px) var(--spacing-4, 16px);
  transition: border-color 0.15s, box-shadow 0.15s, background-color 0.15s;
}

.horse-detail-card.votable {
  cursor: pointer;
  user-select: none;
}

.horse-detail-card.votable:hover {
  border-color: var(--color-primary, #1A5632);
  box-shadow: 0 2px 8px rgba(26, 86, 50, 0.12);
}

.horse-detail-card.votable:focus-visible {
  outline: 2px solid var(--color-primary, #1A5632);
  outline-offset: 2px;
}

.horse-detail-card.voted {
  border-color: var(--color-accent, #B8960C);
  background: #FFFDF0;
}

.horse-detail-card.votable.voted:hover {
  border-color: var(--color-destructive, #C53030);
  box-shadow: 0 2px 8px rgba(197, 48, 48, 0.12);
}

.horse-detail-card.submitting {
  opacity: 0.7;
  pointer-events: none;
}

.card-inner {
  display: flex;
  align-items: baseline;
  gap: var(--spacing-3, 12px);
  flex-wrap: wrap;
}

.horse-name {
  font-family: var(--font-display, 'Barlow Condensed', system-ui, sans-serif);
  font-size: var(--text-subheading, 18px);
  font-weight: 600;
  color: var(--color-ink-primary, #1A2E1A);
  white-space: nowrap;
  flex-shrink: 0;
}

.info-line {
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-primary, #1A2E1A);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  min-width: 0;
}

.vote-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  background: var(--color-accent, #B8960C);
  color: #ffffff;
  border-radius: 20px;
  padding: 2px 10px;
  font-size: var(--text-caption, 12px);
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
}

.vote-checkmark {
  font-size: 14px;
  line-height: 1;
}

.vote-label {
  line-height: 1;
}

.vote-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(185, 150, 12, 0.3);
  border-top-color: var(--color-accent, #B8960C);
  border-radius: 50%;
  animation: horse-spin 0.6s linear infinite;
  flex-shrink: 0;
}

@keyframes horse-spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 767px) {
  .horse-detail-card {
    padding: var(--spacing-2, 8px) var(--spacing-3, 12px);
  }

  .card-inner {
    gap: var(--spacing-2, 8px);
  }

  .horse-name {
    font-size: var(--text-body, 16px);
  }

  .info-line {
    font-size: var(--text-caption, 12px);
    white-space: normal;
    overflow: visible;
  }
}
</style>
