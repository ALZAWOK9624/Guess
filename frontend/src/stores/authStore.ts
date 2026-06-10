import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<{ id: number; username: string; isAdmin: boolean } | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)

  const isLoggedIn = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.isAdmin ?? false)

  function setUser(u: typeof user.value) {
    user.value = u
  }

  function setTokens(access: string, refresh: string) {
    accessToken.value = access
    refreshToken.value = refresh
  }

  function logout() {
    user.value = null
    accessToken.value = null
    refreshToken.value = null
  }

  return { user, accessToken, refreshToken, isLoggedIn, isAdmin, setUser, setTokens, logout }
})
