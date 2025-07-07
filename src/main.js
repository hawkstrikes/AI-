import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router.js'

// Socket.io setup
import { io } from 'socket.io-client'

const app = createApp(App)
const pinia = createPinia()

// Initialize socket connection
const socket = io(window.location.origin, {
  autoConnect: true,
  transports: ['websocket', 'polling'],
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionAttempts: 5,
  timeout: 20000,
  forceNew: true
})

// Provide socket to all components
app.provide('socket', socket)

// Make socket globally available
window.socket = socket

// Use plugins
app.use(pinia)
app.use(router)

// Global error handling
app.config.errorHandler = (err, vm, info) => {
  console.error('Global error:', err, info)
}

// Socket connection status monitoring
socket.on('connect', () => {
  console.log('✅ Socket connected')
})

socket.on('disconnect', () => {
  console.log('❌ Socket disconnected')
})

socket.on('connect_error', (error) => {
  console.error('❌ Socket connection error:', error)
})

app.mount('#app')