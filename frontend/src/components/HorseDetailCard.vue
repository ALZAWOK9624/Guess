<script setup lang="ts">
import { computed } from 'vue'
import type { HorseSnapshotData } from '@/types/race'

function positionLabel(pos: number): string {
  if (pos === 1) return '第一'
  if (pos === 2) return '第二'
  if (pos === 3) return '第三'
  return `第${pos}`
}

function formatPrevResult(snap: HorseSnapshotData): string {
  if (!snap.previous_result) return '-'
  const parts: string[] = []
  if (snap.previous_result_date) parts.push(snap.previous_result_date)
  parts.push(snap.previous_result)
  if (snap.previous_result_position != null) parts.push(positionLabel(snap.previous_result_position))
  return parts.join(' ')
}

function formatBestWin(snap: HorseSnapshotData): string {
  if (!snap.best_win) return '-'
  if (snap.best_win_date) return `${snap.best_win_date} ${snap.best_win}`
  return snap.best_win
}

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
    location: null,
    origin: null,
    sire: null,
    damsire: null,
    previous_result: null,
    previous_result_date: null,
    previous_result_position: null,
    best_win: null,
    best_win_date: null,
  }),
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
  location: null,
  origin: null,
  sire: null,
  damsire: null,
  previous_result: null,
  previous_result_date: null,
  previous_result_position: null,
  best_win: null,
  best_win_date: null,
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

const displayJockey = computed(() => props.jockey ?? null)

const sexAgeStr = computed(() => {
  const sex = safeData.value.sex || '-'
  const age = displayAge.value !== null ? `${displayAge.value}` : '-'
  return `${sex}${age}`
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
    <table class="horse-table">
      <colgroup>
        <col style="width:18%" />
        <col style="width:5.5%" />
        <col style="width:7.5%" />
        <col style="width:5.5%" />
        <col style="width:7.5%" />
        <col style="width:5.5%" />
        <col style="width:7.5%" />
        <col style="width:5.5%" />
        <col style="width:14%" />
        <col style="width:5.5%" />
        <col style="width:14%" />
      </colgroup>
      <tr>
        <td class="name-cell" rowspan="2">
          <div class="horse-name">{{ safeData.name }}</div>
          <div class="horse-suffix">{{ sexAgeStr }}</div>
          <div v-if="votable && voted" class="vote-badge" aria-hidden="true">
            <span class="vote-checkmark">✓</span>
            <span class="vote-label">已投</span>
          </div>
          <div v-if="submitting && voted" class="vote-spinner" aria-hidden="true" />
        </td>
        <th class="cl-lbl">骑手</th>
        <td class="cl-val">{{ displayJockey || '-' }}</td>
        <th class="cl-lbl">产地</th>
        <td class="cl-val">{{ safeData.origin || '-' }}</td>
        <th class="cl-lbl">属地</th>
        <td class="cl-val">{{ safeData.location || '-' }}</td>
        <th class="cl-lbl">父</th>
        <td class="cl-val">{{ safeData.sire || '-' }}</td>
        <th class="cl-lbl">母父</th>
        <td class="cl-val">{{ safeData.damsire || '-' }}</td>
      </tr>
      <tr>
        <th class="cl-lbl">前走</th>
        <td class="cl-val-wide" colspan="5">{{ formatPrevResult(safeData) }}</td>
        <th class="cl-lbl">主胜</th>
        <td class="cl-val-wide" colspan="3">{{ formatBestWin(safeData) }}</td>
      </tr>
    </table>
  </div>
</template>

<style scoped>
.horse-detail-card {
  position: relative;
  background: var(--color-surface-raised, #FFFFFF);
  border: 2px solid var(--color-border-hairline, #D4DCD0);
  border-radius: var(--rounded-md, 10px);
  padding: 4px;
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

/* ===== HTML Table Layout ===== */
.horse-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.horse-table th,
.horse-table td {
  border: 1px solid var(--color-border-hairline, #D4DCD0);
  padding: 10px 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Name cell spans 2 rows */
.name-cell {
  position: relative;
  text-align: left;
  vertical-align: middle;
  min-width: 80px;
}

.horse-name {
  font-family: var(--font-display, 'Barlow Condensed', system-ui, sans-serif);
  font-size: var(--text-subheading, 18px);
  font-weight: 600;
  color: var(--color-ink-primary, #1A2E1A);
}

.horse-suffix {
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-secondary, #4A5A4A);
}

/* Label cells */
.cl-lbl {
  font-size: var(--text-caption, 12px);
  color: var(--color-ink-secondary, #4A5A4A);
  font-weight: 600;
  text-align: center;
  background: var(--color-surface-base, #F8FAF7);
}

/* Value cells */
.cl-val {
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-primary, #1A2E1A);
  text-align: center;
}

.cl-val-wide {
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-primary, #1A2E1A);
  text-align: center;
}

/* Vote badge & spinner */
.vote-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  display: flex;
  align-items: center;
  gap: 4px;
  background: var(--color-accent, #B8960C);
  color: #ffffff;
  border-radius: 20px;
  padding: 1px 8px;
  font-size: var(--text-caption, 11px);
  font-weight: 600;
  white-space: nowrap;
}

.vote-checkmark {
  font-size: 12px;
  line-height: 1;
}

.vote-label {
  line-height: 1;
}

.vote-spinner {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  border: 2px solid rgba(185, 150, 12, 0.3);
  border-top-color: var(--color-accent, #B8960C);
  border-radius: 50%;
  animation: horse-spin 0.6s linear infinite;
}

@keyframes horse-spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 767px) {
  .horse-detail-card {
    padding: 2px;
  }

  .horse-name {
    font-size: var(--text-body, 16px);
  }

  .cl-lbl {
    font-size: 11px;
  }

  .cl-val,
  .cl-val-wide {
    font-size: 11px;
  }
}
</style>
