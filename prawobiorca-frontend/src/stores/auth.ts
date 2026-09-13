import { defineStore } from 'pinia'
import { ref } from 'vue'

import * as authApi from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const isUserLogged = ref(false)
  const isAdmin = ref(false)

  async function checkIsLogged(): Promise<void> {
    const currentUser = await authApi.getCurrentUser()
    isUserLogged.value = currentUser !== null
    isAdmin.value = currentUser?.isAdmin ?? false
  }

  async function login(username: string, password: string): Promise<void> {
    await authApi.login(username, password)
    isUserLogged.value = true

    const currentUser = await authApi.getCurrentUser()
    isAdmin.value = currentUser?.isAdmin ?? false
  }

  function resetSession(): void {
    isUserLogged.value = false
    isAdmin.value = false
  }

  async function logout() {
    try {
      await authApi.logout()
    } finally {
      resetSession()
    }
  }

  return { isUserLogged, isAdmin, checkIsLogged, login, logout, resetSession }
})
