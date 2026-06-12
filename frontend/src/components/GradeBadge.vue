<script setup lang="ts">
/**
 * GradeBadge — Race grade indicator badge.
 *
 * Grades:
 * - G1: Gold background
 * - G2_JPN1: Gray background
 * - YOUNG_G1: Light green background
 * - CUSTOM: Gray background with dashed border
 */

defineProps<{
  grade: string
}>()

const labelMap: Record<string, string> = {
  G1: 'G1',
  G2_JPN1: 'G2·JPN1',
  YOUNG_G1: '2岁G1',
  CUSTOM: '自定义',
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
}

.grade-g1 {
  background: var(--color-accent, #B8960C);
  color: #FFFFFF;
}

.grade-g2_jpn1 {
  background: #6B7280;
  color: #FFFFFF;
}

.grade-young_g1 {
  background: var(--color-primary-light, #2D7A4F);
  color: #FFFFFF;
}

.grade-custom {
  background: #6B7280;
  color: #FFFFFF;
  border: 1px dashed var(--color-border-strong, #A8B8A4);
}
</style>
