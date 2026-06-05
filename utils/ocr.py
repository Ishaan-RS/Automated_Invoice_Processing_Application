import io
import os
import shutil
import fitz
import pytesseract
from PIL import Image
import PyPDF2

tesseract_path = shutil.which("tesseract")
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path


def extract_text_from_pdf(file_stream) -> str:
    all_text = ""
    reader = PyPDF2.PdfReader(file_stream)

    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text = page.extract_text()
        if text and text.strip():
            all_text += text + "\n"

    if not any(w.isalnum() for w in all_text.split()):
        file_stream.seek(0)
        document = fitz.open(stream=file_stream.read(), filetype="pdf")
        for page_number in range(len(document)):
            page = document.load_page(page_number)
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = document.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(io.BytesIO(image_bytes))
                try:
                    text = pytesseract.image_to_string(image)
                    all_text += text + "\n"
                except Exception:
                    pass

    return all_text


def extract_text_from_image(file_stream) -> str:
    image = Image.open(file_stream)
    return pytesseract.image_to_string(image)
