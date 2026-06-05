from typing import List, Tuple
from models.invoice import Invoice


def validate_invoice(inv: Invoice) -> Invoice:
    errors = []

    tax_ok, tax_msg = _check_tax_math(inv)
    if not tax_ok:
        errors.append(tax_msg)

    total_ok, total_msg = _check_total_math(inv)
    if not total_ok:
        errors.append(total_msg)

    missing = _check_missing_fields(inv)
    errors.extend(missing)

    inv.validation_errors = errors

    field_penalty = len(missing) * 0.05
    tax_penalty = 0.1 if not tax_ok else 0
    total_penalty = 0.1 if not total_ok else 0
    inv.confidence = max(0.0, inv.confidence - field_penalty - tax_penalty - total_penalty)

    return inv


def _check_tax_math(inv: Invoice) -> Tuple[bool, str]:
    if inv.net_amount is not None and inv.tax_rate is not None and inv.tax_amount is not None:
        expected_tax = round(inv.net_amount * inv.tax_rate / 100, 2)
        if abs(expected_tax - inv.tax_amount) > 0.05:
            return False, f"Tax mismatch: expected {expected_tax}, got {inv.tax_amount}"
    return True, ""


def _check_total_math(inv: Invoice) -> Tuple[bool, str]:
    if inv.net_amount is not None and inv.tax_amount is not None and inv.invoice_total is not None:
        expected_total = round(inv.net_amount + inv.tax_amount, 2)
        if abs(expected_total - inv.invoice_total) > 0.05:
            return False, f"Total mismatch: expected {expected_total}, got {inv.invoice_total}"
    return True, ""


def _check_missing_fields(inv: Invoice) -> List[str]:
    required = [
        ("vendor_name", inv.vendor_name),
        ("invoice_number", inv.invoice_number),
        ("invoice_date", inv.invoice_date),
        ("invoice_total", inv.invoice_total),
    ]
    return [f"Missing field: {name}" for name, val in required if not val]


def find_duplicates(invoices: List[Invoice]) -> List[Tuple[Invoice, Invoice]]:
    seen = {}
    duplicates = []
    for inv in invoices:
        key = (inv.invoice_number.strip().lower(), inv.vendor_name.strip().lower())
        if key in seen:
            duplicates.append((seen[key], inv))
        else:
            seen[key] = inv
    return duplicates
