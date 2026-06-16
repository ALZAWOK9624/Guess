/** Vote API calls. */

import apiClient from './client'
import type { VoteResponse, VoteListEntry } from '@/types/vote'

export async function submitVote(raceId: number, raceHorseId: number): Promise<VoteResponse> {
  const res = await apiClient.post<{ data: VoteResponse }>(`/races/${raceId}/votes`, {
    race_horse_id: raceHorseId,
  })
  return res.data.data
}

export async function getRaceVotes(raceId: number): Promise<VoteListEntry[]> {
  const res = await apiClient.get<{ data: VoteListEntry[] }>(`/races/${raceId}/votes`)
  return res.data.data
}

export async function deleteVote(raceId: number): Promise<void> {
  await apiClient.delete(`/races/${raceId}/votes`)
}
