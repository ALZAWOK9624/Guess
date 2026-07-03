<script setup lang="ts">
const emit = defineEmits<{
  click: []
}>()

function handleClick() {
  emit('click')
}
</script>

<template>
  <button
    class="add-horse-card"
    type="button"
    aria-label="添加马匹"
    @click="handleClick"
  >
    <span class="plus-icon">+</span>
    <span class="add-label">添加马匹</span>
  </button>
</template>

<style scoped>
.add-horse-card {
  width: 100%;
  min-height: 96px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2, 8px);
  background: var(--color-surface-raised, #FFFFFF);
  border: 2px dashed var(--color-border-strong, #A8B8A4);
  border-radius: var(--rounded-md, 10px);
  padding: var(--spacing-4, 16px);
  cursor: pointer;
  transition: border-color 0.15s, background-color 0.15s;
}

.add-horse-card:hover {
  border-color: var(--color-primary, #1A5632);
  background: var(--color-surface-base, #F8FAF7);
}

.add-horse-card:focus-visible {
  outline: 2px solid var(--color-primary, #1A5632);
  outline-offset: 2px;
}

.plus-icon {
  font-size: 32px;
  font-weight: 300;
  color: var(--color-primary, #1A5632);
  line-height: 1;
}

.add-label {
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-secondary, #4A5A4A);
  font-weight: 600;
}

@media (max-width: 767px) {
  .add-horse-card {
    min-height: 72px;
  }

  .plus-icon {
    font-size: 24px;
  }

  .add-label {
    font-size: var(--text-caption, 12px);
  }
}
</style>
