<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  raceStatus: string
  votedHorseName: string | null
  isLoggedIn: boolean
  isSubmitting?: boolean
}>()

const emit = defineEmits<{
  voteClick: []
  modifyClick: []
}>()

type ButtonState =
  | 'voting-unvoted-loggedin'
  | 'voting-unvoted-guest'
  | 'voting-voted'
  | 'locked-voted'
  | 'locked-unvoted'
  | 'settled'

const buttonState = computed<ButtonState>(() => {
  if (props.raceStatus === 'settled') return 'settled'
  if (props.raceStatus === 'locked') {
    return props.votedHorseName ? 'locked-voted' : 'locked-unvoted'
  }
  if (props.raceStatus === 'voting') {
    if (props.votedHorseName) return 'voting-voted'
    return props.isLoggedIn ? 'voting-unvoted-loggedin' : 'voting-unvoted-guest'
  }
  return 'settled'
})

const buttonText = computed(() => {
  switch (buttonState.value) {
    case 'voting-unvoted-loggedin':
    case 'voting-unvoted-guest':
      return '投票'
    case 'voting-voted':
      return `✓ 已投：${props.votedHorseName ?? ''}`
    case 'locked-voted':
      return '投票已截止'
    case 'locked-unvoted':
      return '投票已截止。你未参与本场竞猜。'
    case 'settled':
      return '已结算'
  }
})

const isInteractive = computed(() => {
  return buttonState.value === 'voting-unvoted-loggedin' ||
    buttonState.value === 'voting-voted'
})

function handleClick() {
  if (buttonState.value === 'voting-unvoted-loggedin') {
    emit('voteClick')
    return
  }
  if (buttonState.value === 'voting-voted') {
    emit('modifyClick')
    return
  }
}
</script>

<template>
  <button
    class="vote-button"
    :class="[buttonState, { submitting: isSubmitting }]"
    :disabled="!isInteractive || isSubmitting"
    :aria-disabled="!isInteractive || isSubmitting"
    @click="handleClick"
    type="button"
  >
    <span v-if="isSubmitting" class="spinner" aria-hidden="true" />
    {{ buttonText }}
  </button>
</template>

<style scoped>
.vote-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2, 8px);
  width: 100%;
  padding: 14px 24px;
  border: none;
  border-radius: var(--rounded-md, 10px);
  font-size: var(--text-body, 16px);
  font-weight: 600;
  cursor: pointer;
  min-height: 48px;
  transition: background-color 0.2s, opacity 0.2s;
}

.vote-button:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

/* States */
.voting-unvoted-loggedin,
.voting-unvoted-guest {
  background: var(--color-accent, #B8960C);
  color: #ffffff;
}

.voting-unvoted-loggedin:hover:not(:disabled) {
  background: var(--color-accent-light, #D4B84A);
}

.voting-voted {
  background: var(--color-success, #2D7A4F);
  color: #ffffff;
}

.voting-voted:hover:not(:disabled) {
  background: var(--color-primary-light, #2D7A4F);
}

.locked-voted,
.locked-unvoted,
.settled {
  background: #6B7280;
  color: #ffffff;
}

.submitting {
  opacity: 0.8;
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: vote-spin 0.6s linear infinite;
}

@keyframes vote-spin {
  to { transform: rotate(360deg); }
}
</style>
