<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute, type LocationQueryValue } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

type LoginMode = 'username' | 'qq' | 'invite_code'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loginMode = ref<LoginMode>('username')
const username = ref('')
const qq = ref('')
const inviteCode = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref(
  normalizeQuery(route.query.reset) === 'success' ? '密码重置成功，请用新密码登录' : ''
)
const sessionExpiredMessage = computed(() =>
  normalizeQuery(route.query.session) === 'expired' ? '登录状态已过期，请重新登录' : ''
)

function normalizeQuery(value: LocationQueryValue | LocationQueryValue[]): string | undefined {
  if (value === null || value === undefined) return undefined
  const first = Array.isArray(value) ? value[0] : value
  return first ?? undefined
}

const tabs = [
  { mode: 'username' as LoginMode, label: '用户名登录' },
  { mode: 'qq' as LoginMode, label: 'QQ登录' },
  { mode: 'invite_code' as LoginMode, label: '邀请码登录' },
]


function switchMode(mode: LoginMode) {
  loginMode.value = mode
  errorMessage.value = ''
}

function clearError() {
  errorMessage.value = ''
}

function validateForm(): boolean {
  if (loginMode.value === 'username') {
    if (!username.value.trim()) {
      errorMessage.value = '用户名不能为空'
      return false
    }
    if (!password.value) {
      errorMessage.value = '密码不能为空'
      return false
    }
  } else if (loginMode.value === 'qq') {
    if (!qq.value.trim()) {
      errorMessage.value = 'QQ 号不能为空'
      return false
    }
    if (!password.value) {
      errorMessage.value = '密码不能为空'
      return false
    }
  } else {
    if (!inviteCode.value.trim()) {
      errorMessage.value = '邀请码不能为空'
      return false
    }
    if (inviteCode.value.trim().length !== 8) {
      errorMessage.value = '邀请码必须为 8 位字符'
      return false
    }
  }
  return true
}

