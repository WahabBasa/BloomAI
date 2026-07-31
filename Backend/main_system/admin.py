from django.contrib import admin

from .models import Document, Question, UserAnswer


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'page_count', 'author', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('title', 'author')
    readonly_fields = ('document_id', 'uploaded_at')
    ordering = ('-uploaded_at',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'document', 'created_at')
    list_filter = ('created_at', 'document')
    search_fields = ('question_text', 'answer_explanation')
    readonly_fields = ('question_id', 'created_at')
    ordering = ('-created_at',)


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'mark', 'submitted_at')
    list_filter = ('mark', 'submitted_at')
    search_fields = ('user_answer', 'feedback')
    readonly_fields = ('answer_id', 'submitted_at')
