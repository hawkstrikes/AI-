<template>
  <div class="chat-window">
    <div class="messages" ref="messagesContainer" @scroll="handleScroll">
      <div 
        v-for="(message, index) in messages" 
        :key="`${message.id || index}-${message.timestamp}`" 
        :class="['message', message.sender === currentUser.id ? 'sent' : 'received']"
        :ref="el => setMessageRef(el, index)"
      >
        <div class="message-sender">
          {{ message.sender === 'ai' ? 'AI' : message.sender === currentUser.id ? 'You' : message.sender }}
        </div>
        <div class="message-content">
          <audio 
            v-if="message.is_audio"  
            controls 
            :src="'data:audio/mp3;base64,' + message.message" 
          />
          <span v-else>{{ message.message }}</span>
        </div>
        <div class="message-time" v-if="message.timestamp">
          {{ formatTime(message.timestamp) }}
        </div>
      </div>
      
      <!-- 加载指示器 -->
      <div v-if="isLoading" class="loading-indicator">
        <div class="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <span>AI正在思考...</span>
      </div>
    </div>
    
    <div class="message-input">
      <textarea 
        v-model="textMessage" 
        placeholder="Type your message..."
        @keydown.enter.prevent="handleEnterKey"
        @input="autoResize"
        ref="messageInput"
        :disabled="isLoading"
      />
      <div class="input-buttons">
        <button 
          @click="sendTextMessage"
          :disabled="!textMessage.trim() || isLoading"
          class="send-btn"
        >
          <span v-if="!isLoading">发送</span>
          <span v-else>发送中...</span>
        </button>
        <button 
          @click="toggleRecording"
          :class="{ 'recording': isRecording }"
          :disabled="isLoading"
          class="record-btn"
        >
          {{ isRecording ? '停止录音' : '录音' }}
        </button>
      </div>
    </div>
  </div>
</template>
 
<script setup>
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
 
const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  },
  currentUser: {
    type: Object,
    required: true
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})
 
const emit = defineEmits(['send-message', 'send-audio'])
 
const textMessage = ref('')
const isRecording = ref(false)
const mediaRecorder = ref(null)
const audioChunks = ref([])
const messagesContainer = ref(null)
const messageInput = ref(null)
const messageRefs = ref([])
const shouldAutoScroll = ref(true)
const lastScrollTop = ref(0)

// 设置消息引用
function setMessageRef(el, index) {
  if (el) {
    messageRefs.value[index] = el
  }
}

// 处理滚动事件
function handleScroll() {
  if (!messagesContainer.value) return
  
  const { scrollTop, scrollHeight, clientHeight } = messagesContainer.value
  const isAtBottom = scrollHeight - scrollTop - clientHeight < 50
  
  shouldAutoScroll.value = isAtBottom
  lastScrollTop.value = scrollTop
}

// 自动滚动到底部
function scrollToBottom(force = false) {
  if (!messagesContainer.value) return
  
  if (force || shouldAutoScroll.value) {
    nextTick(() => {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    })
  }
}

// 格式化时间
function formatTime(timestamp) {
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

// 处理回车键
function handleEnterKey(event) {
  if (event.shiftKey) {
    // Shift+Enter 换行
    return
  }
  sendTextMessage()
}

// 自动调整文本框高度
function autoResize() {
  if (!messageInput.value) return
  
  messageInput.value.style.height = 'auto'
  messageInput.value.style.height = Math.min(messageInput.value.scrollHeight, 120) + 'px'
}

function sendTextMessage() {
  if (textMessage.value.trim() && !props.isLoading) {
    emit('send-message', textMessage.value.trim()) 
    textMessage.value = ''
    
    // 重置文本框高度
    if (messageInput.value) {
      messageInput.value.style.height = 'auto'
    }
    
    // 强制滚动到底部
    scrollToBottom(true)
  }
}
 
function toggleRecording() {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
  isRecording.value = !isRecording.value  
}
 
async function startRecording() {
  audioChunks.value = []
  
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder.value = new MediaRecorder(stream)
    
    mediaRecorder.value.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.value.push(event.data) 
      }
    }
    
    mediaRecorder.value.onstop = async () => {
      const audioBlob = new Blob(audioChunks.value, { type: 'audio/webm' })
      const reader = new FileReader()
      reader.onload = () => {
        const base64Data = reader.result.split(',')[1] 
        emit('send-audio', base64Data)
      }
      reader.readAsDataURL(audioBlob) 
      
      // Stop all tracks
      stream.getTracks().forEach(track => track.stop()) 
    }
    
    mediaRecorder.value.start() 
  } catch (error) {
    console.error('Error accessing microphone:', error)
    isRecording.value = false 
  }
}
 
