<template>
  <div id="app" class="app-container">
    <!-- 顶部导航栏 -->
    <header class="app-header">
      <div class="header-content">
        <div class="logo-section">
          <h1 class="app-title">🤖 AI智能聊天</h1>
          <div class="connection-status">
            <span class="status-dot" :class="{ 'connected': isConnected }"></span>
            <span class="status-text">{{ isConnected ? '已连接' : '连接中...' }}</span>
          </div>
        </div>
        <div class="header-actions">
          <button @click="showSettings = !showSettings" class="settings-btn">
            ⚙️ 设置
          </button>
          <button @click="showUserProfile = !showUserProfile" class="profile-btn">
            👤 个人资料
          </button>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="main-content">
      <div class="content-wrapper">
        <!-- 侧边栏 - 桌面端显示 -->
        <aside class="sidebar" :class="{ 'sidebar-open': showSidebar }">
          <div class="sidebar-header">
            <h3>💬 聊天会话</h3>
            <button @click="createNewSession" class="new-session-btn">
              ➕ 新建会话
            </button>
          </div>
          <div class="session-list">
            <div 
              v-for="session in sessions" 
              :key="session.id"
              @click="selectSession(session)"
              class="session-item"
              :class="{ 'active': currentSession?.id === session.id }"
            >
              <div class="session-info">
                <span class="session-name">{{ session.name || '新会话' }}</span>
                <span class="session-time">{{ formatTime(session.lastMessageTime) }}</span>
              </div>
              <button @click.stop="deleteSession(session.id)" class="delete-session-btn">
                🗑️
              </button>
            </div>
          </div>
        </aside>

        <!-- 聊天主区域 -->
        <section class="chat-section">
          <!-- 聊天头部 -->
          <div class="chat-header">
            <div class="chat-header-left">
              <button @click="toggleSidebar" class="menu-toggle-btn">
                ☰
              </button>
              <h2 class="chat-title">
                {{ currentSession?.name || '新会话' }}
              </h2>
            </div>
            <div class="chat-header-right">
              <div class="ai-status">
                <span class="ai-status-text">AI状态: {{ aiStatus }}</span>
              </div>
            </div>
          </div>

          <!-- 聊天消息区域 -->
          <div class="chat-messages" ref="messagesContainer">
            <div 
              v-for="message in currentMessages" 
              :key="message.id"
              class="message"
              :class="message.type"
            >
              <div class="message-content">
                <div class="message-header">
                  <span class="message-sender">
                    {{ message.type === 'user' ? '👤 您' : '🤖 AI助手' }}
                  </span>
                  <span class="message-time">{{ formatTime(message.timestamp) }}</span>
                </div>
                <div class="message-text" v-html="formatMessage(message.content)"></div>
                <div v-if="message.aiModels" class="ai-models-info">
                  <span class="models-label">使用的AI模型:</span>
                  <span v-for="model in message.aiModels" :key="model" class="model-tag">
                    {{ getModelName(model) }}
                  </span>
                </div>
              </div>
            </div>
            
            <!-- 加载指示器 -->
            <div v-if="isLoading" class="loading-indicator">
              <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span class="loading-text">AI正在思考中...</span>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="chat-input-section">
            <div class="input-wrapper">
              <textarea
                v-model="newMessage"
                @keydown.enter.prevent="sendMessage"
                @keydown.ctrl.enter="sendMessage"
                placeholder="输入您的消息... (Enter发送, Ctrl+Enter换行)"
                class="message-input"
                :disabled="isLoading"
                ref="messageInput"
              ></textarea>
              <div class="input-actions">
                <button 
                  @click="toggleAudioRecording" 
                  class="audio-btn"
                  :class="{ 'recording': isRecording }"
                  :disabled="isLoading"
                >
                  {{ isRecording ? '⏹️ 停止录音' : '🎤 语音输入' }}
                </button>
                <button 
                  @click="sendMessage" 
                  class="send-btn"
                  :disabled="!newMessage.trim() || isLoading"
                >
                  📤 发送
                </button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>

    <!-- 设置面板 -->
    <div v-if="showSettings" class="modal-overlay" @click="showSettings = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>⚙️ 系统设置</h3>
          <button @click="showSettings = false" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <Settings />
        </div>
      </div>
    </div>

    <!-- 用户资料面板 -->
    <div v-if="showUserProfile" class="modal-overlay" @click="showUserProfile = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>👤 个人资料</h3>
          <button @click="showUserProfile = false" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <UserProfile />
        </div>
      </div>
    </div>

    <!-- 移动端侧边栏遮罩 -->
    <div v-if="showSidebar" class="sidebar-overlay" @click="showSidebar = false"></div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useSocket } from '../components/useSocket.js'
