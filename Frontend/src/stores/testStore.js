import { defineStore } from 'pinia'
import { dummyQuestions } from '../data/dummyQuestions'

export const useTestStore = defineStore('test', {
  state: () => ({
    questions: [],
    currentQuestionIndex: 0,
    userAnswers: {},
    isTestCompleted: false,
    isLoading: false,
  }),
  
  getters: {
    currentQuestion: (state) => {
      return state.questions[state.currentQuestionIndex] || null
    },
    
    totalQuestions: (state) => {
      return state.questions.length
    },
    
    answeredQuestions: (state) => {
      return Object.keys(state.userAnswers).length
    },
    
    isLastQuestion: (state) => {
      return state.currentQuestionIndex === state.questions.length - 1
    },
    
    results: (state) => {
      const results = []
      
      state.questions.forEach((question) => {
        results.push({
          id: question.id,
          question: question.question,
          userAnswer: state.userAnswers[question.id] || '',
          correctAnswer: question.correctAnswer,
          explanation: question.explanation,
          isCorrect: state.userAnswers[question.id] === question.correctAnswer
        })
      })
      
      return results
    }
  },
  
  actions: {
    loadQuestions() {
      this.isLoading = true
      // Simulate API call with timeout
      setTimeout(() => {
        this.questions = dummyQuestions
        this.isLoading = false
      }, 500)
    },
    
    nextQuestion() {
      if (this.currentQuestionIndex < this.questions.length - 1) {
        this.currentQuestionIndex++
      }
    },
    
    previousQuestion() {
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--
      }
    },
    
    submitAnswer(questionId, answer) {
      this.userAnswers[questionId] = answer
    },
    
    completeTest() {
      this.isTestCompleted = true
    },
    
    resetTest() {
      this.currentQuestionIndex = 0
      this.userAnswers = {}
      this.isTestCompleted = false
    }
  }
})