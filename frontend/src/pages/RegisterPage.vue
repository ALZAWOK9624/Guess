<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const qq = ref('')
const inviteCode = ref('')
const loading = ref(false)
const fieldErrors = ref<Record<string, string>>({})
const globalError = ref('')

function validateForm(): boolean {
  fieldErrors.value = {}
  globalError.value = ''

  if (!username.value.trim()) {
    fieldErrors.value.username = '用户名不能为空'
    return false
  }
  if (username.value.trim().length < 3 || username.value.trim().length > 20) {
    fieldErrors.value.username = '用户名长度需在 3-20 个字符之间'
    return false
  }

  if (!password.value) {
    fieldErrors.value.password = '密码不能为空'
    return false
  }
  if (password.value.length < 6) {
    fieldErrors.value.password = '密码至少需要 6 个字符'
    return false
  }

  if (!qq.value.trim()) {
    fieldErrors.value.qq = 'QQ 号不能为空'
    return false
  }
  if (qq.value.trim().length < 5 || qq.value.trim().length > 20) {
    fieldErrors.value.qq = 'QQ 号长度需在 5-20 个字符之间'
    return false
  }

  if (!inviteCode.value.trim()) {
    fieldErrors.value.inviteCode = '邀请码不能为空'
    return false
  }
  if (inviteCode.value.trim().length !== 8) {
    fieldErrors.value.inviteCode = '邀请码必须为 8 位字符'
    return false
  }

  return true
}

async function handleSubmit() {
  if (!validateForm()) return

  loading.value = true
  globalError.value = ''

  try {
    await authStore.register({
      username: username.value.trim(),
      password: password.value,
      qq: qq.value.trim(),
      invite_code: inviteCode.value.trim().toUpperCase(),
    })
    // Redirect after successful registration
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (err: any) {
    const detail = err?.response?.data?.detail
    if (detail?.code) {
      globalError.value = detail.message
    } else if (err?.response?.status === 422) {
      // Validation error — map field-level errors
      const errors = err?.response?.data?.detail || []
      for (const e of errors) {
        if (e.loc?.includes('body')) {
          fieldErrors.value[e.loc[e.loc.length - 1]] = e.msg || '字段校验失败'
        }
      }
    } else {
      globalError.value = '注册失败，请重试'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-page">
    <div class="register-card">
      <h1 class="register-title">注册</h1>

      <form @submit.prevent="handleSubmit" novalidate>
        <!-- Global error -->
        <div v-if="globalError" class="error-banner" role="alert" aria-live="polite">
          {{ globalError }}
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
            :aria-invalid="!!fieldErrors.username"
            :aria-describedby="fieldErrors.username ? 'username-error' : undefined"
          />
          <p v-if="fieldErrors.username" :id="'username-error'" class="field-error" role="alert">
            {{ fieldErrors.username }}
          </p>
        </div>

        <!-- Password -->
        <div class="form-field">
          <label for="password">密码（至少 6 位）</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="请输入密码"
            maxlength="128"
            :aria-invalid="!!fieldErrors.password"
            :aria-describedby="fieldErrors.password ? 'password-error' : undefined"
          />
          <p v-if="fieldErrors.password" :id="'password-error'" class="field-error" role="alert">
            {{ fieldErrors.password }}
          </p>
        </div>

        <!-- QQ -->
        <div class="form-field">
          <label for="qq">QQ 号</label>
          <input
            id="qq"
            v-model="qq"
            type="text"
            placeholder="请输入 QQ 号"
            maxlength="20"
            inputmode="numeric"
            :aria-invalid="!!fieldErrors.qq"
            :aria-describedby="fieldErrors.qq ? 'qq-error' : undefined"
          />
          <p v-if="fieldErrors.qq" :id="'qq-error'" class="field-error" role="alert">
            {{ fieldErrors.qq }}
          </p>
        </div>

        <!-- Invite code -->
        <div class="form-field">
          <label for="invite-code">邀请码</label>
          <input
            id="invite-code"
            v-model="inviteCode"
            type="text"
            placeholder="请输入邀请码"
            maxlength="8"
            class="invite-input"
            :aria-invalid="!!fieldErrors.inviteCode"
            :aria-describedby="fieldErrors.inviteCode ? 'invite-code-error' : undefined"
          />
          <p v-if="fieldErrors.inviteCode" :id="'invite-code-error'" class="field-error" role="alert">
            {{ fieldErrors.inviteCode }}
          </p>
        </div>

        <!-- Submit -->
        <button
          type="submit"
          class="submit-btn"
          :disabled="loading"
          :aria-busy="loading"
        >
          <span v-if="loading" class="spinner"></span>
          {{ loading ? '注册中...' : '注  册' }}
        </button>
      </form>

      <p class="login-link">
        已有账号？<router-link to="/login">去登录</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.register-page {
  min-height: 100dvh;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-6) var(--spacing-4);
  background: var(--color-surface-base);
}

.register-card {
  width: 100%;
  max-width: 400px;
  background: var(--color-surface-raised);
  border-radius: var(--rounded-lg);
  padding: var(--spacing-8);
  box-shadow: var(--shadow-md);
}

.register-title {
  font-family: 'Barlow Condensed', system-ui, sans-serif;
  font-size: 36px;
  font-weight: 600;
  color: var(--color-primary);
  text-align: center;
  margin-bottom: var(--spacing-6);
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

.invite-input {
  text-transform: uppercase;
  letter-spacing: 2px;
  font-family: 'Barlow Condensed', monospace;
}

.field-error {
  font-size: 12px;
  color: var(--color-destructive);
  margin-top: var(--spacing-4);
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

.login-link {
  text-align: center;
  margin-top: var(--spacing-5);
  font-size: 14px;
  color: var(--color-ink-secondary);
}

.login-link a {
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: none;
  transition: opacity var(--transition-fast);
}

.login-link a:hover {
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
}
</style>