import Settings from '../components/Settings.vue'
import UserProfile from '../components/UserProfile.vue'

export default {
  name: 'AppView',
  components: {
    Settings,
    UserProfile
  },
  setup() {
    // 响应式数据
    const isConnected = ref(false)
    const isLoading = ref(false)
    const isRecording = ref(false)
    const showSettings = ref(false)
    const showUserProfile = ref(false)
    const showSidebar = ref(false)
    const newMessage = ref('')
    const messagesContainer = ref(null)
    const messageInput = ref(null)
    
    const currentSession = ref(null)
    const sessions = ref([])
    const messages = reactive({})
    const aiStatus = ref('就绪')
    
    // Socket连接
    const { socket, connect, disconnect } = useSocket()
    
    // 计算属性
    const currentMessages = computed(() => {
      if (!currentSession.value) return []
      return messages[currentSession.value.id] || []
    })
    
    // 方法
    const connectToServer = async () => {
      try {
        await connect()
        isConnected.value = true
        aiStatus.value = '已连接'
      } catch (error) {
        aiStatus.value = '连接失败'
      }
    }
    
    const disconnectFromServer = () => {
      disconnect()
      isConnected.value = false
      aiStatus.value = '已断开'
    }
    
    const createNewSession = () => {
      const sessionId = `session_${Date.now()}`
      const newSession = {
        id: sessionId,
        name: `新会话 ${sessions.value.length + 1}`,
        lastMessageTime: new Date(),
        messages: []
      }
      
      sessions.value.unshift(newSession)
      selectSession(newSession)
      showSidebar.value = false
    }
    
    const selectSession = (session) => {
      currentSession.value = session
      if (!messages[session.id]) {
        messages[session.id] = []
      }
      showSidebar.value = false
    }
    
    const deleteSession = (sessionId) => {
      const index = sessions.value.findIndex(s => s.id === sessionId)
      if (index > -1) {
        sessions.value.splice(index, 1)
        delete messages[sessionId]
        
        if (currentSession.value?.id === sessionId) {
          currentSession.value = sessions.value[0] || null
        }
      }
    }
    
    const sendMessage = async () => {
      if (!newMessage.value.trim() || isLoading.value) return
      
      const message = {
        id: `msg_${Date.now()}`,
        content: newMessage.value,
        type: 'user',
        timestamp: new Date()
      }
      
      // 添加到当前会话
      if (currentSession.value) {
        if (!messages[currentSession.value.id]) {
          messages[currentSession.value.id] = []
        }
        messages[currentSession.value.id].push(message)
        
        // 更新会话时间
        currentSession.value.lastMessageTime = new Date()
      }
      
      const messageText = newMessage.value
      newMessage.value = ''
      isLoading.value = true
      aiStatus.value = '思考中...'
      
      try {
        // 发送消息到服务器
        if (socket.value && isConnected.value) {
          socket.value.emit('send_message', {
            message: messageText,
            session_id: currentSession.value?.id,
            ai_model: 'unified'
          })
        } else {
          // 模拟AI回复
          await simulateAIResponse(messageText)
        }
      } catch (error) {
        addErrorMessage('发送消息失败，请重试')
      } finally {
        isLoading.value = false
        aiStatus.value = '就绪'
      }
      
      // 滚动到底部
      await nextTick()
      scrollToBottom()
    }
    
    const simulateAIResponse = async (userMessage) => {
      // 模拟AI回复延迟
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000))
      
      const aiResponse = {
        id: `ai_${Date.now()}`,
        content: generateSimulatedResponse(userMessage),
        type: 'ai',
        timestamp: new Date(),
        aiModels: ['unified']
      }
      
      if (currentSession.value && messages[currentSession.value.id]) {
        messages[currentSession.value.id].push(aiResponse)
      }
    }
    
    const generateSimulatedResponse = (userMessage) => {
      const responses = [
        `我理解您的问题：${userMessage}。让我为您详细解答...`,
        `这是一个很有趣的问题！关于${userMessage}，我想说...`,
        `谢谢您的提问。${userMessage}这个问题可以从多个角度来思考...`,
        `我完全理解您的想法。${userMessage}确实值得深入探讨...`,
        `这让我想到了一个相关的观点：${userMessage}...`
      ]
      return responses[Math.floor(Math.random() * responses.length)]
    }
    
    const addErrorMessage = (errorText) => {
      const errorMessage = {
        id: `error_${Date.now()}`,
        content: errorText,
        type: 'error',
        timestamp: new Date()
      }
      
      if (currentSession.value && messages[currentSession.value.id]) {
        messages[currentSession.value.id].push(errorMessage)
      }
    }
    
    const toggleAudioRecording = () => {
      isRecording.value = !isRecording.value
      // TODO: 实现语音录制功能
    }
    
    const toggleSidebar = () => {
      showSidebar.value = !showSidebar.value
    }
    
    const scrollToBottom = () => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    }
    
    const formatTime = (timestamp) => {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      const now = new Date()
      const diff = now - date
      
      if (diff < 60000) return '刚刚'
      if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
      if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
      
      return date.toLocaleDateString('zh-CN')
    }
    
    const formatMessage = (content) => {
      // 简单的消息格式化
      return content.replace(/\n/g, '<br>')
    }
    
    const getModelName = (modelKey) => {
      const modelNames = {
        'deepseek': 'DeepSeek',
        'minichat': 'MiniChat',
        'step_star': 'Step Star',
        'unified': '统一AI'
      }
      return modelNames[modelKey] || modelKey
    }
    
    // 生命周期
    onMounted(async () => {
      await connectToServer()
      
      // 创建默认会话
      if (sessions.value.length === 0) {
        createNewSession()
      }
      
      // 监听socket事件
      if (socket.value) {
        socket.value.on('ai_response', (data) => {
          const aiResponse = {
            id: `ai_${Date.now()}`,
            content: data.response,
            type: 'ai',
            timestamp: new Date(),
            aiModels: data.ai_models_used || ['unified']
          }
          
          if (currentSession.value && messages[currentSession.value.id]) {
            messages[currentSession.value.id].push(aiResponse)
            scrollToBottom()
          }
        })
        
        socket.value.on('connect_error', (error) => {
          isConnected.value = false
          aiStatus.value = '连接错误'
        })
      }
    })
    
    onUnmounted(() => {
      disconnectFromServer()
    })
    
    return {
      // 响应式数据
      isConnected,
      isLoading,
      isRecording,
      showSettings,
      showUserProfile,
      showSidebar,
      newMessage,
      messagesContainer,
      messageInput,
      currentSession,
      sessions,
      currentMessages,
      aiStatus,
      
      // 方法
      createNewSession,
      selectSession,
      deleteSession,
      sendMessage,
      toggleAudioRecording,
      toggleSidebar,
      formatTime,
      formatMessage,
      getModelName
    }
  }
}
</script>

