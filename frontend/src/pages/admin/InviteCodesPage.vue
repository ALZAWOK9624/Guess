<script setup lang="ts">
import InviteCodeTable from '@/components/InviteCodeTable.vue'
</script>

<template>
  <div class="invite-codes-page">
    <h1 class="page-title">邀请码管理</h1>
    <p class="page-description">
      邀请码是用户注册的唯一凭证，每个码终生绑定一个用户。
    </p>
    <InviteCodeTable />
  </div>
</template>

<style scoped>
.invite-codes-page {
  padding: var(--spacing-6, 24px);
}

.page-title {
  font-family: 'Barlow Condensed', system-ui, sans-serif;
  font-size: var(--text-heading, 24px);
  font-weight: 600;
  color: var(--color-ink-primary, #1A2E1A);
  margin: 0 0 var(--spacing-2, 8px);
}

.page-description {
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-secondary, #4A5A4A);
  margin: 0 0 var(--spacing-6, 24px);
}
</style>
