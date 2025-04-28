import { defineStore } from 'pinia'
import apiService from '../services/apiService'

export const useTestStore = defineStore('test', {
  state: () => ({
    documentId: null,
    questions: [],
    currentQuestionIndex: 0,
    userAnswers: {},
    isTestCompleted: false,
    isLoading: false,
    error: null
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
          id: question.question_id,
          question: question.question_text,
          userAnswer: state.userAnswers[question.question_id] || '',
          correctAnswer: question.answer_explanation,
          explanation: question.answer_explanation,
          isCorrect: question.has_been_answered && question.last_mark > 0
        })
      })
      
      return results
    }
  },
  
  actions: {
    async loadQuestions(documentId) {
      this.isLoading = true
      this.error = null
      
      try {
        // Store the document ID
        this.documentId = documentId
        
        // Fetch questions from API
        const response = await apiService.getQuestions(documentId)
        
        if (response && response.questions) {
          this.questions = response.questions.map(q => ({
            ...q,
            // Ensure the question has the properties your UI expects
            question_id: q.question_id,
            question_text: q.question_text,
            has_been_answered: q.has_been_answered || false,
            last_mark: q.last_mark || null
          }))
        } else {
          throw new Error('Invalid response format from API')
        }
      } catch (error) {
        this.error = error.message || 'Failed to load questions'
        console.error('Error loading questions:', error)
        this.questions = []
      } finally {
        this.isLoading = false
      }
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
    
  // Update the submitAnswer method in testStore.js
  async submitAnswer(questionId, answer) {
    try {
      // First update the local state
      this.userAnswers[questionId] = answer
      
      // Then submit to the API
      const response = await apiService.submitAnswer(questionId, answer)
      
      // Update the question with the grading information from the response
      if (response && response.mark !== undefined) {
        const questionIndex = this.questions.findIndex(q => q.question_id === questionId)
        if (questionIndex !== -1) {
          this.questions[questionIndex].has_been_answered = true
          this.questions[questionIndex].last_mark = response.mark
        }
      }
    } catch (error) {
      console.error('Error submitting answer:', error)
      // You might want to handle this error in the UI
    }
  },


    // Add this method to testStore.js actions
  async refreshQuestionGrades() {
    if (!this.documentId) return
    
    try {
      // Fetch the latest question data with grading information
      const response = await apiService.getQuestions(this.documentId)
      
      if (response && response.questions) {
        // Update existing questions with the latest grading information
        response.questions.forEach(updatedQ => {
          const questionIndex = this.questions.findIndex(q => q.question_id === updatedQ.question_id)
          if (questionIndex !== -1) {
            this.questions[questionIndex].has_been_answered = updatedQ.has_been_answered || false
            this.questions[questionIndex].last_mark = updatedQ.last_mark || null
          }
        })
      }
    } catch (error) {
      console.error('Error refreshing question grades:', error)
    }
  },

  // Update the completeTest method to refresh grades before completing
  async completeTest() {
    await this.refreshQuestionGrades()
    this.isTestCompleted = true
  },  
    

    
    resetTest() {
      this.documentId = null
      this.currentQuestionIndex = 0
      this.userAnswers = {}
      this.isTestCompleted = false
      this.questions = []
      this.error = null
    }
  }
})