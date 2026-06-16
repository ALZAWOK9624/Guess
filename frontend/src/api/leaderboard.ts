/** Leaderboard API calls. */

import apiClient from './client'
import type { LeaderboardEntry } from '@/types/leaderboard'

export async function getLeaderboard(): Promise<LeaderboardEntry[]> {
  const response = await apiClient.get('/leaderboard')
  return response.data.data as LeaderboardEntry[]
}
