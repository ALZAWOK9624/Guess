<script setup lang="ts">
import { ref } from 'vue'
import HorseSearchSelect from '@/components/HorseSearchSelect.vue'
import type { Horse } from '@/types/horse'

const selectedHorses = ref<Horse[]>([])

function canSubmit(): boolean {
  return selectedHorses.value.length >= 2
}
</script>

<template>
  <div class="create-race-page">
    <h1 class="page-title">创建比赛</h1>

    <div class="form-section">
      <p class="section-desc">选择参赛马匹（至少 2 匹）</p>
      <HorseSearchSelect v-model:selectedHorses="selectedHorses" />
      <p v-if="selectedHorses.length > 0 && selectedHorses.length < 2" class="validation-hint">
        请至少选择 2 匹马
      </p>
    </div>

    <div class="action-bar">
      <p class="hint">比赛名称、日期、等级等字段将在 Story 2.3 中实现</p>
      <button class="btn btn-primary" :disabled="!canSubmit()">
        创建比赛 (Story 2.3)
      </button>
    </div>
  </div>
</template>

<style scoped>
.create-race-page {
  padding: var(--spacing-4, 16px);
  max-width: 720px;
  margin: 0 auto;
}

.page-title {
  font-family: var(--font-display, 'Barlow Condensed', system-ui, sans-serif);
  font-size: var(--text-heading, 24px);
  font-weight: 600;
  color: var(--color-primary, #1A5632);
  margin-bottom: var(--spacing-6, 24px);
}

.form-section {
  margin-bottom: var(--spacing-6, 24px);
}

.section-desc {
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-secondary, #4A5A4A);
  margin-bottom: var(--spacing-3, 12px);
}

.validation-hint {
  margin-top: var(--spacing-2, 8px);
  font-size: var(--text-caption, 12px);
  color: var(--color-destructive, #C53030);
}

.action-bar {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3, 12px);
  align-items: flex-start;
}

.hint {
  font-size: var(--text-caption, 12px);
  color: var(--color-ink-disabled, #9CAA9C);
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 24px;
  border: none;
  border-radius: var(--rounded-md, 10px);
  font-size: var(--text-body, 16px);
  font-weight: 600;
  cursor: pointer;
  min-height: 44px;
  transition: opacity 0.15s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--color-primary, #1A5632);
  color: #FFFFFF;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-light, #2D7A4F);
}

@media (prefers-reduced-motion: reduce) {
  .btn {
    transition: none;
  }
}
</style>
