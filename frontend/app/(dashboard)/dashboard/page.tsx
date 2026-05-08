'use client'
import { useAuthStore } from '@/store/authStore'
import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { ArrowRight, Calendar, DollarSign, Map, Plus } from 'lucide-react'

type Trip = {
  id: string
  title: string
  destination: string
  start_date?: string
  status: string
  budget?: number
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  const { data: trips, isLoading } = useQuery({
    queryKey: ['trips'],
    queryFn: () => api.get('/api/v1/trips').then((r) => r.data as Trip[]),
  })

  const stats = [
    {
      label: 'Trips Planned',
      value: trips?.length ?? 0,
      icon: Map,
      iconClass: 'bg-emerald-100 text-emerald-700',
    },
    {
      label: 'Upcoming',
      value: trips?.filter((t) => t.status === 'planning').length ?? 0,
      icon: Calendar,
      iconClass: 'bg-amber-100 text-amber-700',
    },
    {
      label: 'Total Budget',
      value: `$${(trips?.reduce((s, t) => s + (t.budget || 0), 0) ?? 0).toLocaleString()}`,
      icon: DollarSign,
      iconClass: 'bg-cyan-100 text-cyan-700',
    },
  ]

  return (
    <div className="space-y-6 sm:space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold tracking-[0.16em] text-emerald-700">OVERVIEW</p>
          <h1 className="mt-2 text-3xl font-bold text-slate-900 sm:text-4xl">
          Good morning, {user?.displayName?.split(' ')[0]} 👋
          </h1>
          <p className="mt-1 text-sm text-slate-600">Ready to plan your next adventure?</p>
        </div>

        <Link href="/trips/new" className="btn-brand min-h-12 rounded-xl px-5 py-3 text-sm">
          <Plus className="mr-2 h-4 w-4" /> New Trip
        </Link>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {stats.map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-panel rounded-2xl p-5 sm:p-6"
          >
            <div className={`mb-4 flex h-11 w-11 items-center justify-center rounded-xl ${s.iconClass}`}>
              <s.icon className="h-5 w-5" />
            </div>
            <p className="text-3xl font-bold text-slate-900">{s.value}</p>
            <p className="mt-0.5 text-sm text-slate-600">{s.label}</p>
          </motion.div>
        ))}
      </div>

      <div className="glass-panel rounded-2xl">
        <div className="flex items-center justify-between border-b border-emerald-100 p-5 sm:p-6">
          <h2 className="text-lg font-semibold text-slate-900">Recent Trips</h2>
          <Link href="/trips" className="inline-flex items-center gap-2 text-sm font-semibold text-emerald-700 hover:text-emerald-800">
            View all
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>

        <div className="divide-y divide-emerald-50">
          {isLoading ? (
            <div className="p-8 text-center text-slate-500">Loading your trips...</div>
          ) : trips?.length === 0 ? (
            <div className="p-10 text-center sm:p-12">
              <Map className="mx-auto mb-3 h-12 w-12 text-emerald-200" />
              <p className="font-semibold text-slate-700">No trips yet</p>
              <p className="mb-4 text-sm text-slate-500">Create your first AI-powered itinerary in seconds.</p>
              <Link href="/trips/new" className="btn-brand">
                <Plus className="mr-2 h-4 w-4" /> Plan a Trip
              </Link>
            </div>
          ) : (
            trips?.slice(0, 5).map((trip) => (
              <Link
                key={trip.id}
                href="/trips"
                className="group flex flex-col gap-3 p-4 transition-colors hover:bg-emerald-50/60 sm:flex-row sm:items-center sm:justify-between sm:px-6"
              >
                <div className="min-w-0">
                  <p className="truncate font-semibold text-slate-800">{trip.title}</p>
                  <p className="truncate text-sm text-slate-500">
                    {trip.destination} • {trip.start_date ?? 'Date TBD'}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span
                    className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                      trip.status === 'completed'
                        ? 'bg-emerald-100 text-emerald-700'
                        : 'bg-amber-100 text-amber-700'
                    }`}
                  >
                    {trip.status}
                  </span>
                  <ArrowRight className="h-4 w-4 text-slate-300 transition-colors group-hover:text-slate-500" />
                </div>
              </Link>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
