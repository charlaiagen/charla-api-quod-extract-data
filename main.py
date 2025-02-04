# %%
# --- Custom modules for the project --- #
from agents import generic_openai_agent as llm
from structured_output import output_classes as output
from pdf_parsing import pdf_parser

# --- Python modules --- #
import logfire # for debugging, logging and tracing results
import toml # for prompts
from pydantic_ai import Agent, RunContext # AI models and agents
from llmsherpa.readers import LayoutPDFReader

# --- Load the prompts --- #
prompts = toml.load("prompts/prompts.toml")

# %%
# --- Configure logfire --- #
logfire.configure()

# --- Build agents --- #
field_extraction_agent = Agent(
    model=llm.gpt_4o_mini,
    result_type=output.DocumentStructure,
    model_settings={
        "temperature": 0
    },
    system_prompt=prompts["system_prompts"]["extraction_agent_system_prompt"]
)

# %%
# --- Load the pdf file using character density parameters --- #
# text = pdf_parser.extract_text_with_custom_settings("data/Wibson_-_Balanco_2023.pdf")

# --- Load the pdf file using llmsherpa's LayoutPDFReader --- #
# llmsherpa_api_url = "http://localhost:5010/api/parseDocument?renderFormat=all"
# pdf_reader = LayoutPDFReader(llmsherpa_api_url)
# doc = pdf_reader.read_pdf("data/rominor.pdf")
# text = doc.to_text()

# --- Load the pdf file using pypdf --- #
pdf_path = "data/Wibson_-_Balanco_2023.pdf"
text = pdf_parser.extract_text_from_pdf_pypdf(pdf_path)

# %%
# --- Passes a dinamyc prompt to the agent, containing the extracted text --- #
@field_extraction_agent.system_prompt
def get_raw_text_from_pdf(ctx: RunContext[str]) -> str:
    return f"<raw-data>{ctx.deps}</raw-data>"

field_extraction = field_extraction_agent.run_sync("Realize as ações descritas.", deps=text)

logfire.notice("Field extraction result: {field_extraction}", field_extraction=dict(field_extraction.data))
logfire.info("Result type: {field_extraction}", field_extraction=type(field_extraction.data))
# %%
