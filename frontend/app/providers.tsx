'use client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { useEffect } from 'react'
import { onAuthStateChanged } from 'firebase/auth'
import { auth } from '@/lib/firebase'
import { useAuthStore } from '@/store/authStore'
import { isDevMode, DEV_TOKEN } from '@/lib/auth'

const queryClient = new QueryClient()

function AuthProvider({ children }: { children: React.ReactNode }) {
  const { setUser, setToken, setLoading, token } = useAuthStore()

  // Sync token to localStorage for api.ts interceptor
  useEffect(() => {
    if (token) localStorage.setItem('travelai-token', token)
    else localStorage.removeItem('travelai-token')
  }, [token])

  useEffect(() => {
    if (isDevMode()) {
      // In dev mode, check if we have a stored token from a previous demo login
      const stored = localStorage.getItem('travelai-token')
      if (stored === DEV_TOKEN) {
        // Restore session silently — auth store already has user from localStorage via persist
      }
      setLoading(false)
      return
    }

    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setUser(user)
      if (user) {
        const t = await user.getIdToken()
        setToken(t)
      } else {
        setToken(null)
      }
      setLoading(false)
    })
    return unsubscribe
  }, [setUser, setToken, setLoading])

  return <>{children}</>
}

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>{children}</AuthProvider>
      <Toaster position="top-right" />
    </QueryClientProvider>
  )
}
