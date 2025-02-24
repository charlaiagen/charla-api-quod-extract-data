import pytesseract
from PIL import Image
import numpy as np
from transformers import DetrImageProcessor, TableTransformerForObjectDetection
import torch
import matplotlib.pyplot as plt

def detect_tables_with_transformer(image_path):
    """
    Detect tables in an image using Table Transformer (IFRS model)
    
    Args:
        image_path: Path to the image file or PIL Image object
    Returns:
        List of detected table coordinates
    """
    MODEL_NAME = "apkonsta/table-transformer-detection-ifrs"
    
    # Load the model and processor
    processor = DetrImageProcessor.from_pretrained(
        MODEL_NAME,
        max_size=1600,  # Limit maximum size while keeping aspect ratio
        do_resize=True,
        size={'height': 1024, 'width': 1024},  # More balanced size
    )
    model = TableTransformerForObjectDetection.from_pretrained(MODEL_NAME)
    
    # Move model to GPU if available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    model = model.to(device)
    
    # Load and process the image
    if isinstance(image_path, str):
        image = Image.open(image_path)
    else:
        image = image_path
    
    print(f"Original image size: {image.size}")
    
    # Convert image to RGB if it's not
    if image.mode != 'RGB':
        print(f"Converting image from {image.mode} to RGB")
        image = image.convert('RGB')
    
    # Process image
    inputs = processor(images=image, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Get predictions
    with torch.no_grad():  # Disable gradient computation
        outputs = model(**inputs)
    
    # Convert outputs to XYXY format with adjusted parameters
    target_sizes = torch.tensor([image.size[::-1]]).to(device)
    results = processor.post_process_object_detection(
        outputs, 
        threshold=0.1,  # Lower confidence threshold
        target_sizes=target_sizes
    )[0]
    
    # Filter overlapping boxes
    boxes = results["boxes"]
    scores = results["scores"]
    
    # Convert to numpy for easier manipulation
    boxes_np = boxes.cpu().detach().numpy()
    scores_np = scores.cpu().detach().numpy()
    
    # Calculate areas
    areas = (boxes_np[:, 2] - boxes_np[:, 0]) * (boxes_np[:, 3] - boxes_np[:, 1])
    
    # Sort by confidence
    order = scores_np.argsort()[::-1]
    keep = []
    
    while order.size > 0:
        i = order[0]
        keep.append(i)
        
        if order.size == 1:
            break
            
        # Calculate IoU with rest of boxes
        xx1 = np.maximum(boxes_np[i, 0], boxes_np[order[1:], 0])
        yy1 = np.maximum(boxes_np[i, 1], boxes_np[order[1:], 1])
        xx2 = np.minimum(boxes_np[i, 2], boxes_np[order[1:], 2])
        yy2 = np.minimum(boxes_np[i, 3], boxes_np[order[1:], 3])
        
        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        inter = w * h
        
        ovr = inter / (areas[i] + areas[order[1:]] - inter)
        
        # Get indices of boxes with lower IoU than threshold
        inds = np.where(ovr <= 0.45)[0]
        order = order[inds + 1]
    
    # Update results with filtered boxes
    results["boxes"] = boxes[keep]
    results["scores"] = scores[keep]
    
    print(f"\nNumber of detected tables: {len(results['scores'])}")
    for i, (score, box) in enumerate(zip(results["scores"], results["boxes"]), 1):
        print(f"Table {i} detected with confidence: {score:.2f}")
        print(f"Bounding box: {box.tolist()}\n")
    
    return results

def extract_table_with_tesseract(image, coords=None):
    """
    Extract table content using Tesseract OCR
    
    Args:
        image: PIL Image object
        coords: Optional coordinates to crop the image to specific table region
    Returns:
        Extracted text
    """
    if coords:
        # Crop image to table coordinates if provided
        image = image.crop(coords)
    
    # Configure Tesseract to look for tables
    custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
    
    # Extract text with table structure preserved
    text = pytesseract.image_to_string(image, config=custom_config)
    return text

def visualize_detection(image, results):
    """
    Visualize detected tables on the image
    """
    plt.figure(figsize=(20, 12))
    plt.imshow(image)
    
    # Define different colors for different tables
    colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'cyan', 'magenta']
    
    for i, (score, box) in enumerate(zip(results["scores"].cpu(), results["boxes"].cpu())):
        box = box.detach().numpy()
        score = score.detach().numpy()
        color = colors[i % len(colors)]
        
        x1, y1, x2, y2 = box
        rect = plt.Rectangle((x1, y1), x2-x1, y2-y1, 
                           fill=False, color=color, linewidth=2)
        plt.gca().add_patch(rect)
        plt.text(x1, y1-10, f'IFRS Table {i+1}: {score:.2f}', 
                bbox=dict(facecolor='white', alpha=0.8),
                color=color)
    
    plt.axis('off')
    plt.show()

def process_document_with_tables(image_path):
    """
    Main function to process a document and extract tables
    
    Args:
        image_path: Path to the image file or PIL Image object
    """
    print("Starting IFRS table detection...")
    
    # Detect tables
    results = detect_tables_with_transformer(image_path)
    
    # Load image if path provided
    if isinstance(image_path, str):
        image = Image.open(image_path)
    else:
        image = image_path
    
    if len(results["scores"]) == 0:
        print("No tables detected. Try adjusting the image quality or checking if tables are clearly visible.")
        return []
        
    # Visualize detections
    visualize_detection(image, results)
    
    # Extract text from each detected table
    tables = []
    for i, (score, box) in enumerate(zip(results["scores"].cpu(), results["boxes"].cpu()), 1):
        if score > 0.1:  # Lower confidence threshold
            coords = box.detach().numpy().tolist()
            table_text = extract_table_with_tesseract(image, coords)
            tables.append({
                'table_number': i,
                'confidence': score.item(),
                'coordinates': coords,
                'content': table_text
            })
    
    return tables

if __name__ == "__main__":
    # Example usage
    image_path = "your_document.pdf"  # or your PIL Image object
    tables = process_document_with_tables(image_path)
    
    for i, table in enumerate(tables, 1):
        print(f"\nTable {table['table_number']} (confidence: {table['confidence']:.2f}):")
        print(table['content'])
