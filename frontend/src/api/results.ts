/** Result entry API calls — drag-sort result submission. */

import apiClient from './client'
import type { ResultEntryResponse, ResultPosition } from '@/types/race'

export async function submitResults(
  raceId: number,
  positions: ResultPosition[],
): Promise<ResultEntryResponse> {
  const res = await apiClient.put<{ data: ResultEntryResponse }>(
    `/races/${raceId}/results`,
    { positions },
  )
  return res.data.data
}
