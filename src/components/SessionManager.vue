<template>
  <div class="session-manager">
    <div class="session-header">
      <h3>Sessions</h3>
      <button @click="createNewSession" class="new-session-btn">
        New Session
      </button>
    </div>
    
    <div class="session-list">
      <div 
        v-for="session in sessions" 
        :key="session.id"
        :class="['session-item', { active: activeSessionId === session.id }]"
        @click="selectSession(session.id)"
      >
        <div class="session-info">
          <div class="session-name">{{ session.name || `Session ${session.id.slice(0, 8)}` }}</div>
          <div class="session-meta">
            {{ formatDate(session.created_at) }}
          </div>
        </div>
        <button 
          @click.stop="deleteSession(session.id)"
          class="delete-btn"
        >
          ×
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useChatStore } from '../stores/chat'

const chatStore = useChatStore()
const sessions = ref([])
const activeSessionId = ref(null)

const emit = defineEmits(['session-selected'])

onMounted(() => {
  loadSessions()
})

async function loadSessions() {
  try {
    const response = await fetch(`${window.location.origin}/api/sessions`)
    if (response.ok) {
      sessions.value = await response.json()
    }
  } catch (error) {
    console.error('Failed to load sessions:', error)
  }
}

async function createNewSession() {
  try {
    const sessionId = generateSessionId()
    const response = await fetch(`${window.location.origin}/api/sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        session_id: sessionId,
        user_id: chatStore.currentUser?.id || 'user1'
      })
    })
    
    if (response.ok) {
      const newSession = await response.json()
      sessions.value.push(newSession)
      selectSession(sessionId)
    }
  } catch (error) {
    console.error('Failed to create session:', error)
  }
}

function selectSession(sessionId) {
  activeSessionId.value = sessionId
  emit('session-selected', sessionId)
  chatStore.setActiveSession(sessionId)
}

async function deleteSession(sessionId) {
  try {
    const response = await fetch(`${window.location.origin}/api/sessions/${sessionId}`, {
      method: 'DELETE'
    })
    
    if (response.ok) {
      sessions.value = sessions.value.filter(s => s.id !== sessionId)
      if (activeSessionId.value === sessionId) {
        activeSessionId.value = null
        emit('session-selected', null)
      }
    }
  } catch (error) {
    console.error('Failed to delete session:', error)
  }
}

function generateSessionId() {
  return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
}

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString()
}
</script>

<style scoped>
.session-manager {
  width: 250px;
  background: #f8f9fa;
  border-right: 1px solid #dee2e6;
  display: flex;
  flex-direction: column;
}

.session-header {
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-header h3 {
  margin: 0;
  font-size: 1.1rem;
}

.new-session-btn {
  padding: 0.25rem 0.5rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}

.session-list {
  flex: 1;
  overflow-y: auto;
}

.session-item {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e9ecef;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-item:hover {
  background: #e9ecef;
}

.session-item.active {
  background: #007bff;
  color: white;
}

.session-info {
  flex: 1;
}

.session-name {
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.session-meta {
  font-size: 0.75rem;
  opacity: 0.7;
}

.delete-btn {
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.session-item.active .delete-btn {
  color: white;
}
</style> 