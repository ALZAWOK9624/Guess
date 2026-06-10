<script setup lang="ts">
import { useAuthStore } from '@/stores/authStore'
import { useRoute } from 'vue-router'
import { computed } from 'vue'

const authStore = useAuthStore()
const route = useRoute()
const isAdminRoute = computed(() => route.path.startsWith('/admin'))
</script>

<template>
  <div class="app-layout">
    <!-- Desktop Header (≥768px) — hidden on admin routes -->
    <header v-if="!isAdminRoute" class="desktop-header">
      <div class="header-inner">
        <router-link to="/" class="logo">
          <span class="logo-icon">&#127950;</span>
          <span class="logo-text">Guess</span>
        </router-link>

        <nav class="nav-links">
          <router-link to="/" class="nav-link">首页</router-link>
          <router-link to="/leaderboard" class="nav-link">排行榜</router-link>
          <router-link v-if="authStore.isAdmin" to="/admin" class="nav-link">管理</router-link>
        </nav>

        <div class="user-area">
          <!-- Placeholder: full auth implementation in Story 1.5b -->
          <router-link to="/login" class="login-btn">登录</router-link>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <slot />
    </main>

    <!-- Mobile Bottom Nav (<768px) — hidden on admin routes -->
    <nav v-if="!isAdminRoute" class="mobile-bottom-nav" aria-label="主导航">
      <router-link to="/" class="nav-item">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
          <polyline points="9 22 9 12 15 12 15 22" />
        </svg>
        <span class="nav-label">首页</span>
      </router-link>

      <router-link to="/leaderboard" class="nav-item">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5C7 4 6 7 6 9z" />
          <path d="M18 9h1.5a2.5 2.5 0 0 0 0-5C17 4 18 7 18 9z" />
          <path d="M4 22h16" />
          <path d="M10 22V14h4v8" />
          <path d="M12 14c-1.5 0-3-2-3-4V7c0-1.1.9-2 2-2h2a2 2 0 0 1 2 2v3c0 2-1.5 4-3 4z" />
        </svg>
        <span class="nav-label">排行榜</span>
      </router-link>

      <router-link v-if="authStore.isAdmin" to="/admin" class="nav-item">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="7" height="7" />
          <rect x="14" y="3" width="7" height="7" />
          <rect x="14" y="14" width="7" height="7" />
          <rect x="3" y="14" width="7" height="7" />
        </svg>
        <span class="nav-label">管理</span>
      </router-link>
    </nav>
  </div>
</template>

<style scoped>
/* =========================================
   Desktop Header (≥768px)
   ========================================= */

.desktop-header {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--header-height);
  background: var(--color-primary);
  color: #fff;
  z-index: 100;
}

.header-inner {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 0 var(--spacing-4);
  height: 100%;
  display: flex;
  align-items: center;
  gap: var(--spacing-8);
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-family: var(--font-display);
  font-size: var(--text-subheading);
  font-weight: 700;
  color: #fff;
  text-decoration: none;
  white-space: nowrap;
}

.logo-icon {
  font-size: 20px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.nav-link {
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--rounded-sm);
  color: rgba(255, 255, 255, 0.85);
  font-size: var(--text-body-sm);
  transition: background var(--transition-fast), color var(--transition-fast);
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.nav-link.router-link-active,
.nav-link.router-link-exact-active {
  color: #fff;
  font-weight: 600;
}

.user-area {
  margin-left: auto;
}

.login-btn {
  display: inline-flex;
  align-items: center;
  padding: var(--spacing-1) var(--spacing-4);
  border-radius: var(--rounded-md);
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  font-size: var(--text-body-sm);
  transition: background var(--transition-fast);
}

.login-btn:hover {
  background: rgba(255, 255, 255, 0.25);
}

/* =========================================
   Main Content
   ========================================= */

.main-content {
  min-height: 100vh;
  min-height: 100dvh;
  padding-bottom: calc(var(--bottom-nav-height) + env(safe-area-inset-bottom, 0));
}

/* Desktop main content padding for header */
@media (min-width: 768px) {
  .main-content {
    padding-top: var(--header-height);
    padding-bottom: 0;
    max-width: var(--max-width);
    margin: 0 auto;
    padding-left: var(--spacing-4);
    padding-right: var(--spacing-4);
  }
}

/* =========================================
   Mobile Bottom Nav (<768px)
   ========================================= */

.mobile-bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: var(--bottom-nav-height);
  padding-bottom: env(safe-area-inset-bottom, 0);
  display: flex;
  align-items: stretch;
  background: var(--color-surface-raised);
  border-top: 1px solid var(--color-border-hairline);
  z-index: 100;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  color: var(--color-ink-secondary);
  text-decoration: none;
  font-size: 10px;
  font-weight: 500;
  -webkit-tap-highlight-color: transparent;
  transition: color var(--transition-fast);
}

.nav-item:hover {
  color: var(--color-primary);
}

.nav-item.router-link-active,
.nav-item.router-link-exact-active {
  color: var(--color-primary);
  font-weight: 600;
}

.nav-icon {
  width: 24px;
  height: 24px;
}

.nav-label {
  line-height: 1;
}

/* =========================================
   Responsive: Show/hide headers
   ========================================= */

@media (min-width: 768px) {
  .desktop-header {
    display: block;
  }

  .mobile-bottom-nav {
    display: none;
  }
}
</style>
