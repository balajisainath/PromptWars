'use client'

import { motion } from 'framer-motion'
import { Compass, Mountain, UtensilsCrossed, Waves } from 'lucide-react'

const themes = [
  { title: 'City Discovery', desc: 'Walkable neighborhoods, architecture, and cafe-rich routes.', icon: Compass },
  { title: 'Nature Escape', desc: 'Parks, trails, and scenic transitions with realistic timing.', icon: Mountain },
  { title: 'Food First', desc: 'Markets, local staples, and reservation-friendly evenings.', icon: UtensilsCrossed },
  { title: 'Coastal Slowdown', desc: 'Beach rhythm with low-friction travel between stops.', icon: Waves },
]

export default function ExplorePage() {
  return (
    <div className="space-y-6 sm:space-y-8">
      <div>
        <p className="text-xs font-semibold tracking-[0.16em] text-emerald-700">EXPLORE</p>
        <h1 className="mt-2 text-3xl font-bold text-slate-900 sm:text-4xl">Inspiration for your next itinerary</h1>
        <p className="mt-2 text-sm text-slate-600">Browse planning themes and turn one into a personalized trip in one click.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {themes.map((theme, index) => (
          <motion.article
            key={theme.title}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.08 }}
            className="glass-panel rounded-2xl p-5"
          >
            <div className="mb-3 inline-flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-100">
              <theme.icon className="h-5 w-5 text-emerald-700" />
            </div>
            <h2 className="text-lg font-semibold text-slate-900">{theme.title}</h2>
            <p className="mt-2 text-sm text-slate-600">{theme.desc}</p>
            <button className="btn-soft mt-4">Use this theme</button>
          </motion.article>
        ))}
      </div>
    </div>
  )
}
