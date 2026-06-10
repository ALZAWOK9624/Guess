<script setup lang="ts">
const props = withDefaults(defineProps<{
  skeleton?: boolean
}>(), {
  skeleton: false,
})
</script>

<template>
  <div class="race-card" :class="{ 'is-skeleton': skeleton }">
    <!-- Skeleton mode -->
    <template v-if="skeleton">
      <div class="card-header">
        <div class="skeleton-block grade-badge-skeleton"></div>
        <div class="skeleton-block title-skeleton"></div>
        <div class="skeleton-block badge-skeleton"></div>
      </div>
      <div class="card-body">
        <div class="skeleton-block date-skeleton"></div>
        <div class="skeleton-block meta-skeleton"></div>
      </div>
    </template>

    <!-- Normal mode (content slot for future stories) -->
    <template v-else>
      <slot />
    </template>
  </div>
</template>

<style scoped>
.race-card {
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-hairline);
  border-radius: var(--rounded-lg);
  padding: var(--spacing-16);
  transition: box-shadow 0.2s;
}

.race-card.is-skeleton {
  pointer-events: none;
}

.card-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-8);
  margin-bottom: var(--spacing-12);
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-8);
}

.skeleton-block {
  background: linear-gradient(
    90deg,
    var(--color-surface-base) 25%,
    var(--color-border-hairline) 50%,
    var(--color-surface-base) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
  border-radius: var(--rounded-sm);
}

.grade-badge-skeleton {
  width: 40px;
  height: 24px;
}

.title-skeleton {
  flex: 1;
  height: 20px;
  max-width: 200px;
}

.badge-skeleton {
  width: 60px;
  height: 22px;
  margin-left: auto;
}

.date-skeleton {
  width: 120px;
  height: 14px;
}

.meta-skeleton {
  width: 160px;
  height: 14px;
}

@media (prefers-reduced-motion: reduce) {
  .skeleton-block {
    animation: none;
    background: var(--color-surface-base);
  }
  .race-card {
    transition: none;
  }
}
</style>
