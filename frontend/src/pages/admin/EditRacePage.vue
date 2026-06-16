<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import HorseSearchSelect from '@/components/HorseSearchSelect.vue'
import ConfirmDeleteModal from '@/components/ConfirmDeleteModal.vue'
import { getRace, updateRace, deleteRace } from '@/api/races'
import type { Horse } from '@/types/horse'
import type { RaceDetail, RaceHorseSnapshot, Grade } from '@/types/race'

const route = useRoute()
const router = useRouter()
const raceId = Number(route.params.id)

// Form fields
const raceName = ref('')
const raceDate = ref('')
const raceGrade = ref<string>('G1')
const selectedHorses = ref<Horse[]>([])
const customPositiveScores = ref('')
const customPenaltyRules = ref('')
const isSubmitting = ref(false)
const isLoading = ref(true)
const formError = ref('')
const notEditable = ref(false)
const notEditableMessage = ref('')

// Per-horse jockey (keyed by race_horse_id for PATCH updates)
const horseJockeys = ref<Record<number, string>>({})
// Map race_horse_id → horse_id for jockey submission
const raceHorseIdMap = ref<Record<number, number>>({})

// Delete state
const showDeleteModal = ref(false)
const isDeleting = ref(false)
const deleteError = ref('')

const grades = [
  { value: 'G1', label: 'G1' },
  { value: 'G2_JPN1', label: 'G2·JPN1' },
  { value: 'YOUNG_G1', label: '2岁G1' },
  { value: 'CUSTOM', label: '自定义' },
]

const showCustomFields = computed(() => raceGrade.value === 'CUSTOM')

// Store initial values for change detection
const initialValues = ref<{
  name: string
  date: string
  grade: string
  horses: Horse[]
  jockeys: Record<number, string>
}>({
  name: '', date: '', grade: 'G1', horses: [],
  jockeys: {},
})

const canSubmit = computed(() => {
  if (notEditable.value) return false
  if (!raceName.value.trim()) return false
  if (!raceDate.value) return false
  if (selectedHorses.value.length < 2) return false
  if (showCustomFields.value && !customPositiveScores.value.trim()) return false
  return true
})

function loadRaceHorseJockeys(race: RaceDetail) {
  const j: Record<number, string> = {}
  const idMap: Record<number, number> = {}
  for (const rh of race.horses) {
    // Use jockey from RaceHorse (new) or fallback to snapshot_data (old)
    const jockey = (rh as any).jockey || rh.snapshot_data.jockey || ''
    j[rh.race_horse_id] = jockey
    idMap[rh.race_horse_id] = rh.horse_id
  }
  horseJockeys.value = j
  raceHorseIdMap.value = idMap
}

onMounted(async () => {
  try {
    const race = await getRace(raceId)

    if (race.status !== 'voting') {
      notEditable.value = true
      notEditableMessage.value =
        race.status === 'locked' ? '比赛已锁定，不可编辑' : '比赛已结算，不可编辑'
    }

    raceName.value = race.name
    raceDate.value = race.date
    raceGrade.value = race.grade

    // Convert horse snapshots back to Horse type
    // The weight/jockey are now per-race, so we don't put them in the Horse objects
    const mapped: Horse[] = race.horses.map(h => ({
      id: h.horse_id,
      name: h.snapshot_data.name,
      sex: h.snapshot_data.sex,
      birth_year: h.snapshot_data.birth_year ?? h.snapshot_data.age ?? null,
      origin: h.snapshot_data.origin,
      hemisphere: h.snapshot_data.hemisphere ?? null,
      location: null,
      sire: h.snapshot_data.sire,
      damsire: h.snapshot_data.damsire,
      previous_result: h.snapshot_data.previous_result,
      best_win: h.snapshot_data.best_win,
      previous_result_date: null,
      previous_result_position: null,
      best_win_date: null,
      manually_updated_fields: null,
      created_at: '',
      updated_at: '',
    }))
    selectedHorses.value = mapped

    // Load per-horse jockey
    loadRaceHorseJockeys(race)

    // Store initial values
    initialValues.value = {
      name: race.name,
      date: race.date,
      grade: race.grade,
      horses: [...selectedHorses.value],
      jockeys: { ...horseJockeys.value },
    }

    // Pre-fill custom scoring
    if (race.custom_scoring) {
      customPositiveScores.value = race.custom_scoring.positive_scores.join(',')
      if (race.custom_scoring.penalty_rules?.length) {
        customPenaltyRules.value = race.custom_scoring.penalty_rules
          .map(r => `${r.position}:${r.points}`).join(',')
      }
    }
  } catch (err: any) {
    formError.value = '加载比赛失败'
  } finally {
    isLoading.value = false
  }
})

