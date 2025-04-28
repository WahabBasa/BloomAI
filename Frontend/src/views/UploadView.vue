<template>
  <div class="upload-container">
    <h1>Active Recall Learning System</h1>
    
    <div class="upload-area">
      <h2>Upload Study Material</h2>
      <UploadForm />
      
      <div class="previous-uploads">
        <h3>Previously Uploaded Materials</h3>
        <div class="upload-list">
          <div class="upload-item">
            <span>Sample Study Guide.pdf</span>
            <span class="upload-date">Uploaded on Apr 25, 2025</span>
          </div>
        </div>
      </div>
      
      <div class="actions">
        <button @click="startPractice" class="start-button">
          Start Practice
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { useTestStore } from '../stores/testStore'
import UploadForm from '../components/UploadForm.vue'

export default {
  name: 'UploadView',
  components: {
    UploadForm
  },
  setup() {
    const router = useRouter()
    const testStore = useTestStore()
    
    const startPractice = () => {
      // Get the document ID from localStorage if available
      const documentId = localStorage.getItem('currentDocumentId');
      
      if (documentId) {
        // Load questions for the selected document
        testStore.loadQuestions(documentId);
        router.push('/test');
      } else {
        // If no document is selected, show an alert or handle appropriately
        alert('Please upload or select a document first');
      }
    }
    
    return {
      startPractice
    }
  }
}
</script>

<style scoped>
.upload-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
}

.upload-area {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.previous-uploads {
  margin-top: 30px;
}

.upload-list {
  background-color: white;
  border-radius: 4px;
  padding: 10px;
}

.upload-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.upload-date {
  color: #666;
  font-size: 0.9em;
}

.actions {
  margin-top: 30px;
  text-align: center;
}

.start-button {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 12px 24px;
  font-size: 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.start-button:hover {
  background-color: #45a049;
}
</style>