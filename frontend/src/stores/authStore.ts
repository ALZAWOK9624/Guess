import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { register as registerApi, login as loginApi } from '@/api/auth'
import { getTokenExpiry } from '@/utils/jwt'
import type { LoginRequest, RegisterRequest, UserInfo } from '@/types/auth'

const GUEST_PATHS = ['/login', '/register', '/reset-password']

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfo | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)

  const isLoggedIn = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.is_admin ?? false)

  let sessionExpiryTimer: ReturnType<typeof setTimeout> | null = null

  function setUser(u: UserInfo | null) {
    user.value = u
  }

  function setTokens(access: string, refresh: string) {
    accessToken.value = access
    refreshToken.value = refresh
  }

  function clearSessionExpiryTimer() {
    if (sessionExpiryTimer) {
      clearTimeout(sessionExpiryTimer)
      sessionExpiryTimer = null
    }
  }

  function redirectToLoginWithExpiredSession() {
    const pathname = window.location.pathname
    if (GUEST_PATHS.includes(pathname)) {
      return
    }
    const currentPath = window.location.pathname + window.location.search
    window.location.href = `/login?session=expired&redirect=${encodeURIComponent(currentPath)}`
  }

  function handleSessionExpired() {
    const wasAdmin = user.value?.is_admin ?? false
    clearAuth()
    if (wasAdmin) {
      redirectToLoginWithExpiredSession()
    }
  }

  function scheduleSessionExpiry(token: string) {
    clearSessionExpiryTimer()
    if (!user.value?.is_admin) {
      return
    }
    const exp = getTokenExpiry(token)
    if (!exp) return

    const delay = exp * 1000 - Date.now()
    if (delay <= 0) {
      handleSessionExpired()
      return
    }

    sessionExpiryTimer = setTimeout(() => {
      handleSessionExpired()
    }, delay)
  }

  function persistAuth(data: { accessToken: string; refreshToken: string; user: UserInfo }) {
    setUser(data.user)
    setTokens(data.accessToken, data.refreshToken)
    localStorage.setItem('auth', JSON.stringify(data))
    scheduleSessionExpiry(data.refreshToken)
  }

  function clearAuth() {
    clearSessionExpiryTimer()
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('auth')
  }

  async function register(data: RegisterRequest) {
    const result = await registerApi(data)
    persistAuth({
      accessToken: result.access_token,
      refreshToken: result.refresh_token,
      user: result.user,
    })
  }

  async function login(data: LoginRequest) {
    const result = await loginApi(data)
    persistAuth({
      accessToken: result.access_token,
      refreshToken: result.refresh_token,
      user: result.user,
    })
  }

  function logout() {
    clearAuth()
  }

  // Restore session from localStorage on init
  function restoreSession() {
    const stored = localStorage.getItem('auth')
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        setUser(parsed.user)
        setTokens(parsed.accessToken, parsed.refreshToken)
        scheduleSessionExpiry(parsed.refreshToken)
      } catch {
        localStorage.removeItem('auth')
      }
    }
  }

  return {
    user,
    accessToken,
    refreshToken,
    isLoggedIn,
    isAdmin,
    setUser,
    setTokens,
    persistAuth,
    clearAuth,
    register,
    login,
    logout,
    restoreSession,
  }
})

