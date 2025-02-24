import pdfplumber
import matplotlib.pyplot as plt
import numpy as np

def extract_tables_from_pdf(pdf_path, page_number=0):
    """
    Extract tables from a PDF file using pdfplumber
    
    Args:
        pdf_path: Path to the PDF file
        page_number: Page number to extract tables from (0-based index)
    Returns:
        List of extracted tables
    """
    with pdfplumber.open(pdf_path) as pdf:
        if page_number >= len(pdf.pages):
            raise ValueError(f"Page number {page_number} out of range. PDF has {len(pdf.pages)} pages.")
        
        page = pdf.pages[page_number]
        
        # Extract tables
        tables = page.extract_tables()
        
        # Get page dimensions for visualization
        width = float(page.width)
        height = float(page.height)
        
        # Get table bounding boxes for visualization
        table_bboxes = page.find_tables()
        
        return {
            'tables': tables,
            'bboxes': table_bboxes,
            'page_dims': (width, height)
        }

def visualize_tables(pdf_path, page_number=0):
    """
    Visualize detected tables in the PDF
    """
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number]
        
        # Convert page to image
        img = page.to_image()
        
        # Draw rectangles around tables
        tables = page.find_tables()
        for table in tables:
            img.draw_rect(table.bbox)
        
        # Show the image
        img.show()

def format_table(table):
    """
    Format a table for pretty printing
    """
    if not table:
        return "Empty table"
    
    # Calculate column widths
    col_widths = [max(len(str(cell)) for cell in col) for col in zip(*table)]
    
    # Format each row
    formatted_rows = []
    for row in table:
        formatted_row = " | ".join(
            str(cell).ljust(width) for cell, width in zip(row, col_widths)
        )
        formatted_rows.append(formatted_row)
    
    # Add separator line after header
    separator = "-" * len(formatted_rows[0])
    formatted_rows.insert(1, separator)
    
    return "\n".join(formatted_rows)

def process_pdf_tables(pdf_path, page_number=0):
    """
    Main function to process tables in a PDF
    
    Args:
        pdf_path: Path to the PDF file
        page_number: Page number to process (0-based index)
    """
    # Extract tables
    result = extract_tables_from_pdf(pdf_path, page_number)
    tables = result['tables']
    
    # Print tables
    print(f"Found {len(tables)} tables in page {page_number}")
    for i, table in enumerate(tables, 1):
        print(f"\nTable {i}:")
        print(format_table(table))
        print("\n" + "="*50 + "\n")
    
    # Visualize tables
    visualize_tables(pdf_path, page_number)
    
    return tables

if __name__ == "__main__":
    # Example usage
    pdf_path = "your_document.pdf"
    tables = process_pdf_tables(pdf_path)
