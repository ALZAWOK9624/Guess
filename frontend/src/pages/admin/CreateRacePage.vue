<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import HorseSearchSelect from '@/components/HorseSearchSelect.vue'
import { createRace } from '@/api/races'
import type { Horse } from '@/types/horse'

const router = useRouter()

// Form fields
const raceName = ref('')
const raceDate = ref('')
const raceGrade = ref<string>('G1')
const selectedHorses = ref<Horse[]>([])
const customPositiveScores = ref('')
const customPenaltyRules = ref('')
const isSubmitting = ref(false)
const formError = ref('')
const errors = ref<Record<string, string>>({})

// Per-horse jockey (keyed by horse id)
const horseJockeys = ref<Record<number, string>>({})

// Initialize jockey when horses change
watch(selectedHorses, (horses) => {
  for (const h of horses) {
    if (!(h.id in horseJockeys.value)) {
      horseJockeys.value[h.id] = ''
    }
  }
  const currentIds = new Set(horses.map(h => h.id))
  for (const id of Object.keys(horseJockeys.value)) {
    if (!currentIds.has(Number(id))) {
      delete horseJockeys.value[Number(id)]
    }
  }
}, { deep: true })

const grades = [
  { value: 'G1', label: 'G1' },
  { value: 'G2_JPN1', label: 'G2·JPN1' },
  { value: 'YOUNG_G1', label: '2岁G1' },
  { value: 'CUSTOM', label: '自定义' },
]

const showCustomFields = computed(() => raceGrade.value === 'CUSTOM')

const canSubmit = computed(() => {
  if (!raceName.value.trim()) return false
  if (!raceDate.value) return false
  if (selectedHorses.value.length < 2) return false
  if (showCustomFields.value && !customPositiveScores.value.trim()) return false
  return true
})

function validate(): boolean {
  const errs: Record<string, string> = {}
  if (!raceName.value.trim()) errs.name = '请输入比赛名称'
  if (!raceDate.value) errs.date = '请选择比赛日期'
  if (selectedHorses.value.length < 2) errs.horses = '请至少选择 2 匹参赛马'
  if (showCustomFields.value) {
    const trimmedInput = customPositiveScores.value.trim()
    if (!trimmedInput) {
      errs.positive_scores = '请输入正序积分列表'
    } else {
      const parts = trimmedInput.split(',').map(s => s.trim())
      if (parts.some(p => p === '')) {
        errs.positive_scores = '积分格式无效，请使用逗号分隔数字'
      } else {
        const scores = parts.map(s => parseInt(s))
        if (scores.some(isNaN) || scores.some(n => n <= 0)) {
          errs.positive_scores = '积分必须为正整数，用逗号分隔（如 10,7,5,3,2,1）'
        }
      }
    }
    if (customPenaltyRules.value.trim()) {
      const ruleParts = customPenaltyRules.value.split(',').map(p => p.trim())
      for (const part of ruleParts) {
        if (part === '' || !part.includes(':') || part.split(':').length !== 2) {
          errs.penalty_rules = '扣分规则格式无效，格式：-1:-5,-2:-2（倒数位置:扣分）'
          break
        }
        const [pos, pts] = part.split(':')
        if (isNaN(parseInt(pos)) || isNaN(parseInt(pts))) {
          errs.penalty_rules = '扣分规则格式无效，请使用整数'
          break
        }
      }
    }
  }
  errors.value = errs
  return Object.keys(errs).length === 0
}

function parseCustomScoring() {
  const scores = customPositiveScores.value
    .split(',')
    .map(s => parseInt(s.trim()))
    .filter(n => !isNaN(n))

  const penalties = customPenaltyRules.value
    ? customPenaltyRules.value
        .split(',')
        .map(p => {
          const [pos, pts] = p.split(':')
          return {
            position: parseInt(pos.trim()),
            points: parseInt(pts.trim()),
          }
        })
        .filter(r => !isNaN(r.position) && !isNaN(r.points))
    : []

  return { positive_scores: scores, penalty_rules: penalties.length > 0 ? penalties : undefined }
}

