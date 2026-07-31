"""Agent that grades a learner's answer against the reference explanation.

Built per request. As a module-level singleton it accumulated every previously
graded question and answer in memory and replayed them on the next grading
call, and its single mutable context provider was overwritten by whichever
request got there last.
"""

from typing import Literal

from pydantic import Field

from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import (
    SystemPromptContextProviderBase,
    SystemPromptGenerator,
)

from main_system.agents.llm_client import get_client


class GradingContextProvider(SystemPromptContextProviderBase):
    """Supplies the question, reference explanation and user answer being graded."""

    def __init__(self, question: str, explanation: str, user_answer: str):
        super().__init__("Grading Context")
        self.question = question
        self.explanation = explanation
        self.user_answer = user_answer

    def get_info(self) -> str:
        return (
            f'QUESTION: "{self.question}"\n\n'
            f'EXPLANATION: "{self.explanation}"\n\n'
            f'USER ANSWER: "{self.user_answer}"'
        )


class GradingInputSchema(BaseIOSchema):
    """Input schema for the GradingAgent."""

    question: str = Field(..., description="The active recall question text")
    explanation: str = Field(..., description="The correct answer explanation")
    user_answer: str = Field(..., description="The user's submitted answer")


class GradingOutputSchema(BaseIOSchema):
    """Output schema containing the grade and the feedback that justifies it."""

    score: Literal[0, 0.5, 1] = Field(
        ...,
        description="Score for the answer: 0 (incorrect), 0.5 (partially correct), or 1 (fully correct)",
    )
    feedback: str = Field(
        ...,
        description=(
            "Brief constructive feedback addressed to the learner, naming what the answer got right "
            "and which key concepts it missed"
        ),
    )


def build_grading_agent(question: str, explanation: str, user_answer: str) -> BaseAgent:
    """Build a grader scoped to one submitted answer.

    Args:
        question: The question being answered.
        explanation: The reference explanation to grade against.
        user_answer: What the learner wrote.

    Returns:
        A `BaseAgent` with empty memory and its own context provider.
    """
    return BaseAgent(
        config=BaseAgentConfig(
            client=get_client(),
            model="gpt-4o-mini",
            system_prompt_generator=SystemPromptGenerator(
                background=[
                    "This Assistant is an expert at evaluating learning responses against reference explanations.",
                    "It understands how to identify key concepts in both the reference explanation and user responses.",
                    "It excels at determining whether a user has demonstrated understanding of the correct answer.",
                    "It provides fair and objective assessment focusing on conceptual understanding rather than exact wording.",
                ],
                steps=[
                    "Carefully analyze the question to understand what knowledge is being tested.",
                    "Identify the key concepts in the reference explanation that constitute a correct answer.",
                    "Compare the user's answer against these key concepts to determine understanding.",
                    "Assign a score: 0 (incorrect), 0.5 (partially correct), or 1 (fully correct).",
                    "Write brief, constructive feedback explaining the score.",
                ],
                output_instructions=[
                    "Assign only scores of 0, 0.5, or 1.",
                    "0: The answer misses the key concepts or is fundamentally incorrect.",
                    "0.5: The answer shows partial understanding but misses some key concepts.",
                    "1: The answer demonstrates full understanding of the key concepts.",
                    "Evaluate based on conceptual understanding, not exact wording.",
                    "Address the feedback to the learner, keep it to two or three sentences, and make it "
                    "specific about what was correct and what was missing.",
                ],
                context_providers={
                    "grading_context": GradingContextProvider(
                        question=question,
                        explanation=explanation,
                        user_answer=user_answer,
                    )
                },
            ),
            input_schema=GradingInputSchema,
            output_schema=GradingOutputSchema,
        )
    )
