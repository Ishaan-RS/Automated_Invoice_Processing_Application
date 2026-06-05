import json
import re
import logging

from models.invoice import Invoice, LineItem

logger = logging.getLogger(__name__)

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("ollama Python package not installed. Using fallback extraction only.")

EXTRACTION_PROMPT = """
Extract invoice fields from the text below. Return ONLY valid JSON with:
- "country": string
- "bill_to_name": string
- "currency": string (3-letter code)
- "invoice_date": string (DD-MM-YYYY)
- "invoice_number": string
- "invoice_total": number or null
- "po_number": string (starting with PO if present)
- "net_amount": number or null
- "tax_rate": number or null (percentage)
- "tax_amount": number or null
- "vendor_address": string
- "vendor_email": string
- "vendor_name": string
- "line_items": array of {"description": string, "quantity": number|null, "unit_price": number|null, "total": number|null}
- "confidences": object with same keys mapping to 0.0-1.0 confidence

Invoice text:
{text}
"""


def extract_invoice(text: str, filename: str) -> Invoice:
    if OLLAMA_AVAILABLE and text.strip():
        try:
            response = ollama.chat(
                model="phi3:mini",
                messages=[{"role": "user", "content": EXTRACTION_PROMPT.format(text=text[:8000])}],
            )
            content = response["message"]["content"]
            content = _clean_json(content)
            data = json.loads(content)
        except Exception as e:
            logger.warning(f"Ollama extraction failed for {filename}: {e}")
            data = _fallback_extract(text)
    else:
        data = _fallback_extract(text)

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
