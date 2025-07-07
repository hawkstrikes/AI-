import { io } from 'socket.io-client'

// 强制使用HTTP协议，避免HTTPS/SSL问题
const SOCKET_URL = window.location.origin

export default function useSocket() {
  return io(SOCKET_URL, {
    transports: ['websocket', 'polling'],  // 支持websocket和polling
    withCredentials: true,
    autoConnect: true,
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionAttempts: 5,
    timeout: 20000
  });
}
