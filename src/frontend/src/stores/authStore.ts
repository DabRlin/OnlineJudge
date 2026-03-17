/**
 * 认证状态管理 Store
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User, UserLogin, UserRegister } from '@/types'
import { authApi } from '@/services/auth'
import { message } from 'antd'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  loading: boolean

  // Actions
  login: (data: UserLogin) => Promise<void>
  register: (data: UserRegister) => Promise<void>
  logout: () => void
  fetchCurrentUser: () => Promise<void>
  updateUser: (user: Partial<User>) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      loading: false,

      /**
       * 用户登录
       */
      login: async (data: UserLogin) => {
        try {
          set({ loading: true })
          const tokenResponse = await authApi.login(data)
          
          // 保存 token
          set({ token: tokenResponse.access_token })
          
          // 获取用户信息
          const user = await authApi.getCurrentUser()
          set({
            user,
            isAuthenticated: true,
            loading: false,
          })
          
          message.success('登录成功！')
        } catch (error: any) {
          set({ loading: false })
          message.error(error.response?.data?.detail || '登录失败，请检查用户名和密码')
          throw error
        }
      },

      /**
       * 用户注册
       */
      register: async (data: UserRegister) => {
        try {
          set({ loading: true })
          await authApi.register(data)
          
          // 注册成功后自动登录
          await get().login({
            username: data.username,
            password: data.password,
          })
          
          message.success('注册成功！')
        } catch (error: any) {
          set({ loading: false })
          message.error(error.response?.data?.detail || '注册失败，请稍后重试')
          throw error
        }
      },

      /**
       * 用户登出
       */
      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        })
        message.info('已退出登录')
      },

      /**
       * 获取当前用户信息
       */
      fetchCurrentUser: async () => {
        try {
          const { token } = get()
          if (!token) {
            return
          }

          set({ loading: true })
          const user = await authApi.getCurrentUser()
          set({
            user,
            isAuthenticated: true,
            loading: false,
          })
        } catch (error) {
          // Token 无效，清除认证状态
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            loading: false,
          })
        }
      },

      /**
       * 更新用户信息
       */
      updateUser: (userData: Partial<User>) => {
        set((state) => ({
          user: state.user ? { ...state.user, ...userData } : null,
        }))
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
