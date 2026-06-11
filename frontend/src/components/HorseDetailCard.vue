<script setup lang="ts">
import { computed } from 'vue'
import type { HorseSnapshotData } from '@/types/race'

const props = withDefaults(defineProps<{
  snapshotData?: HorseSnapshotData | null
  horseId: number
}>(), {
  snapshotData: () => ({
    name: '',
    sex: null,
    age: null,
    origin: null,
    sire: null,
    damsire: null,
    weight: null,
    jockey: null,
    previous_result: null,
    best_win: null,
  }),
})

const safeData = computed(() => props.snapshotData ?? {
  name: '',
  sex: null,
  age: null,
  origin: null,
  sire: null,
  damsire: null,
  weight: null,
  jockey: null,
  previous_result: null,
  best_win: null,
})
</script>

<template>
  <div class="horse-detail-card">
    <h3 class="horse-name">{{ safeData.name }}</h3>
    <div class="horse-attributes">
      <div class="attr-row">
        <span class="attr-label">性别</span>
        <span class="attr-value">{{ safeData.sex || '-' }}</span>
      </div>
      <div class="attr-row">
        <span class="attr-label">年龄</span>
        <span class="attr-value">{{ safeData.age ?? '-' }}</span>
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
        <span class="attr-value">{{ safeData.weight || '-' }}</span>
      </div>
      <div class="attr-row">
        <span class="attr-label">骑手</span>
        <span class="attr-value">{{ safeData.jockey || '-' }}</span>
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
  background: var(--color-surface-raised, #FFFFFF);
  border: 1px solid var(--color-border-hairline, #D4DCD0);
  border-radius: var(--rounded-md, 10px);
  padding: var(--spacing-4, 16px);
}

.horse-name {
  font-family: var(--font-display, 'Barlow Condensed', system-ui, sans-serif);
  font-size: var(--text-subheading, 18px);
  font-weight: 600;
  color: var(--color-ink-primary, #1A2E1A);
  margin: 0 0 var(--spacing-3, 12px);
  padding-bottom: var(--spacing-2, 8px);
  border-bottom: 1px solid var(--color-border-hairline, #D4DCD0);
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
