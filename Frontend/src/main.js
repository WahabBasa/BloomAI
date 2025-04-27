import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Create the application instance
const app = createApp(App)

// Add Pinia store
app.use(createPinia())

// Add router
app.use(router)

// Mount the app to the DOM
app.mount('#app')