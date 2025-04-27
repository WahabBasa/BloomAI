<template>
  <div class="results-container">
    <h1>Your Results</h1>
    
    <div v-if="!isTestCompleted" class="not-completed">
      <p>You haven't completed a test yet.</p>
      <button @click="goToUpload" class="action-button">Go to Upload</button>
    </div>
    
    <div v-else class="results-content">
      <div class="results-summary">
        <div class="summary-item">
          <div class="summary-value">{{ correctAnswers }}</div>
          <div class="summary-label">Correct</div>
        </div>
        <div class="summary-item">
          <div class="summary-value">{{ totalQuestions - correctAnswers }}</div>
          <div class="summary-label">Incorrect</div>
        </div>
        <div class="summary-item">
          <div class="summary-value">{{ scorePercentage }}%</div>
          <div class="summary-label">Score</div>
        </div>
      </div>
      
      <h2>Question Review</h2>
      
      <div class="results-list">
        <ResultItem
          v-for="result in results"
          :key="result.id"
          :result="result"
        />
      </div>
      
      <div class="actions">
        <button @click="retakeTest" class="action-button">
          Retake Test
        </button>
        <button @click="goToUpload" class="action-button secondary">
          Back to Upload
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useTestStore } from '../stores/testStore'
import ResultItem from '../components/ResultItem.vue'

export default {
  name: 'ResultsView',
  components: {
    ResultItem
  },
  setup() {
    const router = useRouter()
    const testStore = useTestStore()
    
    // Redirect if coming directly to results without completing test
    if (!testStore.isTestCompleted && testStore.questions.length > 0) {
      router.push('/test')
    }
    
    const correctAnswers = computed(() => {
      return testStore.results.filter(result => result.isCorrect).length
    })
    
    const scorePercentage = computed(() => {
      if (testStore.totalQuestions === 0) return 0
      return Math.round((correctAnswers.value / testStore.totalQuestions) * 100)
    })
    
    const retakeTest = () => {
      testStore.resetTest()
      router.push('/test')
    }
    
    const goToUpload = () => {
      router.push('/')
    }
    
    return {
      isTestCompleted: computed(() => testStore.isTestCompleted),
      results: computed(() => testStore.results),
      totalQuestions: computed(() => testStore.totalQuestions),
      correctAnswers,
      scorePercentage,
      retakeTest,
      goToUpload
    }
  }
}
</script>

<style scoped>
.results-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

h1, h2 {
  text-align: center;
}

h1 {
  margin-bottom: 30px;
}

h2 {
  margin: 30px 0 20px;
}

.not-completed {
  text-align: center;
  padding: 40px;
  background-color: #f5f5f5;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.results-content {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.results-summary {
  display: flex;
  justify-content: space-around;
  margin: 20px 0;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
}

.summary-item {
  text-align: center;
}

.summary-value {
  font-size: 2rem;
  font-weight: bold;
  color: #333;
}

.summary-label {
  font-size: 1rem;
  color: #666;
}

.results-list {
  margin-bottom: 30px;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}

.action-button {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 12px 24px;
  font-size: 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.action-button:hover {
  background-color: #45a049;
}

.action-button.secondary {
  background-color: #757575;
}

.action-button.secondary:hover {
  background-color: #616161;
}
</style>