# main_system/services/recall_service.py

import logging
import os

from main_system.tools.content_extractor import (
    PDFExtractorTool,
    PDFExtractorToolInputSchema,
)

from main_system.agents.llm_client import require_api_key

from main_system.agents.agents.qgen_agent import (
    ActiveRecallQuestionInputSchema,
    build_question_agent,
)

from main_system.agents.agents.agen_agent import (
    AnswerGeneratorInputSchema,
    build_answer_agent,
)

from main_system.agents.agents.g_agent import (
    GradingInputSchema,
    build_grading_agent,
)

# Import Django models
from main_system.models import Document, Question, UserAnswer

logger = logging.getLogger(__name__)

DEFAULT_QUESTION_COUNT = 5

# The extractor holds no per-request state, so one instance is fine.
pdf_tool = PDFExtractorTool()


def process_pdf(document_id):
    """
    Process a PDF document to extract content and generate questions

    Args:
        document_id: The UUID of the document to process

    Returns:
        A list of question objects
    """
    require_api_key()

    try:
        # Get the document from the database
        document = Document.objects.get(pk=document_id)

        # Resolve the stored relative path against the Backend/ directory
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), document.file_path
        )

        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found at {file_path}")

        # Extract content from the PDF
        pdf_output = pdf_tool.run(PDFExtractorToolInputSchema(file_path=file_path))

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

        document_title = document.title or "Untitled Document"

        # A fresh agent per document: no memory carried over from the last one.
        question_agent = build_question_agent(
            content=pdf_output.content,
            document_title=document_title,
            page_count=document.page_count,
        )
        question_response = question_agent.run(
            ActiveRecallQuestionInputSchema(question_count=DEFAULT_QUESTION_COUNT)
        )
        question_texts = question_response.questions

        # The document text reaches this agent through its context provider, so
        # the input schema carries only the questions.
        answer_agent = build_answer_agent(
            document_content=pdf_output.content,
            document_title=document_title,
        )
        answer_response = answer_agent.run(
            AnswerGeneratorInputSchema(questions=question_texts)
        )
        explanations = answer_response.explanations

        # zip() would silently drop the tail of the longer list, leaving the
        # user with fewer questions than the model generated -- or with
        # explanations attached to the wrong questions.
        if len(explanations) != len(question_texts):
            raise ValueError(
                f"Answer generator returned {len(explanations)} explanations for "
                f"{len(question_texts)} questions; refusing to pair them up."
            )

        # Create question objects with questions and explanations
        questions = []
        for question_text, explanation in zip(question_texts, explanations):
            question = Question.objects.create(
                document=document,
                question_text=question_text,
                answer_explanation=explanation,
            )
            questions.append(question)

        return questions

    except Exception:
        logger.exception("Error processing PDF for document %s", document_id)
        raise


def grade_answer(answer_id):
    """
    Grade a user's answer to a question

    Args:
        answer_id: The UUID of the answer to grade

    Returns:
        The updated UserAnswer object with a grade and feedback
    """
    require_api_key()

    try:
        # Get the answer from the database
        user_answer = UserAnswer.objects.get(pk=answer_id)
        question = user_answer.question

        grading_agent = build_grading_agent(
            question=question.question_text,
            explanation=question.answer_explanation,
            user_answer=user_answer.user_answer,
        )
        grading_output = grading_agent.run(
            GradingInputSchema(
                question=question.question_text,
                explanation=question.answer_explanation,
                user_answer=user_answer.user_answer,
            )
        )

        # Store the score as a percentage: 0, 50 or 100
        user_answer.mark = int(grading_output.score * 100)
        user_answer.feedback = grading_output.feedback
        user_answer.save()

        return user_answer

    except Exception:
        logger.exception("Error grading answer %s", answer_id)
        raise
