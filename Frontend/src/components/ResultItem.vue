<template>
  <div class="result-item" :class="result.status">
    <div class="result-header">
      <h3 class="question">{{ result.question }}</h3>
      <span class="status-badge">{{ statusLabel }}</span>
    </div>

    <div class="user-answer">
      <h4>Your Answer:</h4>
      <p>{{ result.userAnswer || 'No answer provided' }}</p>
    </div>
    
    <div v-if="result.feedback" class="feedback">
      <h4>Feedback:</h4>
      <p>{{ result.feedback }}</p>
    </div>

    <div class="explanation">
      <h4>Explanation:</h4>
      <p>{{ result.explanation }}</p>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

const STATUS_LABELS = {
  correct: 'Correct',
  partial: 'Partially correct',
  incorrect: 'Incorrect',
  unanswered: 'Not answered'
}

export default {
  name: 'ResultItem',
  props: {
    result: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    return {
      statusLabel: computed(() => STATUS_LABELS[props.result.status] ?? STATUS_LABELS.unanswered)
    }
  }
}
</script>

<style scoped>
.result-item {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 15px;
  border-left: 4px solid #ff5252;
}

.result-item.correct {
  border-left-color: #4CAF50;
}

.result-item.partial {
  border-left-color: #FFA000;
}

.result-item.unanswered {
  border-left-color: #9e9e9e;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 15px;
}

.question {
  font-size: 1.1rem;
}

.status-badge {
  flex-shrink: 0;
  font-size: 0.8rem;
  padding: 3px 10px;
  border-radius: 999px;
  white-space: nowrap;
  background-color: #ffebee;
  color: #c62828;
}

.result-item.correct .status-badge {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.result-item.partial .status-badge {
  background-color: #fff8e1;
  color: #ef6c00;
}

.result-item.unanswered .status-badge {
  background-color: #f0f0f0;
  color: #616161;
}

.user-answer, .feedback, .explanation {
  margin-bottom: 15px;
}

.user-answer h4, .feedback h4, .explanation h4 {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 5px;
}

.feedback, .explanation {
  background-color: #f9f9f9;
  padding: 10px;
  border-radius: 4px;
}

.feedback {
  background-color: #eef4fb;
}

.feedback p, .explanation p {
  line-height: 1.5;
}

@media (max-width: 600px) {
  .user-answer, .feedback, .explanation {
    padding: 5px;
  }
}
</style>