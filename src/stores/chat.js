import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useChatStore = defineStore('chat', () => {
  const currentSession = ref(null)
  const messages = ref([])
  const aiSettings = ref({
    service: 'step_star',
    temperature: 0.7,
    max_tokens: 1024
  })
  const currentUser = ref({
    id: 'user1',
    name: 'User'
  })

  function addMessage(msg) {
    messages.value.push(msg)
  }

  function updateSettings(settings) {
    aiSettings.value = { ...aiSettings.value, ...settings }
  }

  function setActiveSession(sessionId) {
    currentSession.value = sessionId
  }

  async function loadHistory(sessionId) {
    try {
      const response = await fetch(`${window.location.origin}/api/messages/${sessionId}`)
      if (response.ok) {
        messages.value = await response.json()
      }
    } catch (error) {
      console.error('Failed to load history:', error)
    }
  }

  return {
    currentSession,
    messages,
    aiSettings,
    currentUser,
    addMessage,
    updateSettings,
    setActiveSession,
    loadHistory
  }
}) 