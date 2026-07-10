<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { getLeaderboard } from '@/api/leaderboard'
import type { LeaderboardEntry, LeaderboardFilters } from '@/types/leaderboard'
import LeaderboardRow from '@/components/LeaderboardRow.vue'

type PageState = 'loading' | 'empty' | 'error' | 'success'

const authStore = useAuthStore()
const pageState = ref<PageState>('loading')
const leaderboard = ref<LeaderboardEntry[]>([])
const errorMessage = ref('加载失败，请刷新重试')
const refreshing = ref(false)

// Filter state
const filterOpen = ref(false)
const filters = ref<LeaderboardFilters>({})
const ageRangeOptions = ['2岁', '2+岁', '3岁', '3+岁', '4+岁', '其他']
const sexRestrictionOptions = ['无', '牝限', '牡牝限', '牡限']
const raceGradeOptions = ['G1', 'G2', 'G3', 'JPN1', 'JPN2', '其他', '自定义']
const countryOptions = ['日本', '英国', '美国', '澳大利亚', '中国香港', '法国', '阿联酋', '爱尔兰', '沙特', '南非', '德国', '加拿大', '新西兰', '韩国', '阿根廷', '乌拉圭', '巴西', '智利', '秘鲁', '其他']
const surfaceOptions = ['草地', '泥地', '全天候', '其他']
const distanceMin = ref<number | undefined>(undefined)
const distanceMax = ref<number | undefined>(undefined)
const horseCountMin = ref<number | undefined>(undefined)
const horseCountMax = ref<number | undefined>(undefined)

function hasActiveFilters(): boolean {
  return !!(
    filters.value.age_range?.length || filters.value.sex_restriction?.length ||
    filters.value.race_grade?.length || filters.value.country?.length ||
    filters.value.surface?.length ||
    distanceMin.value !== undefined || distanceMax.value !== undefined ||
    horseCountMin.value !== undefined || horseCountMax.value !== undefined
  )
}

function toggleArrayField(field: 'age_range' | 'sex_restriction' | 'race_grade' | 'country' | 'surface', value: string) {
  const arr = filters.value[field]
  if (arr?.includes(value)) {
    filters.value[field] = arr.filter(v => v !== value)
    if (filters.value[field]?.length === 0) filters.value[field] = undefined
  } else {
    filters.value[field] = [...(arr || []), value]
  }
  loadData()
}

function toNum(v: unknown): number | undefined {
  return typeof v === 'number' && !isNaN(v) ? v : undefined
}

async function loadData() {
  pageState.value = 'loading'
  errorMessage.value = '加载失败，请刷新重试'
  try {
    const allFilters: LeaderboardFilters = {
      ...filters.value,
      distance_min: toNum(distanceMin.value),
      distance_max: toNum(distanceMax.value),
      horse_count_min: toNum(horseCountMin.value),
      horse_count_max: toNum(horseCountMax.value),
    }
    const data = await getLeaderboard(allFilters)
    leaderboard.value = data
    const hasActivity = data.length > 0 && data.some(e => e.races_participated > 0)
    pageState.value = hasActivity ? 'success' : 'empty'
  } catch (err) {
    console.error('Leaderboard load failed:', err)
    pageState.value = 'error'
  }
}

async function handleRefresh() {
  refreshing.value = true
  await loadData()
  refreshing.value = false
}

function clearFilters() {
  filters.value = {}
  distanceMin.value = undefined
  distanceMax.value = undefined
  horseCountMin.value = undefined
  horseCountMax.value = undefined
  loadData()
}

onMounted(loadData)
</script>

