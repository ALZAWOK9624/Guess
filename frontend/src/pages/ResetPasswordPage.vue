<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { resetPassword } from '@/api/auth'

const router = useRouter()

const inviteCode = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)

function clearError() {
  error.value = ''
}

function validateForm(): boolean {
  if (!inviteCode.value.trim()) {
    error.value = '邀请码不能为空'
    return false
  }
  if (inviteCode.value.trim().length !== 8) {
    error.value = '邀请码必须为 8 位字符'
    return false
  }
  const pwd = newPassword.value.trim()
  const confirmPwd = confirmPassword.value.trim()
  if (!pwd) {
    error.value = '新密码不能为空'
    return false
  }
  if (pwd.length < 6) {
    error.value = '密码至少需要 6 个字符'
    return false
  }
  if (pwd.length > 128) {
    error.value = '密码长度不能超过 128 个字符'
    return false
  }
  if (!confirmPwd) {
    error.value = '请确认新密码'
    return false
  }
  if (pwd !== confirmPwd) {
    error.value = '两次密码输入不一致'
    return false
  }
  return true
}

async function handleSubmit() {
  if (!validateForm()) return

  loading.value = true
  error.value = ''

  try {
    await resetPassword({
      invite_code: inviteCode.value.trim(),
      new_password: newPassword.value.trim(),
    })
    router.push('/login?reset=success')
  } catch (err: any) {
    if (err?.response?.status === 422) {
      const errors = err?.response?.data?.detail
      if (Array.isArray(errors)) {
        for (const e of errors) {
          if (e.loc?.includes('body')) {
            const field = e.loc[e.loc.length - 1]
            if (field === 'invite_code') {
              error.value = '邀请码格式不正确'
            } else if (field === 'new_password') {
              error.value = '密码格式不正确'
            }
            break
          }
        }
        if (!error.value) error.value = '输入格式有误'
      }
    } else if (err?.response?.status === 400) {
      error.value = '邀请码无效'
    } else if (err?.message === 'Network Error') {
      error.value = '网络错误，请重试'
    } else if (err?.response?.status === 500) {
      error.value = '服务器错误，请稍后重试'
    } else {
      error.value = '邀请码无效'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="reset-page">
    <div class="reset-card">
      <h1 class="reset-title">重置密码</h1>

      <form @submit.prevent="handleSubmit" novalidate>
        <div v-if="error" class="error-banner" role="alert" aria-live="polite">
          {{ error }}
        </div>

        <div class="form-field">
          <label for="reset-invite-code">邀请码（注册时绑定的）</label>
          <input
            id="reset-invite-code"
            v-model="inviteCode"
            type="text"
            placeholder="请输入 8 位邀请码"
            maxlength="8"
            :aria-invalid="!!error"
            autocomplete="off"
            @input="clearError"
          />
        </div>

        <div class="form-field">
          <label for="reset-new-password">新密码</label>
          <input
            id="reset-new-password"
            v-model="newPassword"
            type="password"
            placeholder="请输入新密码（至少6位）"
            maxlength="128"
            :aria-invalid="!!error"
            autocomplete="new-password"
            @input="clearError"
          />
        </div>

        <div class="form-field">
          <label for="reset-confirm-password">确认新密码</label>
          <input
            id="reset-confirm-password"
            v-model="confirmPassword"
            type="password"
            placeholder="再次输入新密码"
            maxlength="128"
            :aria-invalid="!!error"
            autocomplete="new-password"
            @input="clearError"
          />
        </div>

        <button
          type="submit"
          class="submit-btn"
          :disabled="loading"
          :aria-busy="loading.toString()"
        >
          <span v-if="loading" class="spinner"></span>
          {{ loading ? '重置中…' : '确认重置' }}
        </button>
      </form>

      <div class="reset-links">
        <router-link to="/login" class="reset-link">已有账号？去登录</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.reset-page {
  min-height: 100dvh;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-24) var(--spacing-16);
  background: var(--color-surface-base);
}

.reset-card {
  width: 100%;
  max-width: 400px;
  background: var(--color-surface-raised);
  border-radius: var(--rounded-lg);
  padding: var(--spacing-32);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.reset-title {
  font-family: 'Barlow Condensed', system-ui, sans-serif;
  font-size: 36px;
  font-weight: 600;
  color: var(--color-primary);
  text-align: center;
  margin-bottom: var(--spacing-24);
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

.reset-links {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: var(--spacing-20);
}

.reset-link {
  font-size: 14px;
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: none;
  text-align: center;
}

.reset-link:hover {
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
