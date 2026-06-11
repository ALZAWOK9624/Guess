/** Horse API calls. */

import apiClient from './client'
import type { Horse, HorseCreatePayload, HorseUpdatePayload } from '@/types/horse'

export async function getHorses(name?: string): Promise<Horse[]> {
  const params = name ? { name } : undefined
  const res = await apiClient.get<{ data: Horse[] }>('/horses', { params })
  return res.data.data
}

export async function getHorse(id: number): Promise<Horse> {
  const res = await apiClient.get<{ data: Horse }>(`/horses/${id}`)
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
