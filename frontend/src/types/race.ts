/** Race types. */

export interface RaceListItem {
  id: number
  name: string
  date: string
  grade: Grade
  status: RaceStatus
  horse_count: number
  vote_count: number
  created_at: string
  custom_scoring?: CustomScoring | null
}

export interface RaceDetail {
  id: number
  name: string
  date: string
  grade: Grade
  status: RaceStatus
  custom_scoring: CustomScoring | null
  horses: RaceHorseSnapshot[]
  horse_votes?: RaceDetailHorseVotes | null  // only for settled races
  vote_count: number
  created_at: string
  updated_at: string
}

export interface RaceHorseSnapshot {
  horse_id: number
  race_horse_id: number
  snapshot_data: HorseSnapshotData
  position: number | null
}

export interface PublicResultVote {
  username: string
  points: number | null
}

export interface RaceHorseResult {
  race_horse_id: number
  horse_id: number
  snapshot_data: Record<string, any>
  position: number | null
  votes: PublicResultVote[]
}

export interface RaceDetailHorseVotes {
  horses: RaceHorseResult[]
}

export interface HorseSnapshotData {
  name: string
  sex: string | null
  age: number | null
  origin: string | null
  sire: string | null
  damsire: string | null
  weight: string | null
  jockey: string | null
  previous_result: string | null
  best_win: string | null
}

export interface CustomScoring {
  positive_scores: number[]
  penalty_rules?: PenaltyRule[] | null
}

export interface PenaltyRule {
  position: number
  points: number
}

export type Grade = 'G1' | 'G2_JPN1' | 'YOUNG_G1' | 'CUSTOM'
export type RaceStatus = 'voting' | 'locked' | 'settled'

export interface RaceCreatePayload {
  name: string
  date: string
  grade: Grade
  horse_ids: number[]
  custom_scoring?: CustomScoring | null
}

export interface RaceUpdatePayload {
  name?: string
  date?: string
  grade?: Grade
  horse_ids?: number[]
  custom_scoring?: CustomScoring | null
}

/** Result entry types */
export interface ResultPosition {
  race_horse_id: number
  position: number  // 0 = DNF, 1+ = finishing order
}

export interface UserScore {
  user_id: number
  username: string
  points: number
}

export interface ResultEntryResponse {
  race_id: number
  status: string
  scores: UserScore[]
}
