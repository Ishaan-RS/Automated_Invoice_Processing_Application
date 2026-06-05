from dataclasses import dataclass, field, asdict
from typing import Optional, List


@dataclass
class LineItem:
    description: str = ""
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total: Optional[float] = None


@dataclass
class Invoice:
    scan_id: str = ""
    country: str = ""
    bill_to_name: str = ""
    currency: str = ""
    invoice_date: str = ""
    invoice_number: str = ""
    invoice_total: Optional[float] = None
    po_number: str = ""
    net_amount: Optional[float] = None
    tax_rate: Optional[float] = None
    tax_amount: Optional[float] = None
    vendor_address: str = ""
    vendor_email: str = ""
    vendor_name: str = ""
    line_items: List[LineItem] = field(default_factory=list)

    confidence: float = 1.0
    field_confidences: dict = field(default_factory=dict)
    validation_errors: list = field(default_factory=list)
    approved: bool = False

    def to_dict(self):
        d = asdict(self)
        d["line_items"] = [asdict(li) for li in self.line_items]
        return d

    @property
    def needs_review(self) -> bool:
        return self.confidence < 0.7 or len(self.validation_errors) > 0
