from pydantic import BaseModel, Field
from typing import Optional, List
import json
import os
import uuid

class QuestionItem(BaseModel):
    """
    Represents a single question with its answer explanation, user response, and mark.
    This serves as the data interface between backend and frontend.
    """
    
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for this question")
    question_text: str = Field(..., description="The text of the active recall question")
    answer_explanation: str = Field(..., description="Detailed explanation of the correct answer")
    source_content: str = Field("", description="The extracted PDF content that this question is based on")
    user_answer: Optional[str] = Field(None, description="The answer provided by the user")
    mark: Optional[int] = Field(None, description="Numerical evaluation of the user's answer (0-100)")
    
    def to_dict(self):
        """Convert to a dictionary for frontend consumption or storage"""
        return {
            "questionId": self.question_id,
            "question": self.question_text,
            "explanation": self.answer_explanation,
            "sourceContent": self.source_content,
            "userAnswer": self.user_answer,
            "mark": self.mark
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from a dictionary (from frontend or storage)"""
        return cls(
            question_id=data.get("questionId", str(uuid.uuid4())),
            question_text=data.get("question", ""),
            answer_explanation=data.get("explanation", ""),
            source_content=data.get("sourceContent", ""),
            user_answer=data.get("userAnswer"),
            mark=data.get("mark")
        )


class QuestionStore:
    """
    Simple storage mechanism for question items.
    """
    
    def __init__(self, storage_dir: str = "data/questions"):
        """Initialize with a storage directory"""
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def save_question(self, question: QuestionItem) -> bool:
        """Save a question to storage"""
        try:
            file_path = os.path.join(self.storage_dir, f"{question.question_id}.json")
            
            with open(file_path, 'w') as file:
                json.dump(question.to_dict(), file, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving question: {str(e)}")
            return False
    
    def load_question(self, question_id: str) -> Optional[QuestionItem]:
        """Load a question from storage"""
        try:
            file_path = os.path.join(self.storage_dir, f"{question_id}.json")
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r') as file:
                data = json.load(file)
            
            return QuestionItem.from_dict(data)
        except Exception as e:
            print(f"Error loading question: {str(e)}")
            return None
    
    def save_questions(self, questions: List[QuestionItem]) -> bool:
        """Save multiple questions at once"""
        success = True
        for question in questions:
            if not self.save_question(question):
                success = False
        return success
    
    def get_all_questions(self) -> List[QuestionItem]:
        """Get all stored questions"""
        questions = []
        
        try:
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json'):
                    question_id = filename.replace('.json', '')
                    question = self.load_question(question_id)
                    if question:
                        questions.append(question)
        except Exception as e:
            print(f"Error listing questions: {str(e)}")
        
        return questions
    
    def update_user_answer(self, question_id: str, answer: str) -> bool:
        """Update a user's answer for a question"""
        question = self.load_question(question_id)
        if not question:
            return False
        
        question.user_answer = answer
        return self.save_question(question)
    
    def update_mark(self, question_id: str, mark: int) -> bool:
        """Update the mark for a question"""
        question = self.load_question(question_id)
        if not question or not (0 <= mark <= 100):
            return False
        
        question.mark = mark
        return self.save_question(question)
    
    def delete_question(self, question_id: str) -> bool:
        """Delete a question"""
        try:
            file_path = os.path.join(self.storage_dir, f"{question_id}.json")
            
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            
            return False
        except Exception as e:
            print(f"Error deleting question: {str(e)}")
            return False