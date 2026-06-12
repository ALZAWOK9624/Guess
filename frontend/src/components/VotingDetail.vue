<script setup lang="ts">
import type { VoteListEntry } from '@/types/vote'

defineProps<{
  votes: VoteListEntry[]
  loading?: boolean
}>()
</script>

<template>
  <div class="voting-detail">
    <h3 class="section-title">投票分布</h3>

    <!-- Loading state -->
    <div v-if="loading" class="skeleton-list">
      <div v-for="n in 3" :key="n" class="skeleton-row" />
    </div>

    <!-- Empty state -->
    <div v-else-if="votes.length === 0" class="empty-state">
      暂无投票
    </div>

    <!-- Vote list -->
    <ul v-else class="vote-list">
      <li
        v-for="vote in votes"
        :key="index"
        class="vote-item"
      >
        <span class="vote-user">{{ vote.username }}</span>
        <span class="vote-arrow">→</span>
        <span class="vote-horse">{{ vote.horse_name }}</span>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.voting-detail {
  margin-top: var(--spacing-6, 24px);
}

.section-title {
  font-size: var(--text-subheading, 18px);
  font-weight: 600;
  color: var(--color-ink-primary, #1A2E1A);
  margin: 0 0 var(--spacing-3, 12px);
}

.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-row {
  height: 36px;
  background: var(--border-hairline, #D4DCD0);
  border-radius: var(--rounded-sm, 6px);
  animation: skeleton-shimmer 1.5s infinite ease-in-out;
}

.empty-state {
  font-size: var(--text-body, 16px);
  color: var(--color-ink-secondary, #4A5A4A);
  padding: var(--spacing-4, 16px) 0;
}

.vote-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2, 8px);
}

.vote-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-2, 8px);
  font-size: var(--text-body, 16px);
  padding: var(--spacing-2, 8px) 0;
  border-bottom: 1px solid var(--border-hairline, #D4DCD0);
}

.vote-item:last-child {
  border-bottom: none;
}

.vote-user {
  font-weight: 500;
  color: var(--color-ink-primary, #1A2E1A);
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.vote-arrow {
  color: var(--color-ink-disabled, #9CAA9C);
  flex-shrink: 0;
}

.vote-horse {
  color: var(--color-ink-primary, #1A2E1A);
  font-weight: 500;
}
</style>
