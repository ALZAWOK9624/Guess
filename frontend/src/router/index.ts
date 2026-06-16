import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

// Extend RouteMeta to support custom meta fields
declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    isAdmin?: boolean
  }
}

const guestPageNames: string[] = ['login', 'register', 'reset-password']

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/pages/HomePage.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/pages/LoginPage.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/pages/RegisterPage.vue'),
    meta: { title: '注册' }
  },
  {
    path: '/reset-password',
    name: 'reset-password',
    component: () => import('@/pages/ResetPasswordPage.vue'),
    meta: { title: '重置密码' }
  },
  {
    path: '/leaderboard',
    name: 'leaderboard',
    component: () => import('@/pages/LeaderboardPage.vue'),
    meta: { title: '排行榜' }
  },
  {
    path: '/races/:id',
    name: 'race-detail',
    component: () => import('@/pages/RaceDetailPage.vue'),
    meta: { title: '比赛详情' }
  },
  // Admin routes — top-level, share AppLayout with all other pages
  {
    path: '/admin',
    name: 'admin-dashboard',
    component: () => import('@/pages/admin/DashboardPage.vue'),
    meta: { requiresAuth: true, isAdmin: true, title: '管理后台' }
  },
  {
    path: '/admin/horses',
    name: 'admin-horses',
    component: () => import('@/pages/admin/HorsesPage.vue'),
    meta: { requiresAuth: true, isAdmin: true, title: '马匹管理' }
  },
  {
    path: '/admin/races/new',
    name: 'admin-create-race',
    component: () => import('@/pages/admin/CreateRacePage.vue'),
    meta: { requiresAuth: true, isAdmin: true, title: '创建比赛' }
  },
  {
    path: '/admin/races/:id/edit',
    name: 'admin-edit-race',
    component: () => import('@/pages/admin/EditRacePage.vue'),
    meta: { requiresAuth: true, isAdmin: true, title: '编辑比赛' }
  },
  {
    path: '/admin/races/:id/results',
    name: 'admin-results',
    component: () => import('@/pages/admin/ResultsPage.vue'),
    meta: { requiresAuth: true, isAdmin: true, title: '结果录入' }
  },
  {
    path: '/admin/invite-codes',
    name: 'admin-invite-codes',
    component: () => import('@/pages/admin/InviteCodesPage.vue'),
    meta: { requiresAuth: true, isAdmin: true, title: '邀请码管理' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Auth guard: protect admin routes, redirect logged-in users away from auth pages
router.beforeEach((to) => {
  const authStore = useAuthStore()

  // Admin-only routes — requires admin privileges
  if (to.meta.isAdmin && !authStore.isAdmin) {
    return { name: 'home' }
  }

  // Auth-required routes — requires login
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  // Redirect logged-in users away from login/register/reset-password
  if (authStore.isLoggedIn && guestPageNames.includes(String(to.name))) {
    return { name: 'home' }
  }
})

export default router