async function handleSubmit() {
  if (!validate() || isSubmitting.value) return
  isSubmitting.value = true
  formError.value = ''

  try {
    // Build horse_jockeys with non-empty values only
    const hj: Record<string, string> = {}
    for (const h of selectedHorses.value) {
      if (horseJockeys.value[h.id]?.trim()) {
        hj[String(h.id)] = horseJockeys.value[h.id].trim()
      }
    }

    const payload = {
      name: raceName.value.trim(),
      date: raceDate.value,
      grade: raceGrade.value as 'G1' | 'G2_JPN1' | 'YOUNG_G1' | 'CUSTOM',
      horse_ids: selectedHorses.value.map(h => h.id),
      horse_jockeys: Object.keys(hj).length > 0 ? hj : undefined,
      custom_scoring: showCustomFields.value ? parseCustomScoring() : undefined,
    }
    await createRace(payload)
    router.push('/')
  } catch (err: any) {
    formError.value =
      err?.response?.data?.detail?.message || '创建失败，请重试'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="create-race-page">
    <h1 class="page-title">创建比赛</h1>

    <form class="race-form" @submit.prevent="handleSubmit">
      <!-- 比赛名称 -->
      <div class="form-group">
        <label class="form-label" for="race-name">
          比赛名称 <span class="required">*</span>
        </label>
        <input
          id="race-name"
          v-model="raceName"
          type="text"
          class="form-input"
          placeholder="输入比赛名称"
          maxlength="200"
          aria-required="true"
          :aria-invalid="!!errors.name"
        />
        <p v-if="errors.name" class="field-error">{{ errors.name }}</p>
      </div>

      <!-- 日期 -->
      <div class="form-group">
        <label class="form-label" for="race-date">
          日期 <span class="required">*</span>
        </label>
        <input
          id="race-date"
          v-model="raceDate"
          type="date"
          class="form-input"
          :class="{ 'is-empty': !raceDate }"
          aria-required="true"
          :aria-invalid="!!errors.date"
        />
        <p v-if="errors.date" class="field-error">{{ errors.date }}</p>
      </div>

      <!-- 等级 -->
      <div class="form-group">
        <fieldset class="grade-fieldset">
          <legend class="form-label">
            等级 <span class="required">*</span>
          </legend>
          <div class="grade-options" role="radiogroup">
            <label
              v-for="g in grades"
              :key="g.value"
              class="grade-option"
              :class="{ active: raceGrade === g.value }"
            >
              <input
                v-model="raceGrade"
                type="radio"
                name="grade"
                :value="g.value"
              />
              <span class="grade-label">{{ g.label }}</span>
            </label>
          </div>
        </fieldset>

        <!-- Custom scoring fields -->
        <div v-if="showCustomFields" class="custom-scoring-fields">
          <div class="form-group">
            <label class="form-label" for="positive-scores">
              正序积分列表 <span class="required">*</span>
            </label>
            <input
              id="positive-scores"
              v-model="customPositiveScores"
              type="text"
              class="form-input"
              placeholder="例：10,7,5,3,2,1"
              aria-required="true"
              :aria-invalid="!!errors.positive_scores"
            />
            <p v-if="errors.positive_scores" class="field-error">{{ errors.positive_scores }}</p>
            <p class="field-hint">从第 1 名开始的积分，用逗号分隔</p>
          </div>

          <div class="form-group">
            <label class="form-label" for="penalty-rules">扣分规则（选填）</label>
            <input
              id="penalty-rules"
              v-model="customPenaltyRules"
              type="text"
              class="form-input"
              placeholder="例：-1:-5,-2:-2"
              :aria-invalid="!!errors.penalty_rules"
            />
            <p v-if="errors.penalty_rules" class="field-error">{{ errors.penalty_rules }}</p>
            <p v-else class="field-hint">格式：倒数位置:扣分，用逗号分隔。如 -1:-5 表示倒数第一扣 5 分</p>
          </div>

          <p class="custom-note">自定义规则仅作用于本场比赛，不会保存为模板。</p>
        </div>
      </div>

      <!-- 参赛马匹 -->
      <div class="form-group">
        <label class="form-label">
          参赛马匹 <span class="required">*</span>
          <span class="label-hint">（至少 2 匹）</span>
        </label>
        <HorseSearchSelect v-model:selectedHorses="selectedHorses" />
        <p v-if="errors.horses" class="field-error">{{ errors.horses }}</p>
      </div>

      <!-- Per-horse jockey -->
      <div v-if="selectedHorses.length > 0" class="form-group">
        <label class="form-label">骑手信息</label>
        <div class="horse-jockey-list">
          <div
            v-for="horse in selectedHorses"
            :key="horse.id"
            class="horse-jockey-row"
          >
            <span class="horse-label">{{ horse.name }}</span>
            <input
              v-model="horseJockeys[horse.id]"
              type="text"
              class="form-input"
              placeholder="骑手名"
              maxlength="50"
            />
          </div>
        </div>
      </div>

      <!-- Form-level error -->
      <p v-if="formError" class="form-error" role="alert">{{ formError }}</p>

      <!-- Submit button -->
      <div class="form-actions">
        <button type="button" class="btn btn-cancel" @click="router.push('/admin')">取消</button>
        <button type="submit" class="btn btn-primary" :disabled="!canSubmit || isSubmitting">
          {{ isSubmitting ? '创建中…' : '确认创建' }}
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.create-race-page {
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
.race-form { display: flex; flex-direction: column; gap: var(--spacing-5, 20px); }
.form-group { display: flex; flex-direction: column; gap: var(--spacing-2, 8px); }
.form-label { font-size: var(--text-body-sm, 14px); font-weight: 600; color: var(--color-ink-primary, #1A2E1A); }
.label-hint { font-weight: 400; color: var(--color-ink-secondary, #4A5A4A); }
.required { color: var(--color-destructive, #C53030); }
.form-input {
  padding: 10px 12px;
  border: 1px solid var(--color-border-strong, #A8B8A4);
  border-radius: var(--rounded-md, 10px);
  font-size: var(--text-body, 16px);
  color: var(--color-ink-primary, #1A2E1A);
  background: var(--color-surface-raised, #FFFFFF);
  min-height: 44px;
}
.form-input:focus { outline: 2px solid var(--color-primary, #1A5632); outline-offset: 2px; border-color: var(--color-primary, #1A5632); }
.form-input::placeholder { color: var(--color-ink-disabled, #9CAA9C); }
.grade-fieldset { border: none; padding: 0; margin: 0; }
.grade-options { display: flex; flex-wrap: wrap; gap: var(--spacing-3, 12px); }
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
.grade-option.active { border-color: var(--color-primary, #1A5632); background: var(--color-primary, #1A5632); color: #fff; }
.grade-option input { position: absolute; opacity: 0; width: 0; height: 0; }
.custom-scoring-fields {
  margin-top: var(--spacing-4, 16px);
  padding: var(--spacing-4, 16px);
  background: var(--color-surface-base, #F8FAF7);
  border-radius: var(--rounded-md, 10px);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4, 16px);
}
.field-hint { font-size: var(--text-caption, 12px); color: var(--color-ink-secondary, #4A5A4A); }
.custom-note { font-size: var(--text-caption, 12px); color: var(--color-ink-disabled, #9CAA9C); padding: 8px; border: 1px dashed var(--color-border-hairline, #D4DCD0); border-radius: var(--rounded-sm, 6px); }
.field-error { font-size: var(--text-caption, 12px); color: var(--color-destructive, #C53030); }
.form-error { font-size: var(--text-body-sm, 14px); color: var(--color-destructive, #C53030); padding: 10px 12px; background: var(--color-destructive-light, #FED7D7); border-radius: var(--rounded-md, 10px); }
.form-actions { display: flex; gap: var(--spacing-3, 12px); justify-content: flex-end; padding-top: var(--spacing-4, 16px); border-top: 1px solid var(--color-border-hairline, #D4DCD0); }
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
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: var(--color-primary, #1A5632); color: #FFFFFF; }
.btn-primary:hover:not(:disabled) { background: var(--color-primary-light, #2D7A4F); }
.btn-cancel { background: var(--color-surface-raised, #FFFFFF); color: var(--color-ink-primary, #1A2E1A); border: 1px solid var(--color-border-strong, #A8B8A4); }

/* Per-horse jockey */
.horse-jockey-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2, 8px);
}
.horse-jockey-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-3, 12px);
  padding: 8px 12px;
  background: var(--color-surface-base, #F8FAF7);
  border-radius: var(--rounded-md, 8px);
}
.horse-label {
  min-width: 100px;
  font-weight: 600;
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-primary, #1A2E1A);
}

@media (prefers-reduced-motion: reduce) {
  .grade-option, .btn, .form-input { transition: none; }
}
</style>

<style scoped>
.create-race-page {
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

.required {
  color: var(--color-destructive, #C53030);
}

.form-input {
  padding: 10px 12px;
  border: 1px solid var(--color-border-strong, #A8B8A4);
  border-radius: var(--rounded-md, 10px);
  font-size: var(--text-body, 16px);
  color: var(--color-ink-primary, #1A2E1A);
  background: var(--color-surface-raised, #FFFFFF);
  min-height: 44px;
  transition: border-color 0.15s;
}

.form-input:focus {
  outline: 2px solid var(--color-primary, #1A5632);
  outline-offset: 2px;
  border-color: var(--color-primary, #1A5632);
}

.form-input::placeholder {
  color: var(--color-ink-disabled, #9CAA9C);
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
  transition: all 0.15s;
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

.field-error {
  font-size: var(--text-caption, 12px);
  color: var(--color-destructive, #C53030);
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
  background: var(--color-surface-raised, #FFFFFF);
  color: var(--color-ink-primary, #1A2E1A);
  border: 1px solid var(--color-border-strong, #A8B8A4);
}

@media (prefers-reduced-motion: reduce) {
  .grade-option,
  .btn,
  .form-input {
    transition: none;
  }
}
</style>
