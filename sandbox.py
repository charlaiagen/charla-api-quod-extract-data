# %%
# from pdf_parsing import pdf_parser

# text = pdf_parser.extract_text_from_pdf("data/monark.pdf")

# print(text)
# %%
# ======================== Docling ========================= #
import logging
import time
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from pathlib import Path
import pandas as pd

# %%
pipeline_options = PdfPipelineOptions(do_table_structure=True)
pipeline_options.table_structure_options.do_cell_matching = False
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options
        )
    }
)

# %%
# source = "data/monark.pdf" # document per local path or URL
# converter = DocumentConverter()
# result = converter.convert(source)
# print(result.document.export_to_markdown())
# output: ## Docling Technical Report [...]"

# %%
def main():

    input_doc_path = Path("data/atradius.pdf")
    output_dir = Path("data/[OCR2]testes-atradius/")

    doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options
        )
    }
)

    start_time = time.time()

    conv_res = doc_converter.convert(input_doc_path)

    output_dir.mkdir(parents=True, exist_ok=True)

    doc_filename = conv_res.input.file.stem

    # Export tables
    for table_ix, table in enumerate(conv_res.document.tables):
        table_df: pd.DataFrame = table.export_to_dataframe()
        print(f"## Table {table_ix}")
        print(table_df.to_markdown())

        # Save the table as csv
        element_csv_filename = output_dir / f"{doc_filename}-table-{table_ix+1}.csv"
        print(f"Saving CSV table to {element_csv_filename}")
        table_df.to_csv(element_csv_filename)

        # Save the table as html
        element_html_filename = output_dir / f"{doc_filename}-table-{table_ix+1}.html"
        print(f"Saving HTML table to {element_html_filename}")
        with element_html_filename.open("w") as fp:
            fp.write(table.export_to_html())

    end_time = time.time() - start_time

#     _log.info(f"Document converted and tables exported in {end_time:.2f} seconds.")
# # %%
if __name__ == "__main__":
    main()

# %%
# import pdfplumber
#
# def extract_text_from_pdf(pdf_path, num_pages=None):
    # """Extracts text from a PDF file."""
    # text = ""
    # with pdfplumber.open(pdf_path) as reader:
        # pages_to_read = reader.pages[:num_pages+1] if num_pages else reader.pages
        # text = "".join(page.extract_text(layout=True) for page in pages_to_read)
#
    # return text
# %%
# text = extract_text_from_pdf("data/monark.pdf")
# %%
# print(text)
# %%
# text
# %%
from pdf_parsing import pdf_parser

# %%
text = pdf_parser.extract_text_from_pdf("data/monark.pdf")
# %%
print(text)
# %%
import PyPDF2

# %%
def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text
# %%
text = extract_text_from_pdf("data/monark.pdf")
print(text)
# %%
