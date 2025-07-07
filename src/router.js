import { createRouter, createWebHistory } from 'vue-router'
import SimpleChat from './views/SimpleChat.vue'

const routes = [
  {
    path: '/',
    name: 'SimpleChat',
    component: SimpleChat
  },
  {
    path: '/chat',
    name: 'Chat',
    component: SimpleChat
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router