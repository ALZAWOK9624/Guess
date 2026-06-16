/** Leaderboard type definitions. */

export interface LeaderboardEntry {
  username: string
  total_points: number
  races_participated: number
  avg_points: number
}

export interface LeaderboardResponse {
  data: LeaderboardEntry[]
}
