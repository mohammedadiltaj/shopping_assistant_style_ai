import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
    customer_id: number
    email: string
    first_name?: string
    last_name?: string
}

interface AuthState {
    token: string | null
    user: User | null
    login: (token: string, user: User) => void
    logout: () => void
    isAuthenticated: () => boolean
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set, get) => ({
            token: null,
            user: null,
            login: (token, user) => set({ token, user }),
            logout: () => set({ token: null, user: null }),
            isAuthenticated: () => !!get().token
        }),
        {
            name: 'shopping-assistant-auth',
        }
    )
)
