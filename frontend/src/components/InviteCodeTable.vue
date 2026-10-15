<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { getInviteCodes, createInviteCode, deleteInviteCode } from '@/api/admin'
import type { InviteCode, InviteCodeStatus } from '@/types/admin'

const search = ref('')
const qq = ref('')
const inviteCodes = ref<InviteCode[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const generating = ref(false)
const deletingCode = ref<string | null>(null)

let debounceTimer: ReturnType<typeof setTimeout> | null = null

const statusLabels: Record<InviteCodeStatus, string> = {
  unused: '尚未使用',
  used: '已绑定',
}

const statusColors: Record<InviteCodeStatus, string> = {
  unused: 'var(--color-primary-light)',
  used: 'var(--color-ink-disabled)',
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
  if (!qq.value.trim()) {
    error.value = '请先输入 QQ 号'
    setTimeout(() => { error.value = null }, 3000)
    return
  }
  if (qq.value.trim().length < 5 || qq.value.trim().length > 20) {
    error.value = 'QQ 号长度需在 5-20 个字符之间'
    setTimeout(() => { error.value = null }, 3000)
    return
  }
  generating.value = true
  try {
    const code = await createInviteCode(qq.value.trim())
    inviteCodes.value.unshift(code)
    qq.value = ''
  } catch {
    error.value = '生成邀请码失败，请重试'
    setTimeout(() => { error.value = null }, 3000)
  } finally {
    generating.value = false
  }
}

async function handleDelete(item: InviteCode) {
  const msg = item.status === 'used'
    ? `确定删除邀请码 ${item.code}？这将同时删除用户 "${item.bound_username}" 及其所有投票记录，不可撤销！`
    : `确定删除邀请码 ${item.code}？此操作不可撤销。`
  const confirmed = confirm(msg)
  if (!confirmed) return

  deletingCode.value = item.code
  try {
    await deleteInviteCode(item.code)
    inviteCodes.value = inviteCodes.value.filter((c) => c.code !== item.code)
  } catch {
    error.value = '删除失败，请重试'
    setTimeout(() => { error.value = null }, 3000)
  } finally {
    deletingCode.value = null
  }
}

async function copyCode(code: string) {
  try {
    await navigator.clipboard.writeText(code)
  } catch {
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
      <div class="generate-group">
        <input
          v-model="qq"
          type="text"
          class="qq-input"
          placeholder="输入 QQ 号"
          maxlength="20"
          inputmode="numeric"
          aria-label="绑定 QQ 号"
        />
        <button
          class="btn btn-primary"
          :disabled="generating"
          @click="handleCreate"
        >
          {{ generating ? '生成中...' : '生成邀请码' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="error-banner">
      {{ error }}
      <button class="btn btn-text" @click="loadCodes">刷新重试</button>
    </div>

    <div v-if="loading" class="skeleton">
      <div class="skeleton-row" v-for="i in 5" :key="i"></div>
    </div>

    <div v-else-if="inviteCodes.length === 0" class="empty-state">
      还没有邀请码。输入 QQ 号后点击「生成邀请码」创建第一个。
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
                class="btn btn-sm btn-danger"
                :disabled="deletingCode === item.code"
                @click="handleDelete(item)"
              >
                {{ deletingCode === item.code ? '删除中...' : '删除' }}
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

.generate-group {
  display: flex;
  gap: var(--spacing-2, 8px);
  align-items: center;
}

.qq-input {
  width: 130px;
  padding: 8px 12px;
  border: 1px solid var(--color-border-hairline, #D4DCD0);
  border-radius: var(--rounded-sm, 6px);
  font-size: var(--text-body, 16px);
  font-family: var(--font-body);
  color: var(--color-ink-primary, #1A2E1A);
  background: var(--color-surface-raised, #FFFFFF);
}

.qq-input:focus {
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

.btn-danger:hover:not(:disabled) {
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
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
  border-radius: var(--rounded-sm, 6px);
}

@media (prefers-reduced-motion: reduce) {
  .skeleton-row {
    animation: none;
    background: var(--color-surface-base, #F8FAF7);
  }
}

.empty-state {
  text-align: center;
  padding: var(--spacing-8, 32px) var(--spacing-4, 16px);
  color: var(--color-ink-secondary, #4A5A4A);
  font-size: var(--text-body, 16px);
}

/* Table card, row hover and livelier primary button */
.table-wrapper {
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-hairline);
  border-radius: var(--rounded-lg);
  box-shadow: var(--shadow-sm);
  animation: rise-in var(--duration-slow) var(--ease-out) backwards;
}

thead tr {
  background: var(--color-surface-base);
}

tbody tr {
  transition: background var(--duration-fast) ease;
}

tbody tr:hover {
  background: var(--color-primary-tint);
}

tbody tr:last-child td {
  border-bottom: none;
}

.btn {
  transition: opacity var(--duration-fast) ease, transform var(--duration-fast) var(--ease-out), filter var(--duration-fast) ease, background var(--duration-fast) ease;
}

.btn:active:not(:disabled) {
  transform: scale(0.97);
}

.btn-primary {
  background: var(--gradient-brand-soft);
}

.btn-primary:hover:not(:disabled) {
  filter: brightness(1.08);
}
</style>
