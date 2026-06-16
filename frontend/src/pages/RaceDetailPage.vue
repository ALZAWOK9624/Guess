<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import GradeBadge from '@/components/GradeBadge.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import HorseDetailCard from '@/components/HorseDetailCard.vue'
import VoteButton from '@/components/VoteButton.vue'
import HorseSelectCard from '@/components/HorseSelectCard.vue'
import VotingDetail from '@/components/VotingDetail.vue'
import RaceResultView from '@/components/RaceResultView.vue'
import { getRace } from '@/api/races'
import { useVote } from '@/composables/useVote'
import type { RaceDetail } from '@/types/race'

type PageState = 'loading' | 'error' | 'success'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const raceId = Number(route.params.id)

const pageState = ref<PageState>('loading')
const race = ref<RaceDetail | null>(null)
const errorMessage = ref('加载失败，请刷新重试')

const {
  selectedHorse,
  votedHorseName,
  isSubmitting,
  isInSelectionMode,
  votes,
  votesLoading,
  votesError,
  errorMessage: voteError,
  selectHorse,
  enterSelectionMode,
  exitSelectionMode,
  loadVotes,
} = useVote(null)

// After votes load, check if current user has a vote and set votedHorseName
function checkUserVote() {
  if (!authStore.isLoggedIn || !authStore.user) return
  const myVote = votes.value.find(v => v.user_id === authStore.user!.id)
  if (myVote) {
    votedHorseName.value = myVote.horse_name
  }
}

const isRaceVoting = computed(() => race.value?.status === 'voting')
const isRaceLocked = computed(() => race.value?.status === 'locked')
const isRaceSettled = computed(() => race.value?.status === 'settled')


function handleVoteClick() {
  // Guest redirect
  if (!authStore.isLoggedIn) {
    router.push({ path: '/login', query: { redirect: `/races/${raceId}` } })
    return
  }
  // Logged-in: enter selection mode with pre-selected current vote
  if (race.value) {
    enterSelectionMode(race.value.horses)
  }
}

function handleVotedClick() {
  // Already voted — enter selection mode to modify
  if (race.value) {
    enterSelectionMode(race.value.horses)
  }
}

onMounted(async () => {
  try {
    race.value = await getRace(raceId)
    pageState.value = 'success'

    // Fetch vote distribution for voting and locked races
    if (race.value.status === 'voting' || race.value.status === 'locked') {
      await loadVotes(raceId)
      checkUserVote()
    }
  } catch {
    pageState.value = 'error'
  }
})
</script>

