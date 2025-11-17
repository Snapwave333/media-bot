import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '../services/api'

interface User {
  id: number
  email: string
  full_name: string | null
  subscription_status: string | null
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName?: string) => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true })
        try {
          const response = await api.post('/auth/login', { email, password })
          const { access_token } = response.data

          set({ token: access_token, isAuthenticated: true })

          // Fetch user data
          await get().fetchUser()
        } finally {
          set({ isLoading: false })
        }
      },

      register: async (email: string, password: string, fullName?: string) => {
        set({ isLoading: true })
        try {
          await api.post('/auth/register', {
            email,
            password,
            full_name: fullName,
          })

          // Auto-login after registration
          await get().login(email, password)
        } finally {
          set({ isLoading: false })
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        })
      },

      fetchUser: async () => {
        try {
          const response = await api.get('/auth/me')
          set({ user: response.data })
        } catch (error) {
          set({ user: null, token: null, isAuthenticated: false })
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token }),
    }
  )
)
