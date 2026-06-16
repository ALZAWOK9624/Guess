/** Admin API calls. */

import apiClient from './client'
import type { InviteCode } from '@/types/admin'

export async function getInviteCodes(search?: string): Promise<InviteCode[]> {
  const params = search ? { search } : undefined
  const res = await apiClient.get<{ data: InviteCode[] }>('/admin/invite-codes', { params })
  return res.data.data
}

export async function createInviteCode(qq: string): Promise<InviteCode> {
  const res = await apiClient.post<{ data: InviteCode }>('/admin/invite-codes', { qq })
  return res.data.data
}

export async function deleteInviteCode(code: string): Promise<void> {
  await apiClient.delete(`/admin/invite-codes/${code}`)
}