<template>
  <div class="race-detail-page" :class="{ 'has-vote-bar': isRaceVoting || isRaceLocked }">
    <!-- Loading -->
    <div v-if="pageState === 'loading'" class="state-container">
      <p>加载中…</p>
    </div>

    <!-- Error -->
    <div v-else-if="pageState === 'error'" class="state-container">
      <p class="error-text">{{ errorMessage }}</p>
      <button
        class="refresh-btn"
        @click="router.go(0)"
      >
        刷新重试
      </button>
    </div>

    <!-- Race Detail -->
    <template v-else-if="race">
      <div class="race-header">
        <button class="back-btn" @click="router.push('/')" aria-label="返回首页">
          ← 返回
        </button>

        <div class="race-title-row">
          <GradeBadge :grade="race.grade as any" />
          <h1 class="race-name">{{ race.name }}</h1>
          <StatusBadge :status="race.status as any" />
        </div>

        <p class="race-date">{{ race.date }}</p>
        <p class="race-meta">{{ race.horses.length }} 匹参赛 · {{ race.vote_count }} 人已投</p>
      </div>

      <!-- Custom scoring info -->
      <div v-if="race.custom_scoring" class="custom-scoring-info">
        <p class="scoring-title">自定义积分规则</p>
        <p class="scoring-detail">
          正序积分：{{ race.custom_scoring.positive_scores.join(', ') }}
        </p>
        <p
          v-if="race.custom_scoring.penalty_rules?.length"
          class="scoring-detail"
        >
          扣分规则：{{ race.custom_scoring.penalty_rules.map(r => `倒数第${Math.abs(r.position)}名扣${Math.abs(r.points)}分`).join('，') }}
        </p>
      </div>

      <!-- Horse list — normal view (non-selection mode) -->
      <div v-if="!isInSelectionMode" class="horse-list">
        <h2 class="section-title">参赛马匹</h2>
        <HorseDetailCard
          v-for="horse in race.horses"
          :key="horse.horse_id"
          :snapshot-data="horse.snapshot_data"
          :horse-id="horse.horse_id"
          :class="{ 'voted-horse': isRaceLocked && votedHorseName && horse.snapshot_data.name === votedHorseName }"
        />
      </div>

      <!-- Horse list — selection mode (voting) -->
      <div v-else class="selection-section">
        <h2 class="section-title">
          {{ votedHorseName ? '修改投票 — 点击其他马匹更换选择' : '选择你要投注的马匹' }}
        </h2>
        <div class="select-card-list">
          <HorseSelectCard
            v-for="horse in race.horses"
            :key="horse.race_horse_id"
            :horse="horse"
            :selected="selectedHorse?.race_horse_id === horse.race_horse_id"
            :name="'vote-group-' + raceId"
            @select="selectHorse(horse, race.id)"
          />
        </div>

        <!-- Vote error message -->
        <p v-if="voteError" class="vote-error">{{ voteError }}</p>

        <!-- Cancel button (only cancel, no confirm needed — tap horse = submit) -->
        <div class="selection-actions">
          <button class="cancel-btn" :disabled="isSubmitting" @click="exitSelectionMode">
            {{ isSubmitting ? '提交中…' : '取消' }}
          </button>
        </div>
      </div>

      <!-- Voting Detail — show vote distribution for voting/locked races -->
      <VotingDetail
        v-if="isRaceVoting || isRaceLocked"
        :votes="votes"
        :loading="votesLoading"
      />

      <!-- Settled Race Result View — show rankings, votes, and points -->
      <RaceResultView
        v-if="isRaceSettled && race.horse_votes"
        :horses="race.horse_votes.horses"
      />

      <!-- Admin: Modify Result button for settled races -->
      <div
        v-if="isRaceSettled && authStore.isAdmin"
        class="admin-actions"
      >
        <button
          class="modify-result-btn"
          @click="router.push(`/admin/races/${raceId}/results`)"
        >
          修改结果
        </button>
      </div>

      <!-- Vote error toast -->
      <p v-if="voteError && !isInSelectionMode" class="vote-error toast">
        {{ voteError }}
      </p>

      <!-- VoteButton — fixed bottom bar on mobile, inline on desktop -->
      <div
        v-if="isRaceVoting || isRaceLocked || isRaceSettled"
        class="vote-bar"
      >
        <!-- Locked/unvoted message -->
        <p v-if="isRaceLocked && !votedHorseName" class="locked-message">
          投票已截止。你未参与本场竞猜。
        </p>

        <!-- VoteButton -->
        <VoteButton
          v-if="!isInSelectionMode"
          :race-status="race.status"
          :voted-horse-name="votedHorseName"
          :is-logged-in="authStore.isLoggedIn"
          :is-submitting="isSubmitting"
          @vote-click="handleVoteClick"
          @modify-click="handleVotedClick"
        />
      </div>
    </template>
  </div>
</template>

<style scoped>
.race-detail-page {
  padding: var(--spacing-4, 16px);
  max-width: 960px;
  margin: 0 auto;
}

.race-detail-page.has-vote-bar {
  padding-bottom: calc(80px + env(safe-area-inset-bottom, 0px));
}

.race-header {
  margin-bottom: var(--spacing-6, 24px);
}

.back-btn {
  background: none;
  border: none;
  color: var(--color-primary, #1A5632);
  font-size: var(--text-body, 16px);
  cursor: pointer;
  padding: 0;
  margin-bottom: var(--spacing-3, 12px);
  min-height: 44px;
  display: inline-flex;
  align-items: center;
}

.race-title-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-3, 12px);
  margin-bottom: var(--spacing-2, 8px);
  flex-wrap: wrap;
}

