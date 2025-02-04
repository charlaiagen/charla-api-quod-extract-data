#%%
import os
import fitz

from transformers import LayoutLMv3ForTokenClassification, LayoutLMv3Processor
from PIL import Image

# Load pre-trained model and processor
model = LayoutLMv3ForTokenClassification.from_pretrained("microsoft/layoutlmv3-base")
processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=True)

# %%

def pdf_to_images(pdf_path:str, output_dir='output_png'):
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_paths = []

    for page_index in range(len(doc)):
        page = doc[page_index]
        pix = page.get_pixmap()
        image_path = os.path.join(output_dir, f"page_{page_index}.png")
        pix.save(image_path)
        image_paths.append(image_path)

    return image_paths
# %%

images = pdf_to_images("data/monark.pdf", "data/monark_images")
for img_path in images:
    image = Image.open(img_path)
    encoding = processor(image, return_tensors="pt")

    outputs = model(**encoding)
    predictions = outputs.logits.argmax(-1).squeeze().tolist()

    tokens = processor.tokenizer.convert_ids_to_tokens(encoding['input_ids'].squeeze().tolist())
    results = [(token, prediction) for token, prediction in zip(tokens, predictions)]
    print(results)