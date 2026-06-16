<script setup lang="ts">
/**
 * Admin Layout — top navigation bar with dropdown menu.
 * Replaces the old sidebar with a compact top-bar + dropdown pattern.
 */
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isDropdownOpen = ref(false)

interface NavItem {
  to: string
  label: string
}

const navItems: NavItem[] = [
  { to: '/admin', label: '仪表盘' },
  { to: '/admin/races/new', label: '创建比赛' },
  { to: '/admin/horses', label: '马匹管理' },
  { to: '/admin/invite-codes', label: '邀请码' }
]

/** Normalize route path: strip trailing slash for consistent matching */
function normalizedPath(path: string): string {
  return path.replace(/\/+$/, '') || '/'
}

/** Check if a nav item matches the current route */
function isActive(item: NavItem): boolean {
  const currentPath = normalizedPath(route.path)
  const itemPath = normalizedPath(item.to)
  if (itemPath === '/admin') {
    return currentPath === '/admin'
  }
  return currentPath.startsWith(itemPath)
}

function toggleDropdown() {
  isDropdownOpen.value = !isDropdownOpen.value
}

function closeDropdown() {
  isDropdownOpen.value = false
  // Return focus to trigger button
  const trigger = document.querySelector<HTMLButtonElement>('.nav-dropdown-trigger')
  trigger?.focus()
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && isDropdownOpen.value) {
    closeDropdown()
  }
}

function handleClickOutside(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (!target.closest('.admin-top-nav')) {
    closeDropdown()
  }
}

// Close dropdown on route change
watch(() => route.fullPath, () => {
  closeDropdown()
})

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <div class="admin-layout">
    <!-- Top Navigation Bar -->
    <header class="admin-top-nav">
      <div class="top-nav-inner">
        <router-link to="/" class="top-nav-brand">
          <span class="brand-icon">&#127950;</span>
          <span class="brand-text">Guess</span>
        </router-link>

        <span class="brand-separator" aria-hidden="true"></span>

        <span class="top-nav-title">管理后台</span>

        <div class="top-nav-menu-wrapper">
          <button
            class="nav-dropdown-trigger"
            :class="{ open: isDropdownOpen }"
            @click.stop="toggleDropdown"
            :aria-expanded="isDropdownOpen"
            aria-haspopup="true"
          >
            <svg class="trigger-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
            <span class="trigger-label">导航</span>
            <svg class="chevron-icon" :class="{ open: isDropdownOpen }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>

          <!-- Dropdown Menu -->
          <transition name="dropdown-fade">
            <nav v-if="isDropdownOpen" class="nav-dropdown" role="menu" @keydown.escape="closeDropdown">
              <router-link
                v-for="item in navItems"
                :key="item.to"
                :to="item.to"
                class="nav-dropdown-item"
                :class="{ active: isActive(item) }"
                role="menuitem"
                @click="closeDropdown"
              >
                <svg class="dropdown-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <!-- 仪表盘 -->
                  <template v-if="item.to === '/admin'">
                    <rect x="3" y="3" width="7" height="7" />
                    <rect x="14" y="3" width="7" height="7" />
                    <rect x="14" y="14" width="7" height="7" />
                    <rect x="3" y="14" width="7" height="7" />
                  </template>
                  <!-- 创建比赛 -->
                  <template v-else-if="item.to === '/admin/races/new'">
                    <circle cx="12" cy="12" r="10" />
                    <line x1="12" y1="8" x2="12" y2="16" />
                    <line x1="8" y1="12" x2="16" y2="12" />
                  </template>
                  <!-- 马匹管理 -->
                  <template v-else-if="item.to === '/admin/horses'">
                    <path d="M18 4h-3a3 3 0 0 0-3 3v0a3 3 0 0 0 3 3h3a3 3 0 0 0 3-3v0a3 3 0 0 0-3-3z" />
                    <path d="M6 4h3a3 3 0 0 1 3 3v0a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3v0a3 3 0 0 1 3-3z" />
                    <path d="M18 14h-3a3 3 0 0 0-3 3v0a3 3 0 0 0 3 3h3a3 3 0 0 0 3-3v0a3 3 0 0 0-3-3z" />
                    <path d="M6 14h3a3 3 0 0 1 3 3v0a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3v0a3 3 0 0 1 3-3z" />
                  </template>
                  <!-- 邀请码 -->
                  <template v-else>
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                  </template>
                </svg>
                {{ item.label }}
              </router-link>
            </nav>
          </transition>
        </div>
      </div>
    </header>

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
  min-height: 100dvh;
}

/* =========================================
   Top Navigation Bar
   ========================================= */

.admin-top-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--header-height);
  background: var(--color-primary);
  color: #fff;
  z-index: 200;
}

.top-nav-inner {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 0 var(--spacing-4);
  height: 100%;
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.top-nav-brand {
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

.brand-icon {
  font-size: 20px;
}

.brand-separator {
  width: 1px;
  height: 24px;
  background: rgba(255, 255, 255, 0.2);
  flex-shrink: 0;
}

.top-nav-title {
  font-family: var(--font-display);
  font-size: var(--text-body);
  font-weight: 600;
  opacity: 0.9;
  white-space: nowrap;
}

/* =========================================
   Dropdown Trigger Button
   ========================================= */

.top-nav-menu-wrapper {
  margin-left: auto;
  position: relative;
}

.nav-dropdown-trigger {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-1) var(--spacing-3);
  height: 36px;
  border-radius: var(--rounded-sm);
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-size: var(--text-body-sm);
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.15);
  transition: background var(--transition-fast);
  white-space: nowrap;
}

.nav-dropdown-trigger:hover {
  background: rgba(255, 255, 255, 0.2);
}

.nav-dropdown-trigger.open {
  background: rgba(255, 255, 255, 0.2);
}

.trigger-icon {
  width: 18px;
  height: 18px;
}

.trigger-label {
  display: none;
}

.chevron-icon {
  width: 14px;
  height: 14px;
  transition: transform var(--transition-fast);
}

.chevron-icon.open {
  transform: rotate(180deg);
}

/* =========================================
   Dropdown Menu
   ========================================= */

.nav-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  min-width: 200px;
  max-height: 360px;
  overflow-y: auto;
  background: #fff;
  border-radius: var(--rounded-md);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  padding: var(--spacing-1);
}

.nav-dropdown-item {
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

.nav-dropdown-item:hover {
  background: var(--color-surface-base);
  color: var(--color-primary);
}

.nav-dropdown-item.active {
  background: #E8F5E9;
  color: var(--color-primary);
  font-weight: 600;
}

.dropdown-item-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

/* =========================================
   Dropdown Transition
   ========================================= */

.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: opacity var(--transition-fast), transform var(--transition-fast);
}

.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* =========================================
   Main Content
   ========================================= */

.admin-content {
  padding: var(--spacing-6);
  padding-top: calc(var(--header-height) + var(--spacing-4));
  max-width: var(--max-width);
  margin: 0 auto;
}

/* =========================================
   Desktop (≥768px) — show trigger label
   ========================================= */

@media (min-width: 768px) {
  .trigger-label {
    display: inline;
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
