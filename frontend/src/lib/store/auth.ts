'use client'
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface AuthUser {
  id: number
  phone_number: string
  full_name: string
  email?: string | null
  national_id?: string | null
  is_staff?: boolean
}

interface AuthStore {
  user: AuthUser | null
  token: string | null
  setAuth: (token: string, user: AuthUser) => void
  updateUser: (data: Partial<AuthUser>) => void
  logout: () => void
  isLoggedIn: () => boolean
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      setAuth: (token, user) => {
        document.cookie = `afi_token=${token}; path=/; max-age=${60 * 60 * 24 * 30}; SameSite=Lax`
        set({ token, user })
      },
      updateUser: (data) => {
        const current = get().user
        if (current) set({ user: { ...current, ...data } })
      },
      logout: () => {
        document.cookie = 'afi_token=; path=/; max-age=0; SameSite=Lax'
        set({ token: null, user: null })
      },
      isLoggedIn: () => !!get().token,
    }),
    { name: 'afi_auth' }
  )
)
