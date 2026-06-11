<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue'
import { getHorses, createHorse } from '@/api/horses'
import type { Horse, HorseCreatePayload } from '@/types/horse'

type PageState = 'idle' | 'loading' | 'empty' | 'error' | 'success'

const selectedHorses = defineModel<Horse[]>('selectedHorses', { default: () => ([]) })

const searchText = ref('')
const results = ref<Horse[]>([])
const pageState = ref<PageState>('idle')
const showDropdown = ref(false)
const focusedIndex = ref(-1)

// Quick create modal state
const showQuickCreate = ref(false)
const newHorseName = ref('')
const quickCreateSaving = ref(false)
const quickCreateError = ref('')

let debounceTimer: ReturnType<typeof setTimeout> | null = null

async function doSearch(query: string) {
  if (!query.trim()) {
    results.value = []
    showDropdown.value = false
    pageState.value = 'idle'
    return
  }

  pageState.value = 'loading'
  showDropdown.value = true
  focusedIndex.value = -1

  try {
    const data = await getHorses(query)
    results.value = data
    pageState.value = data.length === 0 ? 'empty' : 'success'
  } catch (err) {
    pageState.value = 'error'
  }
}

function debouncedSearch() {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    doSearch(searchText.value)
  }, 300)
}

watch(searchText, debouncedSearch)

function isSelected(horse: Horse): boolean {
  return selectedHorses.value.some((h) => h.id === horse.id)
}

function toggleHorse(horse: Horse) {
  const idx = selectedHorses.value.findIndex((h) => h.id === horse.id)
  if (idx !== -1) {
    selectedHorses.value = selectedHorses.value.filter((h) => h.id !== horse.id)
  } else {
    selectedHorses.value = [...selectedHorses.value, horse]
  }
}

function removeHorse(horse: Horse) {
  selectedHorses.value = selectedHorses.value.filter((h) => h.id !== horse.id)
}

function handleInputFocus() {
  if (searchText.value.trim()) {
    showDropdown.value = true
  }
}

function handleInputBlur() {
  // Delay hiding dropdown to allow click events on dropdown items
  setTimeout(() => {
    showDropdown.value = false
  }, 200)
}

async function submitQuickCreate() {
  const name = newHorseName.value.trim()
  if (!name) return

  quickCreateSaving.value = true
  quickCreateError.value = ''

  try {
    const payload: HorseCreatePayload = { name }
    const created = await createHorse(payload)
    // Push to selected list (don't unshift — match backend ordering visually)
    selectedHorses.value = [...selectedHorses.value, created]
    // Clear modal and search
    showQuickCreate.value = false
    newHorseName.value = ''
    searchText.value = ''
    showDropdown.value = false
  } catch (err: unknown) {
    const response = (err as Record<string, unknown>)?.response as Record<string, unknown> | undefined
    const detail = response?.data as Record<string, unknown> | undefined
    const message = ((detail?.detail as Record<string, unknown> | undefined)?.message as string) || '创建失败，请重试'
    quickCreateError.value = message
  } finally {
    quickCreateSaving.value = false
  }
}

function handleKeydown(e: KeyboardEvent) {
  if (!showDropdown.value || pageState.value !== 'success') return

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    focusedIndex.value = Math.min(focusedIndex.value + 1, results.value.length - 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    focusedIndex.value = Math.max(focusedIndex.value - 1, 0)
  } else if (e.key === 'Enter' && focusedIndex.value >= 0) {
    e.preventDefault()
    toggleHorse(results.value[focusedIndex.value])
  } else if (e.key === 'Escape') {
    showDropdown.value = false
  }
}

onUnmounted(() => {
  if (debounceTimer) clearTimeout(debounceTimer)
})
</script>

