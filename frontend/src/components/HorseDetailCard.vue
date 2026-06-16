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
  referenceDate?: string | null  // race date for age calculation; uses today if null
  votable?: boolean
  voted?: boolean
  submitting?: boolean
}>(), {
  snapshotData: () => ({
    name: '',
    sex: null,
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
  origin: null,
  sire: null,
  damsire: null,
  previous_result: null,
  best_win: null,
})

const displayWeight = computed(() => props.weight ?? props.snapshotData?.weight ?? null)
const displayJockey = computed(() => props.jockey ?? props.snapshotData?.jockey ?? null)

// Compute age: from props (new) → snapshotData.birth_year (new snap) → snapshotData.age (legacy snap)
const rawBirthYear = computed(() => props.birthYear ?? props.snapshotData?.birth_year ?? props.snapshotData?.age ?? null)
const rawHemisphere = computed(() => props.hemisphere ?? props.snapshotData?.hemisphere ?? null)

const displayAge = computed(() => {
  if (rawBirthYear.value === null || rawBirthYear.value === undefined) return null
  const refDate = props.referenceDate ? new Date(props.referenceDate) : new Date()
  const hs = rawHemisphere.value || 'north'
  return computeAge(rawBirthYear.value, hs, refDate)
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
    <div class="card-header">
      <h3 class="horse-name">{{ safeData.name }}</h3>
      <div v-if="votable && voted" class="vote-badge" aria-hidden="true">
        <span class="vote-checkmark">✓</span>
        <span class="vote-label">已投</span>
      </div>
      <div v-if="submitting && voted" class="vote-spinner" aria-hidden="true" />
    </div>
    <div class="horse-attributes">
      <div class="attr-row">
        <span class="attr-label">性别</span>
        <span class="attr-value">{{ safeData.sex || '-' }}</span>
      </div>
      <div class="attr-row">
        <span class="attr-label">年龄</span>
        <span class="attr-value">{{ displayAge !== null ? `${displayAge}岁` : '-' }}</span>
      </div>
      <div class="attr-row">
        <span class="attr-label">产地</span>
        <span class="attr-value">{{ safeData.origin || '-' }}</span>
      </div>
      <div class="attr-row">
        <span class="attr-label">父马</span>
        <span class="attr-value">{{ safeData.sire || '-' }}</span>
      </div>
      <div class="attr-row">
        <span class="attr-label">母父马</span>
        <span class="attr-value">{{ safeData.damsire || '-' }}</span>
      </div>
      <div class="attr-row">
        <span class="attr-label">负重</span>
        <span class="attr-value">{{ displayWeight || '-' }}</span>
      </div>
      <div class="attr-row">
        <span class="attr-label">骑手</span>
        <span class="attr-value">{{ displayJockey || '-' }}</span>
      </div>
      <div class="attr-row">
        <span class="attr-label">前走成绩</span>
        <span class="attr-value">{{ safeData.previous_result || '-' }}</span>
      </div>
      <div class="attr-row">
        <span class="attr-label">主胜鞍</span>
        <span class="attr-value">{{ safeData.best_win || '-' }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.horse-detail-card {
  position: relative;
  background: var(--color-surface-raised, #FFFFFF);
  border: 2px solid var(--color-border-hairline, #D4DCD0);
  border-radius: var(--rounded-md, 10px);
  padding: var(--spacing-4, 16px);
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

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-3, 12px);
  padding-bottom: var(--spacing-2, 8px);
  border-bottom: 1px solid var(--color-border-hairline, #D4DCD0);
}

.horse-name {
  font-family: var(--font-display, 'Barlow Condensed', system-ui, sans-serif);
  font-size: var(--text-subheading, 18px);
  font-weight: 600;
  color: var(--color-ink-primary, #1A2E1A);
  margin: 0;
  padding: 0;
  border: none;
}

.vote-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  background: var(--color-accent, #B8960C);
  color: #ffffff;
  border-radius: 20px;
  padding: 3px 10px;
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
  width: 16px;
  height: 16px;
  border: 2px solid rgba(185, 150, 12, 0.3);
  border-top-color: var(--color-accent, #B8960C);
  border-radius: 50%;
  animation: horse-spin 0.6s linear infinite;
  flex-shrink: 0;
}

@keyframes horse-spin {
  to { transform: rotate(360deg); }
}

.horse-attributes {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: var(--spacing-2, 8px);
}

.attr-row {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.attr-label {
  font-size: var(--text-caption, 12px);
  color: var(--color-ink-secondary, #4A5A4A);
  font-weight: 600;
}

.attr-value {
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-primary, #1A2E1A);
}
</style>
