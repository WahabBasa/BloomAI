import instructor
import openai
from pydantic import BaseModel, Field
from typing import Optional, Literal

from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase, SystemPromptGenerator


class GradingContextProvider(SystemPromptContextProviderBase):
    def __init__(self, title):
        super().__init__(title)
        self.question = None
        self.explanation = None
        self.user_answer = None

    def get_info(self) -> str:
        return f'QUESTION: "{self.question}"\n\nEXPLANATION: "{self.explanation}"\n\nUSER ANSWER: "{self.user_answer}"'


class GradingInputSchema(BaseIOSchema):
    """Input schema for the GradingAgent."""
    
    question: str = Field(..., description="The active recall question text")
    explanation: str = Field(..., description="The correct answer explanation")
    user_answer: str = Field(..., description="The user's submitted answer")


class GradingOutputSchema(BaseIOSchema):
    """Output schema containing only the grade for the user's answer."""
    
    score: Literal[0, 0.5, 1] = Field(..., description="Score for the answer: 0 (incorrect), 0.5 (partially correct), or 1 (fully correct)")
    markdown_score: str = Field(..., description="The score formatted as markdown (e.g., '## Score: 0.5')")


# Create the grading context provider
grading_context_provider = GradingContextProvider(title="Grading Context")

# Create the grading agent
grading_agent = BaseAgent(
    config=BaseAgentConfig(
        client=instructor.from_openai(openai.OpenAI()),
        model="gpt-4o-mini",
        system_prompt_generator=SystemPromptGenerator(
            background=[
                "This Assistant is an expert at evaluating learning responses against reference explanations.",
                "It understands how to identify key concepts in both the reference explanation and user responses.",
                "It excels at determining whether a user has demonstrated understanding of the correct answer.",
                "It provides fair and objective assessment focusing on conceptual understanding rather than exact wording."
            ],
            steps=[
                "Carefully analyze the question to understand what knowledge is being tested.",
                "Identify the key concepts in the reference explanation that constitute a correct answer.",
                "Compare the user's answer against these key concepts to determine understanding.",
                "Assign a score: 0 (incorrect), 0.5 (partially correct), or 1 (fully correct).",
                "Provide brief, constructive feedback explaining the score."
            ],
            output_instructions=[
                "Assign only scores of 0, 0.5, or 1.",
                "0: The answer misses the key concepts or is fundamentally incorrect.",
                "0.5: The answer shows partial understanding but misses some key concepts.",
                "1: The answer demonstrates full understanding of the key concepts.",
                "Evaluate based on conceptual understanding, not exact wording.",
                "Format the score as markdown using '## Score: X' format."
            ],
            context_providers={"grading_context": grading_context_provider},
        ),
        input_schema=GradingInputSchema,
        output_schema=GradingOutputSchema,
    )
)