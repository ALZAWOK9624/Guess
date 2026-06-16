<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

const isAdminDropdownOpen = ref(false)

interface AdminNavItem {
  to: string
  label: string
}

const adminNavItems: AdminNavItem[] = [
  { to: '/admin', label: '仪表盘' },
  { to: '/admin/races/new', label: '创建比赛' },
  { to: '/admin/horses', label: '马匹管理' },
  { to: '/admin/invite-codes', label: '邀请码' }
]

function toggleAdminDropdown() {
  isAdminDropdownOpen.value = !isAdminDropdownOpen.value
}

function closeAdminDropdown() {
  isAdminDropdownOpen.value = false
}

function handleLogout() {
  authStore.logout()
  router.push('/')
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && isAdminDropdownOpen.value) {
    closeAdminDropdown()
  }
}

function handleClickOutside(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (!target.closest('.admin-dropdown-area')) {
    closeAdminDropdown()
  }
}

watch(() => route.fullPath, () => {
  closeAdminDropdown()
})

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleKeydown)
})

/** Normalize route path for consistent matching */
function normalizedPath(path: string): string {
  return path.replace(/\/+$/, '') || '/'
}

function isAdminItemActive(item: AdminNavItem): boolean {
  const currentPath = normalizedPath(route.path)
  const itemPath = normalizedPath(item.to)
  if (itemPath === '/admin') {
    return currentPath === '/admin'
  }
  return currentPath.startsWith(itemPath)
}
</script>

<template>
  <div class="app-layout">
    <!-- Desktop Header (≥768px) -->
    <header class="desktop-header">
      <div class="header-inner">
        <router-link to="/" class="logo">
          <span class="logo-icon">&#127950;</span>
          <span class="logo-text">Guess</span>
        </router-link>

        <nav class="nav-links">
          <router-link to="/" class="nav-link">首页</router-link>
          <router-link to="/leaderboard" class="nav-link">排行榜</router-link>

          <!-- Admin Dropdown (desktop) -->
          <div v-if="authStore.isAdmin" class="admin-dropdown-area">
            <button
              class="nav-link admin-dropdown-trigger"
              :class="{ 'dropdown-open': isAdminDropdownOpen }"
              @click.stop="toggleAdminDropdown"
              :aria-expanded="isAdminDropdownOpen"
              aria-haspopup="true"
            >
              管理
              <svg class="chevron-icon" :class="{ open: isAdminDropdownOpen }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="6 9 12 15 18 9" />
              </svg>
            </button>

            <transition name="dropdown-fade">
              <nav v-if="isAdminDropdownOpen" class="admin-dropdown" role="menu">
                <router-link
                  v-for="item in adminNavItems"
                  :key="item.to"
                  :to="item.to"
                  class="admin-dropdown-item"
                  :class="{ active: isAdminItemActive(item) }"
                  role="menuitem"
                  @click="closeAdminDropdown"
                >
                  <svg class="dropdown-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <template v-if="item.to === '/admin'">
                      <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" />
                      <rect x="14" y="14" width="7" height="7" /><rect x="3" y="14" width="7" height="7" />
                    </template>
                    <template v-else-if="item.to === '/admin/races/new'">
                      <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="16" /><line x1="8" y1="12" x2="16" y2="12" />
                    </template>
                    <template v-else-if="item.to === '/admin/horses'">
                      <path d="M18 4h-3a3 3 0 0 0-3 3v0a3 3 0 0 0 3 3h3a3 3 0 0 0 3-3v0a3 3 0 0 0-3-3z" />
                      <path d="M6 4h3a3 3 0 0 1 3 3v0a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3v0a3 3 0 0 1 3-3z" />
                      <path d="M18 14h-3a3 3 0 0 0-3 3v0a3 3 0 0 0 3 3h3a3 3 0 0 0 3-3v0a3 3 0 0 0-3-3z" />
                      <path d="M6 14h3a3 3 0 0 1 3 3v0a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3v0a3 3 0 0 1 3-3z" />
                    </template>
                    <template v-else>
                      <rect x="3" y="11" width="18" height="11" rx="2" ry="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" />
                    </template>
                  </svg>
                  {{ item.label }}
                </router-link>
              </nav>
            </transition>
          </div>
        </nav>

        <div class="user-area">
          <template v-if="authStore.isLoggedIn">
            <span class="username">{{ authStore.user?.username }}</span>
            <button class="logout-btn" @click="handleLogout">退出</button>
          </template>
          <router-link v-else to="/login" class="login-btn">登录</router-link>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <slot />
    </main>

    <!-- Mobile Bottom Nav (<768px) -->
    <nav class="mobile-bottom-nav" aria-label="主导航">
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

      <!-- Admin Dropdown (mobile) -->
      <div v-if="authStore.isAdmin" class="admin-dropdown-area mobile-dropdown-area">
        <button
          class="nav-item"
          :class="{ 'active-dropdown': isAdminDropdownOpen }"
          @click.stop="toggleAdminDropdown"
          :aria-expanded="isAdminDropdownOpen"
          aria-haspopup="true"
        >
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="7" height="7" />
            <rect x="14" y="3" width="7" height="7" />
            <rect x="14" y="14" width="7" height="7" />
            <rect x="3" y="14" width="7" height="7" />
          </svg>
          <span class="nav-label">管理</span>
        </button>

        <transition name="dropdown-fade">
          <nav v-if="isAdminDropdownOpen" class="admin-dropdown mobile-dropdown" role="menu">
            <router-link
              v-for="item in adminNavItems"
              :key="item.to"
              :to="item.to"
              class="admin-dropdown-item"
              :class="{ active: isAdminItemActive(item) }"
              role="menuitem"
              @click="closeAdminDropdown"
            >
              <svg class="dropdown-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <template v-if="item.to === '/admin'">
                  <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" />
                  <rect x="14" y="14" width="7" height="7" /><rect x="3" y="14" width="7" height="7" />
                </template>
                <template v-else-if="item.to === '/admin/races/new'">
                  <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="16" /><line x1="8" y1="12" x2="16" y2="12" />
                </template>
                <template v-else-if="item.to === '/admin/horses'">
                  <path d="M18 4h-3a3 3 0 0 0-3 3v0a3 3 0 0 0 3 3h3a3 3 0 0 0 3-3v0a3 3 0 0 0-3-3z" />
                  <path d="M6 4h3a3 3 0 0 1 3 3v0a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3v0a3 3 0 0 1 3-3z" />
                  <path d="M18 14h-3a3 3 0 0 0-3 3v0a3 3 0 0 0 3 3h3a3 3 0 0 0 3-3v0a3 3 0 0 0-3-3z" />
                  <path d="M6 14h3a3 3 0 0 1 3 3v0a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3v0a3 3 0 0 1 3-3z" />
                </template>
                <template v-else>
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" />
                </template>
              </svg>
              {{ item.label }}
            </router-link>
          </nav>
        </transition>
      </div>
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
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 2px;
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

