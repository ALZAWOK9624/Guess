/** Auth API — registration (login/refresh added in Story 1.5a/1.5b). */

import apiClient from './client'
import type { RegisterRequest, RegisterResponse } from '@/types/auth'

export async function register(data: RegisterRequest): Promise<RegisterResponse> {
  const response = await apiClient.post('/auth/register', data)
  return response.data.data
}
