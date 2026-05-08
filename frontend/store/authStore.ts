import { create } from 'zustand'
import { User } from 'firebase/auth'
import { auth, googleProvider } from '@/lib/firebase'
import { signInWithPopup, signOut as firebaseSignOut } from 'firebase/auth'
import { DEV_TOKEN, DEV_USER, isDevMode, devLogin } from '@/lib/auth'

interface MockUser {
  uid: string
  email: string
  displayName: string
  photoURL: string | null
  getIdToken: () => Promise<string>
}

interface AuthState {
  user: User | MockUser | null
  token: string | null
  loading: boolean
  setUser: (user: User | MockUser | null) => void
  setToken: (token: string | null) => void
  setLoading: (loading: boolean) => void
  signIn: () => Promise<void>
  signInAsDemo: () => Promise<void>
  signOut: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  loading: true,
  setUser: (user) => set({ user }),
  setToken: (token) => set({ token }),
  setLoading: (loading) => set({ loading }),

  signIn: async () => {
    if (isDevMode()) {
      const mockUser: MockUser = { ...DEV_USER, getIdToken: async () => DEV_TOKEN }
      await devLogin()
      set({ user: mockUser, token: DEV_TOKEN, loading: false })
      return
    }
    await signInWithPopup(auth, googleProvider)
  },

  signInAsDemo: async () => {
    const mockUser: MockUser = { ...DEV_USER, getIdToken: async () => DEV_TOKEN }
    await devLogin()
    set({ user: mockUser, token: DEV_TOKEN, loading: false })
  },

  signOut: async () => {
    if (!isDevMode()) {
      try { await firebaseSignOut(auth) } catch { /* ignore */ }
    }
    set({ user: null, token: null })
  },
}))
