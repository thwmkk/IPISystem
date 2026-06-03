import api from './axios'
import type { LoginRequest, LoginResponse, UserInfo } from '@/types/user'

export const authApi = {
  login(data: LoginRequest) {
    return api.post<LoginResponse>('/auth/login/', data)
  },

  me() {
    return api.get<UserInfo>('/auth/me/')
  },

  refreshToken(refresh: string) {
    return api.post<{ access: string }>('/auth/refresh/', { refresh })
  },
}
