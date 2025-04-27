<template>
  <div class="app">
    <header class="app-header">
      <h1 class="app-title">Active Recall Learning System</h1>
      <nav class="app-nav">
        <router-link to="/" class="nav-link">Home</router-link>
        <router-link to="/test" class="nav-link">Practice</router-link>
        <router-link to="/results" class="nav-link">Results</router-link>
      </nav>
    </header>
    
    <main class="app-content">
      <router-view />
    </main>
    
    <footer class="app-footer">
      <p>© 2025 Active Recall Learning System</p>
    </footer>
  </div>
</template>

<style>
/* Global styles */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: Arial, sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f9f9f9;
}

/* App layout */
.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  background-color: #4CAF50;
  color: white;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.app-title {
  font-size: 1.5rem;
  margin: 0;
}

.app-nav {
  display: flex;
  gap: 20px;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav-link:hover,
.router-link-active {
  background-color: rgba(255, 255, 255, 0.2);
}

.app-content {
  flex: 1;
  padding: 1rem;
}

.app-footer {
  background-color: #f1f1f1;
  color: #666;
  text-align: center;
  padding: 1rem;
  margin-top: auto;
}

/* Common form elements */
button {
  cursor: pointer;
}

/* Responsive adjustments */
@media (max-width: 600px) {
  .app-header {
    flex-direction: column;
    gap: 10px;
  }
}
</style>