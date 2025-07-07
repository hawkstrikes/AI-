<template>
  <div class="session-view">
    <div class="session-header">
      <h2>{{ sessionName }}</h2>
      <button @click="leaveSession" class="leave-button">
        <i class="fas fa-sign-out-alt"></i> Leave Session
      </button>
    </div>
    
    <div class="session-container">
      <UserList :users="activeUsers" />
      <ChatWindow 
        :messages="messages"
        :current-user="currentUser"
        @send-message="sendMessage"
        @send-audio="sendAudio"
      />
      <Settings
        :ai-service="currentAIService"
        :personality="currentPersonality"
        :voice-profile="currentVoiceProfile"
        @update-settings="updateSettings"
      />
    </div>
  </div>
<AudioRecorder @audio-ready="handleAudioReady" />
</template>
 
<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useChatStore } from '../stores/chat'
import UserList from '../components/UserList.vue' 
import ChatWindow from '../components/ChatWindow.vue' 
import Settings from '../components/Settings.vue' 
import AudioRecorder from '../components/AudioRecorder.vue'
 
const route = useRoute()
const router = useRouter()
const chatStore = useChatStore()
const sessionId = ref(route.params.id) 
const sessionName = ref('Session ' + sessionId.value.slice(0, 5))
const activeUsers = ref([])
const messages = ref([])
 
const currentAIService = ref('step_star')
const currentPersonality = ref({
  traits: ['friendly', 'helpful'],
  temperature: 0.7,
  max_tokens: 1024 
})
const currentVoiceProfile = ref({
  id: 'en-US-Wavenet-D',
  settings: {
    pitch: 0,
    speaking_rate: 1.0
  }
})
 
const currentUser = computed(() => chatStore.currentUser) 
 
onMounted(() => {
  // Load chat history
  chatStore.loadHistory(sessionId.value)
  
  // Setup socket connection
  const socket = window.socket
  if (socket) {
    socket.connect()
    
    // Join session 
    socket.emit('join_session', { 
      session_id: sessionId.value, 
      user_id: currentUser.value.id  
    })
    
    // Setup event listeners 
    socket.on('user_joined', handleUserJoined)
    socket.on('user_left', handleUserLeft)
    socket.on('new_message', handleNewMessage)
  }
})
 
onUnmounted(() => {
  // Leave session 
  const socket = window.socket
  if (socket) {
    socket.emit('leave_session', { 
      session_id: sessionId.value, 
      user_id: currentUser.value.id  
    })
    
    // Disconnect socket 
    socket.disconnect() 
  }
})
 
function handleUserJoined(user) {
  if (!activeUsers.value.some(u  => u.id  === user.user_id))  {
    activeUsers.value.push({ 
      id: user.user_id, 
      name: 'User' + user.user_id.slice(-4) 
    })
  }
}
 
function handleUserLeft(user) {
  activeUsers.value  = activeUsers.value.filter(u  => u.id  !== user.user_id) 
}
 
function handleNewMessage(message) {
  messages.value.push({ 
    sender: message.sender, 
    message: message.message, 
    is_audio: message.is_audio, 
    timestamp: new Date().toISOString()
  })
}
 
function sendMessage(text) {
  const socket = window.socket
  if (socket) {
    socket.emit('send_message', {
      session_id: sessionId.value, 
      user_id: currentUser.value.id, 
      message: text,
      is_audio: false,
      want_audio: false
    })
  }
}
 
function sendAudio(audioData) {
  const socket = window.socket
  if (socket) {
    socket.emit('send_message', {
      session_id: sessionId.value, 
      user_id: currentUser.value.id, 
      message: audioData,
      is_audio: true,
      want_audio: false
    })
  }
}
 
function updateSettings(settings) {
  currentAIService.value = settings.aiService || currentAIService.value 
  currentPersonality.value = settings.personality || currentPersonality.value 
  currentVoiceProfile.value = settings.voiceProfile || currentVoiceProfile.value 
  
  // Update chat store settings
  chatStore.updateSettings({
    service: currentAIService.value,
    personality: currentPersonality.value,
    voice_profile: currentVoiceProfile.value
  })
  
  // Notify server about settings change
  const socket = window.socket
  if (socket) {
    socket.emit('update_settings', {
      session_id: sessionId.value, 
      settings: {
        ai_service: currentAIService.value, 
        personality: currentPersonality.value, 
        voice_profile: currentVoiceProfile.value 
      }
    })
  }
}
 
function leaveSession() {
  router.push({  name: 'home' })
}
</script>
 
<style scoped>
.session-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}
 
.session-header {
  padding: 1rem;
  background: #2c3e50;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
 
.session-header h2 {
  margin: 0;
}
 
.leave-button {
  background: #dc3545;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
 
.session-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}
</style>