'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import api from '@/lib/api'
import toast from 'react-hot-toast'
import { ArrowLeft, ArrowRight, Calendar, DollarSign, Loader2, MapPin, Sparkles } from 'lucide-react'

const TRAVEL_STYLES = ['Adventure', 'Cultural', 'Relaxation', 'Family', 'Romantic', 'Budget', 'Luxury']

export default function NewTripPage() {
  const router = useRouter()
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    title: '',
    destination: '',
    description: '',
    start_date: '',
    end_date: '',
    budget: '',
    currency: 'USD',
    group_size: 1,
    travel_style: '',
  })

  const update = (key: string, value: string | number) => setForm((f) => ({ ...f, [key]: value }))

  const handleCreate = async () => {
    setLoading(true)
    try {
      const { data: trip } = await api.post('/api/v1/trips', {
        ...form,
        budget: form.budget ? parseFloat(form.budget) : null,
      })
      toast.success('Trip created! Generating itinerary...')
      await api.post('/api/v1/itineraries/generate', { trip_id: trip.id })
      router.push(`/trips/${trip.id}`)
    } catch {
      toast.error('Failed to create trip. Check your API keys.')
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl">
      <button onClick={() => router.back()} className="mb-6 flex items-center gap-2 text-sm text-slate-500 hover:text-slate-700">
        <ArrowLeft className="h-4 w-4" /> Back
      </button>

      <h1 className="mb-2 text-3xl font-bold text-slate-900 sm:text-4xl">Plan a New Trip</h1>
      <p className="mb-8 text-sm text-slate-600">Tell us about your dream trip and our AI will build your itinerary.</p>

      <div className="mb-8 flex gap-2">
        {[1, 2, 3].map((s) => (
          <div key={s} className={`h-1.5 flex-1 rounded-full transition-colors ${step >= s ? 'bg-emerald-700' : 'bg-emerald-100'}`} />
        ))}
      </div>

      <div className="glass-panel rounded-2xl p-5 sm:p-6">
        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div key="step1" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-5">
              <div>
                <label className="mb-1.5 block text-sm font-medium text-slate-700">Trip Name</label>
                <input value={form.title} onChange={(e) => update('title', e.target.value)} placeholder="e.g. Tokyo Adventure 2026" className="input-shell" />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-slate-700"><MapPin className="mr-1 inline h-4 w-4" />Destination</label>
                <input value={form.destination} onChange={(e) => update('destination', e.target.value)} placeholder="e.g. Tokyo, Japan" className="input-shell" />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-slate-700">Describe Your Ideal Trip</label>
                <textarea value={form.description} onChange={(e) => update('description', e.target.value)} rows={4} placeholder="e.g. I want to explore ancient temples, try authentic street food, and see Mount Fuji. I love hiking and cultural experiences." className="input-shell resize-none" />
              </div>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div key="step2" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-5">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="mb-1.5 block text-sm font-medium text-slate-700"><Calendar className="mr-1 inline h-4 w-4" />Start Date</label>
                  <input type="date" value={form.start_date} onChange={(e) => update('start_date', e.target.value)} className="input-shell" />
                </div>
                <div>
                  <label className="mb-1.5 block text-sm font-medium text-slate-700">End Date</label>
                  <input type="date" value={form.end_date} onChange={(e) => update('end_date', e.target.value)} className="input-shell" />
                </div>
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-slate-700">Group Size</label>
                <input type="number" min="1" max="50" value={form.group_size} onChange={(e) => update('group_size', parseInt(e.target.value || '1'))} className="input-shell" />
              </div>
            </motion.div>
          )}

          {step === 3 && (
            <motion.div key="step3" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-5">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <div className="sm:col-span-2">
                  <label className="mb-1.5 block text-sm font-medium text-slate-700"><DollarSign className="mr-1 inline h-4 w-4" />Total Budget</label>
                  <input type="number" value={form.budget} onChange={(e) => update('budget', e.target.value)} placeholder="2000" className="input-shell" />
                </div>
                <div>
                  <label className="mb-1.5 block text-sm font-medium text-slate-700">Currency</label>
                  <select value={form.currency} onChange={(e) => update('currency', e.target.value)} className="input-shell">
                    {['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD'].map((c) => <option key={c}>{c}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Travel Style</label>
                <div className="flex flex-wrap gap-2">
                  {TRAVEL_STYLES.map((s) => (
                    <button key={s} onClick={() => update('travel_style', s)} className={`rounded-lg border px-4 py-2 text-sm font-medium transition-colors ${form.travel_style === s ? 'border-emerald-700 bg-emerald-700 text-white' : 'border-slate-200 text-slate-600 hover:border-emerald-300'}`}>
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className="mt-8 flex justify-between">
        {step > 1 ? (
          <button onClick={() => setStep((s) => s - 1)} className="flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-800">
            <ArrowLeft className="h-4 w-4" /> Back
          </button>
        ) : <div />}

        {step < 3 ? (
          <button onClick={() => setStep((s) => s + 1)} disabled={step === 1 && !form.destination} className="btn-brand disabled:cursor-not-allowed disabled:bg-slate-300 disabled:text-slate-500">
            Continue <ArrowRight className="h-4 w-4" />
          </button>
        ) : (
          <button onClick={handleCreate} disabled={loading} className="btn-brand disabled:cursor-not-allowed disabled:bg-emerald-300">
            {loading ? <><Loader2 className="h-4 w-4 animate-spin" /> Generating AI Itinerary...</> : <><Sparkles className="h-4 w-4" /> Generate Itinerary</>}
          </button>
        )}
      </div>
    </div>
  )
}
