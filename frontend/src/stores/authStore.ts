import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { register as registerApi, login as loginApi } from '@/api/auth'
import type { LoginRequest, RegisterRequest, UserInfo } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfo | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)

  const isLoggedIn = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.is_admin ?? false)

  function setUser(u: UserInfo | null) {
    user.value = u
  }

  function setTokens(access: string, refresh: string) {
    accessToken.value = access
    refreshToken.value = refresh
  }

  function persistAuth(data: { accessToken: string; refreshToken: string; user: UserInfo }) {
    setUser(data.user)
    setTokens(data.accessToken, data.refreshToken)
    localStorage.setItem('auth', JSON.stringify(data))
  }

  function clearAuth() {
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
