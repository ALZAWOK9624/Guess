<script setup lang="ts">
import { ref, watch } from 'vue'

const sidebarOpen = ref(false)

function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value
}

function closeSidebar() {
  if (window.innerWidth >= 768) return
  sidebarOpen.value = false
}

// Lock body scroll when sidebar is open on mobile
watch(sidebarOpen, (open) => {
  if (open && window.innerWidth < 768) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

// Handle resize across 768px boundary
window.addEventListener('resize', () => {
  if (window.innerWidth >= 768) {
    sidebarOpen.value = false
    document.body.style.overflow = ''
  }
})
</script>

<template>
  <div class="admin-layout">
    <!-- Mobile Header with Hamburger -->
    <header class="mobile-admin-header">
      <button class="hamburger-btn" @click="toggleSidebar" aria-label="切换菜单">
        <span class="hamburger-line" :class="{ open: sidebarOpen }"></span>
        <span class="hamburger-line" :class="{ open: sidebarOpen }"></span>
        <span class="hamburger-line" :class="{ open: sidebarOpen }"></span>
      </button>
      <span class="mobile-admin-title">管理后台</span>
    </header>

    <!-- Sidebar -->
    <aside class="sidebar" :class="{ open: sidebarOpen }">
      <div class="sidebar-header">
        <router-link to="/" class="sidebar-logo">
          <span class="logo-icon">&#127950;</span>
          <span class="logo-text">Guess</span>
        </router-link>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/admin" class="sidebar-link" @click="closeSidebar">
          <svg class="sidebar-link-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="7" height="7" />
            <rect x="14" y="3" width="7" height="7" />
            <rect x="14" y="14" width="7" height="7" />
            <rect x="3" y="14" width="7" height="7" />
          </svg>
          仪表盘
        </router-link>

        <router-link to="/admin/races/new" class="sidebar-link" @click="closeSidebar">
          <svg class="sidebar-link-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="16" />
            <line x1="8" y1="12" x2="16" y2="12" />
          </svg>
          创建比赛
        </router-link>

        <router-link to="/admin/horses" class="sidebar-link" @click="closeSidebar">
          <svg class="sidebar-link-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 4h-3a3 3 0 0 0-3 3v0a3 3 0 0 0 3 3h3a3 3 0 0 0 3-3v0a3 3 0 0 0-3-3z" />
            <path d="M6 4h3a3 3 0 0 1 3 3v0a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3v0a3 3 0 0 1 3-3z" />
            <path d="M18 14h-3a3 3 0 0 0-3 3v0a3 3 0 0 0 3 3h3a3 3 0 0 0 3-3v0a3 3 0 0 0-3-3z" />
            <path d="M6 14h3a3 3 0 0 1 3 3v0a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3v0a3 3 0 0 1 3-3z" />
          </svg>
          马匹管理
        </router-link>

        <router-link to="/admin/invite-codes" class="sidebar-link" @click="closeSidebar">
          <svg class="sidebar-link-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
          邀请码
        </router-link>
      </nav>
    </aside>

    <!-- Overlay for mobile -->
    <div v-if="sidebarOpen" class="sidebar-overlay" @click="closeSidebar"></div>

    <!-- Main Content -->
    <div class="admin-content">
      <router-view />
    </div>
  </div>
</template>

<style scoped>
/* =========================================
   Admin Layout Container
   ========================================= */

.admin-layout {
  display: flex;
  min-height: 100dvh;
}

/* =========================================
   Sidebar
   ========================================= */

.sidebar {
  width: var(--sidebar-width);
  background: var(--color-primary);
  color: #fff;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 200;
  transform: translateX(-100%);
  transition: transform var(--transition-fast);
}

.sidebar.open {
  transform: translateX(0);
}

.sidebar-header {
  padding: var(--spacing-5);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-family: var(--font-display);
  font-size: var(--text-subheading);
  font-weight: 700;
  color: #fff;
  text-decoration: none;
}

.logo-icon {
  font-size: 20px;
}

.sidebar-nav {
  padding: var(--spacing-3);
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  overflow-y: auto;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--rounded-sm);
  color: rgba(255, 255, 255, 0.8);
  font-size: var(--text-body-sm);
  text-decoration: none;
  transition: background var(--transition-fast), color var(--transition-fast);
}

.sidebar-link:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.sidebar-link.router-link-active,
.sidebar-link.router-link-exact-active {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  font-weight: 600;
}

.sidebar-link-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

/* =========================================
   Mobile Admin Header
   ========================================= */

.mobile-admin-header {
  display: flex;
  align-items: center;
  height: var(--header-height);
  padding: 0 var(--spacing-4);
  background: var(--color-primary);
  color: #fff;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 150;
}

.mobile-admin-title {
  font-family: var(--font-display);
  font-size: var(--text-subheading);
  font-weight: 600;
  margin-left: var(--spacing-3);
}

.hamburger-btn {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  width: 44px;
  height: 44px;
  padding: 10px;
  border-radius: var(--rounded-sm);
  cursor: pointer;
  background: none;
  border: none;
}

.hamburger-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.hamburger-line {
  display: block;
  width: 24px;
  height: 2px;
  background: #fff;
  border-radius: 2px;
  transition: transform var(--transition-fast), opacity var(--transition-fast);
}

.hamburger-line:nth-child(1).open {
  transform: rotate(45deg) translate(5px, 5px);
}

.hamburger-line:nth-child(2).open {
  opacity: 0;
}

.hamburger-line:nth-child(3).open {
  transform: rotate(-45deg) translate(5px, -5px);
}

/* =========================================
   Sidebar Overlay (Mobile)
   ========================================= */

.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 199;
}

/* =========================================
   Main Content
   ========================================= */

.admin-content {
  flex: 1;
  padding: var(--spacing-6);
  padding-top: calc(var(--header-height) + var(--spacing-4));
  min-width: 0;
}

/* =========================================
   Desktop (≥768px)
   ========================================= */

@media (min-width: 768px) {
  .sidebar {
    position: fixed;
    transform: none;
  }

  .mobile-admin-header {
    display: none;
  }

  .sidebar-overlay {
    display: none !important;
  }

  .admin-content {
    margin-left: var(--sidebar-width);
    padding-top: var(--spacing-6);
  }
}
</style>