<template>
  <div class="horse-search-select">
    <!-- Search input -->
    <div class="search-wrapper">
      <label class="sr-only" for="horse-search-input">搜索马匹</label>
      <input
        id="horse-search-input"
        v-model="searchText"
        type="text"
        class="search-input"
        placeholder="搜索马匹名称..."
        aria-label="搜索马匹名称"
        :aria-expanded="showDropdown"
        aria-controls="horse-listbox"
        aria-haspopup="listbox"
        aria-autocomplete="list"
        role="combobox"
        @focus="handleInputFocus"
        @blur="handleInputBlur"
        @keydown="handleKeydown"
      />
      <span v-if="pageState === 'loading'" class="search-spinner" aria-hidden="true"></span>
    </div>

    <!-- Selected tags -->
    <div v-if="selectedHorses.length > 0" class="selected-tags">
      <span
        v-for="horse in selectedHorses"
        :key="horse.id"
        class="tag"
      >
        {{ horse.name }}
        <button
          class="tag-remove"
          @click="removeHorse(horse)"
          :aria-label="`移除${horse.name}`"
          type="button"
        >
          ×
        </button>
      </span>
    </div>

    <!-- Dropdown -->
    <div v-if="showDropdown" id="horse-listbox" class="dropdown" role="listbox">
      <!-- Loading -->
      <div v-if="pageState === 'loading'" class="dropdown-state">
        <div class="skeleton-item"></div>
        <div class="skeleton-item"></div>
        <div class="skeleton-item"></div>
      </div>

      <!-- Error -->
      <div v-else-if="pageState === 'error'" class="dropdown-state error-state">
        加载失败
      </div>

      <!-- Results -->
      <ul v-else-if="pageState === 'success'">
        <li
          v-for="(horse, idx) in results"
          :key="horse.id"
          class="dropdown-item"
          :class="{ selected: isSelected(horse), focused: idx === focusedIndex }"
          role="option"
          :aria-selected="isSelected(horse)"
          @mousedown.prevent="toggleHorse(horse)"
        >
          <span class="horse-name">{{ horse.name }}</span>
          <span v-if="horse.origin" class="horse-meta">{{ horse.origin }}</span>
          <span v-if="isSelected(horse)" class="check-mark" aria-hidden="true">✓</span>
        </li>
      </ul>

      <!-- Empty -->
      <div v-else-if="pageState === 'empty'" class="dropdown-state empty-state">
        <p class="empty-text">无匹配马匹</p>
        <button
          class="quick-create-btn"
          @mousedown.prevent="quickCreateError = ''; showQuickCreate = true"
          type="button"
        >
          + 新建马匹
        </button>
      </div>
    </div>

    <!-- Quick Create Modal -->
    <Teleport to="body">
      <div
        v-if="showQuickCreate"
        class="modal-overlay"
        @mousedown.self="!quickCreateSaving && (showQuickCreate = false)"
      >
        <div class="modal-content" role="dialog" aria-label="新建马匹" @mousedown.stop>
          <h3 class="modal-title">新建马匹</h3>

          <div v-if="quickCreateError" class="error-banner">{{ quickCreateError }}</div>

          <form @submit.prevent="submitQuickCreate" class="quick-create-form">
            <label class="form-label">
              名称 <span class="required">*</span>
              <input
                v-model="newHorseName"
                type="text"
                class="form-input"
                placeholder="马匹名称（必填）"
                maxlength="100"
                required
                autofocus
              />
            </label>
            <p class="hint-text">创建后可在管理后台补充性别、年龄等其他字段。</p>
            <div class="form-actions">
              <button
                type="button"
                class="btn btn-cancel"
                @click="showQuickCreate = false"
              >
                取消
              </button>
              <button
                type="submit"
                class="btn btn-primary"
                :disabled="!newHorseName.trim() || quickCreateSaving"
              >
                {{ quickCreateSaving ? '创建中...' : '确认创建' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.horse-search-select {
  position: relative;
}

/* Search wrapper */
.search-wrapper {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border-hairline, #D4DCD0);
  border-radius: var(--rounded-sm, 6px);
  font-size: var(--text-body, 16px);
  font-family: var(--font-body);
  color: var(--color-ink-primary, #1A2E1A);
  background: var(--color-surface-raised, #FFFFFF);
  min-height: 44px;
}

.search-input:focus {
  outline: 2px solid var(--color-primary, #1A5632);
  outline-offset: 2px;
}

.search-input::placeholder {
  color: var(--color-ink-disabled, #9CAA9C);
}

.search-spinner {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-border-hairline);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: translateY(-50%) rotate(360deg); }
}

/* Screen reader only */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

/* Selected tags */
.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-2, 8px);
  margin-top: var(--spacing-2, 8px);
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-1, 4px);
  padding: 4px 8px;
  background: var(--color-surface-base, #F8FAF7);
  border: 1px solid var(--color-border-hairline, #D4DCD0);
  border-radius: var(--rounded-sm, 6px);
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-primary, #1A2E1A);
}

.tag-remove {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  min-width: 44px;
  min-height: 44px;
  margin: -12px;
  padding: 12px;
  border: none;
  background: none;
  font-size: 16px;
  color: var(--color-ink-secondary, #4A5A4A);
  cursor: pointer;
  border-radius: var(--rounded-sm, 6px);
}

.tag-remove:hover {
  color: var(--color-destructive, #C53030);
  background: var(--color-destructive-light, #FED7D7);
}

/* Dropdown */
.dropdown {
  position: absolute;
  z-index: 100;
  width: 100%;
  margin-top: var(--spacing-1, 4px);
  background: var(--color-surface-raised, #FFFFFF);
  border: 1px solid var(--color-border-hairline, #D4DCD0);
  border-radius: var(--rounded-md, 10px);
  box-shadow: var(--shadow-md, 0 2px 4px rgba(26, 86, 50, 0.08));
  max-height: 280px;
  overflow-y: auto;
}

.dropdown-state {
  padding: var(--spacing-4, 16px);
  text-align: center;
  color: var(--color-ink-secondary, #4A5A4A);
  font-size: var(--text-body-sm, 14px);
}

.error-state {
  color: var(--color-destructive, #C53030);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-3, 12px);
}

.empty-text {
  color: var(--color-ink-secondary, #4A5A4A);
  font-size: var(--text-body-sm, 14px);
}

/* Dropdown items */
.dropdown-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-2, 8px);
  padding: var(--spacing-3, 12px) var(--spacing-4, 16px);
  cursor: pointer;
  min-height: 44px;
  font-size: var(--text-body, 16px);
  color: var(--color-ink-primary, #1A2E1A);
  border-bottom: 1px solid var(--color-border-hairline, #D4DCD0);
  transition: background var(--transition-fast, 150ms ease);
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover,
.dropdown-item.focused {
  background: var(--color-surface-base, #F8FAF7);
}

.dropdown-item.selected {
  background: #F0F7F2;
}

.dropdown-item.selected .horse-name {
  font-weight: 600;
}

.horse-name {
  flex: 1;
}

.horse-meta {
  font-size: var(--text-caption, 12px);
  color: var(--color-ink-secondary, #4A5A4A);
}

.check-mark {
  color: var(--color-primary, #1A5632);
  font-weight: 700;
  font-size: 14px;
}

/* Quick create button */
.quick-create-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-1, 4px);
  padding: 8px 20px;
  font-size: var(--text-body-sm, 14px);
  font-weight: 600;
  color: var(--color-primary, #1A5632);
  border: 1px solid var(--color-primary, #1A5632);
  border-radius: var(--rounded-sm, 6px);
  background: var(--color-surface-raised, #FFFFFF);
  cursor: pointer;
  min-height: 44px;
  transition: background var(--transition-fast, 150ms ease);
}

.quick-create-btn:hover {
  background: #F0F7F2;
}

/* Skeleton items */
.skeleton-item {
  height: 20px;
  background: linear-gradient(90deg, var(--color-surface-base) 25%, var(--color-border-hairline) 50%, var(--color-surface-base) 75%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
  border-radius: var(--rounded-sm, 6px);
  margin-bottom: var(--spacing-2, 8px);
}

.skeleton-item:last-child {
  margin-bottom: 0;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--spacing-4, 16px);
}

.modal-content {
  background: var(--color-surface-raised, #FFFFFF);
  border-radius: var(--rounded-lg, 14px);
  padding: var(--spacing-5, 20px);
  width: 100%;
  max-width: 400px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}

.modal-title {
  font-family: var(--font-display, 'Barlow Condensed', system-ui, sans-serif);
  font-size: 22px;
  font-weight: 600;
  color: var(--color-primary, #1A5632);
  margin-bottom: var(--spacing-4, 16px);
}

/* Quick create form */
.quick-create-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3, 12px);
}

.form-label {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1, 4px);
  font-size: var(--text-body-sm, 14px);
  font-weight: 500;
  color: var(--color-ink-primary, #1A2E1A);
}

.required {
  color: var(--color-destructive, #C53030);
}

.form-input {
  padding: 8px 12px;
  border: 1px solid var(--color-border-hairline, #D4DCD0);
  border-radius: var(--rounded-sm, 6px);
  font-size: var(--text-body, 16px);
  font-family: var(--font-body);
  color: var(--color-ink-primary, #1A2E1A);
  background: var(--color-surface-base, #F8FAF7);
  min-height: 44px;
}

.form-input:focus {
  outline: 2px solid var(--color-primary, #1A5632);
  outline-offset: 2px;
}

.hint-text {
  font-size: var(--text-caption, 12px);
  color: var(--color-ink-secondary, #4A5A4A);
}

.form-actions {
  display: flex;
  gap: var(--spacing-3, 12px);
  justify-content: flex-end;
  margin-top: var(--spacing-2, 8px);
}

/* Buttons */
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

.btn-cancel {
  background: var(--color-surface-base, #F8FAF7);
  border: 1px solid var(--color-border-hairline, #D4DCD0);
  color: var(--color-ink-primary, #1A2E1A);
}

/* Error banner */
.error-banner {
  padding: var(--spacing-3, 12px);
  margin-bottom: var(--spacing-3, 12px);
  background: var(--color-destructive-light, #FED7D7);
  color: var(--color-destructive, #C53030);
  border-radius: var(--rounded-sm, 6px);
  font-size: var(--text-body-sm, 14px);
}

@media (prefers-reduced-motion: reduce) {
  .search-spinner {
    animation: none;
    border-color: var(--color-border-hairline);
  }
  .skeleton-item {
    animation: none;
    background: var(--color-surface-base);
  }
  .dropdown-item {
    transition: none;
  }
  .quick-create-btn {
    transition: none;
  }
}
</style>