function getChangedHorseIds(): number[] | undefined {
  const currentIds = selectedHorses.value.map(h => h.id).sort()
  const initialIds = initialValues.value.horses.map(h => h.id).sort()
  if (currentIds.length !== initialIds.length) return selectedHorses.value.map(h => h.id)
  for (let i = 0; i < currentIds.length; i++) {
    if (currentIds[i] !== initialIds[i]) return selectedHorses.value.map(h => h.id)
  }
  return undefined
}

function parseCustomScoring() {
  const scores = customPositiveScores.value
    .split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n))

  const penalties = customPenaltyRules.value
    ? customPenaltyRules.value
        .split(',').map(p => {
          const [pos, pts] = p.split(':')
          return { position: parseInt(pos.trim()), points: parseInt(pts.trim()) }
        }).filter(r => !isNaN(r.position) && !isNaN(r.points))
    : []

  return { positive_scores: scores, penalty_rules: penalties.length > 0 ? penalties : undefined }
}

async function handleSubmit() {
  if (!canSubmit.value || isSubmitting.value) return
  isSubmitting.value = true
  formError.value = ''

  try {
    const payload: Record<string, any> = {}

    if (raceName.value.trim() !== initialValues.value.name) {
      payload.name = raceName.value.trim()
    }
    if (raceDate.value !== initialValues.value.date) {
      payload.date = raceDate.value
    }
    if (raceGrade.value !== initialValues.value.grade) {
      payload.grade = raceGrade.value as Grade
      if (raceGrade.value === 'CUSTOM') {
        payload.custom_scoring = parseCustomScoring()
      }
    }

    const changedHorses = getChangedHorseIds()
    if (changedHorses !== undefined) {
      payload.horse_ids = changedHorses
    }

    // Check jockey changes (keyed by race_horse_id)
    const jockeyChanges: Record<string, string> = {}
    for (const rhId of Object.keys(horseJockeys.value)) {
      const numRhId = Number(rhId)
      const currentJ = horseJockeys.value[numRhId]
      const initialJ = initialValues.value.jockeys[numRhId] || ''
      if (currentJ !== initialJ) jockeyChanges[rhId] = currentJ || ''
    }
    if (Object.keys(jockeyChanges).length > 0) payload.horse_jockeys = jockeyChanges

    if (raceGrade.value !== 'CUSTOM' && 'custom_scoring' in payload) {
      delete payload.custom_scoring
    }

    if (Object.keys(payload).length === 0) {
      router.push('/admin')
      return
    }

    await updateRace(raceId, payload)
    router.push('/admin')
  } catch (err: any) {
    formError.value = err?.response?.data?.detail?.message || '保存失败，请重试'
  } finally {
    isSubmitting.value = false
  }
}

function promptDelete() {
  deleteError.value = ''
  showDeleteModal.value = true
}

function cancelDelete() {
  showDeleteModal.value = false
  deleteError.value = ''
}

async function handleDelete() {
  if (isDeleting.value) return
  isDeleting.value = true
  deleteError.value = ''
  try {
    await deleteRace(raceId)
    router.push('/admin')
  } catch (err: any) {
    deleteError.value = err?.response?.data?.detail?.message || '删除失败，请重试'
  } finally {
    isDeleting.value = false
  }
}
</script>

