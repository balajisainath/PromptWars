'use client'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import {
  ArrowRight,
  Brain,
  CalendarCheck,
  Compass,
  Globe,
  Route,
  Shield,
  Sparkles,
  Wallet,
} from 'lucide-react'
import { useEffect } from 'react'

export default function Home() {
  const { user, loading, signIn } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    if (!loading && user) router.push('/dashboard')
  }, [user, loading, router])

  const highlights = [
    { icon: Brain, title: 'Multi-Agent Planning', desc: 'A coordinated AI pipeline generates practical day plans, not just ideas.' },
    { icon: Route, title: 'Route-Aware Timing', desc: 'Travel windows and activity pacing are considered before finalizing your itinerary.' },
    { icon: Wallet, title: 'Budget Intelligence', desc: 'Daily spend estimates keep your plans aligned with what you want to spend.' },
    { icon: Shield, title: 'Validation Layer', desc: 'Constraint checks surface conflicts early so your trip plan remains realistic.' },
    { icon: Globe, title: 'Geo Context', desc: 'Location-aware recommendations adapt plans to where you actually are.' },
    { icon: CalendarCheck, title: 'Trip Memory', desc: 'Future plans learn from your travel history and saved preferences.' },
  ]

  return (
    <main className="pb-10 pt-4 sm:pt-8">
      <section className="app-shell relative overflow-hidden rounded-[2rem] border border-white/70 bg-gradient-to-br from-emerald-900 via-emerald-800 to-teal-900 px-4 py-8 text-white shadow-2xl sm:px-8 sm:py-12 lg:px-12 lg:py-16">
        <div className="pointer-events-none absolute -right-10 top-8 h-48 w-48 rounded-full bg-amber-300/25 blur-2xl" />
        <div className="pointer-events-none absolute -left-8 bottom-6 h-40 w-40 rounded-full bg-emerald-200/20 blur-2xl" />

        <div className="relative grid items-center gap-10 lg:grid-cols-[1.2fr_0.8fr]">
          <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
            <span className="inline-flex items-center gap-2 rounded-full border border-emerald-200/30 bg-emerald-200/10 px-4 py-1.5 text-xs font-semibold tracking-wide text-emerald-100 sm:text-sm">
              <Sparkles className="h-4 w-4" />
              AI TRIP ENGINE FOR REAL-WORLD PLANNING
            </span>

            <h1 className="mt-5 text-4xl font-bold leading-tight sm:text-5xl lg:text-6xl">
              Plan a trip you can
              <span className="block text-amber-300">actually follow.</span>
            </h1>

            <p className="mt-5 max-w-2xl text-sm text-emerald-50/90 sm:text-base lg:text-lg">
              Describe your destination, pace, and budget in plain language. TravelAI turns that into a validated
              itinerary with timing, route context, and practical day-by-day flow.
            </p>

            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center">
              <motion.button whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.98 }} onClick={signIn} className="btn-brand min-h-12 rounded-2xl px-6 py-3 text-base sm:text-sm">
                Start Planning
                <ArrowRight className="ml-2 h-4 w-4" />
              </motion.button>

              <button
                onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
                className="inline-flex min-h-12 items-center justify-center rounded-2xl border border-emerald-100/35 px-6 py-3 text-sm font-semibold text-emerald-50 transition hover:bg-emerald-50/10"
              >
                Explore Features
              </button>
            </div>

            <div className="mt-8 flex flex-wrap items-center gap-4 text-xs text-emerald-100/90 sm:text-sm">
              <span className="inline-flex items-center gap-2"><Compass className="h-4 w-4" />Mobile-first UX</span>
              <span className="inline-flex items-center gap-2"><Route className="h-4 w-4" />Smart route-aware plans</span>
              <span className="inline-flex items-center gap-2"><Shield className="h-4 w-4" />Built-in validation</span>
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 26 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, delay: 0.1 }} className="glass-panel rounded-3xl p-5 sm:p-6">
            <p className="mb-4 text-sm font-semibold text-emerald-950/70">Sample Trip Request</p>
            <div className="rounded-2xl bg-white p-4">
              <p className="text-sm text-slate-700">
                “Plan a 5-day Tokyo trip in October with food markets, one anime district day, budget under $220/day,
                and short metro hops.”
              </p>
            </div>
            <div className="mt-4 space-y-3 text-sm">
              {['Intent extracted', 'Attractions ranked', 'Timing validated', 'Budget optimized'].map((step, index) => (
                <div key={step} className="flex items-center justify-between rounded-xl bg-white px-4 py-3">
                  <span className="font-medium text-slate-700">{step}</span>
                  <span className="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700">
                    {index < 3 ? 'Done' : 'Live'}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      <section id="features" className="app-shell py-14 sm:py-16 lg:py-20">
        <div className="mb-8 sm:mb-10 lg:mb-12">
          <p className="text-xs font-semibold tracking-[0.16em] text-emerald-700">WHY THIS FEELS DIFFERENT</p>
          <h2 className="mt-2 text-3xl font-bold sm:text-4xl">Built for speed, clarity, and confidence</h2>
          <p className="mt-3 max-w-2xl text-sm text-slate-600 sm:text-base">
            The interface favors clear decisions on small screens first, then expands progressively for larger displays.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {highlights.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.2 }}
              transition={{ delay: i * 0.07 }}
              className="glass-panel rounded-2xl p-5 sm:p-6"
            >
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-100">
                <feature.icon className="h-5 w-5 text-emerald-700" />
              </div>
              <h3 className="text-lg font-semibold text-slate-900">{feature.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      <section className="app-shell">
        <div className="overflow-hidden rounded-3xl border border-emerald-200 bg-gradient-to-r from-emerald-700 to-teal-700 px-6 py-10 text-white sm:px-8 sm:py-12 lg:px-12">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <h2 className="text-3xl font-bold sm:text-4xl">Ready for your next trip?</h2>
              <p className="mt-2 max-w-xl text-sm text-emerald-50 sm:text-base">
                Sign in and generate a personalized itinerary in under 30 seconds.
              </p>
            </div>
            <motion.button whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.98 }} onClick={signIn} className="inline-flex min-h-12 items-center justify-center rounded-2xl bg-white px-6 py-3 text-sm font-semibold text-emerald-800">
              Get Started Free
              <ArrowRight className="ml-2 h-4 w-4" />
            </motion.button>
          </div>
        </div>
      </section>
    </main>
  )
}
