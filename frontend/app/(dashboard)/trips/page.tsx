'use client'
import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { ArrowRight, Calendar, MapPin, Plus } from 'lucide-react'

export default function TripsPage() {
  const { data: trips, isLoading } = useQuery({
    queryKey: ['trips'],
    queryFn: () => api.get('/api/v1/trips').then((r) => r.data),
  })

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-emerald-200 border-t-emerald-700" />
      </div>
    )
  }

  return (
    <div className="space-y-6 sm:space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold tracking-[0.16em] text-emerald-700">TRIPS</p>
          <h1 className="mt-2 text-3xl font-bold text-slate-900 sm:text-4xl">My Trips</h1>
        </div>
        <Link href="/trips/new" className="btn-brand min-h-12">
          <Plus className="h-4 w-4" /> New Trip
        </Link>
      </div>

      {trips?.length === 0 ? (
        <div className="glass-panel rounded-2xl p-12 text-center sm:p-16">
          <p className="mb-4 text-slate-500">No trips yet. Start planning!</p>
          <Link href="/trips/new" className="btn-brand inline-flex">
            <Plus className="h-4 w-4" /> Plan a Trip
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {trips?.map((trip: { id: string; title: string; destination: string; start_date: string; end_date: string; budget: number; currency: string; status: string }, i: number) => (
            <motion.div key={trip.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
              <Link href={`/trips/${trip.id}`} className="glass-panel group block rounded-2xl p-5 transition-shadow hover:shadow-xl">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-semibold text-slate-800">{trip.title}</h3>
                  <ArrowRight className="mt-0.5 h-4 w-4 text-slate-300 transition-colors group-hover:text-slate-500" />
                </div>
                <div className="space-y-1.5 text-sm text-slate-500">
                  {trip.destination && <p className="flex items-center gap-2"><MapPin className="h-3.5 w-3.5" />{trip.destination}</p>}
                  {trip.start_date && <p className="flex items-center gap-2"><Calendar className="h-3.5 w-3.5" />{trip.start_date} → {trip.end_date}</p>}
                </div>
                <div className="flex items-center justify-between mt-4">
                  {trip.budget && <span className="text-sm font-medium text-slate-700">${trip.budget} {trip.currency}</span>}
                  <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${trip.status === 'completed' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>{trip.status}</span>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
