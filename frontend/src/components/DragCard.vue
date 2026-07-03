<script setup lang="ts">
import type { RaceHorseSnapshot } from '@/types/race'

const props = withDefaults(
  defineProps<{
    horse: RaceHorseSnapshot
    isDnf?: boolean
    index: number
    isDragging?: boolean
  }>(),
  {
    isDnf: false,
    isDragging: false,
  },
)

const emit = defineEmits<{
  dragStart: [index: number]
  dragEnd: [event: DragEvent]
}>()

const snapshot = () => props.horse.snapshot_data
</script>

<template>
  <div
    class="drag-card"
    :class="{ 'is-dnf': isDnf, 'is-dragging': isDragging }"
    draggable="true"
    @dragstart="emit('dragStart', index)"
    @dragend="emit('dragEnd', $event)"
  >
    <div class="drag-handle" aria-label="拖拽排序" title="拖拽排序">
      <span class="handle-dots">⠿</span>
    </div>
    <div class="card-content">
      <span class="horse-name">{{ snapshot().name }}</span>
      <span class="horse-meta">
        {{ props.horse.jockey || '' }}
      </span>
    </div>
    <div v-if="isDnf" class="dnf-badge">DNF</div>
  </div>
</template>

<style scoped>
.drag-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  min-height: 56px;
  background: #fff;
  border: 1px solid var(--border-hairline, #d4dcd0);
  border-radius: var(--radius-md, 10px);
  cursor: grab;
  user-select: none;
  transition: box-shadow 0.15s ease, opacity 0.15s ease;
}

.drag-card:hover {
  border-color: var(--color-primary, #1a5632);
}

.drag-card:active {
  cursor: grabbing;
}

.drag-card.is-dragging {
  opacity: 0.7;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: scale(1.02);
}

.drag-card.is-dnf {
  opacity: 0.5;
  background: #f3f4f6;
}

.drag-handle {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  min-height: 48px;
  color: #9ca3af;
  cursor: grab;
  touch-action: none;
}

.handle-dots {
  font-size: 18px;
  line-height: 1;
  letter-spacing: 2px;
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.horse-name {
  font-size: var(--text-body, 15px);
  font-weight: 600;
  color: var(--color-text, #1f2937);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.horse-meta {
  font-size: var(--text-body-sm, 13px);
  color: var(--color-text-muted, #6b7280);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dnf-badge {
  font-size: var(--text-body-sm, 13px);
  font-weight: 600;
  color: #ef4444;
  background: #fef2f2;
  padding: 2px 8px;
  border-radius: var(--radius-sm, 6px);
  white-space: nowrap;
}
</style>
