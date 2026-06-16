<script setup lang="ts">
import InviteCodeTable from '@/components/InviteCodeTable.vue'
</script>

<template>
  <div class="invite-codes-page">
    <h1 class="page-title">邀请码管理</h1>
    <p class="page-description">
      邀请码是用户注册的唯一凭证。生成时需要绑定 QQ 号，用户注册时需提供匹配的 QQ 号和邀请码。
      已绑定的邀请码可点击「删除」同时移除用户和其投票记录。
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
