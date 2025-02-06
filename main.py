# --- Custom modules for the project --- #
from agents import generic_openai_agent as llm # Declares the OpenAI models that the agents will use
from structured_output import output_classes as output # Declares the output classes that the agents will return
from pdf_parsing import pdf_parser # Declares the pdf parsing functions to extract raw text from pdf files

# --- Python modules --- #
import logfire # for debugging, logging and tracing results
import toml # for prompts
from pydantic_ai import Agent, RunContext # AI models and agents

# --- Load the prompts --- #
prompts = toml.load("prompts/prompts.toml")

# --- Configure logfire --- #
logfire.configure()

# --- Build agents --- #
# Agent to extract the fields from the pdf file. The result (result_type) is a DocumentStructure object, which is a structured representation of the fields we want to extract.
# The system_prompt refers to the prompt that the agent will use to generate the fields.
# This agent will later receive a dynamic system prompt, which will contain the extracted raw text from the pdf file (refer to @field_extraction_agent.system_prompt)
field_extraction_agent = Agent(
    model=llm.gpt_4o,
    result_type=output.DocumentStructure,
    model_settings={
        "temperature": 0
    },
    system_prompt=prompts["system_prompts"]["extraction_agent_system_prompt"]
)

# Agent to write the code that builds a pd.DataFrame from the extracted fields.
# The result (result_type) is a string, which is the Python code that builds the DataFrame.
# The system prompt refers to the prompt that the agent will use to generate the code. #TODO: Put this prompt in prompts.toml
# This agent will later receive a dynamic system prompt, which will contain the extracted fields (refer to @df_building_agent.system_prompt).
df_building_agent = Agent(
    model=llm.gpt_4o,
    result_type=str,
    model_settings={
        "temperature": 0
    },
    system_prompt=(
        """
        Elabore um código em Python que construa um pd.DataFrame a partir dos dados fornecidos.
        Escreva somente a importação das bibliotecas, a declaração de variáveis, a função de construção
        do DataFrame e a chamada da função. Caso inclua explicações, faça-o em comentários.
        """
    )

)

# --- Load the pdf file using pypdf --- #
pdf_path = "data/atradius.pdf"
text = pdf_parser.extract_text_from_pdf_pypdf(pdf_path)

# --- Dynamic System Prompts --- #
# Passes a dynamic prompt to the agent, containing the extracted text from the pdf file.
@field_extraction_agent.system_prompt
def get_raw_text_from_pdf(ctx: RunContext[str]) -> str:
    return f"<raw-data>{ctx.deps}</raw-data>"

# Passes a dynamic system prompt to the agent, containing the extracted fields from the pdf file.
@df_building_agent.system_prompt
def get_results_from_field_extraction(ctx: RunContext[output.DocumentStructure]) -> str:
    return f"<field-extraction>{ctx.deps}</field-extraction>"

# --- Run the agents --- #
field_extraction = field_extraction_agent.run_sync(
    """
    Analise o texto fornecido e extraia
    os dados conforme a instrução passada.
    """,
    deps=text
    )

df_building_code = df_building_agent.run_sync(
    "Execute a tarefa de construção do DataFrame.",
    deps=field_extraction.data
    )

# --- Logging the results --- #
# Logs the field extraction result
logfire.notice(
    "Field extraction result: {field_extraction}",
    field_extraction=dict(field_extraction.data)
    )
# Logs the type of the field extraction result
logfire.info(
    "Result type: {field_extraction}",
    field_extraction=type(field_extraction.data)
    )
# Logs the code generation result - a Python code that builds a pd.DataFrame from the extracted data
logfire.notice(
    "Code generation result: {df_building_code}",
    df_building_code=str(df_building_code.data)
)
# Logs the type of the code generation result - should be a string #TODO: check if there's a better data type to store code.
logfire.info(
    "Code generation result type: {df_building_code}",
    df_building_code=type(df_building_code.data)
)