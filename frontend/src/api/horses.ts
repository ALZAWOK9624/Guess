/** Horse API calls. */

import apiClient from './client'
import type { Horse, HorseCreatePayload, HorseUpdatePayload, OriginStat, LocationStat } from '@/types/horse'

export async function getHorses(name?: string): Promise<Horse[]> {
  const params = name ? { name } : undefined
  const res = await apiClient.get<{ data: Horse[] }>('/horses', { params })
  return res.data.data
}

export async function getHorse(id: number): Promise<Horse> {
  const res = await apiClient.get<{ data: Horse }>(`/horses/${id}`)
  return res.data.data
}

export async function getOriginsStats(): Promise<OriginStat[]> {
  const res = await apiClient.get<{ data: OriginStat[] }>('/horses/origins/stats')
  return res.data.data
}

export async function getLocationsStats(): Promise<LocationStat[]> {
  const res = await apiClient.get<{ data: LocationStat[] }>('/horses/locations/stats')
  return res.data.data
}

export async function createHorse(data: HorseCreatePayload): Promise<Horse> {
  const res = await apiClient.post<{ data: Horse }>('/horses', data)
  return res.data.data
}

export async function updateHorse(id: number, data: HorseUpdatePayload): Promise<Horse> {
  const res = await apiClient.patch<{ data: Horse }>(`/horses/${id}`, data)
  return res.data.data
}

export async function deleteHorse(id: number): Promise<void> {
  await apiClient.delete(`/horses/${id}`)
}

export async function toggleHemisphere(origin: string): Promise<{ origin: string; new_hemisphere: string; affected_count: number }> {
  const res = await apiClient.post<{ data: { origin: string; new_hemisphere: string; affected_count: number } }>(
    `/horses/origins/${encodeURIComponent(origin)}/toggle-hemisphere`,
  )
  return res.data.data
}

export async function updateBestWin(horseId: number, raceId: number): Promise<Horse> {
  const res = await apiClient.post<{ data: Horse }>(`/horses/${horseId}/update-best-win`, { race_id: raceId })
  return res.data.data
}
