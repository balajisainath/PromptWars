'use client'
import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/store/authStore'
import { Compass, LayoutDashboard, LogOut, Map, Plus, Settings } from 'lucide-react'

const navItems = [
  { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/trips', icon: Map, label: 'My Trips' },
  { href: '/explore', icon: Compass, label: 'Explore' },
  { href: '/settings', icon: Settings, label: 'Settings' },
]

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, signOut } = useAuthStore()
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    if (!loading && !user) router.push('/login')
  }, [user, loading, router])

  if (loading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-emerald-200 border-t-emerald-700" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-transparent lg:grid lg:grid-cols-[260px_1fr]">
      <aside className="hidden border-r border-emerald-100 bg-white/90 backdrop-blur lg:sticky lg:top-0 lg:flex lg:h-screen lg:flex-col">
        <div className="border-b border-emerald-100 p-6">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-100">
              <Map className="h-5 w-5 text-emerald-700" />
            </div>
            <span className="text-lg font-bold text-slate-900">TravelAI</span>
          </div>
        </div>

        <nav className="flex-1 space-y-1 p-4">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition-colors ${
                pathname === item.href
                  ? 'bg-emerald-100 text-emerald-800'
                  : 'text-slate-600 hover:bg-emerald-50 hover:text-slate-900'
              }`}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="border-t border-emerald-100 p-4">
          <Link
            href="/trips/new"
            className="mb-3 flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-700 px-4 py-3 text-sm font-medium text-white transition-colors hover:bg-emerald-800"
          >
            <Plus className="h-4 w-4" />
            New Trip
          </Link>
          <div className="flex items-center gap-3">
            {user.photoURL && (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={user.photoURL} alt="" className="h-8 w-8 rounded-full" />
            )}
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-slate-800 truncate">{user.displayName}</p>
              <p className="text-xs text-slate-500 truncate">{user.email}</p>
            </div>
            <button onClick={signOut} className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700" aria-label="Sign out">
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </aside>

      <main className="pb-24 lg:pb-10">
        <header className="sticky top-0 z-20 border-b border-emerald-100 bg-white/85 backdrop-blur lg:hidden">
          <div className="app-shell flex items-center justify-between py-3">
            <div className="flex items-center gap-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-100">
                <Map className="h-4 w-4 text-emerald-700" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-900">TravelAI</p>
                <p className="text-xs text-slate-500">Plan smarter</p>
              </div>
            </div>
            <button onClick={signOut} className="rounded-xl border border-slate-200 p-2 text-slate-600">
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </header>

        <div className="app-shell py-5 lg:py-8">{children}</div>
      </main>

      <nav className="fixed inset-x-4 bottom-4 z-30 rounded-2xl border border-emerald-100 bg-white/95 p-1.5 shadow-xl backdrop-blur lg:hidden">
        <div className="grid grid-cols-4 gap-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex min-h-12 flex-col items-center justify-center gap-1 rounded-xl text-[11px] font-semibold transition-colors ${
                  isActive ? 'bg-emerald-100 text-emerald-800' : 'text-slate-500'
                }`}
              >
                <item.icon className="h-4 w-4" />
                {item.label.split(' ')[0]}
              </Link>
            )
          })}
        </div>
      </nav>

      <Link
        href="/trips/new"
        className="fixed bottom-24 right-5 z-20 inline-flex h-12 w-12 items-center justify-center rounded-full bg-emerald-700 text-white shadow-lg lg:hidden"
        aria-label="Create new trip"
      >
        <Plus className="h-5 w-5" />
      </Link>
    </div>
  )
}
