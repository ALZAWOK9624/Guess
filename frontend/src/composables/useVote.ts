import { ref, onUnmounted, type Ref } from 'vue'
import { submitVote, getRaceVotes } from '@/api/votes'
import type { VoteListEntry, VoteResponse } from '@/types/vote'
import type { RaceHorseSnapshot } from '@/types/race'

interface UseVoteReturn {
  selectedHorseId: Ref<number | null>
  selectedHorse: Ref<RaceHorseSnapshot | null>
  votedHorseName: Ref<string | null>
  isSubmitting: Ref<boolean>
  isInSelectionMode: Ref<boolean>
  votes: Ref<VoteListEntry[]>
  votesLoading: Ref<boolean>
  votesError: Ref<string | null>
  errorMessage: Ref<string | null>
  selectHorse: (horse: RaceHorseSnapshot, raceId: number) => Promise<void>
  enterSelectionMode: (raceHorses: RaceHorseSnapshot[]) => void
  exitSelectionMode: () => void
  loadVotes: (raceId: number) => Promise<void>
  reset: () => void
}

export function useVote(initialVotedHorseName: string | null = null): UseVoteReturn {
  const selectedHorseId = ref<number | null>(null)
  const selectedHorse = ref<RaceHorseSnapshot | null>(null)
  const votedHorseName = ref<string | null>(initialVotedHorseName)
  const isSubmitting = ref(false)
  const isInSelectionMode = ref(false)
  const votes = ref<VoteListEntry[]>([])
  const votesLoading = ref(false)
  const votesError = ref<string | null>(null)
  const errorMessage = ref<string | null>(null)
  let unmounted = false

  onUnmounted(() => { unmounted = true })

  async function selectHorse(horse: RaceHorseSnapshot, raceId: number) {
    if (isSubmitting.value) return
    // Skip if same horse already selected
    if (selectedHorseId.value === horse.race_horse_id) return
    selectedHorseId.value = horse.race_horse_id
    selectedHorse.value = horse
    // Direct submission when in selection mode
    if (isInSelectionMode.value) {
      await confirmVote(raceId)
    }
  }

  async function confirmVote(raceId: number) {
    if (selectedHorseId.value === null) return

    const previousVotedName = votedHorseName.value
    const optimisticName = selectedHorse.value?.snapshot_data.name ?? null

    votedHorseName.value = optimisticName
    isSubmitting.value = true
    errorMessage.value = null

    try {
      const result: VoteResponse = await submitVote(raceId, selectedHorseId.value)
      if (unmounted) return
      votedHorseName.value = result.horse_name
      isInSelectionMode.value = false
      selectedHorseId.value = null
      selectedHorse.value = null
    } catch (err: unknown) {
      if (unmounted) return
      votedHorseName.value = previousVotedName
      const axiosErr = err as { response?: { data?: { detail?: { message?: string } } } }
      errorMessage.value = axiosErr?.response?.data?.detail?.message ?? '投票失败，请重试'
    } finally {
      isSubmitting.value = false
    }

    // Refresh vote distribution (independent try/catch — don't let failure affect vote state)
    try {
      if (!unmounted) await loadVotes(raceId)
    } catch {
      // Vote distribution refresh failure is non-critical
    }
  }

  /** Enter selection mode, pre-selecting the user's existing vote if any. */
  function enterSelectionMode(raceHorses: RaceHorseSnapshot[]) {
    isInSelectionMode.value = true
    selectedHorseId.value = null
    selectedHorse.value = null
    errorMessage.value = null
    // Pre-select existing vote
    if (votedHorseName.value) {
      const existing = raceHorses.find(h => h.snapshot_data.name === votedHorseName.value)
      if (existing) {
        selectedHorseId.value = existing.race_horse_id
        selectedHorse.value = existing
      }
    }
  }

  function exitSelectionMode() {
    isInSelectionMode.value = false
    selectedHorseId.value = null
    selectedHorse.value = null
    errorMessage.value = null
  }

  async function loadVotes(raceId: number) {
    votesLoading.value = true
    votesError.value = null
    try {
      const data = await getRaceVotes(raceId)
      votes.value = data
    } catch (err) {
      votes.value = []
      votesError.value = '投票分布加载失败'
    } finally {
      votesLoading.value = false
    }
  }

  function reset() {
    selectedHorseId.value = null
    selectedHorse.value = null
    votedHorseName.value = null
    isSubmitting.value = false
    isInSelectionMode.value = false
    votes.value = []
    votesLoading.value = false
    votesError.value = null
    errorMessage.value = null
  }

  return {
    selectedHorseId,
    selectedHorse,
    votedHorseName,
    isSubmitting,
    isInSelectionMode,
    votes,
    votesLoading,
    votesError,
    errorMessage,
    selectHorse,
    enterSelectionMode,
    exitSelectionMode,
    loadVotes,
    reset,
  }
}
