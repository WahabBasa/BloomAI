"""
URL configuration for recall_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from main_system import views

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # Document Management Endpoints
    path('api/documents/', views.get_documents, name='get_documents'),
    path('api/documents/upload/', views.upload_document, name='upload_document'),
    path('api/documents/<str:document_id>/', views.get_document, name='get_document'),
    
    # Question Endpoints
    path('api/documents/<str:document_id>/questions/', views.get_questions, name='get_questions'),
    path('api/questions/<str:question_id>/', views.get_question, name='get_question'),
    
    # Answer Endpoints
    path('api/questions/<str:question_id>/answer/', views.submit_answer, name='submit_answer'),
    path('api/answers/<str:answer_id>/', views.get_answer, name='get_answer'),
]