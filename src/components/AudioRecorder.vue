<template>
  <div class="audio-recorder">
    <button 
      @mousedown="startRecording" 
      @mouseup="stopRecording"
      @touchstart="startRecording"
      @touchend="stopRecording"
      :disabled="isProcessing"
    >
      <i class="fas" :class="[isRecording ? 'fa-stop' : 'fa-microphone']"></i>
      {{ isRecording ? '松开结束' : '长按录音' }}
    </button>
    
    <div v-if="audioBlob" class="audio-preview">
      <audio controls :src="audioUrl"></audio>
      <button @click="sendAudio" class="send-button">
        <i class="fas fa-paper-plane"></i> 发送
      </button>
    </div>
    
    <div v-if="isProcessing" class="processing-indicator">
      <i class="fas fa-spinner fa-spin"></i> 处理中...
    </div>
  </div>
</template>
 
<script setup>
import { ref, computed } from 'vue'
import RecordRTC from 'recordrtc'
 
const emits = defineEmits(['audio-ready'])
const isRecording = ref(false)
const isProcessing = ref(false)
const audioBlob = ref(null)
const recorder = ref(null)
 
const audioUrl = computed(() => 
  audioBlob.value  ? URL.createObjectURL(audioBlob.value)  : ''
)
 
const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({  audio: true })
    recorder.value  = new RecordRTC(stream, {
      type: 'audio',
      mimeType: 'audio/webm',
      recorderType: RecordRTC.StereoAudioRecorder
    })
    recorder.value.startRecording() 
    isRecording.value  = true 
  } catch (err) {
    console.error(' 录音失败:', err)
  }
}
 
const stopRecording = () => {
  if (!recorder.value)  return 
  
  isRecording.value  = false 
  isProcessing.value  = true
  
  recorder.value.stopRecording(()  => {
    audioBlob.value  = recorder.value.getBlob() 
    isProcessing.value  = false 
    recorder.value  = null
  })
}
 
const sendAudio = () => {
  if (audioBlob.value)  {
    emits('audio-ready', audioBlob.value) 
    audioBlob.value  = null 
  }
}
</script>
 
<style scoped>
.audio-recorder {
  margin-top: 1rem;
}
 
button {
  padding: 0.8rem 1.5rem;
  background: #ff4757;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
 
button:disabled {
  background: #ccc;
}
 
.audio-preview {
  margin-top: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}
 
.send-button {
  background: #2ed573;
  padding: 0.5rem 1rem;
}
 
.processing-indicator {
  margin-top: 0.5rem;
  color: #3498db;
}
</style>