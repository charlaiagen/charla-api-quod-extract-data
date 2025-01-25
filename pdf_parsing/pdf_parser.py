# --- Imports --- #
import io
import fitz
import pdfplumber
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
def extract_text_from_pdf(pdf_path, num_pages=None):
    """Extracts text from a PDF file."""
    text = ""
    with pdfplumber.open(pdf_path) as reader:
        pages_to_read = reader.pages[:num_pages+1] if num_pages else reader.pages
        text = "".join(page.extract_text(layout=True) for page in pages_to_read)

    if not text:
        text = pdf_ocr(pdf_path, num_pages)

    return text