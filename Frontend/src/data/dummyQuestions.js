// Sample questions data for testing Active Recall Learning System
export const dummyQuestions = [
    {
      id: 1,
      question: "What is the primary purpose of the Active Recall Learning System?",
      correctAnswer: "To enhance knowledge retention and understanding through interactive learning experiences that leverage active recall techniques.",
      explanation: "Active recall is a learning technique that involves retrieving information from memory rather than passively reviewing it. The system is designed to transform educational content into questions that prompt users to actively engage with the material, which has been proven to strengthen memory pathways and improve long-term retention.",
      difficulty: "easy",
      tags: ["overview", "concept"]
    },
    {
      id: 2,
      question: "Name the four core agents that make up the Active Recall Learning System.",
      correctAnswer: "Extractor Agent, Question Generator, Answer Generator, and Grading Agent.",
      explanation: "The system uses four specialized AI agents working together: the Extractor Agent analyzes and extracts educational content from uploaded documents; the Question Generator transforms this content into targeted recall questions; the Answer Generator creates detailed explanations for each question; and the Grading Agent evaluates user responses against the explained answers.",
      difficulty: "medium",
      tags: ["components", "agents"]
    },
    {
      id: 3,
      question: "How does the Extractor Agent work in the Active Recall Learning System?",
      correctAnswer: "It analyzes PDF documents and extracts relevant educational content for processing by other agents.",
      explanation: "The Extractor Agent is responsible for analyzing uploaded PDF documents and identifying the key educational content within them. It uses natural language processing techniques to extract meaningful information while filtering out irrelevant content. This extracted material forms the basis for question generation in subsequent processing steps.",
      difficulty: "medium",
      tags: ["agents", "functionality"]
    },
    {
      id: 4,
      question: "What is the function of the Test class in the Active Recall Learning System?",
      correctAnswer: "It maintains questions derived from source material, comprehensive answer explanations, user-submitted responses, and performance marks for each question.",
      explanation: "The Test class serves as the central data structure for the system. It stores the questions generated from source material, the detailed explanations for each question, the responses submitted by users, and tracking information about performance on each question. This allows the system to provide meaningful feedback and track learning progress over time.",
      difficulty: "hard",
      tags: ["components", "implementation"]
    },
    {
      id: 5,
      question: "What learning principle does the Active Recall Learning System primarily leverage?",
      correctAnswer: "The testing effect (or retrieval practice), which shows that actively recalling information strengthens memory more effectively than passive review.",
      explanation: "The system is built on the cognitive science principle known as 'the testing effect' or 'retrieval practice.' Research has consistently shown that actively retrieving information from memory (as opposed to simply re-reading or reviewing it) creates stronger neural pathways and significantly improves long-term retention and understanding of the material.",
      difficulty: "medium",
      tags: ["concept", "science"]
    },
    {
      id: 6,
      question: "What transformation occurs between the Question Generator and Answer Generator?",
      correctAnswer: "The Question Generator creates targeted active recall questions, while the Answer Generator produces detailed explanations for those questions.",
      explanation: "This represents a key transformation in the system workflow. The Question Generator takes extracted educational content and converts it into effective active recall questions. These questions are then passed to the Answer Generator, which creates comprehensive explanations that not only provide the correct answer but also context and reasoning to deepen understanding.",
      difficulty: "hard",
      tags: ["agents", "workflow"]
    },
    {
      id: 7,
      question: "What format does the system use for educational content input?",
      correctAnswer: "PDF documents",
      explanation: "The Active Recall Learning System is designed to work with PDF documents as its primary input format. The Extractor Agent specifically analyzes PDF files to extract the relevant educational content that will be transformed into questions and answers.",
      difficulty: "easy",
      tags: ["functionality", "input"]
    },
    {
      id: 8,
      question: "What is the final step in the system's workflow?",
      correctAnswer: "The Grading Agent evaluates user responses against the explained answers.",
      explanation: "After a user has submitted their response to a question, the Grading Agent compares this response to the correct answer and explanation. It evaluates the accuracy and completeness of the user's answer, providing a performance mark that helps track learning progress and identify areas that may need additional focus.",
      difficulty: "medium",
      tags: ["workflow", "agents"]
    }
  ];
  
  export default dummyQuestions;