<template>
  <div class="leaderboard-page">
    <!-- Filter bar -->
    <div class="filter-bar">
      <button class="filter-toggle" @click="filterOpen = !filterOpen">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="4" y1="6" x2="20" y2="6" /><line x1="8" y1="12" x2="20" y2="12" /><line x1="12" y1="18" x2="20" y2="18" />
        </svg>
        筛选
        <span v-if="hasActiveFilters()" class="filter-badge"></span>
      </button>
      <button v-if="hasActiveFilters()" class="clear-btn" @click="clearFilters">清除筛选</button>
      <button class="filter-toggle" @click="handleRefresh" :disabled="refreshing" style="margin-left:auto">
        {{ refreshing ? '刷新中…' : '刷新' }}
      </button>
    </div>

    <!-- Filter panel -->
    <div v-if="filterOpen" class="filter-panel">
      <div class="filter-section">
        <label class="filter-label">年龄范围</label>
        <div class="filter-tags">
          <button v-for="opt in ageRangeOptions" :key="opt" class="filter-tag" :class="{ active: filters.age_range?.includes(opt) }" @click="toggleArrayField('age_range', opt)">{{ opt }}</button>
        </div>
      </div>
      <div class="filter-section">
        <label class="filter-label">性别限定</label>
        <div class="filter-tags">
          <button v-for="opt in sexRestrictionOptions" :key="opt" class="filter-tag" :class="{ active: filters.sex_restriction?.includes(opt) }" @click="toggleArrayField('sex_restriction', opt)">{{ opt }}</button>
        </div>
      </div>
      <div class="filter-section">
        <label class="filter-label">比赛等级</label>
        <div class="filter-tags">
          <button v-for="opt in raceGradeOptions" :key="opt" class="filter-tag" :class="{ active: filters.race_grade?.includes(opt) }" @click="toggleArrayField('race_grade', opt)">{{ opt }}</button>
        </div>
      </div>
      <div class="filter-section">
        <label class="filter-label">国家或地区</label>
        <div class="filter-tags filter-grid">
          <button v-for="opt in countryOptions" :key="opt" class="filter-tag" :class="{ active: filters.country?.includes(opt) }" @click="toggleArrayField('country', opt)">{{ opt }}</button>
        </div>
      </div>
      <div class="filter-section">
        <label class="filter-label">场地</label>
        <div class="filter-tags">
          <button v-for="opt in surfaceOptions" :key="opt" class="filter-tag" :class="{ active: filters.surface?.includes(opt) }" @click="toggleArrayField('surface', opt)">{{ opt }}</button>
        </div>
      </div>
      <div class="filter-section">
        <label class="filter-label">长度范围（米）</label>
        <div class="filter-range">
          <input type="number" v-model.number="distanceMin" placeholder="最小" min="0" @input="loadData" />
          <span class="range-sep">—</span>
          <input type="number" v-model.number="distanceMax" placeholder="最大" min="0" @input="loadData" />
        </div>
      </div>
      <div class="filter-section">
        <label class="filter-label">马匹数量范围</label>
        <div class="filter-range">
          <input type="number" v-model.number="horseCountMin" placeholder="最少" min="0" @input="loadData" />
          <span class="range-sep">—</span>
          <input type="number" v-model.number="horseCountMax" placeholder="最多" min="0" @input="loadData" />
        </div>
      </div>
    </div>

    <!-- Loading skeleton -->
    <template v-if="pageState === 'loading'">
      <div class="skeleton-container" role="status" aria-live="polite" aria-label="加载中">
        <div v-for="i in 5" :key="i" class="skeleton-row"></div>
      </div>
    </template>

    <!-- Empty state -->
    <template v-else-if="pageState === 'empty'">
      <div class="state-container" role="status" aria-live="polite">
        <p class="empty-text">还没有人参与竞猜——成为第一个！</p>
        <router-link to="/" class="home-link">去首页看看</router-link>
      </div>
    </template>

    <!-- Error state -->
    <template v-else-if="pageState === 'error'">
      <div class="state-container" role="alert" aria-live="polite">
        <p class="error-text">{{ errorMessage }}</p>
        <button class="refresh-btn" :disabled="refreshing" @click="handleRefresh">{{ refreshing ? '刷新中…' : '刷新重试' }}</button>
      </div>
    </template>

    <!-- Leaderboard data -->
    <template v-else>
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th scope="col" class="col-rank">排名</th>
              <th scope="col" class="col-name">用户名</th>
              <th scope="col" class="col-points">积分</th>
              <th scope="col" class="col-races">场数</th>
              <th scope="col" class="col-avg">场均</th>
            </tr>
          </thead>
          <tbody>
            <LeaderboardRow v-for="(entry, index) in leaderboard" :key="entry.username" :entry="entry" :rank="index + 1" :is-current-user="entry.username === authStore.user?.username" />
          </tbody>
        </table>
      </div>
      <p class="updated-hint">积分在每次比赛结算后自动更新</p>
    </template>
  </div>
</template>

<style scoped>
.leaderboard-page {
  padding: var(--spacing-16, 16px);
  max-width: 1280px;
  margin: 0 auto;
}

/* Filter bar */
.filter-bar {
  display: flex;
  align-items: center;
  gap: var(--spacing-3, 12px);
  margin-bottom: var(--spacing-4, 16px);
}

