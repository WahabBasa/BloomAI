<template>
  <div class="upload-form">
    <div 
      class="drop-area" 
      :class="{ active: isDragging }"
      @dragover.prevent="dragover"
      @dragleave.prevent="dragleave"
      @drop.prevent="drop"
      @click="triggerFileInput"
    >
      <input 
        type="file" 
        ref="fileInput" 
        class="file-input" 
        @change="onFileSelected" 
        accept=".pdf,.doc,.docx,.txt"
      >
      <div class="upload-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="17 8 12 3 7 8" />
          <line x1="12" y1="3" x2="12" y2="15" />
        </svg>
      </div>
      <p class="upload-text">
        <span class="primary-text">Drag and drop files here</span>
        <span class="secondary-text">or click to select files</span>
      </p>
      <p class="file-types">Supported formats: PDF, DOC, DOCX, TXT</p>
    </div>
    
    <div v-if="selectedFile" class="selected-file">
      <div class="file-info">
        <span class="file-name">{{ selectedFile.name }}</span>
        <span class="file-size">{{ formatFileSize(selectedFile.size) }}</span>
      </div>
      <button class="remove-button" @click.stop="removeFile">✕</button>
    </div>
    
    <button 
      v-if="selectedFile" 
      class="upload-button" 
      :disabled="isUploading"
      @click="uploadFile"
    >
      {{ isUploading ? 'Uploading...' : 'Upload File' }}
    </button>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'UploadForm',
  setup() {
    const fileInput = ref(null)
    const selectedFile = ref(null)
    const isDragging = ref(false)
    const isUploading = ref(false)
    
    const triggerFileInput = () => {
      fileInput.value.click()
    }
    
    const onFileSelected = (event) => {
      const file = event.target.files[0]
      if (file) {
        selectedFile.value = file
      }
    }
    
    const removeFile = () => {
      selectedFile.value = null
      fileInput.value.value = ''
    }
    
    const dragover = (event) => {
      isDragging.value = true
    }
    
    const dragleave = (event) => {
      isDragging.value = false
    }
    
    const drop = (event) => {
      isDragging.value = false
      if (event.dataTransfer.files.length) {
        selectedFile.value = event.dataTransfer.files[0]
      }
    }
    
    const formatFileSize = (bytes) => {
      if (bytes < 1024) return bytes + ' bytes'
      else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
      else return (bytes / 1048576).toFixed(1) + ' MB'
    }
    
    const uploadFile = () => {
      if (!selectedFile.value) return
      
      isUploading.value = true
      
      // Simulate file upload with timeout
      setTimeout(() => {
        isUploading.value = false
        removeFile()
        alert('File uploaded successfully! (This is a dummy implementation)')
      }, 1500)
    }
    
    return {
      fileInput,
      selectedFile,
      isDragging,
      isUploading,
      triggerFileInput,
      onFileSelected,
      removeFile,
      dragover,
      dragleave,
      drop,
      formatFileSize,
      uploadFile
    }
  }
}
</script>

<style scoped>
.upload-form {
  margin-bottom: 20px;
}

.drop-area {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: white;
}

.drop-area.active {
  border-color: #4CAF50;
  background-color: rgba(76, 175, 80, 0.1);
}

.drop-area:hover {
  border-color: #999;
}

.file-input {
  display: none;
}

.upload-icon {
  margin-bottom: 15px;
  color: #666;
}

.upload-text {
  margin-bottom: 10px;
}

.primary-text {
  display: block;
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 5px;
}

.secondary-text {
  color: #666;
}

.file-types {
  font-size: 12px;
  color: #999;
}

.selected-file {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
  padding: 12px;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.file-name {
  font-weight: bold;
  margin-right: 10px;
}

.file-size {
  color: #666;
  font-size: 0.9em;
}

.remove-button {
  background: none;
  border: none;
  color: #ff5252;
  cursor: pointer;
  font-size: 16px;
  padding: 5px;
}

.upload-button {
  display: block;
  width: 100%;
  margin-top: 15px;
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 12px;
  font-size: 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.upload-button:hover:not(:disabled) {
  background-color: #45a049;
}

.upload-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>