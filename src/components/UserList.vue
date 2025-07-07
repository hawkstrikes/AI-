<template>
  <div class="user-list">
    <h3>Participants</h3>
    <ul>
      <li v-for="user in users" :key="user.id"> 
        <div class="user-avatar">{{ user.name.charAt(0) }}</div>
        <div class="user-info">
          <div class="user-name">{{ user.name }}</div>
          <div class="user-status">Online</div>
        </div>
      </li>
    </ul>
  </div>
</template>
 
<script setup>
defineProps({
  users: Array
})
</script>
 
<style scoped>
.user-list {
  width: 200px;
  padding: 1rem;
  background: #fff;
  border-right: 1px solid #ddd;
  overflow-y: auto;
}
 
.user-list h3 {
  margin-bottom: 1rem;
  font-size: 1rem;
  color: #555;
}
 
.user-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
 
.user-list li {
  display: flex;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
}
 
.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #007bff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.7rem;
  font-weight: bold;
}
 
.user-info {
  flex: 1;
}
 
.user-name {
  font-weight: bold;
  font-size: 0.9rem;
}
 
.user-status {
  font-size: 0.7rem;
  color: #28a745;
}
</style>