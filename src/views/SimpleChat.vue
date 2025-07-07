<template>
  <div class="ai-chat-app">
    <!-- 登录注册界面 -->
    <div v-if="!isLoggedIn" class="auth-container">
      <div class="auth-background">
        <div class="auth-particles"></div>
        <div class="auth-particles"></div>
        <div class="auth-particles"></div>
      </div>
      
      <div class="auth-card">
        <div class="auth-header">
          <div class="logo">
            <div class="logo-icon">🤖</div>
            <h1>AI智能助手</h1>
            <p>多模型智能对话平台</p>
          </div>
        </div>
        
        <div class="auth-tabs">
          <button 
            @click="authMode = 'login'" 
            :class="{ active: authMode === 'login' }"
            class="tab-btn"
          >
            <span class="tab-icon">🔐</span>
            登录
          </button>
          <button 
            @click="authMode = 'register'" 
            :class="{ active: authMode === 'register' }"
            class="tab-btn"
          >
            <span class="tab-icon">📝</span>
            注册
          </button>
        </div>

        <!-- 登录表单 -->
        <form v-if="authMode === 'login'" @submit.prevent="login" class="auth-form">
          <div class="input-group">
            <div class="input-icon">👤</div>
            <input 
              v-model="loginForm.username" 
              type="text" 
              placeholder="用户名" 
              required
              class="input-field"
            >
          </div>
          <div class="input-group">
            <div class="input-icon">🔒</div>
            <input 
              v-model="loginForm.password" 
              type="password" 
              placeholder="密码" 
              required
              class="input-field"
            >
          </div>
          <button type="submit" class="submit-btn" :disabled="isLoading">
            <span v-if="isLoading" class="loading-spinner"></span>
            {{ isLoading ? '登录中...' : '登录' }}
          </button>
        </form>

        <!-- 注册表单 -->
        <form v-else @submit.prevent="register" class="auth-form">
          <div class="input-group">
            <div class="input-icon">👤</div>
            <input 
              v-model="registerForm.username" 
              type="text" 
              placeholder="用户名" 
              required
              class="input-field"
            >
          </div>
          <div class="input-group">
            <div class="input-icon">📧</div>
            <input 
              v-model="registerForm.email" 
              type="email" 
              placeholder="邮箱" 
              required
              class="input-field"
            >
          </div>
          <div class="input-group">
            <div class="input-icon">🔒</div>
            <input 
              v-model="registerForm.password" 
              type="password" 
              placeholder="密码" 
              required
              class="input-field"
            >
          </div>
          <button type="submit" class="submit-btn" :disabled="isLoading">
            <span v-if="isLoading" class="loading-spinner"></span>
            {{ isLoading ? '注册中...' : '注册' }}
          </button>
        </form>

        <div v-if="authError" class="error-message">
          <span class="error-icon">⚠️</span>
          {{ authError }}
        </div>
      </div>
    </div>

    <!-- 聊天主界面 -->
    <div v-else class="chat-container">
      <!-- 侧边栏 -->
      <div class="sidebar">
        <div class="sidebar-header">
          <div class="user-profile">
            <div class="avatar">{{ currentUser.username.charAt(0).toUpperCase() }}</div>
            <div class="user-info">
              <div class="username">{{ currentUser.username }}</div>
              <div class="status">
                <span class="status-dot" :class="{ connected: isConnected }"></span>
                {{ isConnected ? '在线' : '连接中...' }}
              </div>
            </div>
          </div>
          <button @click="logout" class="logout-btn" title="退出登录">
            <span class="logout-icon">🚪</span>
          </button>
        </div>

        <div class="session-section">
          <div class="section-header">
            <h3>会话列表</h3>
            <button @click="createNewSession" class="new-session-btn" title="新建会话">
              <span class="btn-icon">➕</span>
            </button>
          </div>
          
          <div class="session-list">
            <div 
              v-for="session in sessions" 
              :key="session.id"
              @click="switchSession(session.id)"
              class="session-item"
              :class="{ active: session.id === session_id }"
            >
              <div class="session-content">
                <div class="session-title">{{ session.title || '新会话' }}</div>
                <div class="session-time">{{ formatTime(session.updated_at || session.created_at) }}</div>
              </div>
              <button @click.stop="deleteSession(session.id)" class="delete-btn" title="删除会话">
                <span class="delete-icon">🗑️</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 主聊天区域 -->
      <div class="chat-main">
        <!-- 聊天头部 -->
        <div class="chat-header">
          <div class="chat-title">
            <h2>{{ currentSessionName || '新会话' }}</h2>
            <div class="ai-status">
              <span class="ai-dot"></span>
              AI助手已就绪
            </div>
          </div>
        </div>

        <!-- 消息区域 -->
        <div class="messages-area" ref="messagesContainer">
          <div class="messages-container">
            <div 
              v-for="message in messages" 
              :key="`${message.id}-${message.timestamp}`"
              class="message-wrapper"
              :class="message.type"
            >
              <div class="message">
                <div class="message-avatar">
                  <span v-if="message.type === 'user'" class="user-avatar">
                    {{ currentUser.username.charAt(0).toUpperCase() }}
                  </span>
                  <span v-else class="ai-avatar">🤖</span>
                </div>
                <div class="message-content">
                  <div class="message-header">
                    <span class="message-sender">
                      {{ message.type === 'user' ? currentUser.username : 'AI助手' }}
                    </span>
                    <span class="message-time">{{ formatTime(message.timestamp) }}</span>
                  </div>
                  <div class="message-text">{{ message.content }}</div>
                  <div v-if="message.ai_models_used && message.ai_models_used.length > 0" class="ai-models">
                    <span class="models-label">使用模型:</span>
                    <span v-for="model in message.ai_models_used" :key="model" class="model-tag">
                      {{ model }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 加载指示器 -->
            <div v-if="isLoading" class="loading-message">
              <div class="loading-avatar">
                <span class="ai-avatar">🤖</span>
              </div>
              <div class="loading-content">
                <div class="loading-header">
                  <span class="message-sender">AI助手</span>
                  <span class="message-time">正在思考...</span>
                </div>
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="input-area">
          <div class="input-container">
            <textarea 
              v-model="newMessage" 
              @keydown.enter.prevent="handleEnterKey"
              @input="autoResize"
              placeholder="输入消息，按Enter发送，Shift+Enter换行..."
              class="message-input"
              ref="messageInput"
              :disabled="isLoading"
            ></textarea>
            <div class="input-actions">
              <button 
                @click="sendMessage" 
                :disabled="!newMessage.trim() || isLoading"
                class="send-btn"
                :class="{ disabled: !newMessage.trim() || isLoading }"
              >
                <span v-if="!isLoading" class="send-icon">📤</span>
                <span v-else class="loading-spinner"></span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted, nextTick, watch } from 'vue'

