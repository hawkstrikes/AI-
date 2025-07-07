<template>
  <div class="user-profile">
    <div class="avatar" @click="toggleDropdown">
      {{ userInitials }}
      <div v-if="showDropdown" class="dropdown">
        <div class="dropdown-item" @click="editProfile">
          <i class="fas fa-user-edit"></i> 编辑资料
        </div>
        <div class="dropdown-item" @click="logout">
          <i class="fas fa-sign-out-alt"></i> 退出登录
        </div>
      </div>
    </div>
    <div v-if="isEditing" class="profile-editor">
      <input v-model="editedName" type="text" placeholder="你的名字">
      <button @click="saveProfile">保存</button>
      <button @click="cancelEdit">取消</button>
    </div>
    <div v-else class="user-name">{{ userName }}</div>
  </div>
</template>
 
<script setup>
import { ref, computed } from 'vue'
import { useChatStore } from '../stores/chat'
 
const chatStore = useChatStore()
const showDropdown = ref(false)
const isEditing = ref(false)
const editedName = ref('')
 
const userInitials = computed(() => {
  if (!chatStore.currentUser?.name) return '?'
  return chatStore.currentUser.name.split(' ').map(n => n[0]).join('').toUpperCase()
})
 
const userName = computed(() => {
  return chatStore.currentUser?.name || '匿名用户'
})
 
function toggleDropdown() {
  showDropdown.value = !showDropdown.value 
}
 
function editProfile() {
  editedName.value = chatStore.currentUser?.name || ''
  isEditing.value = true
  showDropdown.value = false 
}
 
function logout() {
  // 简单的登出逻辑
  chatStore.currentUser = { id: 'user1', name: '匿名用户' }
  showDropdown.value = false 
}
 
function saveProfile() {
  if (editedName.value.trim()) {
    chatStore.currentUser = { 
      ...chatStore.currentUser, 
      name: editedName.value.trim() 
    }
    isEditing.value = false
  }
}
 
function cancelEdit() {
  isEditing.value = false 
}
</script>
 
<style scoped>
.user-profile {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  position: relative;
}
 
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #007bff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-weight: bold;
  position: relative;
  transition: background-color 0.3s ease;
}

.avatar:hover {
  background: #0056b3;
}
 
.dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  z-index: 1000;
  min-width: 150px;
  margin-top: 0.5rem;
}
 
.dropdown-item {
  padding: 0.75rem 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.2s ease;
  border-radius: 4px;
  margin: 0.25rem;
}
 
.dropdown-item:hover {
  background: #f8f9fa;
}
 
.profile-editor {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
 
.profile-editor input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}
 
.profile-editor button {
  padding: 0.5rem 0.75rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: background-color 0.2s ease;
}
 
.profile-editor button:first-of-type {
  background: #28a745;
  color: white;
}

.profile-editor button:first-of-type:hover {
  background: #218838;
}
 
.profile-editor button:last-of-type {
  background: #6c757d;
  color: white;
}

.profile-editor button:last-of-type:hover {
  background: #5a6268;
}
 
.user-name {
  font-weight: 500;
  color: white;
}
</style>