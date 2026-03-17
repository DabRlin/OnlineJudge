/**
 * 认证相关 API 服务
 */

import { api } from './api'
import type {
  User,
  UserRegister,
  UserLogin,
  UserUpdate,
  PasswordUpdate,
  TokenResponse,
} from '@/types'

/**
 * 认证 API
 */
export const authApi = {
  /**
   * 用户注册
   */
  register: async (data: UserRegister): Promise<User> => {
    const response = await api.post<User>('/auth/register', data)
    return response.data
  },

  /**
   * 用户登录
   */
  login: async (data: UserLogin): Promise<TokenResponse> => {
    const formData = new URLSearchParams()
    formData.append('username', data.username)
    formData.append('password', data.password)

    const response = await api.post<TokenResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  /**
   * 获取当前用户信息
   */
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me')
    return response.data
  },

  /**
   * 更新用户信息
   */
  updateUser: async (data: UserUpdate): Promise<User> => {
    const response = await api.put<User>('/auth/me', data)
    return response.data
  },

  /**
   * 修改密码
   */
  updatePassword: async (data: PasswordUpdate): Promise<User> => {
    const response = await api.post<User>('/auth/me/password', data)
    return response.data
  },
}
