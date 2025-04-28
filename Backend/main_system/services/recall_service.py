# main_system/services/recall_service.py

import os
from datetime import datetime
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

# Check if the API key is loaded
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables!")

from main_system.tools.content_extractor import (
    PDFExtractorTool,
    PDFExtractorToolConfig,
    PDFExtractorToolInputSchema,
)

from main_system.agents.agents.qgen_agent import (
    ActiveRecallQuestionInputSchema, 
    active_recall_agent, 
    pdf_content_provider
)

from main_system.agents.agents.agen_agent import (
    AnswerGeneratorInputSchema,
    answer_generator_agent,
    content_provider
)

from main_system.agents.agents.g_agent import (
    GradingInputSchema,
    grading_agent,
    grading_context_provider
)

# Import Django models
from main_system.models import Document, Question, UserAnswer

# Initialize the PDFExtractorTool
pdf_tool = PDFExtractorTool(config=PDFExtractorToolConfig())

def process_pdf(document_id):
    """
    Process a PDF document to extract content and generate questions
    
    Args:
        document_id: The UUID of the document to process
        
    Returns:
        A list of question objects
    """
    try:
        # Get the document from the database
        document = Document.objects.get(pk=document_id)
        
        # For local development, the file path is relative to MEDIA_ROOT
        # Assuming uploads/ directory in the project root
        file_path = os.path.join('uploads', os.path.basename(document.file_path))
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found at {file_path}")
        
        # Extract content from the PDF
        pdf_input = PDFExtractorToolInputSchema(file_path=file_path)
        pdf_output = pdf_tool.run(pdf_input)
        
        # Update document with extracted content
        document.content = pdf_output.content
        document.page_count = pdf_output.metadata.num_pages
        if pdf_output.metadata.title:
            document.title = pdf_output.metadata.title
        if pdf_output.metadata.author:
            document.author = pdf_output.metadata.author
        if pdf_output.metadata.created_date:
            document.created_date = pdf_output.metadata.created_date
        document.save()
        
        # Update pdf_content_provider with the extracted PDF data
        pdf_content_provider.content = pdf_output.content
        pdf_content_provider.title = document.title or "Untitled Document"
        pdf_content_provider.page_count = document.page_count

        # Run the content through the question generator agent
        question_input = ActiveRecallQuestionInputSchema(
            document_id=str(document_id),
            question_count=5  # Generate 5 questions by default
        )
        agent_response = active_recall_agent.run(question_input)
        
        # Store generated questions in a list for later use
        question_texts = agent_response.questions
        
        # Generate explanations using the answer generator agent
        # Update the content provider for the answer generator
        content_provider.document_content = pdf_output.content
        content_provider.questions = question_texts
        
        # Run the answer generator agent
        answer_input = AnswerGeneratorInputSchema(
            document_content=pdf_output.content,
            questions=question_texts,
            document_title=document.title or "Untitled Document"
        )
        answer_response = answer_generator_agent.run(answer_input)
        
        # Create question objects with questions and explanations
        questions = []
        for question_text, explanation in zip(question_texts, answer_response.explanations):
            # Create question in the database
            question = Question.objects.create(
                document=document,
                question_text=question_text,
                answer_explanation=explanation
            )
            questions.append(question)
        
        return questions
    
    except Exception as e:
        # Log the error
        print(f"Error processing PDF: {str(e)}")
        raise

def grade_answer(answer_id):
    """
    Grade a user's answer to a question
    
    Args:
        answer_id: The UUID of the answer to grade
        
    Returns:
        The updated UserAnswer object with a grade
    """
    try:
        # Get the answer from the database
        user_answer = UserAnswer.objects.get(pk=answer_id)
        question = user_answer.question
        
        # Configure the grading context
        grading_context_provider.question = question.question_text
        grading_context_provider.explanation = question.answer_explanation
        grading_context_provider.user_answer = user_answer.user_answer
        
        grading_input = GradingInputSchema(
            question=question.question_text,
            explanation=question.answer_explanation,
            user_answer=user_answer.user_answer
        )
        
        grading_output = grading_agent.run(grading_input)
        
        # Update the answer with the score (convert to 0, 50, or 100)
        user_answer.mark = int(grading_output.score * 100)
        user_answer.save()
        
        return user_answer
    
    except Exception as e:
        # Log the error
        print(f"Error grading answer: {str(e)}")
        raise