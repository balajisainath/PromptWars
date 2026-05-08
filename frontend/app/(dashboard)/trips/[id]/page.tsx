'use client'
import { useQuery } from '@tanstack/react-query'
import { useParams } from 'next/navigation'
import api from '@/lib/api'
import { motion } from 'framer-motion'
import { AlertCircle, Calendar, CheckCircle, Clock, DollarSign, Loader2, MapPin, Users } from 'lucide-react'

export default function TripDetailPage() {
  const { id } = useParams()

  const { data: trip, isLoading: tripLoading } = useQuery({
    queryKey: ['trip', id],
    queryFn: () => api.get(`/api/v1/trips/${id}`).then((r) => r.data),
  })

  const { data: itineraries, isLoading: itiLoading } = useQuery({
    queryKey: ['itineraries', id],
    queryFn: () => api.get(`/api/v1/trips/${id}/itineraries`).then((r) => r.data),
    refetchInterval: 5000,
  })

  const latestItinerary = itineraries?.[0]

  const { data: fullItinerary } = useQuery({
    queryKey: ['itinerary', latestItinerary?.id],
    queryFn: () => api.get(`/api/v1/itineraries/${latestItinerary?.id}`).then((r) => r.data),
    enabled: !!latestItinerary?.id,
  })

  if (tripLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-emerald-200 border-t-emerald-700" />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-5xl space-y-4 sm:space-y-6">
      <div className="glass-panel rounded-2xl p-5 sm:p-6">
        <h1 className="mb-4 text-2xl font-bold text-slate-900 sm:text-3xl">{trip?.title}</h1>
        <div className="flex flex-wrap gap-4 text-sm text-slate-600">
          {trip?.destination && <span className="flex items-center gap-1.5"><MapPin className="h-4 w-4 text-emerald-700" />{trip.destination}</span>}
          {trip?.start_date && <span className="flex items-center gap-1.5"><Calendar className="h-4 w-4 text-emerald-700" />{trip.start_date} → {trip.end_date}</span>}
          {trip?.budget && <span className="flex items-center gap-1.5"><DollarSign className="h-4 w-4 text-emerald-700" />{trip.budget} {trip.currency}</span>}
          {trip?.group_size && <span className="flex items-center gap-1.5"><Users className="h-4 w-4 text-emerald-700" />{trip.group_size} {trip.group_size === 1 ? 'person' : 'people'}</span>}
        </div>
        {trip?.description && <p className="mt-3 text-slate-500 text-sm">{trip.description}</p>}
      </div>

      {itiLoading ? (
        <div className="glass-panel rounded-2xl p-10 text-center sm:p-12">
          <Loader2 className="mx-auto mb-3 h-8 w-8 animate-spin text-emerald-700" />
          <p className="text-slate-600 font-medium">Generating your AI itinerary...</p>
          <p className="text-slate-400 text-sm mt-1">This takes 10-30 seconds. Intent → Memory → Search → Planning → Validation</p>
        </div>
      ) : !latestItinerary ? (
        <div className="glass-panel rounded-2xl p-10 text-center sm:p-12">
          <Loader2 className="mx-auto mb-3 h-8 w-8 animate-spin text-emerald-700" />
          <p className="text-slate-600 font-medium">AI is working on your itinerary...</p>
        </div>
      ) : (
        <div className="glass-panel rounded-2xl">
          <div className="flex flex-col gap-3 border-b border-emerald-100 p-5 sm:flex-row sm:items-center sm:justify-between sm:p-6">
            <h2 className="font-semibold text-slate-800">AI-Generated Itinerary</h2>
            <div className="flex flex-wrap items-center gap-2">
              {latestItinerary.validation_status === 'valid' ? (
                <span className="flex items-center gap-1.5 text-sm font-medium text-emerald-700">
                  <CheckCircle className="h-4 w-4" /> Validated
                </span>
              ) : (
                <span className="flex items-center gap-1.5 text-sm font-medium text-amber-700">
                  <AlertCircle className="h-4 w-4" /> {latestItinerary.validation_status}
                </span>
              )}
              {latestItinerary.total_cost && (
                <span className="ml-2 text-sm text-slate-500">
                  Total: ${latestItinerary.total_cost} {latestItinerary.currency}
                </span>
              )}
            </div>
          </div>

          <div className="divide-y divide-emerald-50">
            {fullItinerary?.days?.map((day: {
              day_number: number
              date: string | null
              day_summary: string
              activities: Array<{
                id: string
                name: string
                start_time: string | null
                end_time: string | null
                description: string | null
                location: string | null
                estimated_cost: number | null
                activity_type: string | null
              }>
            }) => (
              <motion.div
                key={day.day_number}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="p-4 sm:p-6"
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-700 text-sm font-bold text-white">
                    {day.day_number}
                  </div>
                  <div>
                    <p className="font-medium text-slate-800">Day {day.day_number}{day.date ? ` — ${day.date}` : ''}</p>
                    <p className="text-sm text-slate-500">{day.day_summary}</p>
                  </div>
                </div>

                <div className="space-y-3 sm:ml-11">
                  {day.activities.map((act) => (
                    <div key={act.id} className="flex items-start gap-3 rounded-xl bg-white p-3">
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-0.5">
                          <p className="font-medium text-slate-800 text-sm">{act.name}</p>
                          {act.estimated_cost && (
                            <span className="text-xs text-slate-500">${act.estimated_cost}</span>
                          )}
                        </div>
                        {act.start_time && (
                          <p className="mb-1 flex items-center gap-1 text-xs text-emerald-700">
                            <Clock className="h-3 w-3" /> {act.start_time} — {act.end_time}
                          </p>
                        )}
                        {act.location && <p className="flex items-center gap-1 text-xs text-slate-500"><MapPin className="h-3 w-3" />{act.location}</p>}
                        {act.description && <p className="text-xs text-slate-500 mt-1">{act.description}</p>}
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
