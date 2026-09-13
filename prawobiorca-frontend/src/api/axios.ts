import axios, { type InternalAxiosRequestConfig } from 'axios'

import { notifySessionExpired } from '@/api/sessionExpiry'

export const prawobiorcaClient = axios.create({
  baseURL: import.meta.env.VITE_PRAWOBIORCA_API_URL || '/api',
})
prawobiorcaClient.defaults.withCredentials = true

type RetriableConfig = InternalAxiosRequestConfig & { _retried?: boolean }

/**
 * Ścieżki, dla których 401 nie oznacza wygasłego access tokena:
 * `/auth/me` to sonda stanu sesji (401 = niezalogowany), a pozostałe same obsługują tokeny.
 */
const NOT_REFRESHABLE_PATHS = ['/auth/login', '/auth/refresh', '/auth/logout', '/auth/me']

function isRefreshable(url: string | undefined): boolean {
  if (!url) return false
  const path = url.split('?')[0] ?? url
  return !NOT_REFRESHABLE_PATHS.some((excluded) => path.endsWith(excluded))
}

let refreshPromise: Promise<void> | null = null

/**
 * Odświeża tokeny na podstawie ciasteczka refresh. Równoległe wywołania współdzielą
 * jedno żądanie, więc kilka jednoczesnych 401 nie wywoła kilku odświeżeń.
 */
function refreshTokens(): Promise<void> {
  refreshPromise ??= prawobiorcaClient
    .post('/auth/refresh')
    .then(() => undefined)
    .finally(() => {
      refreshPromise = null
    })
  return refreshPromise
}

prawobiorcaClient.interceptors.response.use(
  (response) => response,
  async (error: unknown) => {
    if (!axios.isAxiosError(error) || error.response?.status !== 401) {
      return Promise.reject(error)
    }

    const config = error.config as RetriableConfig | undefined
    if (!config || config._retried || !isRefreshable(config.url)) {
      return Promise.reject(error)
    }

    config._retried = true

    try {
      await refreshTokens()
    } catch {
      notifySessionExpired()
      return Promise.reject(error)
    }

    return prawobiorcaClient(config)
  },
)