export default {
  name: 'SimpleChat',
  setup() {
    // 认证状态
    const isLoggedIn = ref(false)
    const authMode = ref('login')
    const isLoading = ref(false)
    const authError = ref('')
    const isConnected = ref(false)
    
    // 表单数据
    const loginForm = reactive({
      username: '',
      password: ''
    })
    
    const registerForm = reactive({
      username: '',
      email: '',
      password: ''
    })
    
    // 聊天数据
    const currentUser = ref(null)
    const messages = ref([])
    const newMessage = ref('')
    const messagesContainer = ref(null)
    const messageInput = ref(null)
    const session_id = ref('')
    
    // 会话管理
    const sessions = ref([])
    const currentSessionName = ref('新会话')
    
    // 连接状态
    let socket = null
    
    // 认证方法
    const login = async () => {
      isLoading.value = true
      authError.value = ''
      
      try {
        const response = await fetch(`${window.location.origin}/api/auth/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(loginForm)
        })
        
        const data = await response.json()
        
        if (response.ok) {
          currentUser.value = data.user
          localStorage.setItem('token', data.token)
          isLoggedIn.value = true
          connectToChat()
          
          // 登录成功后立即创建会话和加载会话列表
          try {
            await loadSessions()
            await createSession()
            console.log('登录后会话创建成功，session_id:', session_id.value)
            await loadChatHistory()
          } catch (sessionError) {
            console.error('登录后会话创建失败:', sessionError)
            authError.value = '会话创建失败，请重试'
            return
          }
        } else {
          authError.value = data.message || '登录失败'
        }
      } catch (error) {
        authError.value = error.message || '操作失败，请重试'
        console.error('Login error:', error)
      } finally {
        isLoading.value = false
      }
    }
    
    const register = async () => {
      isLoading.value = true
      authError.value = ''
      
      try {
        const response = await fetch(`${window.location.origin}/api/auth/register`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(registerForm)
        })
        
        const data = await response.json()
        
        if (response.ok) {
          authError.value = '注册成功，请登录'
          authMode.value = 'login'
          loginForm.username = registerForm.username
        } else {
          authError.value = data.message || '注册失败'
        }
      } catch (error) {
        authError.value = error.message || '操作失败，请重试'
        console.error('Register error:', error)
      } finally {
        isLoading.value = false
      }
    }
    
    const logout = () => {
      localStorage.removeItem('token')
      isLoggedIn.value = false
      currentUser.value = null
      messages.value = []
      disconnectFromChat()
    }
    
    // 聊天连接
    const connectToChat = () => {
      try {
        if (window.socket) {
          socket = window.socket
          
          socket.on('connect', () => {
            isConnected.value = true
            console.log('Socket.IO connected')
          })
          
          socket.on('ai_response', (data) => {
            isLoading.value = false
            addMessage('ai', data.response, data.ai_models_used)
            scrollToBottom()
          })
          
          socket.on('disconnect', () => {
            isConnected.value = false
            authError.value = '已断开，正在重连...'
          })
          
          socket.io.on('reconnect_attempt', () => {
            authError.value = '正在尝试重连...'
          })
          
          socket.io.on('reconnect', () => {
            isConnected.value = true
            authError.value = ''
          })
          
          socket.on('connect_error', (error) => {
            isConnected.value = false
            console.error('Socket.IO connection error:', error)
          })
          
          socket.on('error', (error) => {
            console.error('Socket.IO error:', error)
            isLoading.value = false
          })
        }
      } catch (error) {
        console.error('Failed to connect to chat:', error)
      }
    }
    
    const disconnectFromChat = () => {
      if (socket) {
        socket.disconnect()
        socket = null
      }
    }
    
    // 消息处理
    const addMessage = (type, content, aiModels = []) => {
      const message = {
        id: Date.now() + Math.random(),
        type,
        content,
        timestamp: new Date().toISOString(),
        ai_models_used: aiModels
      }
      messages.value.push(message)
    }
    
    const sendMessage = async () => {
      if (!newMessage.value.trim() || isLoading.value) return
      
      const message = newMessage.value.trim()
      newMessage.value = ''
      
      // 重置输入框高度
      if (messageInput.value) {
        messageInput.value.style.height = 'auto'
      }
      
      // 添加用户消息
      addMessage('user', message)
      scrollToBottom()
      
      // 设置加载状态
      isLoading.value = true
      
      try {
        // 在所有依赖session_id的操作前加：
        if (!session_id.value) {
          await createSession();
        }
        if (!session_id.value) {
          authError.value = '会话创建失败，请重试';
          return;
        }
        
        // 使用HTTP API发送消息
        const response = await fetch(`${window.location.origin}/api/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            message,
            session_id: session_id.value
          })
        })
        
        const data = await response.json()
        
        if (response.ok) {
          // 添加AI回复
          addMessage('ai', data.response, data.ai_models_used)
          scrollToBottom()
        } else {
          throw new Error(data.error || '发送失败')
        }
      } catch (error) {
        if (error.response) {
          error.response.text().then(text => {
            console.error('sendMessage status:', error.response.status);
            console.error('sendMessage response:', text);
          });
        }
        console.error('Send message error:', error)
        addMessage('ai', '抱歉，发送消息失败，请重试。')
        scrollToBottom()
      } finally {
        isLoading.value = false
      }
    }
    
    // 处理回车键
    const handleEnterKey = (event) => {
      if (event.shiftKey) {
        // Shift+Enter 换行
        return
      }
      sendMessage()
    }
    
    // 自动调整输入框高度
    const autoResize = () => {
      if (!messageInput.value) return
      
      messageInput.value.style.height = 'auto'
      messageInput.value.style.height = Math.min(messageInput.value.scrollHeight, 120) + 'px'
    }
    
    // 滚动到底部
    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
      })
    }
    
    // 会话管理
    const createSession = async () => {
      try {
        const response = await fetch(`${window.location.origin}/api/session/create`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            title: '新会话',
            ai_settings: {}
          })
        })
        
        if (!response.ok) throw new Error('会话创建失败')
        const text = await response.text()
        if (!text) throw new Error('会话创建失败')
        let data
        try {
          data = JSON.parse(text)
        } catch {
          throw new Error('会话数据格式错误')
        }
        if (!data.session_id) throw new Error('会话创建失败')
        session_id.value = data.session_id
        await loadSessions()
        return data.session_id
      } catch (error) {
        if (error.response) {
          error.response.text().then(text => {
            console.error('createSession status:', error.response.status);
            console.error('createSession response:', text);
          });
        }
        console.error('Create session error:', error)
        throw error
      }
    }
    
    const loadSessions = async () => {
      try {
        const response = await fetch(`${window.location.origin}/api/sessions`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        })
        
        const data = await response.json()
        
        if (response.ok) {
          sessions.value = data.sessions
        } else {
          throw new Error(data.error || '加载会话列表失败')
        }
      } catch (error) {
        console.error('Load sessions error:', error)
      }
    }
    
    const switchSession = async (sessionId) => {
      session_id.value = sessionId
      messages.value = []
      await loadChatHistory()
      scrollToBottom()
    }
    
    const deleteSession = async (sessionId) => {
      if (!confirm('确定要删除这个会话吗？')) return
      
      try {
        const response = await fetch(`${window.location.origin}/api/session/${sessionId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        })
        
        if (response.ok) {
          await loadSessions()
          if (session_id.value === sessionId) {
            await createSession()
          }
        } else {
          const data = await response.json()
          throw new Error(data.error || '删除会话失败')
        }
      } catch (error) {
        console.error('Delete session error:', error)
        alert('删除会话失败')
      }
    }
    
    const createNewSession = async () => {
      try {
        await createSession()
        messages.value = []
        scrollToBottom()
      } catch (error) {
        console.error('Create new session error:', error)
        alert('创建新会话失败')
      }
    }
    
    const loadChatHistory = async () => {
      if (!session_id.value) return
      
      try {
        const response = await fetch(`${window.location.origin}/api/session/${session_id.value}/history`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        })
        
        if (!response.ok) throw new Error('会话不存在')
        const text = await response.text()
        if (!text) throw new Error('无历史记录')
        let data
        try {
          data = JSON.parse(text)
        } catch {
          throw new Error('历史数据格式错误')
        }
        
        if (response.ok) {
          messages.value = data.messages.map(msg => ({
            ...msg,
            type: msg.message_type,
            content: msg.content,
            ai_models_used: msg.ai_models_used ? JSON.parse(msg.ai_models_used) : []
          }))
          scrollToBottom()
        } else {
          throw new Error(data.error || '加载聊天记录失败')
        }
      } catch (error) {
        console.error('Load chat history error:', error)
      }
    }
    
    // 工具函数
    const formatTime = (timestamp) => {
      if (!timestamp) return ''
      
      const date = new Date(timestamp)
      const now = new Date()
      const diff = now - date
      
      if (diff < 60000) { // 1分钟内
        return '刚刚'
      } else if (diff < 3600000) { // 1小时内
        return `${Math.floor(diff / 60000)}分钟前`
      } else if (diff < 86400000) { // 24小时内
        return `${Math.floor(diff / 3600000)}小时前`
      } else {
        return date.toLocaleDateString()
      }
    }
    
    // 生命周期
    onMounted(() => {
      // 检查是否已登录
      const token = localStorage.getItem('token')
      if (token) {
        // 验证token有效性
        fetch(`${window.location.origin}/api/auth/verify`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        .then(response => response.json())
        .then(data => {
          if (data.user) {
            currentUser.value = data.user
            isLoggedIn.value = true
            connectToChat()
            loadSessions()
            createSession()
          } else {
            localStorage.removeItem('token')
          }
        })
        .catch(() => {
          localStorage.removeItem('token')
        })
      }
    })
    
    onUnmounted(() => {
      disconnectFromChat()
    })
    
    // 监听消息变化，自动滚动
    watch(messages, () => {
      nextTick(() => {
        scrollToBottom()
      })
    }, { deep: true })
    
    return {
      // 状态
      isLoggedIn,
      authMode,
      isLoading,
      authError,
      isConnected,
      currentUser,
      messages,
      newMessage,
      sessions,
      session_id,
      currentSessionName,
      
      // 表单
      loginForm,
      registerForm,
      
      // 引用
      messagesContainer,
      messageInput,
      
      // 方法
      login,
      register,
      logout,
      sendMessage,
      handleEnterKey,
      autoResize,
      createSession,
      loadSessions,
      switchSession,
      deleteSession,
      createNewSession,
      loadChatHistory,
      formatTime
    }
  }
}
</script>

<style scoped>
/* 全局样式 */
.ai-chat-app {
  height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #0f0f23;
  color: #ffffff;
  overflow: hidden;
}

/* 认证界面 */
.auth-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
}

.auth-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.auth-particles {
  position: absolute;
  width: 4px;
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

.auth-particles:nth-child(1) {
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.auth-particles:nth-child(2) {
  top: 60%;
  right: 20%;
  animation-delay: 2s;
}

.auth-particles:nth-child(3) {
  bottom: 30%;
  left: 50%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); opacity: 1; }
  50% { transform: translateY(-20px) rotate(180deg); opacity: 0.5; }
}

.auth-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 3rem;
  width: 100%;
  max-width: 450px;
  margin: 1rem;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
}

.auth-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.logo-icon {
  font-size: 3rem;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.logo h1 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(45deg, #fff, #e0e0e0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo p {
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  font-size: 1rem;
}

.auth-tabs {
  display: flex;
  margin-bottom: 2rem;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.tab-btn {
  flex: 1;
  padding: 1rem;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 500;
}

.tab-btn.active {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.tab-icon {
  font-size: 1.2rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.input-group {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.7);
  z-index: 1;
}

.input-field {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.input-field::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.input-field:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
}

.submit-btn {
  padding: 1rem;
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  background: rgba(255, 255, 255, 0.2);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #ff6b6b;
  text-align: center;
  font-size: 0.9rem;
  padding: 1rem;
  background: rgba(255, 107, 107, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(255, 107, 107, 0.3);
}

.error-icon {
  font-size: 1.2rem;
}

/* 聊天界面 */
.chat-container {
  display: flex;
  height: 100vh;
  background: #0f0f23;
}

/* 侧边栏 */
.sidebar {
  width: 320px;
  background: #1a1a2e;
  border-right: 1px solid #2d2d44;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 1.5rem;
  border-bottom: 1px solid #2d2d44;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(45deg, #667eea, #764ba2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: white;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.username {
  font-weight: 600;
  color: white;
}

.status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ff6b6b;
  transition: background 0.3s ease;
}

.status-dot.connected {
  background: #51cf66;
}

.logout-btn {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logout-btn:hover {
  background: rgba(255, 107, 107, 0.2);
  color: #ff6b6b;
}

.logout-icon {
  font-size: 1.2rem;
}

.session-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.section-header {
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #2d2d44;
}

.section-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
}

.new-session-btn {
  width: 32px;
  height: 32px;
  background: linear-gradient(45deg, #667eea, #764ba2);
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.new-session-btn:hover {
  transform: scale(1.1);
}

.btn-icon {
  font-size: 1rem;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.session-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  margin-bottom: 0.5rem;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid transparent;
}

.session-item:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.session-item.active {
  background: linear-gradient(45deg, #667eea, #764ba2);
  border-color: rgba(255, 255, 255, 0.3);
}

.session-content {
  flex: 1;
  min-width: 0;
}

.session-title {
  font-weight: 600;
  color: white;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-time {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
}

.delete-btn {
  width: 28px;
  height: 28px;
  background: rgba(255, 107, 107, 0.1);
  border: none;
  border-radius: 6px;
  color: #ff6b6b;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
}

.session-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: rgba(255, 107, 107, 0.2);
  transform: scale(1.1);
}

.delete-icon {
  font-size: 0.9rem;
}

/* 主聊天区域 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #0f0f23;
}

.chat-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #2d2d44;
  background: #1a1a2e;
}

.chat-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chat-title h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
}

.ai-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
}

.ai-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #51cf66;
  animation: pulse 2s ease-in-out infinite;
}

/* 消息区域 */
.messages-area {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.messages-container {
  height: 100%;
  overflow-y: auto;
  padding: 2rem;
}

.message-wrapper {
  margin-bottom: 1.5rem;
  animation: fadeInUp 0.3s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message {
  display: flex;
  gap: 1rem;
  max-width: 80%;
}

.message-wrapper.user .message {
  margin-left: auto;
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-avatar {
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, #667eea, #764ba2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: white;
  font-size: 1rem;
}

.ai-avatar {
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, #51cf66, #40c057);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.message-sender {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
}

.message-time {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
}

.message-text {
  background: rgba(255, 255, 255, 0.1);
  padding: 1rem;
  border-radius: 12px;
  line-height: 1.6;
  color: white;
  word-wrap: break-word;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.message-wrapper.user .message-text {
  background: linear-gradient(45deg, #667eea, #764ba2);
  border-color: rgba(255, 255, 255, 0.2);
}

/* 加载消息 */
.loading-message {
  margin-bottom: 1.5rem;
}

.loading-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-content {
  flex: 1;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.loading-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.typing-indicator {
  display: flex;
  gap: 0.25rem;
}

.typing-dots {
  display: flex;
  gap: 0.25rem;
}

.typing-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #667eea;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* 输入区域 */
.input-area {
  padding: 1.5rem 2rem;
  border-top: 1px solid #2d2d44;
  background: #1a1a2e;
}

.input-container {
  max-width: 800px;
  margin: 0 auto;
}

.input-wrapper {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 0.75rem;
  transition: all 0.3s ease;
}

.input-wrapper:focus-within {
  border-color: rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
}

.message-input {
  flex: 1;
  border: none;
  background: transparent;
  color: white;
  font-size: 1rem;
  resize: none;
  outline: none;
  line-height: 1.5;
  max-height: 120px;
  min-height: 24px;
}

.message-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.send-btn {
  width: 44px;
  height: 44px;
  background: linear-gradient(45deg, #667eea, #764ba2);
  border: none;
  border-radius: 12px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.send-btn:disabled {
  background: rgba(255, 255, 255, 0.2);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.send-icon {
  font-size: 1.2rem;
}

/* 滚动条样式 */
.messages-container::-webkit-scrollbar,
.session-list::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track,
.session-list::-webkit-scrollbar-track {
  background: transparent;
}

.messages-container::-webkit-scrollbar-thumb,
.session-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover,
.session-list::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-container {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    height: 200px;
  }
  
  .chat-main {
    flex: 1;
  }
  
  .auth-card {
    margin: 1rem;
    padding: 2rem;
  }
  
  .message {
    max-width: 90%;
  }
  
  .input-area {
    padding: 1rem;
  }
  
  .chat-header {
    padding: 1rem;
  }
  
  .messages-container {
    padding: 1rem;
  }
}
</style>
