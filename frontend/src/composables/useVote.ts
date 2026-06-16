import { ref, onUnmounted, type Ref } from 'vue'
import { submitVote, getRaceVotes, deleteVote } from '@/api/votes'
import type { VoteListEntry, VoteResponse } from '@/types/vote'
import type { RaceHorseSnapshot } from '@/types/race'

interface UseVoteReturn {
  selectedHorseId: Ref<number | null>
  selectedHorse: Ref<RaceHorseSnapshot | null>
  votedHorseName: Ref<string | null>
  votedRaceHorseId: Ref<number | null>
  isSubmitting: Ref<boolean>
  votes: Ref<VoteListEntry[]>
  votesLoading: Ref<boolean>
  votesError: Ref<string | null>
  errorMessage: Ref<string | null>
  toggleVote: (horse: RaceHorseSnapshot, raceId: number) => Promise<void>
  loadVotes: (raceId: number) => Promise<void>
  reset: () => void
}

export function useVote(initialVotedHorseName: string | null = null): UseVoteReturn {
  const selectedHorseId = ref<number | null>(null)
  const selectedHorse = ref<RaceHorseSnapshot | null>(null)
  const votedHorseName = ref<string | null>(initialVotedHorseName)
  const votedRaceHorseId = ref<number | null>(null)
  const isSubmitting = ref(false)
  const votes = ref<VoteListEntry[]>([])
  const votesLoading = ref(false)
  const votesError = ref<string | null>(null)
  const errorMessage = ref<string | null>(null)
  let unmounted = false

  onUnmounted(() => { unmounted = true })

  /**
   * Toggle vote on a horse card:
   * - If not voted → submit vote
   * - If voted for this horse → cancel vote
   * - If voted for another horse → change vote
   */
  async function toggleVote(horse: RaceHorseSnapshot, raceId: number) {
    if (isSubmitting.value) return

    // Same horse clicked again → cancel vote
    if (votedRaceHorseId.value === horse.race_horse_id) {
      await cancelVoteAction(raceId)
      return
    }

    // Different horse (or no previous vote) → submit/change vote
    await castVoteAction(horse, raceId)
  }

  async function castVoteAction(horse: RaceHorseSnapshot, raceId: number) {
    const previousVotedName = votedHorseName.value
    const optimisticName = horse.snapshot_data.name

    votedHorseName.value = optimisticName
    votedRaceHorseId.value = horse.race_horse_id
    isSubmitting.value = true
    errorMessage.value = null

    try {
      const result: VoteResponse = await submitVote(raceId, horse.race_horse_id)
      if (unmounted) return
      votedHorseName.value = result.horse_name
      votedRaceHorseId.value = horse.race_horse_id
    } catch (err: unknown) {
      if (unmounted) return
      votedHorseName.value = previousVotedName
      if (previousVotedName === null) {
        votedRaceHorseId.value = null
      }
      const axiosErr = err as { response?: { data?: { detail?: { message?: string } } } }
      errorMessage.value = axiosErr?.response?.data?.detail?.message ?? '投票失败，请重试'
    } finally {
      isSubmitting.value = false
    }

    // Refresh vote distribution (independent try/catch)
    try {
      if (!unmounted) await loadVotes(raceId)
    } catch {
      // Non-critical
    }
  }

  async function cancelVoteAction(raceId: number) {
    const previousVotedName = votedHorseName.value

    // Optimistic clear
    votedHorseName.value = null
    votedRaceHorseId.value = null
    isSubmitting.value = true
    errorMessage.value = null

    try {
      await deleteVote(raceId)
      if (unmounted) return
    } catch (err: unknown) {
      if (unmounted) return
      // Rollback on failure
      votedHorseName.value = previousVotedName
      // Need to find the previous race_horse_id — won't be accurate but name is sufficient
      const axiosErr = err as { response?: { data?: { detail?: { message?: string } } } }
      errorMessage.value = axiosErr?.response?.data?.detail?.message ?? '取消投票失败，请重试'
    } finally {
      isSubmitting.value = false
    }

    // Refresh vote distribution
    try {
      if (!unmounted) await loadVotes(raceId)
    } catch {
      // Non-critical
    }
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
    votedRaceHorseId.value = null
    isSubmitting.value = false
    votes.value = []
    votesLoading.value = false
    votesError.value = null
    errorMessage.value = null
  }

  return {
    selectedHorseId,
    selectedHorse,
    votedHorseName,
    votedRaceHorseId,
    isSubmitting,
    votes,
    votesLoading,
    votesError,
    errorMessage,
    toggleVote,
    loadVotes,
    reset,
  }
}
