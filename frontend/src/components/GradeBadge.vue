<script setup lang="ts">
/**
 * GradeBadge — Race grade indicator badge (flat style).
 * All grades share the same muted gray appearance.
 */

defineProps<{
  grade: string
}>()

const labelMap: Record<string, string> = {
  G1: 'G1',
  G2: 'G2',
  G3: 'G3',
  JPN1: 'JPN1',
  JPN2: 'JPN2',
  其他: '其他',
  自定义: '自定义',
}
</script>

<template>
  <span
    class="grade-badge"
    :class="`grade-${(grade ?? '').toLowerCase()}`"
  >
    {{ labelMap[grade] || grade }}
  </span>
</template>

<style scoped>
.grade-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: var(--rounded-sm, 6px);
  font-size: 12px;
  font-weight: 700;
  font-family: 'Barlow Condensed', 'system-ui', sans-serif;
  line-height: 1.4;
  white-space: nowrap;
  background: #6B7280;
  color: #FFFFFF;
}

.grade-自定义 {
  border: 1px dashed var(--color-border-strong, #A8B8A4);
}
</style>
