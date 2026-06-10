/** Auth API — register, login. */

import apiClient from './client'
import type { LoginRequest, LoginResponse, RegisterRequest, RegisterResponse } from '@/types/auth'

export async function register(data: RegisterRequest): Promise<RegisterResponse> {
  const response = await apiClient.post('/auth/register', data)
  return response.data.data
}

export async function login(data: LoginRequest): Promise<LoginResponse> {
  const response = await apiClient.post('/auth/login', data)
  return response.data.data
}
