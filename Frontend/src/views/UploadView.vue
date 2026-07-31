<template>
  <div class="upload-container">
    <h1>Active Recall Learning System</h1>
    
    <div class="upload-area">
      <h2>Upload Study Material</h2>
      <UploadForm />
      
      <div class="previous-uploads">
        <h3>Previously Uploaded Materials</h3>

        <div v-if="isLoadingDocuments" class="upload-list-message">
          Loading your materials...
        </div>
        <div v-else-if="documentsError" class="upload-list-message error">
          {{ documentsError }}
        </div>
        <div v-else-if="documents.length === 0" class="upload-list-message">
          Nothing uploaded yet.
        </div>
        <div v-else class="upload-list">
          <button
            v-for="doc in documents"
            :key="doc.document_id"
            class="upload-item"
            :class="{ selected: doc.document_id === selectedDocumentId }"
            @click="selectDocument(doc.document_id)"
          >
            <span class="upload-title">{{ doc.title }}</span>
            <span class="upload-meta">
              {{ doc.questions_count }} question{{ doc.questions_count === 1 ? '' : 's' }}
              &middot; {{ formatDate(doc.uploaded_at) }}
            </span>
          </button>
        </div>
      </div>

      <div class="actions">
        <button @click="startPractice" class="start-button" :disabled="!selectedDocumentId">
          Start Practice
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTestStore } from '../stores/testStore'
import apiService from '../services/apiService'
import UploadForm from '../components/UploadForm.vue'

export default {
  name: 'UploadView',
  components: {
    UploadForm
  },
  setup() {
    const router = useRouter()
    const testStore = useTestStore()

    // This list used to be a single hardcoded "Sample Study Guide.pdf" row
    // that was never anyone's document.
    const documents = ref([])
    const isLoadingDocuments = ref(true)
    const documentsError = ref('')
    const selectedDocumentId = ref(localStorage.getItem('currentDocumentId'))

    onMounted(async () => {
      try {
        const response = await apiService.getDocuments()
        documents.value = response?.documents ?? []
      } catch (error) {
        documentsError.value = error.message || 'Failed to load your materials'
      } finally {
        isLoadingDocuments.value = false
      }
    })

    const selectDocument = (documentId) => {
      selectedDocumentId.value = documentId
      localStorage.setItem('currentDocumentId', documentId)
    }

    const formatDate = (isoString) => {
      if (!isoString) return ''
      return new Date(isoString).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    const startPractice = () => {
      if (!selectedDocumentId.value) return

      testStore.loadQuestions(selectedDocumentId.value)
      router.push('/test')
    }

    return {
      documents,
      isLoadingDocuments,
      documentsError,
      selectedDocumentId,
      selectDocument,
      formatDate,
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

.upload-list-message {
  background-color: white;
  border-radius: 4px;
  padding: 15px;
  color: #666;
}

.upload-list-message.error {
  color: #c62828;
}

.upload-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px;
  border: none;
  border-bottom: 1px solid #eee;
  background: none;
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.upload-item:last-child {
  border-bottom: none;
}

.upload-item:hover {
  background-color: #f5f5f5;
}

.upload-item.selected {
  background-color: rgba(76, 175, 80, 0.12);
}

.upload-title {
  font-weight: bold;
}

.upload-meta {
  color: #666;
  font-size: 0.9em;
  white-space: nowrap;
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

.start-button:hover:not(:disabled) {
  background-color: #45a049;
}

.start-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>