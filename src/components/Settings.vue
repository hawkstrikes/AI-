<template>
  <div class="settings-container">
    <h2>AI Configuration</h2>
    
    <!-- AI服务选择 -->
    <div class="setting-group">
      <label>AI Service</label>
      <select v-model="currentService">
        <option value="step_star">阶跃星辰AI</option>
        <option value="deepseek">DeepSeek</option>
        <option value="minichat">MiniChat</option>
      </select>
    </div>
 
    <!-- 阶跃星辰AI特有设置 -->
    <div v-if="currentService === 'step_star'" class="setting-group">
      <label>Personality Traits</label>
      <div class="traits-grid">
        <div 
          v-for="trait in traitsOptions"
          :key="trait.value" 
          class="trait-item"
          :class="{ active: currentTraits.includes(trait.value) }"
          @click="toggleTrait(trait.value)" 
        >
          {{ trait.label }}
        </div>
      </div>
      <div class="slider-control">
        <label>Temperature: {{ currentTemperature.toFixed(1) }}</label>
        <input 
          type="range"
          min="0"
          max="1"
          step="0.1"
          v-model.number="currentTemperature" 
        >
      </div>
    </div>
 
    <!-- MiniChat特有设置 -->
    <div v-if="currentService === 'minichat'" class="setting-group">
      <label>Voice Profile</label>
      <select v-model="currentVoice">
        <option value="en-US-Wavenet-D">Male (US)</option>
        <option value="en-US-Wavenet-A">Female (US)</option>
      </select>
      <div class="slider-control">
        <label>Pitch: {{ currentPitch }}</label>
        <input
          type="range"
          min="-20"
          max="20"
          step="1"
          v-model.number="currentPitch" 
        >
      </div>
    </div>
 
    <button @click="applySettings" class="save-btn">Save Settings</button>
  </div>
</template>
 
<script setup>
import { ref, computed } from 'vue'
import { useChatStore } from '../stores/chat'
 
const chatStore = useChatStore()
 
// 可用选项配置 
const traitsOptions = [
  { value: 'friendly', label: 'Friendly' },
  { value: 'professional', label: 'Professional' },
  { value: 'creative', label: 'Creative' }
]
 
// 状态绑定 - 修复属性访问
const currentService = ref(chatStore.aiSettings.service) 
const currentTraits = ref(['friendly', 'helpful']) // 默认值
const currentTemperature = ref(chatStore.aiSettings.temperature) 
const currentVoice = ref('en-US-Wavenet-D') // 默认值
const currentPitch = ref(0) // 默认值
 
// 特征切换 
const toggleTrait = (trait) => {
  const index = currentTraits.value.indexOf(trait) 
  if (index >= 0) {
    currentTraits.value.splice(index, 1)
  } else {
    currentTraits.value.push(trait) 
  }
}
 
// 应用设置
const applySettings = () => {
  chatStore.updateSettings({ 
    service: currentService.value, 
    personality: {
      traits: currentTraits.value, 
      temperature: currentTemperature.value  
    },
    voiceProfile: {
      id: currentVoice.value, 
      pitch: currentPitch.value  
    }
  })
}
</script>
 
<style scoped>
.settings-container {
  padding: 1.5rem;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
 
.setting-group {
  margin-bottom: 1.5rem;
}
 
label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}
 
select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}
 
.traits-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 0.5rem;
  margin: 0.5rem 0;
}
 
.trait-item {
  padding: 0.5rem;
  text-align: center;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}
 
.trait-item.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}
 
.slider-control {
  margin-top: 1rem;
}
 
.slider-control input {
  width: 100%;
}
 
.save-btn {
  margin-top: 1rem;
  padding: 0.7rem;
  width: 100%;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}
</style>