import json
import os
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.conf import settings

from .models import Document, Question, UserAnswer
from .services.recall_service import process_pdf, grade_answer

# Document Management Endpoints
@csrf_exempt
def upload_document(request):
    """API endpoint for uploading PDF documents"""
    if request.method == 'POST':
        try:
            if 'file' not in request.FILES:
                return JsonResponse({'error': 'No file uploaded'}, status=400)
            
            uploaded_file = request.FILES['file']
            
            # Check if it's a PDF
            if not uploaded_file.name.endswith('.pdf'):
                return JsonResponse({'error': 'Only PDF files are supported'}, status=400)
            
            # For local development, save to uploads directory
            # Make sure the directory exists
            upload_dir = os.path.join(settings.BASE_DIR, 'uploads')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            # Create a path to save the file
            file_path = os.path.join('uploads', uploaded_file.name)
            full_path = os.path.join(settings.BASE_DIR, file_path)
            
            # Save the file to disk
            with open(full_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # Create document record in the database
            document = Document.objects.create(
                file_path=file_path,
                title=os.path.splitext(uploaded_file.name)[0],
                content=""  # Content will be extracted by process_pdf
            )
            
            # Process the PDF
            questions = process_pdf(document.document_id)
            
            return JsonResponse({
                'document_id': str(document.document_id),
                'title': document.title,
                'questions_count': len(questions)
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# The rest of the file remains unchanged
def get_documents(request):
    """API endpoint for retrieving all documents"""
    if request.method == 'GET':
        documents = Document.objects.all().order_by('-uploaded_at')
        documents_data = []
        
        for doc in documents:
            questions_count = Question.objects.filter(document=doc).count()
            documents_data.append({
                'document_id': str(doc.document_id),
                'title': doc.title or "Untitled Document",
                'uploaded_at': doc.uploaded_at.isoformat(),
                'page_count': doc.page_count,
                'questions_count': questions_count
            })
        
        return JsonResponse({'documents': documents_data})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_document(request, document_id):
    """API endpoint for retrieving a specific document"""
    if request.method == 'GET':
        try:
            # Convert string to UUID
            doc_uuid = uuid.UUID(document_id)
            document = get_object_or_404(Document, document_id=doc_uuid)
            
            # Get questions for this document
            questions = Question.objects.filter(document=document)
            questions_data = []
            
            for question in questions:
                questions_data.append({
                    'question_id': str(question.question_id),
                    'question_text': question.question_text
                })
            
            return JsonResponse({
                'document_id': str(document.document_id),
                'title': document.title or "Untitled Document",
                'uploaded_at': document.uploaded_at.isoformat(),
                'page_count': document.page_count,
                'author': document.author,
                'created_date': document.created_date.isoformat() if document.created_date else None,
                'questions': questions_data
            })
            
        except (ValueError, uuid.ValueError):
            return JsonResponse({'error': 'Invalid document ID format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# Question Endpoints
def get_questions(request, document_id):
    """API endpoint for retrieving all questions for a document"""
    if request.method == 'GET':
        try:
            # Convert string to UUID
            doc_uuid = uuid.UUID(document_id)
            document = get_object_or_404(Document, document_id=doc_uuid)
            
            questions = Question.objects.filter(document=document)
            questions_data = []
            
            for question in questions:
                # Get the most recent answer for this question if any
                latest_answer = UserAnswer.objects.filter(question=question).first()
                
                questions_data.append({
                    'question_id': str(question.question_id),
                    'question_text': question.question_text,
                    'has_been_answered': latest_answer is not None,
                    'last_mark': latest_answer.mark if latest_answer else None
                })
            
            return JsonResponse({'questions': questions_data})
            
        except (ValueError, uuid.ValueError):
            return JsonResponse({'error': 'Invalid document ID format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_question(request, question_id):
    """API endpoint for retrieving a specific question with its explanation"""
    if request.method == 'GET':
        try:
            # Convert string to UUID
            q_uuid = uuid.UUID(question_id)
            question = get_object_or_404(Question, question_id=q_uuid)
            
            # Get all answers for this question
            answers = UserAnswer.objects.filter(question=question)
            answers_data = []
            
            for answer in answers:
                answers_data.append({
                    'answer_id': str(answer.answer_id),
                    'user_answer': answer.user_answer,
                    'mark': answer.mark,
                    'submitted_at': answer.submitted_at.isoformat()
                })
            
            return JsonResponse({
                'question_id': str(question.question_id),
                'document_id': str(question.document.document_id),
                'document_title': question.document.title or "Untitled Document",
                'question_text': question.question_text,
                'answer_explanation': question.answer_explanation,
                'user_answers': answers_data
            })
            
        except (ValueError, uuid.ValueError):
            return JsonResponse({'error': 'Invalid question ID format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# Answer Endpoints
@csrf_exempt
def submit_answer(request, question_id):
    """API endpoint for submitting an answer to a question"""
    if request.method == 'POST':
        try:
            # Convert string to UUID
            q_uuid = uuid.UUID(question_id)
            question = get_object_or_404(Question, question_id=q_uuid)
            
            # Get the answer from request body
            try:
                data = json.loads(request.body)
                user_answer = data.get('answer', '')
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON data'}, status=400)
            
            if not user_answer:
                return JsonResponse({'error': 'No answer provided'}, status=400)
            
            # Create the answer record
            answer = UserAnswer.objects.create(
                question=question,
                user_answer=user_answer
            )
            
            # Grade the answer
            graded_answer = grade_answer(answer.answer_id)
            
            return JsonResponse({
                'answer_id': str(graded_answer.answer_id),
                'mark': graded_answer.mark,
                'question_id': str(question.question_id)
            })
            
        except (ValueError, uuid.ValueError):
            return JsonResponse({'error': 'Invalid question ID format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_answer(request, answer_id):
    """API endpoint for retrieving a specific answer"""
    if request.method == 'GET':
        try:
            # Convert string to UUID
            a_uuid = uuid.UUID(answer_id)
            answer = get_object_or_404(UserAnswer, answer_id=a_uuid)
            question = answer.question
            
            return JsonResponse({
                'answer_id': str(answer.answer_id),
                'question_id': str(question.question_id),
                'question_text': question.question_text,
                'user_answer': answer.user_answer,
                'mark': answer.mark,
                'submitted_at': answer.submitted_at.isoformat(),
                'answer_explanation': question.answer_explanation
            })
            
        except (ValueError, uuid.ValueError):
            return JsonResponse({'error': 'Invalid answer ID format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)