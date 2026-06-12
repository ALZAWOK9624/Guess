<script setup lang="ts">
import type { RaceHorseSnapshot } from '@/types/race'

const props = defineProps<{
  horse: RaceHorseSnapshot
  selected: boolean
  disabled?: boolean
  name?: string
}>()

const emit = defineEmits<{
  select: []
}>()

function handleClick() {
  if (props.disabled) return
  emit('select')
}
</script>

<template>
  <div
    class="horse-select-card"
    :class="{ selected, disabled }"
    role="radio"
    :aria-checked="selected"
    :aria-disabled="disabled"
    :name="name"
    tabindex="0"
    @click="handleClick"
    @keydown.enter="handleClick"
    @keydown.space.prevent="handleClick"
  >
    <div class="select-indicator">
      <span v-if="selected" class="checkmark" aria-hidden="true">✓</span>
    </div>
    <div class="horse-info">
      <span class="horse-name">{{ horse.snapshot_data.name }}</span>
      <span class="horse-meta">
        {{ horse.snapshot_data.jockey ? `骑手：${horse.snapshot_data.jockey}` : '' }}
        {{ horse.snapshot_data.weight ? ` · ${horse.snapshot_data.weight}` : '' }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.horse-select-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-3, 12px);
  padding: var(--spacing-3, 12px) var(--spacing-4, 16px);
  border: 1px solid var(--border-hairline, #D4DCD0);
  border-radius: var(--rounded-md, 10px);
  background: var(--surface-raised, #FFFFFF);
  cursor: pointer;
  min-height: 48px;
  transition: border-color 0.15s, background-color 0.15s;
  user-select: none;
}

.horse-select-card:hover:not(.disabled) {
  border-color: var(--border-strong, #A8B8A4);
}

.horse-select-card.selected {
  border: 2px solid var(--color-accent, #B8960C);
  background: #FFFDF0;
  padding: calc(var(--spacing-3, 12px) - 1px) calc(var(--spacing-4, 16px) - 1px);
}

.horse-select-card.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

.select-indicator {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.checkmark {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-accent, #B8960C);
  line-height: 1;
}

.horse-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.horse-name {
  font-size: var(--text-body, 16px);
  font-weight: 600;
  color: var(--color-ink-primary, #1A2E1A);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.horse-meta {
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-secondary, #4A5A4A);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