.race-name {
  font-family: var(--font-display, 'Barlow Condensed', system-ui, sans-serif);
  font-size: var(--text-heading, 24px);
  font-weight: 600;
  color: var(--color-ink-primary, #1A2E1A);
  margin: 0;
}

.race-date {
  font-size: var(--text-body, 16px);
  color: var(--color-ink-secondary, #4A5A4A);
  margin: 0 0 var(--spacing-1, 4px);
}

.race-meta {
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-secondary, #4A5A4A);
  margin: 0;
}

.custom-scoring-info {
  background: var(--color-surface-base, #F8FAF7);
  border-radius: var(--rounded-md, 10px);
  padding: var(--spacing-4, 16px);
  margin-bottom: var(--spacing-6, 24px);
}

.scoring-title {
  font-weight: 600;
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-primary, #1A2E1A);
  margin: 0 0 var(--spacing-2, 8px);
}

.scoring-detail {
  font-size: var(--text-caption, 12px);
  color: var(--color-ink-secondary, #4A5A4A);
  margin: 0;
}

.section-title {
  font-size: var(--text-subheading, 18px);
  font-weight: 600;
  color: var(--color-ink-primary, #1A2E1A);
  margin: 0 0 var(--spacing-4, 16px);
}

.horse-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4, 16px);
  margin-top: var(--spacing-4, 16px);
}

/* Locked/ settled state: highlight user's voted horse */
.voted-horse {
  border: 2px solid var(--color-accent, #B8960C) !important;
}

/* Selection mode */
.selection-section {
  margin-top: var(--spacing-4, 16px);
}

.select-card-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3, 12px);
  margin-bottom: var(--spacing-4, 16px);
}

.selection-actions {
  display: flex;
  justify-content: center;
  margin-bottom: var(--spacing-4, 16px);
}

.cancel-btn {
  padding: 12px 24px;
  background: transparent;
  color: var(--color-ink-secondary, #4A5A4A);
  border: 1px solid var(--border-strong, #A8B8A4);
  border-radius: var(--rounded-md, 10px);
  font-size: var(--text-body, 16px);
  font-weight: 500;
  cursor: pointer;
  min-height: 44px;
}

.cancel-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.vote-error {
  color: var(--color-destructive, #C53030);
  font-size: var(--text-body-sm, 14px);
  margin: var(--spacing-2, 8px) 0;
}

.vote-error.toast {
  text-align: center;
}

/* Vote bar */
.vote-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: var(--spacing-3, 12px) var(--spacing-4, 16px);
  padding-bottom: calc(var(--spacing-3, 12px) + env(safe-area-inset-bottom, 0px));
  background: linear-gradient(to top, rgba(248, 250, 247, 1) 80%, rgba(248, 250, 247, 0));
  z-index: 100;
}

.locked-message {
  font-size: var(--text-body-sm, 14px);
  color: var(--color-ink-secondary, #4A5A4A);
  text-align: center;
  margin: 0;
}

.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 40vh;
  text-align: center;
  gap: var(--spacing-4, 16px);
}

.error-text {
  color: var(--color-destructive, #C53030);
  font-size: var(--text-body, 16px);
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
}

.refresh-btn:hover {
  background: var(--color-primary-light, #2D7A4F);
}

/* Admin actions */
.admin-actions {
  display: flex;
  justify-content: center;
  margin-top: var(--spacing-6, 24px);
  margin-bottom: var(--spacing-4, 16px);
}

.modify-result-btn {
  padding: 12px 24px;
  background: transparent;
  color: var(--color-primary, #1A5632);
  border: 1px solid var(--color-primary, #1A5632);
  border-radius: var(--rounded-md, 10px);
  font-size: var(--text-body, 16px);
  font-weight: 600;
  cursor: pointer;
  min-height: 44px;
  transition: background 0.2s, color 0.2s;
}

.modify-result-btn:hover {
  background: var(--color-primary, #1A5632);
  color: #FFFFFF;
}

/* Desktop: vote-bar inline instead of fixed */
@media (min-width: 768px) {
  .vote-bar {
    position: static;
    background: none;
    padding: var(--spacing-4, 16px) 0;
    padding-bottom: 0;
  }

  .race-detail-page.has-vote-bar {
    padding-bottom: var(--spacing-4, 16px);
  }
}
</style>
