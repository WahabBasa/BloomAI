import os
import instructor
import openai
from dotenv import load_dotenv

from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseAgentInputSchema

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

client = instructor.from_openai(openai.OpenAI(api_key=API_KEY))

agent = BaseAgent(config=BaseAgentConfig(client=client, model="gpt-4o-mini"))

response = agent.run(BaseAgentInputSchema(chat_message="Wus good cus?"))

print(response)