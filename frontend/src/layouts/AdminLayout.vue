<script setup lang="ts">
</script>

<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <nav>
        <router-link to="/admin">仪表盘</router-link>
        <router-link to="/admin/horses">马匹管理</router-link>
        <router-link to="/admin/races/new">创建比赛</router-link>
        <router-link to="/admin/invite-codes">邀请码</router-link>
      </nav>
    </aside>
    <main class="main-content">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
}
.sidebar {
  width: var(--sidebar-width);
  background: var(--color-primary);
  color: white;
  padding: 16px;
}
.sidebar nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.sidebar a {
  padding: 8px 12px;
  border-radius: 6px;
}
.sidebar a:hover {
  background: rgba(255,255,255,0.1);
}
.main-content {
  flex: 1;
  padding: 24px;
}
</style>