<style scoped>
/* 基础样式 */
* {
  box-sizing: border-box;
}

.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: 'Microsoft YaHei', 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
}

/* 顶部导航栏 */
.app-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0.5rem 1rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.app-title {
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
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

.status-text {
  color: #666;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.settings-btn, .profile-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  background: #667eea;
  color: white;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.3s ease;
}

.settings-btn:hover, .profile-btn:hover {
  background: #5a6fd8;
  transform: translateY(-1px);
}

/* 主要内容区域 */
.main-content {
  flex: 1;
  overflow: hidden;
}

.content-wrapper {
  display: flex;
  height: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

/* 侧边栏 */
.sidebar {
  width: 300px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease;
}

.sidebar-header {
  padding: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.sidebar-header h3 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1.1rem;
}

.new-session-btn {
  width: 100%;
  padding: 0.75rem;
  border: 2px dashed #667eea;
  border-radius: 8px;
  background: transparent;
  color: #667eea;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.3s ease;
}

.new-session-btn:hover {
  background: #667eea;
  color: white;
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
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.5);
}

.session-item:hover {
  background: rgba(102, 126, 234, 0.1);
}

.session-item.active {
  background: #667eea;
  color: white;
}

.session-info {
  flex: 1;
  min-width: 0;
}

.session-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-time {
  font-size: 0.75rem;
  opacity: 0.7;
}

.delete-session-btn {
  padding: 0.25rem;
  border: none;
  background: transparent;
  cursor: pointer;
  opacity: 0.5;
  transition: opacity 0.3s ease;
}

.delete-session-btn:hover {
  opacity: 1;
}

/* 聊天区域 */
.chat-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.95);
}

.chat-header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.menu-toggle-btn {
  display: none;
  padding: 0.5rem;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 1.2rem;
}