<template>
  <div class="edit-race-page">
    <h1 class="page-title">编辑比赛</h1>

    <div v-if="isLoading" class="loading-state"><p>加载中…</p></div>

    <div v-else-if="notEditable" class="not-editable-state">
      <p class="not-editable-message">{{ notEditableMessage }}</p>
      <button class="btn btn-cancel" @click="router.push('/admin')">返回管理后台</button>
    </div>

    <form v-else class="race-form" @submit.prevent="handleSubmit">

      <div class="form-group">
        <label class="form-label" for="race-name">比赛名称</label>
        <input id="race-name" v-model="raceName" type="text" class="form-input" placeholder="输入比赛名称" maxlength="200" />
      </div>

      <div class="form-group">
        <label class="form-label" for="race-date">日期</label>
        <input id="race-date" v-model="raceDate" type="date" class="form-input" />
      </div>

      <div class="form-group">
        <fieldset class="grade-fieldset">
          <legend class="form-label">等级</legend>
          <div class="grade-options" role="radiogroup">
            <label v-for="g in grades" :key="g.value" class="grade-option" :class="{ active: raceGrade === g.value }">
              <input v-model="raceGrade" type="radio" name="grade" :value="g.value" />
              <span class="grade-label">{{ g.label }}</span>
            </label>
          </div>
        </fieldset>

        <div v-if="showCustomFields" class="custom-scoring-fields">
          <div class="form-group">
            <label class="form-label" for="positive-scores">正序积分列表</label>
            <input id="positive-scores" v-model="customPositiveScores" type="text" class="form-input" placeholder="例：10,7,5,3,2,1" />
            <p class="field-hint">从第 1 名开始的积分，用逗号分隔</p>
          </div>
          <div class="form-group">
            <label class="form-label" for="penalty-rules">扣分规则（选填）</label>
            <input id="penalty-rules" v-model="customPenaltyRules" type="text" class="form-input" placeholder="例：-1:-5,-2:-2" />
          </div>
          <p class="custom-note">自定义规则仅作用于本场比赛，不会保存为模板。</p>
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">
          参赛马匹 <span class="label-hint">（至少 2 匹）</span>
        </label>
        <HorseSearchSelect v-model:selectedHorses="selectedHorses" />
      </div>

      <!-- Per-horse jockey -->
      <div v-if="Object.keys(raceHorseIdMap).length > 0" class="form-group">
        <label class="form-label">骑手信息</label>
        <div class="horse-jockey-list">
          <div v-for="(horseId, rhId) in raceHorseIdMap" :key="rhId" class="horse-jockey-row">
            <span class="horse-label">
              {{ selectedHorses.find(h => h.id === horseId)?.name || `马匹#${horseId}` }}
            </span>
            <input
              v-model="horseJockeys[Number(rhId)]"
              type="text"
              class="form-input"
              placeholder="骑手名"
              maxlength="50"
            />
          </div>
        </div>
      </div>

      <p v-if="formError" class="form-error" role="alert">{{ formError }}</p>

      <div class="form-actions">
        <button type="button" class="btn btn-cancel" @click="router.push('/admin')">取消</button>
        <button type="submit" class="btn btn-primary" :disabled="!canSubmit || isSubmitting">
          {{ isSubmitting ? '保存中…' : '保存修改' }}
        </button>
        <button type="button" class="btn btn-destructive" @click="promptDelete">删除比赛</button>
      </div>

      <p v-if="deleteError" class="form-error" role="alert">{{ deleteError }}</p>
    </form>

    <ConfirmDeleteModal
      v-if="showDeleteModal"
      title="删除比赛"
      :item-name="raceName"
      message="确定删除「{name}」？所有投票记录将被清除。"
      :loading="isDeleting"
      @confirm="handleDelete"
      @cancel="cancelDelete"
    />
  </div>
</template>

