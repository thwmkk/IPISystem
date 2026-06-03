import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { UserInfo } from '@/types/user'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<UserInfo | null>(loadUser())
  const isAuthenticated = ref(!!localStorage.getItem('access_token'))

  // Getters
  const role = computed(() => user.value?.role || null)
  const fullName = computed(() => user.value?.full_name || 'Пользователь')
  const employeeId = computed(() => user.value?.employee_id || null)

  const isManager = computed(() =>
    role.value === 'руководитель' || role.value === 'администратор'
  )
  const isAdmin = computed(() => role.value === 'администратор')

  // Role labels for UI
  const roleLabel = computed(() => {
    const labels: Record<string, string> = {
      'сотрудник': 'Сотрудник',
      'руководитель': 'Руководитель',
      'администратор': 'Администратор',
    }
    return labels[role.value || ''] || ''
  })

  // Actions
  async function login(email: string, password: string) {
    const { data } = await authApi.login({ email, password })
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    localStorage.setItem('user', JSON.stringify(data.user))
    user.value = data.user
    isAuthenticated.value = true
  }

  async function fetchMe() {
    try {
      const { data } = await authApi.me()
      user.value = data
      localStorage.setItem('user', JSON.stringify(data))
    } catch {
      logout()
    }
  }

  function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    user.value = null
    isAuthenticated.value = false
  }

  function loadUser(): UserInfo | null {
    const raw = localStorage.getItem('user')
    if (!raw) return null
    try { return JSON.parse(raw) } catch { return null }
  }

  return {
    user,
    isAuthenticated,
    role,
    fullName,
    employeeId,
    isManager,
    isAdmin,
    roleLabel,
    login,
    fetchMe,
    logout,
  }
})
