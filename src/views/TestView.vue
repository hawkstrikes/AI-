<template>
  <div class="test">
    <h1>Test Page</h1>
    <p>This is a test page to verify routing works.</p>
    <div class="test-content">
      <h2>Connection Test</h2>
      <p>Frontend is running on: {{ frontendUrl }}</p>
      <p>Backend API: {{ backendUrl }}</p>
      <p>Socket Status: {{ socketStatus }}</p>
    </div>
    <router-link to="/" class="btn">Back to Home</router-link>
  </div>
</template>

<script>
export default {
  name: 'TestView',
  data() {
    return {
      frontendUrl: window.location.href,
      backendUrl: 'http://localhost:3000/api/',
      socketStatus: 'Unknown'
    }
  },
  mounted() {
    if (window.socket) {
      this.socketStatus = window.socket.connected ? 'Connected' : 'Disconnected'
    }
  }
}
</script>

<style scoped>
.test {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.test-content {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 5px;
  margin: 20px 0;
}

.btn {
  display: inline-block;
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 5px;
}
</style>