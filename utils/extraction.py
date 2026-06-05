import base64
import io
import json
import logging
import re

from PIL import Image

from models.invoice import Invoice, LineItem

logger = logging.getLogger(__name__)

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("ollama Python package not installed. Using fallback extraction only.")

VISION_PROMPT = """Extract all invoice data from this image. Return ONLY valid JSON.

Fields: vendor_name, vendor_address, vendor_email, bill_to_name, invoice_number, invoice_date (DD-MM-YYYY), po_number, currency (3-letter code), net_amount (number or null), tax_rate (number or null, percentage), tax_amount (number or null), invoice_total (number or null), country, line_items (array of {"description", "quantity", "unit_price", "total"}), confidences (object with same keys, values 0.0-1.0)"""


def extract_invoice_from_image(image: Image.Image, filename: str, fallback_text: str = "") -> Invoice:
    if OLLAMA_AVAILABLE:
        try:
            img_b64 = _pil_to_base64(image)
            response = ollama.chat(
                model="llava:7b",
                messages=[{
                    "role": "user",
                    "content": VISION_PROMPT,
                    "images": [img_b64],
                }],
            )
            content = response["message"]["content"]
            content = _clean_json(content)
            data = json.loads(content)
        except Exception as e:
            logger.warning(f"Vision extraction failed for {filename}: {e}")
            if fallback_text.strip():
                data = _fallback_extract(fallback_text)
            else:
                data = {}
    else:
        if fallback_text.strip():
            data = _fallback_extract(fallback_text)
        else:
            logger.error("Ollama unavailable and no fallback text provided")
            data = {}

    inv = Invoice(
        scan_id=filename,
        country=data.get("country", ""),
        bill_to_name=data.get("bill_to_name", ""),
        currency=data.get("currency", ""),
        invoice_date=data.get("invoice_date", ""),
        invoice_number=str(data.get("invoice_number", "")),
        invoice_total=_safe_float(data.get("invoice_total")),
        po_number=data.get("po_number", ""),
        net_amount=_safe_float(data.get("net_amount")),
        tax_rate=_safe_float(data.get("tax_rate")),
        tax_amount=_safe_float(data.get("tax_amount")),
        vendor_address=data.get("vendor_address", ""),
        vendor_email=data.get("vendor_email", ""),
        vendor_name=data.get("vendor_name", ""),
        line_items=[LineItem(**li) for li in data.get("line_items", []) if isinstance(li, dict)],
    )

    confs = data.get("confidences", {})
    if confs and isinstance(confs, dict):
        inv.field_confidences = confs
        scores = [v for v in confs.values() if isinstance(v, (int, float))]
        inv.confidence = sum(scores) / len(scores) if scores else 1.0

    return inv


def _pil_to_base64(image: Image.Image) -> str:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def _clean_json(content: str) -> str:
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()


def _safe_float(val):
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _fallback_extract(text: str) -> dict:
    data = {"confidences": {}}
    patterns = {
        "invoice_number": [r"(?:Invoice\s*[#:]\s*|INV\s*|Invoice\s*Number[:\s]*)(\S+)", r"INV[-]?(\d+)"],
        "invoice_total": [r"(?:Total|Invoice\s*Total|Amount\s*Due)[:\s]*\$?([\d,]+\.\d{2})"],
        "vendor_name": [r"(?:Vendor|From|Supplier|Bill\s*From)[:\s]*(.+?)(?:\n|$)"],
        "invoice_date": [r"(?:Date|Invoice\s*Date)[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})"],
        "currency": [r"(?:Currency)[:\s]*([A-Z]{3})"],
    }
    for key, pat_list in patterns.items():
        for pattern in pat_list:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data[key] = match.group(1).strip()
                data.setdefault("confidences", {})[key] = 0.6
                break
    return data
