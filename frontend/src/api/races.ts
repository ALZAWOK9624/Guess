/** Race API calls. */

import apiClient from './client'
import type {
  RaceCreatePayload,
  RaceDetail,
  RaceListItem,
  RaceUpdatePayload,
} from '@/types/race'

export async function getRaces(status?: string): Promise<RaceListItem[]> {
  const params = status ? { status } : undefined
  const res = await apiClient.get<{ data: RaceListItem[] }>('/races', { params })
  return res.data.data
}

export async function getRace(id: number): Promise<RaceDetail> {
  const res = await apiClient.get<{ data: RaceDetail }>(`/races/${id}`)
  return res.data.data
}

export async function createRace(data: RaceCreatePayload): Promise<RaceDetail> {
  const res = await apiClient.post<{ data: RaceDetail }>('/races', data)
  return res.data.data
}

export async function updateRace(
  id: number,
  data: RaceUpdatePayload,
): Promise<RaceDetail> {
  const res = await apiClient.patch<{ data: RaceDetail }>(`/races/${id}`, data)
  return res.data.data
}

export async function deleteRace(id: number): Promise<void> {
  await apiClient.delete(`/races/${id}`)
}
