<template>
  <div class="navigation-buttons">
    <button 
      class="nav-button prev" 
      @click="$emit('previous')" 
      :disabled="isFirst"
    >
      Previous
    </button>
    
    <button 
      v-if="!isLast" 
      class="nav-button next" 
      @click="$emit('next')"
    >
      Next
    </button>
    
    <button 
      v-else 
      class="nav-button finish" 
      @click="$emit('finish')"
    >
      Finish Test
    </button>
  </div>
</template>

<script>
export default {
  name: 'NavigationButtons',
  props: {
    isFirst: {
      type: Boolean,
      default: false
    },
    isLast: {
      type: Boolean,
      default: false
    }
  },
  emits: ['previous', 'next', 'finish']
}
</script>

<style scoped>
.navigation-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.nav-button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.nav-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.prev {
  background-color: #e0e0e0;
  color: #333;
}

.prev:hover:not(:disabled) {
  background-color: #d0d0d0;
}

.next {
  background-color: #2196F3;
  color: white;
}

.next:hover:not(:disabled) {
  background-color: #1976D2;
}

.finish {
  background-color: #4CAF50;
  color: white;
}

.finish:hover:not(:disabled) {
  background-color: #45a049;
}
</style>