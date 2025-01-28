# --- Imports --- #
import io
import fitz
import pdfplumber
import PyPDF2
import pytesseract
from typing import List
from dataclasses import dataclass

from PIL import Image

# --- PDF OCR --- #
def pdf_ocr(pdf_path, num_pages=None):
    """Extracts text from a PDF file using OCR."""
    with fitz.open(pdf_path) as pdf_document:
        ocr_text = ""

        if not num_pages:
            num_pages = pdf_document.page_count

        for page_num in range(num_pages):
            # Select page
            page = pdf_document.load_page(page_num)

            # Render page as image
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))

            # Apply OCR
            ocr_text += pytesseract.image_to_string(img, lang='por') + "\n"

# --- PDF Reader --- #
def extract_text_from_pdf_pdf_plumber(pdf_path, num_pages=None):
    """Extracts text from a PDF file."""
    text = ""
    with pdfplumber.open(pdf_path) as reader:
        pages_to_read = reader.pages[:num_pages+1] if num_pages else reader.pages
        text = "".join(page.extract_text(layout=False) for page in pages_to_read)

    if not text:
        text = pdf_ocr(pdf_path, num_pages)

    return text

def extract_text_with_custom_settings(pdf_path):
    with pdfplumber.open(pdf_path) as reader:
        text = ""
        for page in reader.pages:
            text += page.extract_text(
                x_tolerance=3,
                y_tolerance=1.2,
                layout=True,
                keep_blank_chars=True,
            )
    return text

def extract_tables(pdf_path):
    with pdfplumber.open(pdf_path) as reader:
        all_tables = []
        for page in reader.pages:
            tables = page.extract_tables(
                table_settings={
                    "vertical_strategy": "text",
                    "horizontal_strategy": "text",
                    "intersection_y_tolerance": 10,
                    "intersection_x_tolerance": 10,
                }
            )
            all_tables.extend(tables)
    return all_tables

def extract_with_section_markers(pdf_path):
    with pdfplumber.open(pdf_path) as reader:
        text = ""
        for page in reader.pages:
            # Get page dimensions
            width = page.width

            # Extract words with position information
            words = page.extract_words(
                keep_blank_chars=True,
                x_tolerance=3,
                y_tolerance=3,
            )

            current_line_y = words[0]['top'] if words else 0
            line_text = ""

            for word in words:
                # If we're on a new line
                if abs(word['top'] - current_line_y) > 5: # adjust tolerance as needed
                    text += line_text + "\n"
                    line_text = ""
                    current_line_y = word['top']

                # Add position marker
                position = "LEFT" if word['x0'] < (width / 2) else "RIGHT"
                line_text += f"[{position}]{word['text']}"

            text += line_text + "\n"

    return text

# --- PDF Reader PyPDF2 --- #
def extract_text_from_pdf_pypdf2(pdf_path):
    reader = PyPDF2.PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text