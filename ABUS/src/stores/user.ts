import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface UserInfo {
  id: number
  name: string
  username: string
  role: string
  department?: string
  workshop?: string
  supervisor_id?: number
  created_at?: string
}

export const useUserStore = defineStore(
  'user',
  () => {
    const userInfo = ref<UserInfo | null>(null)

    const isLoggedIn = computed(() => userInfo.value !== null)
    const role = computed(() => userInfo.value?.role ?? '')
    const userId = computed(() => userInfo.value?.id ?? 0)

    function setUser(user: UserInfo) {
      userInfo.value = user
    }

    function logout() {
      userInfo.value = null
    }

    return { userInfo, isLoggedIn, role, userId, setUser, logout }
  },
  {
    persist: true
  }
)
