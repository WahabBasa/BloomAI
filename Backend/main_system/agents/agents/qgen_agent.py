"""Agent that turns a document's text into active recall questions.

The agent is built per request. It used to be a module-level singleton, which
meant its `AgentMemory` was never cleared: every previous document's text and
questions were replayed to the model on the next call, so token cost grew with
process uptime, later documents were answered in the shadow of earlier ones,
and two simultaneous uploads raced each other on one shared, mutable context
provider.
"""

from typing import List

from pydantic import Field

from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import (
    SystemPromptContextProviderBase,
    SystemPromptGenerator,
)

from main_system.agents.llm_client import get_client


class PDFContentProvider(SystemPromptContextProviderBase):
    """Supplies the source document to the question generator's system prompt."""

    def __init__(self, content: str, document_title: str, page_count: int):
        # The base class's `title` is the heading this block gets in the system
        # prompt, not the document's title -- those were previously conflated.
        super().__init__("PDF Document Content")
        self.content = content
        self.document_title = document_title
        self.page_count = page_count

    def get_info(self) -> str:
        return (
            f'DOCUMENT TITLE: "{self.document_title}"\n\n'
            f'DOCUMENT CONTENT: "{self.content}"\n\n'
            f"PAGE COUNT: {self.page_count}"
        )


class ActiveRecallQuestionInputSchema(BaseIOSchema):
    """Input schema for the ActiveRecallQuestionGenerator agent."""

    question_count: int = Field(5, description="Number of questions to generate")


class ActiveRecallQuestionOutputSchema(BaseIOSchema):
    """Output schema containing only generated active recall questions in markdown format."""

    questions: List[str] = Field(..., description="List of generated active recall questions in markdown format")


def build_question_agent(content: str, document_title: str, page_count: int) -> BaseAgent:
    """Build a question generator scoped to one document.

    Args:
        content: The document's extracted text.
        document_title: Title shown to the model for context.
        page_count: Page count shown to the model for context.

    Returns:
        A `BaseAgent` with empty memory and its own context provider.
    """
    return BaseAgent(
        config=BaseAgentConfig(
            client=get_client(),
            model="gpt-4o-mini",
            system_prompt_generator=SystemPromptGenerator(
                background=[
                    "This Assistant is an expert at generating effective active recall questions from educational content.",
                    "It understands how to identify key concepts and create questions that promote deep learning and memory retention.",
                    "It specializes in creating questions that force learners to retrieve information from memory, strengthening neural pathways.",
                ],
                steps=[
                    "Carefully analyze the document content to identify key concepts, facts, and relationships.",
                    "Create questions that require recall of important information and understanding of relationships between concepts.",
                    "Format each question in markdown for clear presentation.",
                ],
                output_instructions=[
                    "Generate exactly the requested number of active recall questions.",
                    "Format all questions in markdown.",
                    "Do not include answers, difficulty levels, or concept identifiers.",
                    "Ensure questions cover the most important aspects of the content.",
                ],
                context_providers={
                    "pdf_content": PDFContentProvider(
                        content=content,
                        document_title=document_title,
                        page_count=page_count,
                    )
                },
            ),
            input_schema=ActiveRecallQuestionInputSchema,
            output_schema=ActiveRecallQuestionOutputSchema,
        )
    )
