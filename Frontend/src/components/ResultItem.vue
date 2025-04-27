<template>
  <div class="result-item" :class="{ correct: result.isCorrect }">
    <h3 class="question">{{ result.question }}</h3>
    
    <div class="answers">
      <div class="user-answer">
        <h4>Your Answer:</h4>
        <p>{{ result.userAnswer || 'No answer provided' }}</p>
      </div>
      
      <div class="correct-answer">
        <h4>Correct Answer:</h4>
        <p>{{ result.correctAnswer }}</p>
      </div>
    </div>
    
    <div class="explanation">
      <h4>Explanation:</h4>
      <p>{{ result.explanation }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ResultItem',
  props: {
    result: {
      type: Object,
      required: true
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

.question {
  font-size: 1.1rem;
  margin-bottom: 15px;
}

.answers {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 15px;
}

.user-answer, .correct-answer, .explanation {
  margin-bottom: 10px;
}

.user-answer h4, .correct-answer h4, .explanation h4 {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 5px;
}

.correct-answer p {
  color: #4CAF50;
  font-weight: bold;
}

@media (max-width: 600px) {
  .answers {
    grid-template-columns: 1fr;
  }
}
</style>