import pdfplumber
from PIL import Image
import io

def pdf_page_to_image(pdf_path, page_number=0, resolution=200):
    """
    Convert a PDF page to a PIL Image object stored in memory
    
    Args:
        pdf_path (str): Path to the PDF file
        page_number (int): Page number to convert (0-based index)
        resolution (int): Resolution of the output image in DPI
        
    Returns:
        PIL.Image: Image object of the PDF page
    """
    with pdfplumber.open(pdf_path) as pdf:
        if page_number >= len(pdf.pages):
            raise ValueError(f"Page number {page_number} out of range. PDF has {len(pdf.pages)} pages.")
        
        # Get the specified page
        page = pdf.pages[page_number]
        
        # Convert to image
        img = page.to_image(resolution=resolution)
        
        # Get the PIL Image object directly from the PageImage object
        return img.original

# Example usage:
if __name__ == "__main__":
    # Replace with your PDF path
    pdf_path = "example.pdf"
    try:
        # Convert first page to image
        image = pdf_page_to_image(pdf_path)
        print(f"Successfully converted PDF page to image. Image size: {image.size}")
        
        # You can now use the image object directly without saving to file
        # If you want to save it, you can use:
        # image.save("output.png")
        
    except Exception as e:
        print(f"Error converting PDF: {str(e)}")
