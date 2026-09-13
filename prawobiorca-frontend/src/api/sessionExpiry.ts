let handler: (() => void) | null = null

/**
 * Rejestruje reakcję na trwałą utratę sesji (nieudane odświeżenie tokenów).
 * Wołane z main.ts, żeby warstwa API nie zależała od store'a ani routera.
 */
export function setSessionExpiredHandler(fn: (() => void) | null): void {
  handler = fn
}

export function notifySessionExpired(): void {
  handler?.()
}
