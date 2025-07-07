<template>
  <div class="home">
    <h1>Multi-AI Chat System</h1>
    <p>Welcome to the AI Chat System!</p>
    <div class="navigation">
      <router-link to="/app" class="btn btn-primary">Go to Chat</router-link>
      <router-link to="/test" class="btn btn-secondary">Test Page</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView'
}
</script>

<style scoped>
.home {
  padding: 20px;
}

.navigation {
  margin-top: 20px;
}

.btn {
  display: inline-block;
  padding: 10px 20px;
  margin: 0 10px;
  text-decoration: none;
  border-radius: 5px;
  font-weight: bold;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}
</style>