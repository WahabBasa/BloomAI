import os
import instructor
import openai
from dotenv import load_dotenv


from rich.console import Console
from rich.text import Text

from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseAgentInputSchema, BaseAgentOutputSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator

console = Console()



load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
client = instructor.from_openai(openai.OpenAI(api_key=API_KEY))

system_prompt_generator_custom = SystemPromptGenerator(
    background=["You are a helpfull assistant that will generate active recall questions based on the lowest level of blooms Taxonomy"],
    steps=[
        "Analyze the user's topic from which they want questions to be generated and focus on just the relevant information need at the lowest level of blooms taxonomy",
        "After Identifying on the relveant information for the lowest level procced to generate exaclty 5 medium level active recall quesitons based on them",
    
    ],
    output_instructions=["Your output should be questions that are numbered."]

)

agent = BaseAgent(
    config=BaseAgentConfig(
        client=client,
        model="gpt-4o-mini",
        system_prompt_generator=system_prompt_generator_custom
    )
)

initial_message = "Hello, how can I help you today?"
agent.memory.add_message("assistant", content=BaseAgentInputSchema(chat_message=initial_message))

console.print(Text(f"Assistant: {initial_message}", style="bold green"))

while True:
    
    user_input = console.input("You: ")

    response = agent.run(BaseAgentInputSchema(chat_message=user_input))

    console.print(Text(f"Assistant: {response.chat_message}", style="bold green"))