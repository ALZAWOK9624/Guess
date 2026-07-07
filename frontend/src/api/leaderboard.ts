/** Leaderboard API calls. */

import apiClient from './client'
import type { LeaderboardEntry, LeaderboardFilters } from '@/types/leaderboard'

export async function getLeaderboard(filters?: LeaderboardFilters): Promise<LeaderboardEntry[]> {
  const params: Record<string, string | number | string[]> = {}
  if (filters) {
    if (filters.age_range?.length) params.age_range = filters.age_range
    if (filters.sex_restriction?.length) params.sex_restriction = filters.sex_restriction
    if (filters.race_grade?.length) params.race_grade = filters.race_grade
    if (filters.country?.length) params.country = filters.country
    if (filters.surface?.length) params.surface = filters.surface
    if (filters.distance_min !== undefined) params.distance_min = filters.distance_min
    if (filters.distance_max !== undefined) params.distance_max = filters.distance_max
    if (filters.horse_count_min !== undefined) params.horse_count_min = filters.horse_count_min
    if (filters.horse_count_max !== undefined) params.horse_count_max = filters.horse_count_max
  }
  const response = await apiClient.get('/leaderboard', { params })
  return response.data.data as LeaderboardEntry[]
}
