<template>
  <div class="question-card">
    <h2 class="question-text">{{ question.question_text }}</h2>
    
    <div class="answer-section">
      <label for="answer-input">Your Answer:</label>
      <textarea
        id="answer-input"
        v-model="answer"
        class="answer-input"
        placeholder="Type your answer here..."
      ></textarea>
      
      <button
        class="submit-button"
        @click="submitAnswer"
        :disabled="!answer.trim()"
      >
        Submit Answer
      </button>
    </div>
  </div>
</template>

<script>

import { ref, watch } from 'vue'

export default {
  name: 'QuestionCard',
  props: {
    question: {
      type: Object,
      required: true
    }
  },
  emits: ['answer-submitted'],
  setup(props, { emit }) {
    const answer = ref('')

    // Reset when question changes
    watch(() => props.question.question_id, () => {
      answer.value = ''
    })

    // Submitting is explicit. There used to be a watcher that emitted
    // 'answer-submitted' one second after every typing pause, so a single
    // answer was sent to the backend -- and graded by the LLM -- once per
    // pause while the user was still writing it.
    const submitAnswer = () => {
      const trimmed = answer.value.trim()
      if (!trimmed) return
      emit('answer-submitted', trimmed)
    }

    return {
      answer,
      submitAnswer
    }
  }
}
</script>

<style scoped>
.question-card {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}



.question-text {
  font-size: 1.2rem;
  line-height: 1.5;
  margin-bottom: 20px;
}

.answer-section {
  margin-bottom: 20px;
}

.answer-section label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
}

.answer-input {
  width: 100%;
  min-height: 120px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
  font-family: inherit;
  font-size: 1rem;
  margin-bottom: 15px;
}

.submit-button {
  background-color: #2196F3;
  color: white;
  border: none;
  padding: 10px 20px;
  font-size: 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-button:hover:not(:disabled) {
  background-color: #1976D2;
}

.submit-button:disabled {
  background-color: #BBDEFB;
  cursor: not-allowed;
}
</style>