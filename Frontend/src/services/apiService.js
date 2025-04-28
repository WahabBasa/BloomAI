// Base API URL - updated for Azure App Service
const API_BASE_URL = 'https://bloomai-hackathon-prd-wa-uaen-01-eaexdxhbegfvhgd7.uaenorth-01.azurewebsites.net/api';

/**
 * API Service for interacting with the Django backend
 */
const apiService = {
  /**
   * Document Management
   */
  
  // Get all documents
  async getDocuments() {
    try {
      const response = await fetch(`${API_BASE_URL}/documents/`);
      if (!response.ok) {
        throw new Error(`Error fetching documents: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch documents:', error);
      throw error;
    }
  },
  
  // Upload a document
  async uploadDocument(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch(`${API_BASE_URL}/documents/upload/`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`Error uploading document: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Failed to upload document:', error);
      throw error;
    }
  },
  
  // Get a specific document
  async getDocument(documentId) {
    try {
      const response = await fetch(`${API_BASE_URL}/documents/${documentId}/`);
      if (!response.ok) {
        throw new Error(`Error fetching document: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`Failed to fetch document ${documentId}:`, error);
      throw error;
    }
  },
  
  /**
   * Question Management
   */
  
  // Get questions for a document
  async getQuestions(documentId) {
    try {
      const response = await fetch(`${API_BASE_URL}/documents/${documentId}/questions/`);
      if (!response.ok) {
        throw new Error(`Error fetching questions: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`Failed to fetch questions for document ${documentId}:`, error);
      throw error;
    }
  },
  
  // Get a specific question
  async getQuestion(questionId) {
    try {
      const response = await fetch(`${API_BASE_URL}/questions/${questionId}/`);
      if (!response.ok) {
        throw new Error(`Error fetching question: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`Failed to fetch question ${questionId}:`, error);
      throw error;
    }
  },
  
  /**
   * Answer Management
   */
  
  // Submit an answer to a question
  async submitAnswer(questionId, answer) {
    try {
      const response = await fetch(`${API_BASE_URL}/questions/${questionId}/answer/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ answer }),
      });
      
      if (!response.ok) {
        throw new Error(`Error submitting answer: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`Failed to submit answer for question ${questionId}:`, error);
      throw error;
    }
  },
  
  // Get a specific answer
  async getAnswer(answerId) {
    try {
      const response = await fetch(`${API_BASE_URL}/answers/${answerId}/`);
      if (!response.ok) {
        throw new Error(`Error fetching answer: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`Failed to fetch answer ${answerId}:`, error);
      throw error;
    }
  }
};

export default apiService;