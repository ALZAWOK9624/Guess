<script setup lang="ts">
/**
 * StatusBadge — Race status capsule indicator.
 *
 * Statuses:
 * - voting: Green background
 * - locked: Gray background + 🔒
 * - settled: Dark green background + ✓
 */

defineProps<{
  status: string
}>()

const labelMap: Record<string, string> = {
  voting: '投票中',
  locked: '已锁定',
  settled: '已结算',
}

const iconMap: Record<string, string> = {
  locked: ' 🔒',
  settled: ' ✓',
}
</script>

<template>
  <span class="status-badge" :class="`status-${status}`">
    {{ labelMap[status] || status }}{{ iconMap[status] || '' }}
  </span>
</template>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
  line-height: 1.4;
  white-space: nowrap;
}

.status-voting {
  background: var(--color-primary-light, #2D7A4F);
  color: #FFFFFF;
}

.status-locked {
  background: #6B7280;
  color: #FFFFFF;
}

.status-settled {
  background: var(--color-primary-dark, #0D3A1F);
  color: #FFFFFF;
}
</style>
