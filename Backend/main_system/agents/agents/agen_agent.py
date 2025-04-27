import instructor
import openai
from pydantic import BaseModel, Field
from typing import List, Optional

from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase, SystemPromptGenerator


class ContentAndQuestionsProvider(SystemPromptContextProviderBase):
    def __init__(self, title="Document Content and Questions"):
        super().__init__(title)
        self.document_content = None
        self.questions = None

    def get_info(self) -> str:
        questions_text = "\n".join([f"Question {i+1}: {q}" for i, q in enumerate(self.questions)])
        return f'DOCUMENT CONTENT: "{self.document_content}"\n\nQUESTIONS TO ANSWER:\n{questions_text}'


class AnswerGeneratorInputSchema(BaseIOSchema):
    """Input schema for the AnswerGenerator agent."""
    
    document_content: str = Field(..., description="The extracted text content from the source document")
    questions: List[str] = Field(..., description="List of questions that need explanations")
    document_title: Optional[str] = Field(None, description="Title of the source document if available")


class AnswerGeneratorOutputSchema(BaseIOSchema):
    """Output schema containing generated answer explanations in the same order as the input questions."""
    
    explanations: List[str] = Field(..., description="List of detailed answer explanations including both the correct answer and reasoning for why it's correct")


# Create the content provider
content_provider = ContentAndQuestionsProvider()

# Create the answer generator agent
answer_generator_agent = BaseAgent(
    config=BaseAgentConfig(
        client=instructor.from_openai(openai.OpenAI()),
        model="gpt-4o-mini",
        system_prompt_generator=SystemPromptGenerator(
            background=[
                "This Assistant is an expert at generating comprehensive explanations for active recall questions.",
                "It not only provides the correct answer but also thoroughly explains WHY that answer is correct.",
                "It analyzes educational content to find accurate answers and creates detailed, educational explanations.",
                "It understands how to identify key concepts in source material and connect them to specific questions."
            ],
            steps=[
                "Carefully analyze each question to understand what information is being requested.",
                "Search the source document content to locate the relevant information for each question.",
                "Identify the correct answer based on the source material.",
                "Formulate a clear, educational explanation that provides the correct answer AND explains in detail why this is the correct answer.",
                "Include supporting evidence from the source material that justifies why this answer is correct.",
                "Ensure each explanation helps the learner understand the underlying concepts, not just memorize facts."
            ],
            output_instructions=[
                "Generate explanations for each provided question in the same order as the questions were provided.",
                "Each explanation must include both the correct answer AND reasoning for why that answer is correct.",
                "Make the justification for the correct answer clear and explicit in each explanation.",
                "Format all explanations in clear, concise language appropriate for educational purposes.",
                "Base all explanations directly on information found in the source document.",
                "Ensure explanations reinforce conceptual understanding, not just factual recall."
            ],
            context_providers={"content_and_questions": content_provider},
        ),
        input_schema=AnswerGeneratorInputSchema,
        output_schema=AnswerGeneratorOutputSchema,
    )
)