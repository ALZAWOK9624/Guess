<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { getInviteCodes, createInviteCode, invalidateInviteCode } from '@/api/admin'
import type { InviteCode, InviteCodeStatus } from '@/types/admin'

const search = ref('')
const inviteCodes = ref<InviteCode[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const generating = ref(false)

let debounceTimer: ReturnType<typeof setTimeout> | null = null

const statusLabels: Record<InviteCodeStatus, string> = {
  unused: '尚未使用',
  used: '已绑定',
  disabled: '已失效',
}

const statusColors: Record<InviteCodeStatus, string> = {
  unused: 'var(--color-primary-light)',
  used: 'var(--color-ink-disabled)',
  disabled: 'var(--color-destructive)',
}

function statusLabel(status: InviteCodeStatus): string {
  return statusLabels[status] || status
}

function statusStyle(status: InviteCodeStatus) {
  return { color: statusColors[status] || 'inherit' }
}

async function loadCodes() {
  loading.value = true
  error.value = null
  try {
    inviteCodes.value = await getInviteCodes(search.value || undefined)
  } catch {
    error.value = '加载失败，请刷新重试'
  } finally {
    loading.value = false
  }
}

function debouncedSearch() {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    loadCodes()
  }, 300)
}

watch(search, debouncedSearch)

async function handleCreate() {
  generating.value = true
  try {
    const code = await createInviteCode()
    inviteCodes.value.unshift(code)
  } catch {
    error.value = '生成邀请码失败，请重试'
    setTimeout(() => { error.value = null }, 3000)
  } finally {
    generating.value = false
  }
}

async function handleInvalidate(code: InviteCode) {
  const confirmed = confirm(`确定将邀请码 ${code.code} 失效？该操作不可撤销。`)
  if (!confirmed) return

  try {
    const updated = await invalidateInviteCode(code.code)
    const idx = inviteCodes.value.findIndex((c) => c.code === code.code)
    if (idx !== -1) {
      inviteCodes.value[idx] = updated
    }
  } catch (err: unknown) {
    const detail = (err as Record<string, unknown>)?.response as Record<string, unknown> | undefined
    const message = (detail?.data as Record<string, unknown> | undefined)?.detail as Record<string, unknown> | undefined
    error.value = (message?.message as string) || '操作失败，请重试'
    setTimeout(() => { error.value = null }, 3000)
  }
}

async function copyCode(code: string) {
  try {
    await navigator.clipboard.writeText(code)
  } catch {
    // Fallback for older browsers
    const textarea = document.createElement('textarea')
    textarea.value = code
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
  }
}

onMounted(loadCodes)
onUnmounted(() => {
  if (debounceTimer) clearTimeout(debounceTimer)
})
</script>

<template>
  <div class="invite-code-table">
    <div class="toolbar">
      <input
        v-model="search"
        type="text"
        class="search-input"
        placeholder="搜索邀请码、用户名或QQ号..."
        aria-label="搜索邀请码、用户名或QQ号"
      />
      <button
        class="btn btn-primary"
        :disabled="generating"
        @click="handleCreate"
      >
        {{ generating ? '生成中...' : '生成邀请码' }}
      </button>
    </div>

    <div v-if="error" class="error-banner">
      {{ error }}
      <button class="btn btn-text" @click="loadCodes">刷新重试</button>
    </div>

    <div v-if="loading" class="skeleton">
      <div class="skeleton-row" v-for="i in 5" :key="i"></div>
    </div>

    <div v-else-if="inviteCodes.length === 0" class="empty-state">
      还没有邀请码。点击「生成邀请码」创建第一个。
    </div>

    <div v-else class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th scope="col">邀请码</th>
            <th scope="col">状态</th>
            <th scope="col">绑定用户</th>
            <th scope="col">QQ</th>
            <th scope="col">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in inviteCodes" :key="item.code">
            <td><code class="code-text">{{ item.code }}</code></td>
            <td>
              <span :style="statusStyle(item.status)" class="status-text">
                {{ statusLabel(item.status) }}
              </span>
            </td>
            <td>{{ item.bound_username || '-' }}</td>
            <td>{{ item.bound_qq || '-' }}</td>
            <td class="actions-cell">
              <button class="btn btn-sm" aria-label="复制邀请码" @click="copyCode(item.code)">复制</button>
              <button
                v-if="item.status === 'unused'"
                class="btn btn-sm btn-danger"
                @click="handleInvalidate(item)"
              >
                失效
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.invite-code-table {
  --table-gap: var(--spacing-4, 16px);
}

