"""Agent that writes an explanation for each generated question.

Like the question generator, this is built per request rather than shared, so
its memory starts empty every time. See `qgen_agent` for why that matters.

The document text is supplied once, through the context provider. It used to
be sent a second time as an input-schema field, which doubled the token cost
of the single largest payload in the pipeline for no benefit.
"""

from typing import List

from pydantic import Field

from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import (
    SystemPromptContextProviderBase,
    SystemPromptGenerator,
)

from main_system.agents.llm_client import get_client


class DocumentContentProvider(SystemPromptContextProviderBase):
    """Supplies the source document to the answer generator's system prompt."""

    def __init__(self, document_content: str, document_title: str):
        super().__init__("Source Document")
        self.document_content = document_content
        self.document_title = document_title

    def get_info(self) -> str:
        return (
            f'DOCUMENT TITLE: "{self.document_title}"\n\n'
            f'DOCUMENT CONTENT: "{self.document_content}"'
        )


class AnswerGeneratorInputSchema(BaseIOSchema):
    """Input schema for the AnswerGenerator agent."""

    questions: List[str] = Field(
        ...,
        description="Questions that need explanations. Explanations must be returned in this same order.",
    )


class AnswerGeneratorOutputSchema(BaseIOSchema):
    """Output schema containing generated answer explanations in the same order as the input questions."""

    explanations: List[str] = Field(
        ...,
        description="List of detailed answer explanations including both the correct answer and reasoning for why it's correct",
    )


def build_answer_agent(document_content: str, document_title: str) -> BaseAgent:
    """Build an answer generator scoped to one document.

    Args:
        document_content: The document's extracted text.
        document_title: Title shown to the model for context.

    Returns:
        A `BaseAgent` with empty memory and its own context provider.
    """
    return BaseAgent(
        config=BaseAgentConfig(
            client=get_client(),
            model="gpt-4o-mini",
            system_prompt_generator=SystemPromptGenerator(
                background=[
                    "This Assistant is an expert at generating comprehensive explanations for active recall questions.",
                    "It not only provides the correct answer but also thoroughly explains WHY that answer is correct.",
                    "It analyzes educational content to find accurate answers and creates detailed, educational explanations.",
                    "It understands how to identify key concepts in source material and connect them to specific questions.",
                ],
                steps=[
                    "Carefully analyze each question to understand what information is being requested.",
                    "Search the source document content to locate the relevant information for each question.",
                    "Identify the correct answer based on the source material.",
                    "Formulate a clear, educational explanation that provides the correct answer AND explains in detail why this is the correct answer.",
                    "Include supporting evidence from the source material that justifies why this answer is correct.",
                    "Ensure each explanation helps the learner understand the underlying concepts, not just memorize facts.",
                ],
                output_instructions=[
                    "Return exactly one explanation per question, in the same order the questions were provided.",
                    "Each explanation must include both the correct answer AND reasoning for why that answer is correct.",
                    "Make the justification for the correct answer clear and explicit in each explanation.",
                    "Format all explanations in clear, concise language appropriate for educational purposes.",
                    "Base all explanations directly on information found in the source document.",
                    "Ensure explanations reinforce conceptual understanding, not just factual recall.",
                ],
                context_providers={
                    "source_document": DocumentContentProvider(
                        document_content=document_content,
                        document_title=document_title,
                    )
                },
            ),
            input_schema=AnswerGeneratorInputSchema,
            output_schema=AnswerGeneratorOutputSchema,
        )
    )