.chat-title {
  margin: 0;
  font-size: 1.2rem;
  color: #333;
}

.ai-status {
  font-size: 0.875rem;
  color: #666;
}

/* 消息区域 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background: rgba(248, 250, 252, 0.8);
}

.message {
  margin-bottom: 1rem;
  animation: fadeIn 0.3s ease;
}

.message.user {
  text-align: right;
}

.message.ai {
  text-align: left;
}

.message.error {
  text-align: center;
}

.message-content {
  display: inline-block;
  max-width: 70%;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  position: relative;
}

.message.user .message-content {
  background: #667eea;
  color: white;
  border-bottom-right-radius: 4px;
}

.message.ai .message-content {
  background: white;
  color: #333;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-bottom-left-radius: 4px;
}

.message.error .message-content {
  background: #ff6b6b;
  color: white;
  max-width: 90%;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.75rem;
  opacity: 0.8;
}

.message-text {
  line-height: 1.5;
  word-wrap: break-word;
}

.ai-models-info {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  opacity: 0.7;
}

.models-label {
  margin-right: 0.5rem;
}

.model-tag {
  display: inline-block;
  padding: 0.125rem 0.375rem;
  margin: 0.125rem;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 4px;
  font-size: 0.625rem;
}

/* 加载指示器 */
.loading-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  color: #666;
}

.typing-indicator {
  display: flex;
  gap: 0.25rem;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #667eea;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 输入区域 */
.chat-input-section {
  padding: 1rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.95);
}

.input-wrapper {
  display: flex;
  gap: 0.5rem;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  min-height: 44px;
  max-height: 120px;
  padding: 0.75rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  resize: vertical;
  font-family: inherit;
  font-size: 0.875rem;
  line-height: 1.5;
  background: white;
  transition: border-color 0.3s ease;
}

.message-input:focus {
  outline: none;
  border-color: #667eea;
}

.message-input:disabled {
  background: #f8f9fa;
  cursor: not-allowed;
}

.input-actions {
  display: flex;
  gap: 0.5rem;
}

.audio-btn, .send-btn {
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.audio-btn {
  background: #f8f9fa;
  color: #666;
}

.audio-btn:hover:not(:disabled) {
  background: #e9ecef;
}

.audio-btn.recording {
  background: #ff6b6b;
  color: white;
  animation: pulse 1s infinite;
}

.send-btn {
  background: #667eea;
  color: white;
}

.send-btn:hover:not(:disabled) {
  background: #5a6fd8;
  transform: translateY(-1px);
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  animation: modalSlideIn 0.3s ease;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  padding: 0.5rem;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 1.2rem;
  color: #666;
  transition: color 0.3s ease;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  max-height: calc(90vh - 80px);
}

@keyframes modalSlideIn {
  from { opacity: 0; transform: translateY(-20px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-title {
    font-size: 1.2rem;
  }
  
  .header-actions {
    gap: 0.25rem;
  }
  
  .settings-btn, .profile-btn {
    padding: 0.375rem 0.75rem;
    font-size: 0.75rem;
  }
  
  .content-wrapper {
    position: relative;
  }
  
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    z-index: 100;
    transform: translateX(-100%);
  }
  
  .sidebar.sidebar-open {
    transform: translateX(0);
  }
  
  .sidebar-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 99;
  }
  
  .menu-toggle-btn {
    display: block;
  }
  
  .chat-header {
    padding: 0.75rem;
  }
  
  .chat-title {
    font-size: 1rem;
  }
  
  .chat-messages {
    padding: 0.75rem;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .chat-input-section {
    padding: 0.75rem;
  }
  
  .input-wrapper {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .input-actions {
    justify-content: space-between;
  }
  
  .audio-btn, .send-btn {
    flex: 1;
    padding: 0.875rem;
  }
  
  .modal-content {
    margin: 1rem;
    max-width: calc(100vw - 2rem);
  }
  
  .modal-header {
    padding: 1rem;
  }
  
  .modal-body {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .app-header {
    padding: 0.5rem;
  }
  
  .header-content {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .logo-section {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .connection-status {
    font-size: 0.75rem;
  }
  
  .message-content {
    max-width: 90%;
  }
  
  .input-actions {
    flex-direction: column;
  }
  
  .audio-btn, .send-btn {
    width: 100%;
  }
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar,
.session-list::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track,
.session-list::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb,
.session-list::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.3);
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover,
.session-list::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.5);
}
</style>