.toolbar {
  display: flex;
  gap: var(--spacing-3, 12px);
  margin-bottom: var(--spacing-4, 16px);
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 200px;
  padding: 8px 12px;
  border: 1px solid var(--color-border-hairline, #D4DCD0);
  border-radius: var(--rounded-sm, 6px);
  font-size: var(--text-body, 16px);
  font-family: var(--font-body);
  color: var(--color-ink-primary, #1A2E1A);
  background: var(--color-surface-raised, #FFFFFF);
}

.search-input:focus {
  outline: 2px solid var(--color-primary, #1A5632);
  outline-offset: 2px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  border: none;
  border-radius: var(--rounded-sm, 6px);
  font-size: var(--text-body-sm, 14px);
  cursor: pointer;
  min-height: 44px;
  white-space: nowrap;
  transition: opacity 0.15s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--color-primary, #1A5632);
  color: #FFFFFF;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-light, #2D7A4F);
}

.btn-sm {
  padding: 4px 12px;
  font-size: var(--text-caption, 12px);
  min-height: 44px;
  background: var(--color-surface-raised, #FFFFFF);
  border: 1px solid var(--color-border-hairline, #D4DCD0);
  color: var(--color-ink-primary, #1A2E1A);
}

.btn-sm:hover {
  background: var(--color-surface-base, #F8FAF7);
}

.btn-danger {
  color: var(--color-destructive, #C53030);
  border-color: var(--color-destructive, #C53030);
}

.btn-danger:hover {
  background: var(--color-destructive-light, #FED7D7);
}

.btn-text {
  background: none;
  border: none;
  color: var(--color-primary, #1A5632);
  text-decoration: underline;
  padding: 4px 8px;
  cursor: pointer;
}

.error-banner {
  padding: var(--spacing-3, 12px);
  margin-bottom: var(--spacing-3, 12px);
  background: var(--color-destructive-light, #FED7D7);
  color: var(--color-destructive, #C53030);
  border-radius: var(--rounded-sm, 6px);
  display: flex;
  align-items: center;
  gap: var(--spacing-2, 8px);
  font-size: var(--text-body-sm, 14px);
}

.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-body-sm, 14px);
}

th {
  text-align: left;
  padding: var(--spacing-3, 12px) var(--spacing-2, 8px);
  font-weight: 600;
  color: var(--color-ink-secondary, #4A5A4A);
  border-bottom: 2px solid var(--color-border-hairline, #D4DCD0);
  white-space: nowrap;
}

td {
  padding: var(--spacing-3, 12px) var(--spacing-2, 8px);
  border-bottom: 1px solid var(--color-border-hairline, #D4DCD0);
  white-space: nowrap;
}

.code-text {
  font-family: 'Barlow Condensed', monospace;
  font-size: var(--text-body, 16px);
  font-weight: 600;
  letter-spacing: 1px;
}

.status-text {
  font-weight: 600;
  font-size: var(--text-caption, 12px);
}

.actions-cell {
  display: flex;
  gap: var(--spacing-2, 8px);
}

.skeleton {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3, 12px);
}

.skeleton-row {
  height: 40px;
  background: linear-gradient(90deg, var(--color-surface-base, #F8FAF7) 25%, var(--color-border-hairline, #D4DCD0) 50%, var(--color-surface-base, #F8FAF7) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--rounded-sm, 6px);
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

@media (prefers-reduced-motion: reduce) {
  .skeleton-row {
    animation: none;
    background: var(--color-surface-base, #F8FAF7);
  }
}

.empty-state {
  text-align: center;
  padding: var(--spacing-12, 48px) var(--spacing-4, 16px);
  color: var(--color-ink-secondary, #4A5A4A);
  font-size: var(--text-body, 16px);
}
</style>
