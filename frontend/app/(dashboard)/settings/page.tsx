'use client'
import { useAuthStore } from '@/store/authStore'
import { Bell, Globe, ShieldCheck, UserRound } from 'lucide-react'

export default function SettingsPage() {
  const { user } = useAuthStore()

  return (
    <div className="space-y-6 sm:space-y-8">
      <div>
        <p className="text-xs font-semibold tracking-[0.16em] text-emerald-700">SETTINGS</p>
        <h1 className="mt-2 text-3xl font-bold text-slate-900 sm:text-4xl">Preferences</h1>
        <p className="mt-2 text-sm text-slate-600">Control profile details, planning defaults, and notifications.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <section className="glass-panel rounded-2xl p-5 sm:p-6">
          <h2 className="mb-4 inline-flex items-center gap-2 text-lg font-semibold text-slate-900">
            <UserRound className="h-5 w-5 text-emerald-700" /> Profile
          </h2>
          <div className="space-y-3">
            <input className="input-shell" defaultValue={user?.displayName || ''} placeholder="Display name" />
            <input className="input-shell" defaultValue={user?.email || ''} placeholder="Email" />
            <input className="input-shell" placeholder="Home city" />
          </div>
        </section>

        <section className="glass-panel rounded-2xl p-5 sm:p-6">
          <h2 className="mb-4 inline-flex items-center gap-2 text-lg font-semibold text-slate-900">
            <Bell className="h-5 w-5 text-amber-600" /> Notifications
          </h2>
          <div className="space-y-3 text-sm text-slate-700">
            <label className="flex items-center justify-between rounded-xl bg-white p-3">
              Trip reminders
              <input type="checkbox" defaultChecked />
            </label>
            <label className="flex items-center justify-between rounded-xl bg-white p-3">
              Budget alerts
              <input type="checkbox" defaultChecked />
            </label>
            <label className="flex items-center justify-between rounded-xl bg-white p-3">
              Weekly inspiration
              <input type="checkbox" />
            </label>
          </div>
        </section>

        <section className="glass-panel rounded-2xl p-5 sm:p-6">
          <h2 className="mb-4 inline-flex items-center gap-2 text-lg font-semibold text-slate-900">
            <Globe className="h-5 w-5 text-cyan-700" /> Planning defaults
          </h2>
          <div className="space-y-3">
            <input className="input-shell" placeholder="Preferred currency" />
            <input className="input-shell" placeholder="Typical trip length (days)" />
            <input className="input-shell" placeholder="Activity pace" />
          </div>
        </section>

        <section className="glass-panel rounded-2xl p-5 sm:p-6">
          <h2 className="mb-4 inline-flex items-center gap-2 text-lg font-semibold text-slate-900">
            <ShieldCheck className="h-5 w-5 text-emerald-700" /> Security
          </h2>
          <p className="text-sm text-slate-600">
            Authentication is secured with Google sign-in. Token refresh and session expiration are handled automatically.
          </p>
          <button className="btn-soft mt-4">Review signed-in devices</button>
        </div>
      </div>
    </div>
  )
}
