import instructor
import openai
from pydantic import BaseModel, Field
from typing import List, Optional

from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase, SystemPromptGenerator


class PDFContentProvider(SystemPromptContextProviderBase):
    def __init__(self, title):
        super().__init__(title)
        self.content = None
        self.title = None
        self.page_count = None

    def get_info(self) -> str:
        return f'DOCUMENT TITLE: "{self.title}"\n\nDOCUMENT CONTENT: "{self.content}"\n\nPAGE COUNT: {self.page_count}'


class ActiveRecallQuestionInputSchema(BaseIOSchema):
    """Input schema for the ActiveRecallQuestionGenerator agent."""
    
    document_id: str = Field(..., description="Identifier for the document to generate questions from")
    question_count: Optional[int] = Field(5, description="Number of questions to generate")


class ActiveRecallQuestionOutputSchema(BaseIOSchema):
    """Output schema containing only generated active recall questions in markdown format."""
    
    questions: List[str] = Field(..., description="List of generated active recall questions in markdown format")


# Create the content provider
pdf_content_provider = PDFContentProvider(title="PDF Document Content")

# Create the active recall question generator agent
active_recall_agent = BaseAgent(
    config=BaseAgentConfig(
        client=instructor.from_openai(openai.OpenAI()),
        model="gpt-4o-mini",
        system_prompt_generator=SystemPromptGenerator(
            background=[
                "This Assistant is an expert at generating effective active recall questions from educational content.",
                "It understands how to identify key concepts and create questions that promote deep learning and memory retention.",
                "It specializes in creating questions that force learners to retrieve information from memory, strengthening neural pathways."
            ],
            steps=[
                "Carefully analyze the document content to identify key concepts, facts, and relationships.",
                "Create questions that require recall of important information and understanding of relationships between concepts.",
                "Format each question in markdown for clear presentation."
            ],
            output_instructions=[
                "Generate the specified number of active recall questions.",
                "Format all questions in markdown.",
                "Do not include answers, difficulty levels, or concept identifiers.",
                "Ensure questions cover the most important aspects of the content."
            ],
            context_providers={"pdf_content": pdf_content_provider},
        ),
        input_schema=ActiveRecallQuestionInputSchema,
        output_schema=ActiveRecallQuestionOutputSchema,
    )
)