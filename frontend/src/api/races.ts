/** Race API calls. */

import apiClient from './client'
import type {
  AddRaceHorsePayload,
  GateOrderPayload,
  RaceCreatePayload,
  RaceDetail,
  RaceHorseSnapshot,
  RaceHorseUpdatePayload,
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

export async function addRaceHorse(
  raceId: number,
  data: AddRaceHorsePayload,
): Promise<RaceHorseSnapshot> {
  const res = await apiClient.post<{ data: RaceHorseSnapshot }>(
    `/races/${raceId}/horses`,
    data,
  )
  return res.data.data
}

export async function updateRaceHorse(
  raceId: number,
  raceHorseId: number,
  data: RaceHorseUpdatePayload,
): Promise<RaceHorseSnapshot> {
  const res = await apiClient.patch<{ data: RaceHorseSnapshot }>(
    `/races/${raceId}/horses/${raceHorseId}`,
    data,
  )
  return res.data.data
}

export async function updateGateOrder(
  raceId: number,
  data: GateOrderPayload,
): Promise<RaceDetail> {
  const res = await apiClient.patch<{ data: RaceDetail }>(
    `/races/${raceId}/horses/gate`,
    data,
  )
  return res.data.data
}

export async function lockRace(raceId: number): Promise<{ id: number; name: string; status: string }> {
  const res = await apiClient.post<{ data: { id: number; name: string; status: string } }>(
    `/races/${raceId}/lock`,
  )
  return res.data.data
}