.filter-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: 1px solid var(--color-border-strong, #A8B8A4);
  border-radius: var(--rounded-sm, 6px);
  background: var(--color-surface-raised, #FFFFFF);
  color: var(--color-ink-primary, #1A2E1A);
  font-size: var(--text-body-sm, 14px);
  font-weight: 600;
  cursor: pointer;
  min-height: 40px;
}

.filter-toggle:hover {
  border-color: var(--color-primary, #1A5632);
}

.filter-badge {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-primary, #1A5632);
}

.clear-btn {
  padding: 8px 14px;
  border: 1px solid var(--color-destructive, #C53030);
  border-radius: var(--rounded-sm, 6px);
  background: transparent;
  color: var(--color-destructive, #C53030);
  font-size: var(--text-body-sm, 14px);
  font-weight: 600;
  cursor: pointer;
  min-height: 40px;
}

.clear-btn:hover {
  background: #FFF5F5;
}

/* Filter panel */
.filter-panel {
  background: var(--color-surface-base, #F8FAF7);
  border: 1px solid var(--color-border-hairline, #D4DCD0);
  border-radius: var(--rounded-md, 10px);
  padding: var(--spacing-4, 16px);
  margin-bottom: var(--spacing-4, 16px);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4, 16px);
}

.filter-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2, 8px);
}

.filter-label {
  font-size: var(--text-caption, 12px);
  font-weight: 600;
  color: var(--color-ink-secondary, #4A5A4A);
}

.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(70px, 1fr));
}

.filter-tag {
  padding: 4px 10px;
  border: 1px solid var(--color-border-strong, #A8B8A4);
  border-radius: var(--rounded-sm, 6px);
  background: var(--color-surface-raised, #FFFFFF);
  color: var(--color-ink-primary, #1A2E1A);
  font-size: var(--text-caption, 12px);
  cursor: pointer;
  transition: border-color 0.15s, background-color 0.15s;
}

.filter-tag:hover {
  border-color: var(--color-primary, #1A5632);
}

.filter-tag.active {
  border-color: var(--color-primary, #1A5632);
  background: #F0F7F2;
  color: var(--color-primary, #1A5632);
  font-weight: 600;
}

.filter-range {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-range input {
  width: 120px;
  padding: 6px 10px;
  border: 1px solid var(--color-border-strong, #A8B8A4);
  border-radius: var(--rounded-sm, 6px);
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-primary, #1A2E1A);
  background: var(--color-surface-raised, #FFFFFF);
}

.filter-range input:focus {
  outline: 2px solid var(--color-primary, #1A5632);
  outline-offset: 2px;
}

.range-sep {
  color: var(--color-ink-secondary, #4A5A4A);
}

/* Skeleton */
.skeleton-container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-8);
}

.skeleton-row {
  height: 40px;
  background: linear-gradient(90deg, var(--color-surface-base) 25%, var(--color-border-hairline) 50%, var(--color-surface-base) 75%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
  border-radius: var(--rounded-sm);
}

/* State patterns */
.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  text-align: center;
  gap: var(--spacing-16, 16px);
}

.empty-text {
  color: var(--color-ink-secondary, #4A5A4A);
  font-size: var(--text-body, 16px);
}

.error-text {
  color: var(--color-destructive, #C53030);
  font-size: var(--text-body, 16px);
}

.home-link {
  color: var(--color-primary, #1A5632);
  font-weight: 600;
  font-size: var(--text-body, 16px);
  text-decoration: underline;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
}

.refresh-btn {
  padding: 10px 24px;
  font-size: var(--text-body, 16px);
  font-weight: 600;
  color: #ffffff;
  background: var(--color-primary, #1A5632);
  border: none;
  border-radius: var(--rounded-md, 10px);
  cursor: pointer;
  min-height: 44px;
  transition: background 0.2s;
}

.refresh-btn:hover {
  background: var(--color-primary-light, #2D7A4F);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Table */
.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-body-sm, 14px);
}

thead tr {
  border-bottom: 2px solid var(--color-border-hairline, #D4DCD0);
}

th {
  padding: var(--spacing-3, 12px) var(--spacing-2, 8px);
  font-weight: 600;
  color: var(--color-ink-secondary, #4A5A4A);
  white-space: nowrap;
  text-align: left;
}

th.col-rank { text-align: center; }
th.col-points { text-align: right; }
th.col-races { text-align: center; }
th.col-avg { text-align: right; }

.updated-hint {
  text-align: center;
  font-size: var(--text-caption, 12px);
  color: var(--color-ink-secondary, #4A5A4A);
  margin-top: var(--spacing-8, 8px);
}

@media (prefers-reduced-motion: reduce) {
  .skeleton-row {
    animation: none;
    background: var(--color-surface-base);
  }
  .refresh-btn {
    transition: none;
  }
}
</style>
