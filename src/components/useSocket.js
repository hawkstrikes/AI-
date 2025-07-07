// frontend/src/composables/useSocket.js
import { ref } from 'vue'
import { io } from 'socket.io-client' 
 
export function useSocket() {
  const socket = ref(null)
  const isConnected = ref(false)
  
  const connect = (url, options = {}) => {
    const url = window.location.origin;
    socket.value = io(url, {
      ...options,
      reconnectionAttempts: 3,
      reconnectionDelay: 1000,
      autoConnect: false
    })
 
    socket.value.on('connect', () => {
      isConnected.value = true 
    })
 
    socket.value.on('disconnect', () => {
      isConnected.value = false 
    })
  }
 
  // 添加自动重连逻辑 
  const reconnect = () => {
    if (socket.value && !isConnected.value) {
      socket.value.connect() 
    }
  }
 
  return {
    socket,
    isConnected,
    connect,
    reconnect 
  }
}