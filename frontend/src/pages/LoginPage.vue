<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

function clearError() {
  errorMessage.value = ''
}

function validateForm(): boolean {
  if (!username.value.trim()) {
    errorMessage.value = '用户名不能为空'
    return false
  }
  if (!password.value) {
    errorMessage.value = '密码不能为空'
    return false
  }
  if (password.value.length < 6) {
    errorMessage.value = '密码至少需要 6 个字符'
    return false
  }
  return true
}

async function handleSubmit() {
  if (!validateForm()) return

  loading.value = true
  errorMessage.value = ''

  try {
    await authStore.login({
      username: username.value.trim(),
      password: password.value,
    })
    // Redirect after successful login
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (err: any) {
    if (err?.response?.status === 422) {
      // Validation error — map field-level errors
      const errors = err?.response?.data?.detail || []
      for (const e of errors) {
        if (e.loc?.includes('body')) {
          const field = e.loc[e.loc.length - 1]
          if (field === 'username') {
            errorMessage.value = '用户名格式不正确'
          } else if (field === 'password') {
            errorMessage.value = '密码格式不正确'
          }
          break
        }
      }
      if (!errorMessage.value) {
        errorMessage.value = '输入格式有误'
      }
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
        <!-- Global error -->
        <div v-if="errorMessage" class="error-banner" role="alert" aria-live="polite">
          {{ errorMessage }}
        </div>

        <!-- Username -->
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

        <!-- Password -->
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

        <!-- Submit -->
        <button
          type="submit"
          class="submit-btn"
          :disabled="loading"
          :aria-busy="loading.toString()"
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
  padding: var(--spacing-24) var(--spacing-16);
  background: var(--color-surface-base);
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: var(--color-surface-raised);
  border-radius: var(--rounded-lg);
  padding: var(--spacing-32);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.login-title {
  font-family: 'Barlow Condensed', system-ui, sans-serif;
  font-size: 36px;
  font-weight: 600;
  color: var(--color-primary);
  text-align: center;
  margin-bottom: var(--spacing-32);
}

.form-field {
  margin-bottom: var(--spacing-20);
}

.form-field label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-ink-primary);
  margin-bottom: var(--spacing-8);
}

.form-field input {
  width: 100%;
  padding: 12px var(--spacing-12);
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
  padding: var(--spacing-12);
  border-radius: var(--rounded-md);
  font-size: 14px;
  margin-bottom: var(--spacing-16);
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
  gap: var(--spacing-8);
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
  gap: var(--spacing-8);
  margin-top: var(--spacing-20);
}

.login-link {
  font-size: 14px;
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: none;
  text-align: center;
}

.login-link:hover {
  text-decoration: underline;
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
}
</style>