<style scoped>
.edit-race-page { padding: var(--spacing-4, 16px); max-width: 720px; margin: 0 auto; }
.page-title { font-family: var(--font-display, 'Barlow Condensed', system-ui, sans-serif); font-size: var(--text-heading, 24px); font-weight: 600; color: var(--color-primary, #1A5632); margin-bottom: var(--spacing-6, 24px); }
.loading-state, .not-editable-state { display: flex; flex-direction: column; align-items: center; gap: var(--spacing-4, 16px); padding: var(--spacing-8, 32px); text-align: center; }
.not-editable-message { font-size: var(--text-body, 16px); color: var(--color-ink-secondary, #4A5A4A); }
.race-form { display: flex; flex-direction: column; gap: var(--spacing-5, 20px); }
.form-group { display: flex; flex-direction: column; gap: var(--spacing-2, 8px); }
.form-label { font-size: var(--text-body-sm, 14px); font-weight: 600; color: var(--color-ink-primary, #1A2E1A); }
.label-hint { font-weight: 400; color: var(--color-ink-secondary, #4A5A4A); }
.form-input { padding: 10px 12px; border: 1px solid var(--color-border-strong, #A8B8A4); border-radius: var(--rounded-md, 10px); font-size: var(--text-body, 16px); color: var(--color-ink-primary, #1A2E1A); background: var(--color-surface-raised, #FFFFFF); min-height: 44px; }
.form-input:focus { outline: 2px solid var(--color-primary, #1A5632); outline-offset: 2px; border-color: var(--color-primary, #1A5632); }
.grade-fieldset { border: none; padding: 0; margin: 0; }
.grade-options { display: flex; flex-wrap: wrap; gap: var(--spacing-3, 12px); }
.grade-option { display: flex; align-items: center; gap: var(--spacing-2, 8px); padding: 8px 16px; border: 1px solid var(--color-border-strong, #A8B8A4); border-radius: var(--rounded-md, 10px); cursor: pointer; min-height: 44px; }
.grade-option.active { border-color: var(--color-primary, #1A5632); background: var(--color-primary, #1A5632); color: #fff; }
.grade-option input { position: absolute; opacity: 0; width: 0; height: 0; }
.custom-scoring-fields { margin-top: var(--spacing-4, 16px); padding: var(--spacing-4, 16px); background: var(--color-surface-base, #F8FAF7); border-radius: var(--rounded-md, 10px); display: flex; flex-direction: column; gap: var(--spacing-4, 16px); }
.field-hint { font-size: var(--text-caption, 12px); color: var(--color-ink-secondary, #4A5A4A); }
.custom-note { font-size: var(--text-caption, 12px); color: var(--color-ink-disabled, #9CAA9C); padding: 8px; border: 1px dashed var(--color-border-hairline, #D4DCD0); border-radius: var(--rounded-sm, 6px); }
.form-error { font-size: var(--text-body-sm, 14px); color: var(--color-destructive, #C53030); padding: 10px 12px; background: var(--color-destructive-light, #FED7D7); border-radius: var(--rounded-md, 10px); }
.form-actions { display: flex; gap: var(--spacing-3, 12px); justify-content: flex-end; padding-top: var(--spacing-4, 16px); border-top: 1px solid var(--color-border-hairline, #D4DCD0); }
.btn { display: inline-flex; align-items: center; justify-content: center; padding: 10px 24px; border: none; border-radius: var(--rounded-md, 10px); font-size: var(--text-body, 16px); font-weight: 600; cursor: pointer; min-height: 44px; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: var(--color-primary, #1A5632); color: #FFFFFF; }
.btn-primary:hover:not(:disabled) { background: var(--color-primary-light, #2D7A4F); }
.btn-cancel { background: var(--color-surface-raised, #FFFFFF); color: var(--color-ink-primary, #1A2E1A); border: 1px solid var(--color-border-strong, #A8B8A4); }
.btn-destructive { background: var(--color-surface-raised, #FFFFFF); color: var(--color-destructive, #C53030); border: 1px solid var(--color-destructive, #C53030); }
.btn-destructive:hover:not(:disabled) { background: var(--color-destructive-light, #FED7D7); }

/* Per-horse jockey */
.horse-jockey-list { display: flex; flex-direction: column; gap: var(--spacing-2, 8px); }
.horse-jockey-row { display: flex; align-items: center; gap: var(--spacing-3, 12px); padding: 8px 12px; background: var(--color-surface-base, #F8FAF7); border-radius: var(--rounded-md, 8px); }
.horse-label { min-width: 100px; font-weight: 600; font-size: var(--text-body-sm, 14px); color: var(--color-ink-primary, #1A2E1A); }
</style>

<style scoped>
.edit-race-page {
  padding: var(--spacing-4, 16px);
  max-width: 720px;
  margin: 0 auto;
}

.page-title {
  font-family: var(--font-display, 'Barlow Condensed', system-ui, sans-serif);
  font-size: var(--text-heading, 24px);
  font-weight: 600;
  color: var(--color-primary, #1A5632);
  margin-bottom: var(--spacing-6, 24px);
}

.loading-state,
.not-editable-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-4, 16px);
  padding: var(--spacing-8, 32px);
  text-align: center;
}

.not-editable-message {
  font-size: var(--text-body, 16px);
  color: var(--color-ink-secondary, #4A5A4A);
}

.race-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-5, 20px);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2, 8px);
}

.form-label {
  font-size: var(--text-body-sm, 14px);
  font-weight: 600;
  color: var(--color-ink-primary, #1A2E1A);
}

.label-hint {
  font-weight: 400;
  color: var(--color-ink-secondary, #4A5A4A);
}

.form-input {
  padding: 10px 12px;
  border: 1px solid var(--color-border-strong, #A8B8A4);
  border-radius: var(--rounded-md, 10px);
  font-size: var(--text-body, 16px);
  color: var(--color-ink-primary, #1A2E1A);
  background: var(--color-surface-raised, #FFFFFF);
  min-height: 44px;
}

.form-input:focus {
  outline: 2px solid var(--color-primary, #1A5632);
  outline-offset: 2px;
  border-color: var(--color-primary, #1A5632);
}

.grade-fieldset {
  border: none;
  padding: 0;
  margin: 0;
}

.grade-options {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-3, 12px);
}

.grade-option {
  display: flex;
  align-items: center;
  gap: var(--spacing-2, 8px);
  padding: 8px 16px;
  border: 1px solid var(--color-border-strong, #A8B8A4);
  border-radius: var(--rounded-md, 10px);
  cursor: pointer;
  min-height: 44px;
}

.grade-option.active {
  border-color: var(--color-primary, #1A5632);
  background: var(--color-primary, #1A5632);
  color: #fff;
}

.grade-option input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.custom-scoring-fields {
  margin-top: var(--spacing-4, 16px);
  padding: var(--spacing-4, 16px);
  background: var(--color-surface-base, #F8FAF7);
  border-radius: var(--rounded-md, 10px);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4, 16px);
}

.field-hint {
  font-size: var(--text-caption, 12px);
  color: var(--color-ink-secondary, #4A5A4A);
}

.custom-note {
  font-size: var(--text-caption, 12px);
  color: var(--color-ink-disabled, #9CAA9C);
  padding: 8px;
  border: 1px dashed var(--color-border-hairline, #D4DCD0);
  border-radius: var(--rounded-sm, 6px);
}

.form-error {
  font-size: var(--text-body-sm, 14px);
  color: var(--color-destructive, #C53030);
  padding: 10px 12px;
  background: var(--color-destructive-light, #FED7D7);
  border-radius: var(--rounded-md, 10px);
}

.form-actions {
  display: flex;
  gap: var(--spacing-3, 12px);
  justify-content: flex-end;
  padding-top: var(--spacing-4, 16px);
  border-top: 1px solid var(--color-border-hairline, #D4DCD0);
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 24px;
  border: none;
  border-radius: var(--rounded-md, 10px);
  font-size: var(--text-body, 16px);
  font-weight: 600;
  cursor: pointer;
  min-height: 44px;
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
  background: var(--color-surface-raised, #FFFFFF);
  color: var(--color-ink-primary, #1A2E1A);
  border: 1px solid var(--color-border-strong, #A8B8A4);
}

.btn-destructive {
  background: var(--color-surface-raised, #FFFFFF);
  color: var(--color-destructive, #C53030);
  border: 1px solid var(--color-destructive, #C53030);
}

.btn-destructive:hover:not(:disabled) {
  background: var(--color-destructive-light, #FED7D7);
}
</style>