/* Admin Dropdown Trigger - desktop */
.admin-dropdown-trigger {
  position: relative;
}

.admin-dropdown-trigger.dropdown-open {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.chevron-icon {
  width: 12px;
  height: 12px;
  transition: transform var(--transition-fast);
}

.chevron-icon.open {
  transform: rotate(180deg);
}

.user-area {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
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
  text-decoration: none;
}

.login-btn:hover {
  background: rgba(255, 255, 255, 0.25);
}

.username {
  font-size: var(--text-body-sm);
  font-weight: 600;
  color: #fff;
}

.logout-btn {
  display: inline-flex;
  align-items: center;
  padding: var(--spacing-1) var(--spacing-3);
  border-radius: var(--rounded-md);
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.85);
  font-size: var(--text-body-sm);
  border: 1px solid rgba(255, 255, 255, 0.2);
  cursor: pointer;
  transition: background var(--transition-fast);
  min-height: 32px;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

/* =========================================
   Admin Dropdown (desktop & mobile)
   ========================================= */

.admin-dropdown-area {
  position: relative;
}

.admin-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  min-width: 180px;
  max-height: 360px;
  overflow-y: auto;
  background: #fff;
  border-radius: var(--rounded-md);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  padding: var(--spacing-1);
  z-index: 200;
}

.mobile-dropdown-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.mobile-dropdown-area .nav-item {
  flex: none;
  width: 100%;
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  color: var(--color-ink-secondary);
  font-size: 10px;
  font-weight: 500;
  -webkit-tap-highlight-color: transparent;
  transition: color var(--transition-fast);
  padding: 4px 0;
}

.mobile-dropdown-area .nav-item.active-dropdown {
  color: var(--color-primary);
}

.mobile-dropdown {
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  min-width: 200px;
  background: #fff;
  border-radius: var(--rounded-md);
  box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.1);
  padding: var(--spacing-1);
  z-index: 200;
}

.admin-dropdown-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--rounded-sm);
  color: var(--color-ink-primary);
  font-size: var(--text-body-sm);
  text-decoration: none;
  transition: background var(--transition-fast), color var(--transition-fast);
}

.admin-dropdown-item:hover {
  background: var(--color-surface-base);
  color: var(--color-primary);
}

.admin-dropdown-item.active {
  background: #E8F5E9;
  color: var(--color-primary);
  font-weight: 600;
}

.dropdown-item-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

/* Dropdown transition */
.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: opacity var(--transition-fast), transform var(--transition-fast);
}

.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.mobile-dropdown.dropdown-fade-enter-from,
.mobile-dropdown.dropdown-fade-leave-to {
  transform: translateY(4px);
}

/* =========================================
   Main Content
   ========================================= */

.main-content {
  min-height: 100vh;
  min-height: 100dvh;
  padding-bottom: calc(var(--bottom-nav-height) + env(safe-area-inset-bottom, 0));
}

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
   Responsive
   ========================================= */

@media (min-width: 768px) {
  .desktop-header {
    display: block;
  }

  .mobile-bottom-nav {
    display: none;
  }
}

/* =========================================
   Reduced Motion
   ========================================= */

@media (prefers-reduced-motion: reduce) {
  .dropdown-fade-enter-active,
  .dropdown-fade-leave-active {
    transition: none;
  }
}
</style>
