# --- Imports --- #
import pdfplumber
import numpy as np
from PIL import Image, ImageDraw
import io
import os

# --- Functions --- #
def create_overlapping_quadrants_from_pdf(pdf_path, page_num=0, overlap_percent=20, dpi=300):
    """
    Extracts a page from a PDF and divides it into four quadrants with specified percentage overlap.

    Args:
        pdf_path (str): Path to the input PDF
        page_num (int): Page number to extract (0-indexed)
        overlap_percent (float): Percentage of overlap between quadrants (0-100)
        dpi (int): Resolution for rendering the PDF page

    Returns:
        tuple: (list of quadrant images as PIL Images, original page as PIL Image)
    """
    # Open the PDF
    with pdfplumber.open(pdf_path) as pdf:
        if page_num >= len(pdf.pages):
            raise ValueError(f"Page {page_num} doesn't exist in the PDF. Total page: {len(pdf.pages)}")

        # Get the specified page
        page = pdf.pages[page_num]

        # Render the page to an image
        image = page.to_image(resolution=dpi)
        page_image = image.original

        # Get image dimensions
        width, height = page_image.size

        # Calculate the center points
        center_x = width // 2
        center_y = height // 2

        #Calculate overlap in pixels
        overlap_x = int(width * (overlap_percent / 100))
        overlap_y = int(height * (overlap_percent / 100))

        # Define quadrant boundaries with overlap
        # Q1 (top-left)
        tl_x1, tl_y1 = 0, 0
        tl_x2, tl_y2 = center_x + overlap_x, center_y + overlap_y

        # Q2 (top-right)
        tr_x1, tr_y1 = center_x - overlap_x, 0
        tr_x2, tr_y2 = width, center_y + overlap_y

        # Q3 (bottom-left)
        bl_x1, bl_y1 = 0, center_y - overlap_y
        bl_x2, bl_y2 = center_x + overlap_x, height

        # Q4 (bottom-right)
        br_x1, br_y1 = center_x - overlap_x, center_y - overlap_y
        br_x2, br_y2 = width, height

        # Extract the quadrants
        top_left = page_image.crop((tl_x1, tl_y1, tl_x2, tl_y2))
        top_right = page_image.crop((tr_x1, tr_y1, tr_x2, tr_y2))
        bottom_left = page_image.crop((bl_x1, bl_y1, bl_x2, bl_y2))
        bottom_right = page_image.crop((br_x1, br_y1, br_x2, br_y2))

        return [top_left, top_right, bottom_left, bottom_right], page_image

def visualize_quadrants(quadrants, original_image=None): #TODO: this is not needed in production. DEV only.
    """
    Visualizes the quadrants with colored borders to show the overlap.

    Args:
        quadrants (list): List of four image quadrants as PIL Images
        original_image (PIL.Image, optional): Original image for comparison

    Returns:
        PIL.Image: Visualization image
    """
    # Colors for the borders (R, G, B)
    colors = [
        (255, 0, 0), # Red for top-left
        (0, 255, 0), # Green for top-right
        (0, 0, 255), # Blue for bottom-left
        (255, 255, 0), # Yellow for bottom-right
    ]

    # Create copies with colored borders
    bordered_quadrants = []
    for i, quadrant in enumerate(quadrants):
        bordered = quadrant.copy()
        draw = ImageDraw.Draw(bordered)
        border_thickness = 5
        draw.rectangle([(0, 0), (bordered.width-1, bordered.height-1)],
                       outline=colors[i], width=border_thickness)
        bordered_quadrants.append(bordered)

    # Calculate dimension for the grid
    grid_width = bordered_quadrants[0].width + bordered_quadrants[1].width
    grid_height = bordered_quadrants[0].height + bordered_quadrants[2].height

    # Create a blank canvas for the grid
    grid = Image.new('RGB', (grid_width, grid_height), (255, 255, 255))

    # Paste the quadrants into the grid
    grid.paste(bordered_quadrants[0], (0, 0))
    grid.paste(bordered_quadrants[1], (bordered_quadrants[0].width, 0))
    grid.paste(bordered_quadrants[2], (0, bordered_quadrants[0].height))
    grid.paste(bordered_quadrants[3], (bordered_quadrants[0].width, bordered_quadrants[0].height))

    # If original image is provided, create a comparison visualization
    if original_image is not None:
        # Resize original to match the grid size
        original_resized = original_image.resize((grid_width, grid_height))

        # Create a blank canvas for the comparison
        comparison = Image.new('RGB', (grid_width * 2, grid_height), (255, 255, 255))

        # Paste the original and grid side by side
        comparison.paste(original_resized, (0, 0))
        comparison.paste(grid, (grid_width, 0))

        return comparison

    return grid

def save_quadrants(quadrants, output_dir=".", output_prefix="quadrant_"):
    """
    Saves individual quadrants to files.

    Args:
        quadrants (list): List of four image quadrants as PIL Images
        output_dir (str): Directory to save the quadrants
        output_prefix (str): Prefix for output filenames
    """
    os.makedirs(output_dir, exist_ok=True)

    quadrant_names = ["top_left", "top_right", "bottom_left", "bottom_right"]
    saved_paths = []

    for i, quadrant in enumerate(quadrants):
        output_path = os.path.join(output_dir, f"{output_prefix}{quadrant_names[i]}.png")
        quadrant.save(output_path)
        saved_paths.append(output_path)
        print(f"Saved {output_path}")

    return saved_paths

def process_pdf_with_overlapping_quadrants(pdf_path, page_num=0, overlap_percent=20,
                                          output_dir=".", output_prefix="quadrant_",
                                          create_visualization=True, dpi=200):
    """
    Process a PDF page by dividing it into overlapping quadrants.

    Args:
        pdf_path (str): Path to the input PDF
        page_num (int): Page number to extract (0-indexed)
        overlap_percent (float): Percentage of overlap between quadrants (0-100)
        output_dir (str): Directory to save the quadrants and visualization
        output_prefix (str): Prefix for output filenames
        create_visualization (bool): Whether to create and save a visualization
        dpi (int): Resolution for rendering the PDF page

    Returns:
        list: Paths to the saved quadrant images
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Extract quadrants from PDF
    quadrants, original_image = create_overlapping_quadrants_from_pdf(
        pdf_path, page_num, overlap_percent, dpi)

    # Save individual quadrants
    quadrant_paths = save_quadrants(quadrants, output_dir, output_prefix)

    # Create and save visualization if requested
    if create_visualization:
        visualization = visualize_quadrants(quadrants, original_image)
        viz_path = os.path.join(output_dir, f"{output_prefix}visualization.png")
        visualization.save(viz_path)
        print(f"Saved visualization to {viz_path}")

    return quadrant_paths

# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract overlapping quadrants from a PDF page")
    parser.add_argument("pdf_path", help="Path to the input PDF")
    parser.add_argument("--page", type=int, default=0, help="Page number to extract (0-indexed)")
    parser.add_argument("--overlap", type=float, default=20, help="Percentage of overlap between quadrants")
    parser.add_argument("--output-dir", default=".", help="Directory to save the quadrants")
    parser.add_argument("--prefix", default="quadrant_", help="Prefix for output filenames")
    parser.add_argument("--dpi", type=int, default=200, help="Resolution for rendering the PDF page")
    parser.add_argument("--no-viz", action="store_true", help="Don't create visualization")

    args = parser.parse_args()

    process_pdf_with_overlapping_quadrants(
        args.pdf_path,
        args.page,
        args.overlap,
        args.output_dir,
        args.prefix,
        not args.no_viz,
        args.dpi
    )