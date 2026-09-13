import { ref, watchEffect } from 'vue'

const STORAGE_KEY = 'color-theme'

function getInitialValue(): boolean {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored === 'dark') return true
  if (stored === 'light') return false
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

const isDark = ref(getInitialValue())

watchEffect(() => {
  document.documentElement.classList.toggle('dark', isDark.value)
  localStorage.setItem(STORAGE_KEY, isDark.value ? 'dark' : 'light')
})

function toggleDark() {
  isDark.value = !isDark.value
}

export function useDarkMode() {
  return { isDark, toggleDark }
}
