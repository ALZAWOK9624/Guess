/** Horse types. */

export interface Horse {
  id: number
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
  created_at: string
  updated_at: string
}

export interface HorseCreatePayload {
  name: string
  sex?: string | null
  age?: number | null
  origin?: string | null
  sire?: string | null
  damsire?: string | null
  weight?: string | null
  jockey?: string | null
  previous_result?: string | null
  best_win?: string | null
}

export interface HorseUpdatePayload {
  name?: string | null
  sex?: string | null
  age?: number | null
  origin?: string | null
  sire?: string | null
  damsire?: string | null
  weight?: string | null
  jockey?: string | null
  previous_result?: string | null
  best_win?: string | null
}
