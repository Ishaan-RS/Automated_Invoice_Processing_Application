import io
from typing import List
import fitz
import PyPDF2
from PIL import Image


def pdf_to_images(file_stream) -> List[Image.Image]:
    images = []
    document = fitz.open(stream=file_stream.read(), filetype="pdf")
    for page_number in range(len(document)):
        page = document.load_page(page_number)
        pix = page.get_pixmap(dpi=200)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples).copy()
        images.append(img)
    return images


def load_image(file_stream) -> Image.Image:
    return Image.open(file_stream).copy()


def is_text_clean(text: str) -> bool:
    if len(text.strip()) < 50:
        return False
    invoice_keywords = ["invoice", "total", "date", "vendor", "amount", "tax", "bill", "po "]
    text_lower = text.lower()
    keyword_count = sum(1 for kw in invoice_keywords if kw in text_lower)
    if keyword_count < 2:
        return False
    printable = sum(c.isprintable() for c in text)
    if printable / max(len(text), 1) < 0.8:
        return False
    return True


def extract_text_pypdf2(file_stream) -> str:
    all_text = ""
    reader = PyPDF2.PdfReader(file_stream)
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text = page.extract_text()
        if text and text.strip():
            all_text += text + "\n"
    return all_text


def resize_for_model(image: Image.Image, max_size: int = 1344) -> Image.Image:
    w, h = image.size
    if w <= max_size and h <= max_size:
        return image
    ratio = min(max_size / w, max_size / h)
    return image.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)
