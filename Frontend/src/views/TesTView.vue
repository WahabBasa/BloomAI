<template>
  <div class="test-container">
    <h1>Practice Questions</h1>
    
    <div v-if="isLoading" class="loading">
      Loading questions...
    </div>
    
    <div v-else-if="!currentQuestion" class="no-questions">
      No questions available. Please return to upload page.
    </div>
    
    <div v-else class="test-content">
      <div class="progress-bar">
        <div class="progress-text">
          Question {{ currentQuestionIndex + 1 }} of {{ totalQuestions }}
        </div>
        <div class="progress-track">
          <div 
            class="progress-fill" 
            :style="{ width: `${(currentQuestionIndex + 1) / totalQuestions * 100}%` }"
          ></div>
        </div>
      </div>
      
      <QuestionCard 
        :question="currentQuestion"
        @answer-submitted="submitAnswer"
      />
      
      <NavigationButtons 
        :is-first="currentQuestionIndex === 0"
        :is-last="isLastQuestion"
        @previous="previousQuestion"
        @next="nextQuestion"
        @finish="finishTest"
      />
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useTestStore } from '../stores/testStore'
import QuestionCard from '../components/QuestionCard.vue'
import NavigationButtons from '../components/NavigationButtons.vue'

export default {
  name: 'TestView',
  components: {
    QuestionCard,
    NavigationButtons
  },
  setup() {
    const router = useRouter()
    const testStore = useTestStore()
    
    // Load questions if not already loaded
    if (testStore.questions.length === 0) {
      testStore.loadQuestions()
    }
    
    const submitAnswer = (answer) => {
      if (testStore.currentQuestion) {
        testStore.submitAnswer(testStore.currentQuestion.id, answer)
      }
    }
    
    const finishTest = () => {
      testStore.completeTest()
      router.push('/results')
    }
    
    return {
      isLoading: computed(() => testStore.isLoading),
      currentQuestion: computed(() => testStore.currentQuestion),
      currentQuestionIndex: computed(() => testStore.currentQuestionIndex),
      totalQuestions: computed(() => testStore.totalQuestions),
      isLastQuestion: computed(() => testStore.isLastQuestion),
      userAnswers: computed(() => testStore.userAnswers),
      submitAnswer,
      nextQuestion: testStore.nextQuestion,
      previousQuestion: testStore.previousQuestion,
      finishTest
    }
  }
}
</script>

<style scoped>
.test-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
}

.loading, .no-questions {
  text-align: center;
  padding: 40px;
  background-color: #f5f5f5;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.test-content {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.progress-bar {
  margin-bottom: 20px;
}

.progress-text {
  text-align: center;
  margin-bottom: 10px;
  font-weight: bold;
}

.progress-track {
  background-color: #e0e0e0;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  background-color: #4CAF50;
  height: 100%;
  transition: width 0.3s ease;
}
</style>