from django.db import models
import uuid

class Document(models.Model):
    """Model for storing information about uploaded documents"""
    document_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.CharField(max_length=255)
    content = models.TextField()
    page_count = models.IntegerField(default=0)
    author = models.CharField(max_length=255, blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Document {self.document_id}"

class Question(models.Model):
    """Model for storing questions generated from documents"""
    question_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    answer_explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question {self.question_id}"

class UserAnswer(models.Model):
    """Model for storing user answers to questions"""
    answer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_answers')
    user_answer = models.TextField()
    mark = models.IntegerField(null=True, blank=True)  # 0, 50, or 100
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer for {self.question}"

    class Meta:
        ordering = ['-submitted_at']