async function handleSubmit() {
  if (!validateForm()) return

  loading.value = true
  errorMessage.value = ''

  try {
    const loginData: Record<string, string> = {}
    if (loginMode.value === 'username') {
      loginData.username = username.value.trim()
      loginData.password = password.value
    } else if (loginMode.value === 'qq') {
      loginData.qq = qq.value.trim()
      loginData.password = password.value
    } else {
      loginData.invite_code = inviteCode.value.trim().toUpperCase()
    }
    await authStore.login(loginData as any)
    const redirect = normalizeQuery(route.query.redirect) || '/'
    router.push(redirect)
  } catch (err: any) {
    if (err?.response?.status === 422) {
      errorMessage.value = '输入格式有误'
    } else if (err?.message === 'Network Error') {
      errorMessage.value = '网络错误，请重试'
    } else if (err?.response?.status === 500) {
      errorMessage.value = '服务器错误，请稍后重试'
    } else {
      errorMessage.value = '用户名或密码错误'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <h1 class="login-title">登录</h1>

      <form @submit.prevent="handleSubmit" novalidate>
        <!-- Session expired -->
        <div v-if="sessionExpiredMessage" class="error-banner" role="alert" aria-live="polite">
          {{ sessionExpiredMessage }}
        </div>

        <!-- Success banner -->
        <div v-if="successMessage" class="success-banner" role="status" aria-live="polite">
          {{ successMessage }}
        </div>

        <!-- Error -->
        <div v-if="errorMessage" class="error-banner" role="alert" aria-live="polite">
          {{ errorMessage }}
        </div>

        <!-- Mode tabs -->
        <div class="tab-bar" role="tablist">
          <button
            v-for="tab in tabs"
            :key="tab.mode"
            :class="['tab-btn', { active: loginMode === tab.mode }]"
            :aria-selected="loginMode === tab.mode"
            role="tab"
            type="button"
            @click="switchMode(tab.mode)"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- Username mode -->
        <template v-if="loginMode === 'username'">
          <div class="form-field">
            <label for="username">用户名</label>
            <input
              id="username"
              v-model="username"
              type="text"
              placeholder="请输入用户名"
              maxlength="20"
              :aria-invalid="!!errorMessage"
              autocomplete="username"
              @input="clearError"
            />
          </div>
          <div class="form-field">
            <label for="password">密码</label>
            <input
              id="password"
              v-model="password"
              type="password"
              placeholder="请输入密码"
              maxlength="128"
              :aria-invalid="!!errorMessage"
              autocomplete="current-password"
              @input="clearError"
            />
          </div>
        </template>

        <!-- QQ mode -->
        <template v-if="loginMode === 'qq'">
          <div class="form-field">
            <label for="login-qq">QQ 号</label>
            <input
              id="login-qq"
              v-model="qq"
              type="text"
              placeholder="请输入绑定的 QQ 号"
              maxlength="20"
              inputmode="numeric"
              :aria-invalid="!!errorMessage"
              @input="clearError"
            />
          </div>
          <div class="form-field">
            <label for="qq-password">密码</label>
            <input
              id="qq-password"
              v-model="password"
              type="password"
              placeholder="请输入密码"
              maxlength="128"
              :aria-invalid="!!errorMessage"
              autocomplete="current-password"
              @input="clearError"
            />
          </div>
        </template>

        <!-- Invite code mode -->
        <template v-if="loginMode === 'invite_code'">
          <div class="form-field">
            <label for="login-invite-code">邀请码</label>
            <input
              id="login-invite-code"
              v-model="inviteCode"
              type="text"
              placeholder="请输入 8 位邀请码"
              maxlength="8"
              :aria-invalid="!!errorMessage"
              autocomplete="off"
              @input="clearError"
            />
          </div>
        </template>

        <!-- Submit -->
        <button
          type="submit"
          class="submit-btn"
          :disabled="loading"
          :aria-busy="loading"
        >
          <span v-if="loading" class="spinner"></span>
          {{ loading ? '登录中…' : '登录' }}
        </button>
      </form>

      <div class="login-links">
        <router-link to="/register" class="login-link">没有账号？注册</router-link>
        <router-link to="/reset-password" class="login-link">忘记密码？</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100dvh;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-6) var(--spacing-4);
  background: var(--color-surface-base);
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: var(--color-surface-raised);
  border-radius: var(--rounded-lg);
  padding: var(--spacing-8);
  box-shadow: var(--shadow-md);
}

.login-title {
  font-family: 'Barlow Condensed', system-ui, sans-serif;
  font-size: 36px;
  font-weight: 600;
  color: var(--color-primary);
  text-align: center;
  margin-bottom: var(--spacing-6);
}

.tab-bar {
  display: flex;
  gap: var(--spacing-1);
  margin-bottom: var(--spacing-5);
  background: var(--color-surface-base);
  border-radius: var(--rounded-md);
  padding: 4px;
}

.tab-btn {
  flex: 1;
  padding: var(--spacing-2) var(--spacing-2);
  font-size: 14px;
  font-weight: 600;
  border: none;
  border-radius: var(--rounded-sm);
  cursor: pointer;
  background: transparent;
  color: var(--color-ink-secondary);
  transition: all 0.15s;
  white-space: nowrap;
  min-height: 44px;
}

.tab-btn.active {
  background: var(--color-surface-raised);
  color: var(--color-primary);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.tab-btn:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.form-field {
  margin-bottom: var(--spacing-5);
}

.form-field label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-ink-primary);
  margin-bottom: var(--spacing-2);
}

.form-field input {
  width: 100%;
  padding: var(--spacing-3) var(--spacing-3);
  font-size: 16px;
  color: var(--color-ink-primary);
  background: var(--color-surface-base);
  border: 1px solid var(--color-border-hairline);
  border-radius: var(--rounded-md);
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
  min-height: 44px;
}

.form-field input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-primary) 25%, transparent);
}

.form-field input[aria-invalid="true"] {
  border-color: var(--color-destructive);
}

.error-banner {
  background: var(--color-destructive-light);
  color: var(--color-destructive);
  padding: var(--spacing-3);
  border-radius: var(--rounded-md);
  font-size: 14px;
  margin-bottom: var(--spacing-4);
  text-align: center;
}

.success-banner {
  background: var(--color-primary-light);
  color: var(--color-primary);
  padding: var(--spacing-3);
  border-radius: var(--rounded-md);
  font-size: 14px;
  margin-bottom: var(--spacing-4);
  text-align: center;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  background: var(--color-primary);
  border: none;
  border-radius: var(--rounded-md);
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  min-height: 44px;
}

.submit-btn:hover:not(:disabled) {
  background: var(--color-primary-light);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.submit-btn:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.login-links {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-2);
  margin-top: var(--spacing-5);
}

.login-link {
  font-size: 14px;
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: none;
  padding: var(--spacing-1) 0;
  text-align: center;
  transition: opacity var(--transition-fast);
}

.login-link:hover {
  text-decoration: underline;
  opacity: 0.85;
}

@media (prefers-reduced-motion: reduce) {
  .spinner {
    animation: none;
  }
  .form-field input {
    transition: none;
  }
  .submit-btn {
    transition: none;
  }
  .tab-btn {
    transition: none;
  }
}
</style>
