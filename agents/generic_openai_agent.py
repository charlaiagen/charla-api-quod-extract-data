# --- Imports --- #
import os
from dotenv import load_dotenv

from openai import AsyncAzureOpenAI # in order to use Azure OpenAI API we must use the AsyncAzureOpenAI class
from pydantic_ai.models.openai import OpenAIModel

# --- Load Environment Variables --- #
load_dotenv()

# --- Azure OpenAI Config --- #
client = AsyncAzureOpenAI(
    api_key=os.getenv('AZURE_OPENAI_API_KEY'),
    api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
    azure_endpoint=os.getenv('AZURE_ENDPOINT'),
)

# --- Models --- #
gpt_4o_mini = OpenAIModel(
    'gpt-4o-mini',
    openai_client=client
    )
gpt_4o = OpenAIModel(
    'gpt-4o',
    openai_client=client
    )

# class Calculation(BaseModel):
#     """Captures the result of a calculation"""
#     result: int

# # --- 4o-mini generic agent --- #
# agent_4o_mini = Agent(model=gpt_4o_mini, result_type=Calculation)

# # --- 4o generic agent --- #
# agent_4o = Agent(model=gpt_4o)

# # --- Test call --- #
# result = agent_4o_mini.run_sync("What is 100 + 300")

# logfire.notice('Output from LLM: {result}', result = str(result.data))
# logfire.info('Result type: {result}', result = type(result.data))
# logfire.info('Result: {result}', result = result.data.result)