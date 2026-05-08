'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { useAuthStore } from '@/store/authStore'
import { isDevMode, DEV_TOKEN } from '@/lib/auth'
import { ArrowRight, Compass, Map, ShieldCheck, FlaskConical } from 'lucide-react'

export default function LoginPage() {
  const { user, loading, signIn, signInAsDemo, token } = useAuthStore()
  const router = useRouter()
  const devMode = isDevMode()

  useEffect(() => {
    if (!loading && user) router.push('/dashboard')
  }, [user, loading, router])

  // Persist dev token to localStorage so api.ts interceptor can read it
  useEffect(() => {
    if (token) localStorage.setItem('travelai-token', token)
    else localStorage.removeItem('travelai-token')
  }, [token])

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="grid w-full max-w-4xl overflow-hidden rounded-3xl bg-white shadow-2xl lg:grid-cols-[1.1fr_0.9fr]"
      >
        {/* Left panel */}
        <div className="hidden bg-gradient-to-br from-blue-900 via-blue-800 to-slate-800 p-10 text-white lg:block">
          <div className="mb-10 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-white/10">
            <Compass className="h-6 w-6" />
          </div>
          <h2 className="text-3xl font-bold leading-tight">AI-powered travel planning, built for the real world.</h2>
          <p className="mt-3 text-sm text-blue-100/90">
            LangGraph + Gemini + Graphiti — personalized itineraries with route validation, budget checks, and weather awareness.
          </p>
          <div className="mt-8 space-y-3 text-sm text-blue-100">
            <div className="flex items-center gap-2"><ShieldCheck className="h-4 w-4" />Firebase Auth (or Demo Mode)</div>
            <div className="flex items-center gap-2"><Map className="h-4 w-4" />Route-aware AI itinerary generation</div>
          </div>
        </div>

        {/* Right panel */}
        <div className="p-8 sm:p-10">
          <div className="mx-auto w-full max-w-sm">
            <div className="mb-5 inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-100">
              <Map className="h-7 w-7 text-blue-700" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900">Welcome to TravelAI</h1>
            <p className="mt-2 text-sm text-slate-500">Sign in to start planning AI-powered trips.</p>

            {/* Demo mode banner */}
            {devMode && (
              <div className="mt-5 rounded-xl bg-amber-50 border border-amber-200 px-4 py-3 text-sm text-amber-800">
                <FlaskConical className="inline h-4 w-4 mr-1.5 -mt-0.5" />
                <strong>Demo Mode</strong> — Firebase not configured. Use Demo Login below.
              </div>
            )}

            {/* Google sign-in (shown only when Firebase is configured) */}
            {!devMode && (
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={signIn}
                className="mt-6 flex min-h-12 w-full items-center justify-center gap-3 rounded-xl border border-slate-200 px-6 py-3 font-medium text-slate-700 transition-colors hover:bg-slate-50"
              >
                <svg className="h-5 w-5" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                </svg>
                Continue with Google
                <ArrowRight className="h-4 w-4" />
              </motion.button>
            )}

            {/* Demo login button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={signInAsDemo}
              className={`${devMode ? 'mt-6' : 'mt-3'} flex min-h-12 w-full items-center justify-center gap-3 rounded-xl px-6 py-3 font-medium transition-colors ${
                devMode
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              <FlaskConical className="h-4 w-4" />
              {devMode ? 'Continue as Demo User' : 'Try Demo (no login)'}
            </motion.button>

            <p className="mt-5 text-xs text-slate-400">
              Demo mode uses real Gemini AI — itineraries are generated live with your API key.
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
