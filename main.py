# %%
# --- Custom modules for the project --- #
from agents import generic_openai_agent as llm
from structured_output import output_classes as output
from pdf_parsing import pdf_parser

# --- Python modules --- #
import logfire # for debugging, logging and tracing results
import toml # for prompts
from pydantic_ai import Agent # AI models and agents
from llmsherpa.readers import LayoutPDFReader

# --- Load the prompts --- #
prompts = toml.load("prompts/prompts.toml")

# %%
# --- Configure logfire --- #
logfire.configure()

# --- Build agents --- #
field_extraction_agent = Agent(
    model=llm.gpt_4o,
    result_type=output.DocumentStructure,
    model_settings={
        "temperature": 0
    }
)

# %%
# --- Load the pdf file using character density parameters --- #
# text = pdf_parser.extract_text_with_custom_settings("data/Wibson_-_Balanco_2023.pdf")

# --- Load the pdf file using llmsherpa's LayoutPDFReader --- #
llmsherpa_api_url = "http://localhost:5010/api/parseDocument?renderFormat=all"
pdf_reader = LayoutPDFReader(llmsherpa_api_url)
doc = pdf_reader.read_pdf("data/rominor.pdf")
text = doc.to_text()

# %%
ppt = prompts["field_extraction"]["field_extraction"].format(text=text)
field_extraction = field_extraction_agent.run_sync(ppt)

logfire.notice("Field extraction result: {field_extraction}", field_extraction=dict(field_extraction.data))
logfire.info("Result type: {field_extraction}", field_extraction=type(field_extraction.data))
# %%
