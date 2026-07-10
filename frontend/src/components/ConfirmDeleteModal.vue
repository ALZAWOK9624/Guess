<script setup lang="ts">
/**
 * ConfirmDeleteModal — Reusable destructive confirmation dialog.
 *
 * Usage:
 *   <ConfirmDeleteModal
 *     v-if="showModal"
 *     title="删除比赛"
 *     :item-name="raceName"
 *     :loading="isDeleting"
 *     @confirm="handleDelete"
 *     @cancel="showModal = false"
 *   />
 */

const props = withDefaults(defineProps<{
  title?: string
  itemName: string
  message?: string
  loading?: boolean
  confirmText?: string
  loadingText?: string
}>(), {
  title: '确认删除',
  message: '确定删除「{name}」？此操作不可撤销。',
  loading: false,
  confirmText: '确认删除',
  loadingText: '删除中…',
})

const titleId = 'confirm-delete-title'

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

function displayMessage(): string {
  return props.message.replace('{name}', props.itemName)
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && !props.loading) {
    emit('cancel')
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      class="modal-overlay"
      role="dialog"
      aria-modal="true"
      :aria-labelledby="titleId"
      @keydown="onKeydown"
      @click.self="emit('cancel')"
    >
      <div class="modal-content">
        <h2 :id="titleId" class="modal-title">{{ title }}</h2>

        <p class="modal-message">
          {{ displayMessage() }}
        </p>

        <div class="modal-actions">
          <button
            class="btn btn-cancel"
            :disabled="loading"
            @click="emit('cancel')"
          >
            取消
          </button>
          <button
            class="btn btn-destructive"
            :disabled="loading"
            @click="emit('confirm')"
          >
            {{ loading ? loadingText : confirmText }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(26, 46, 26, 0.5);
  padding: var(--spacing-4, 16px);
}

.modal-content {
  background: var(--color-surface-raised, #FFFFFF);
  border-radius: var(--rounded-lg, 14px);
  padding: var(--spacing-6, 24px);
  max-width: 400px;
  width: 100%;
  box-shadow: 0 4px 12px rgba(26, 86, 50, 0.15);
}

.modal-title {
  font-family: var(--font-display, 'Barlow Condensed', system-ui, sans-serif);
  font-size: var(--text-heading, 24px);
  font-weight: 600;
  color: var(--color-ink-primary, #1A2E1A);
  margin: 0 0 var(--spacing-4, 16px);
}

.modal-message {
  font-size: var(--text-body, 16px);
  color: var(--color-ink-primary, #1A2E1A);
  line-height: var(--text-body-line-height, 1.6);
  margin: 0 0 var(--spacing-6, 24px);
}

.modal-actions {
  display: flex;
  gap: var(--spacing-3, 12px);
  justify-content: flex-end;
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
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-cancel {
  background: var(--color-surface-raised, #FFFFFF);
  color: var(--color-ink-primary, #1A2E1A);
  border: 1px solid var(--color-border-strong, #A8B8A4);
}

.btn-destructive {
  background: var(--color-destructive, #C53030);
  color: #FFFFFF;
}

.btn-destructive:hover:not(:disabled) {
  opacity: 0.9;
}
</style>
