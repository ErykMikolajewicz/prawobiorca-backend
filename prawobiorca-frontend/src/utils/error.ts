import axios, { AxiosError } from 'axios'

export function hasMessage(obj: unknown): obj is { message: string } {
  if (typeof obj !== 'object' || obj === null) return false
  const rec = obj as Record<string, unknown>
  return typeof rec.message === 'string'
}

export function getApiErrorMessage(
  error: unknown,
  options?: {
    conflictMessage?: string
    defaultServerMessage?: string
    unauthorizedMessage?: string
  },
): string {
  const defaultServer =
    options?.defaultServerMessage ?? 'Wystąpił błąd po stronie serwera. Spróbuj ponownie później.'
  const conflictMsg = options?.conflictMessage ?? 'Zasób jest już zajęty.'
  const unauthorizedMsg =
    options?.unauthorizedMessage ?? 'Nieprawidłowa nazwa użytkownika lub hasło.'

  if (!axios.isAxiosError(error)) {
    return 'Wystąpił błąd. Spróbuj ponownie.'
  }

  const axiosErr = error as AxiosError

  if (axiosErr.response) {
    const status = axiosErr.response.status
    if (status === 401) return unauthorizedMsg
    if (status === 409) return conflictMsg

    const data = axiosErr.response.data
    if (hasMessage(data)) return data.message

    return defaultServer
  }

  if (axiosErr.request) {
    return 'Nie można połączyć się z serwerem. Sprawdź połączenie sieciowe.'
  }

  return 'Wystąpił błąd. Spróbuj ponownie.'
}
