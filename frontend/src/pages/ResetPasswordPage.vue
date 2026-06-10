<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { resetPassword } from '@/api/auth'

const router = useRouter()
const route = useRoute()

// Step 1: identity verification
const username = ref('')
const inviteCode = ref('')
const step1Error = ref('')

// Step 2: new password setup
const newPassword = ref('')
const confirmPassword = ref('')
const step2Error = ref('')

const loading = ref(false)
const currentStep = ref(1)

function clearStep1Error() {
  step1Error.value = ''
}

function clearStep2Error() {
  step2Error.value = ''
}

function validateStep1(): boolean {
  if (!username.value.trim()) {
    step1Error.value = '用户名不能为空'
    return false
  }
  if (username.value.trim().length < 3 || username.value.trim().length > 20) {
    step1Error.value = '用户名长度需在 3-20 个字符之间'
    return false
  }
  if (!inviteCode.value.trim()) {
    step1Error.value = '邀请码不能为空'
    return false
  }
  if (inviteCode.value.trim().length !== 8) {
    step1Error.value = '邀请码必须为 8 位字符'
    return false
  }
  return true
}

function validateStep2(): boolean {
  const pwd = newPassword.value.trim()
  const confirmPwd = confirmPassword.value.trim()
  if (!pwd) {
    step2Error.value = '新密码不能为空'
    return false
  }
  if (pwd.length < 6) {
    step2Error.value = '密码至少需要 6 个字符'
    return false
  }
  if (pwd.length > 128) {
    step2Error.value = '密码长度不能超过 128 个字符'
    return false
  }
  if (!confirmPwd) {
    step2Error.value = '请确认新密码'
    return false
  }
  if (pwd !== confirmPwd) {
    step2Error.value = '两次密码输入不一致'
    return false
  }
  return true
}

function goToStep2() {
  if (!validateStep1()) return
  currentStep.value = 2
}

function goToStep1() {
  currentStep.value = 1
  step2Error.value = ''
}

async function handleSubmit() {
  if (!validateStep2()) return

  loading.value = true
  step2Error.value = ''

  try {
    await resetPassword({
      username: username.value.trim(),
      invite_code: inviteCode.value.trim(),
      new_password: newPassword.value.trim(),
    })
    // Success — redirect to login with success message
    router.push('/login?reset=success')
  } catch (err: any) {
    if (err?.response?.status === 422) {
      const errors = err?.response?.data?.detail
      if (Array.isArray(errors)) {
        for (const e of errors) {
          if (e.loc?.includes('body')) {
            const field = e.loc[e.loc.length - 1]
            if (field === 'username') {
              step1Error.value = '用户名格式不正确'
            } else if (field === 'invite_code') {
              step1Error.value = '邀请码格式不正确'
            } else if (field === 'new_password') {
              step2Error.value = '密码格式不正确'
            }
            break
          }
        }
      }
      if (!step1Error.value && !step2Error.value) {
        step1Error.value = '输入格式有误'
      }
      // Go back to step 1 if the error is about step 1 fields
      if (step1Error.value) {
        currentStep.value = 1
      }
    } else if (err?.response?.status === 400) {
      // INVITE_CODE_MISMATCH — go back to step 1
      step1Error.value = '邀请码与用户不匹配'
      currentStep.value = 1
    } else if (err?.message === 'Network Error') {
      step2Error.value = '网络错误，请重试'
    } else if (err?.response?.status === 500) {
      step2Error.value = '服务器错误，请稍后重试'
    } else {
      step1Error.value = '邀请码与用户不匹配'
      currentStep.value = 1
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

      <!-- Step 1: Identity Verification -->
      <div v-if="currentStep === 1" class="step-panel">
        <h2 class="step-heading">验证身份</h2>

        <form @submit.prevent="goToStep2" novalidate>
          <div v-if="step1Error" class="error-banner" role="alert" aria-live="polite">
            {{ step1Error }}
          </div>

          <div class="form-field">
            <label for="reset-username">用户名</label>
            <input
              id="reset-username"
              v-model="username"
              type="text"
              placeholder="请输入用户名"
              maxlength="20"
              :aria-invalid="!!step1Error"
              autocomplete="username"
              @input="clearStep1Error"
            />
          </div>

          <div class="form-field">
            <label for="reset-invite-code">邀请码（注册时绑定的）</label>
            <input
              id="reset-invite-code"
              v-model="inviteCode"
              type="text"
              placeholder="请输入 8 位邀请码"
              maxlength="8"
              :aria-invalid="!!step1Error"
              autocomplete="off"
              @input="clearStep1Error"
            />
          </div>

          <button
            type="submit"
            class="submit-btn"
            :disabled="loading"
            :aria-busy="loading.toString()"
          >
            <span v-if="loading" class="spinner"></span>
            下一步
          </button>
        </form>
      </div>

      <!-- Step 2: Set New Password -->
      <div v-else class="step-panel">
        <h2 class="step-heading">设置新密码</h2>

        <form @submit.prevent="handleSubmit" novalidate>
          <div v-if="step2Error" class="error-banner" role="alert" aria-live="polite">
            {{ step2Error }}
          </div>

          <div class="form-field">
            <label for="reset-new-password">新密码</label>
            <input
              id="reset-new-password"
              v-model="newPassword"
              type="password"
              placeholder="请输入新密码（至少6位）"
              maxlength="128"
              :aria-invalid="!!step2Error"
              autocomplete="new-password"
              @input="clearStep2Error"
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
              :aria-invalid="!!step2Error"
              autocomplete="new-password"
              @input="clearStep2Error"
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

        <button class="back-btn" @click="goToStep1" :disabled="loading">
          返回上一步
        </button>
      </div>

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

.step-heading {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-ink-secondary);
  margin-bottom: var(--spacing-20);
  text-align: center;
}

.step-panel {
  transition: opacity 0.2s ease;
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

.back-btn {
  width: 100%;
  padding: 12px;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-primary);
  background: none;
  border: 1px solid var(--color-primary);
  border-radius: var(--rounded-md);
  cursor: pointer;
  margin-top: var(--spacing-12);
  min-height: 44px;
  transition: background 0.2s;
  text-align: center;
}

.back-btn:hover:not(:disabled) {
  background: color-mix(in srgb, var(--color-primary) 8%, transparent);
}

.back-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.back-btn:focus-visible {
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
  .back-btn {
    transition: none;
  }
  .step-panel {
    transition: none;
  }
}
</style>