function stopRecording() {
  if (mediaRecorder.value) {
    mediaRecorder.value.stop() 
  }
}

// 监听消息变化
watch(() => props.messages, (newMessages, oldMessages) => {
  // 检查是否有新消息
  if (newMessages.length > oldMessages.length) {
    scrollToBottom()
  }
}, { deep: true })

// 监听加载状态
watch(() => props.isLoading, (loading) => {
  if (loading) {
    scrollToBottom(true)
  }
})

onMounted(() => {
  scrollToBottom(true)
})

onUnmounted(() => {
  if (mediaRecorder.value && isRecording.value) {
    stopRecording()
  }
})
</script>
 
<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
 
.messages {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  background: #f8f9fa;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
}

.messages::-webkit-scrollbar {
  width: 6px;
}

.messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
 
.message {
  margin-bottom: 1rem;
  max-width: 70%;
  display: flex;
  flex-direction: column;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
 
.message.sent {
  margin-left: auto;
  text-align: right;
  align-items: flex-end;
}
 
.message.received {
  margin-right: auto;
  align-items: flex-start;
}
 
.message-sender {
  font-weight: 600;
  font-size: 0.75rem;
  color: #666;
  margin-bottom: 0.3rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
 
.message-content {
  padding: 0.8rem 1.2rem;
  border-radius: 1.2rem;
  display: inline-block;
  word-break: break-word;
  max-width: 100%;
  min-width: 60px;
  white-space: pre-wrap;
  line-height: 1.5;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
 
.sent .message-content {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
}
 
.received .message-content {
  background: white;
  color: #333;
  border: 1px solid #e9ecef;
}

.message-time {
  font-size: 0.7rem;
  color: #999;
  margin-top: 0.2rem;
  font-style: italic;
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  color: #666;
  font-style: italic;
}

.typing-indicator {
  display: flex;
  gap: 0.2rem;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #007bff;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}
 
.message-input {
  display: flex;
  flex-direction: column;
  padding: 1rem;
  background: #fff;
  border-top: 1px solid #e9ecef;
  gap: 0.5rem;
}
 
.message-input textarea {
  flex: 1;
  padding: 0.8rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  resize: none;
  min-height: 50px;
  max-height: 120px;
  font-family: inherit;
  font-size: 0.9rem;
  line-height: 1.4;
  transition: border-color 0.3s ease;
}

.message-input textarea:focus {
  outline: none;
  border-color: #007bff;
}

.message-input textarea:disabled {
  background: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
}

.input-buttons {
  display: flex;
  gap: 0.5rem;
}

.message-input button {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.send-btn {
  background: #007bff;
  color: white;
  flex: 1;
}

.send-btn:hover:not(:disabled) {
  background: #0056b3;
  transform: translateY(-1px);
}

.send-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
  transform: none;
}

.record-btn {
  background: #dc3545;
  color: white;
  min-width: 80px;
}

.record-btn:hover:not(:disabled) {
  background: #c82333;
  transform: translateY(-1px);
}

.record-btn.recording {
  background: #28a745;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

.record-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
  transform: none;
  animation: none;
}

/* 移动端优化 */
@media (max-width: 768px) {
  .message {
    max-width: 85%;
  }
  
  .message-input {
    padding: 0.8rem;
  }
  
  .input-buttons {
    flex-direction: column;
  }
  
  .record-btn {
    min-width: auto;
  }
}
</style>