import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const currentUser = ref({
    id: 'user1',
    name: 'User'
  })

  function setUser(user) {
    currentUser.value = user
  }

  function logout() {
    currentUser.value = { id: '', name: '' }
  }

  return {
    currentUser,
    setUser,
    logout
  }
}) 