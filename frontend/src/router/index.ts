import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

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
  {
    path: '/admin',
    name: 'admin-dashboard',
    component: () => import('@/pages/admin/DashboardPage.vue'),
    meta: { title: '管理后台', requiresAuth: true, isAdmin: true }
  },
  {
    path: '/admin/horses',
    name: 'admin-horses',
    component: () => import('@/pages/admin/HorsesPage.vue'),
    meta: { title: '马匹管理', requiresAuth: true, isAdmin: true }
  },
  {
    path: '/admin/races/new',
    name: 'admin-create-race',
    component: () => import('@/pages/admin/CreateRacePage.vue'),
    meta: { title: '创建比赛', requiresAuth: true, isAdmin: true }
  },
  {
    path: '/admin/races/:id/edit',
    name: 'admin-edit-race',
    component: () => import('@/pages/admin/EditRacePage.vue'),
    meta: { title: '编辑比赛', requiresAuth: true, isAdmin: true }
  },
  {
    path: '/admin/races/:id/results',
    name: 'admin-results',
    component: () => import('@/pages/admin/ResultsPage.vue'),
    meta: { title: '结果录入', requiresAuth: true, isAdmin: true }
  },
  {
    path: '/admin/invite-codes',
    name: 'admin-invite-codes',
    component: () => import('@/pages/admin/InviteCodesPage.vue'),
    meta: { title: '邀请码管理', requiresAuth: true, isAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Auth guard placeholder — will be fully implemented in Story 1.5b
router.beforeEach((to) => {
  if (to.meta.requiresAuth) {
    // TODO: Check auth store state
  }
})

export default router
