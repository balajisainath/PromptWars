import api from './api'

export const DEV_TOKEN = 'dev-demo-token'

export const DEV_USER = {
  uid: 'demo-user-001',
  email: 'demo@travelai.dev',
  displayName: 'Demo Traveler',
  photoURL: null,
}

export function isDevMode(): boolean {
  // Dev mode when Firebase is not configured
  const apiKey = process.env.NEXT_PUBLIC_FIREBASE_API_KEY
  return !apiKey || apiKey.startsWith('your_')
}

export async function devLogin(): Promise<void> {
  // Call /auth/verify with the dev token to create the user in the DB
  try {
    await api.post(
      '/api/v1/auth/verify',
      { token: DEV_TOKEN },
      { headers: { Authorization: `Bearer ${DEV_TOKEN}` } }
    )
  } catch {
    // User may already exist — that's fine
  }
}
