import json
import pandas as pd
from typing import List
from models.invoice import Invoice


def to_dataframe(invoices: List[Invoice]) -> pd.DataFrame:
    rows = []
    for inv in invoices:
        row = {
            "Scan ID": inv.scan_id,
            "Vendor Name": inv.vendor_name,
            "Vendor Email": inv.vendor_email,
            "Vendor Address": inv.vendor_address,
            "Invoice Number": inv.invoice_number,
            "Invoice Date": inv.invoice_date,
            "PO Number": inv.po_number,
            "Currency": inv.currency,
            "Net Amount": inv.net_amount,
            "Tax Rate (%)": inv.tax_rate,
            "Tax Amount": inv.tax_amount,
            "Invoice Total": inv.invoice_total,
            "Bill To Name": inv.bill_to_name,
            "Country": inv.country,
            "Confidence": round(inv.confidence, 2),
            "Needs Review": inv.needs_review,
            "Approved": inv.approved,
            "Validation Errors": "; ".join(inv.validation_errors) if inv.validation_errors else "",
        }
        rows.append(row)
    df = pd.DataFrame(rows)
    return df


def to_json(invoices: List[Invoice]) -> str:
    data = [inv.to_dict() for inv in invoices]
    return json.dumps(data, indent=2, default=str)


def to_erp_csv(invoices: List[Invoice]) -> pd.DataFrame:
    rows = []
    for inv in invoices:
        row = {
            "VendorName": inv.vendor_name,
            "VendorEmail": inv.vendor_email,
            "InvoiceNumber": inv.invoice_number,
            "InvoiceDate": inv.invoice_date,
            "PONumber": inv.po_number,
            "Currency": inv.currency,
            "Subtotal": inv.net_amount,
            "TaxPercent": inv.tax_rate,
            "TaxAmount": inv.tax_amount,
            "TotalAmount": inv.invoice_total,
            "VendorAddress": inv.vendor_address,
        }
        rows.append(row)
    return pd.DataFrame(rows)


def to_excel(invoices: List[Invoice], filepath: str):
    summary_df = to_dataframe(invoices)
    line_items = []
    for inv in invoices:
        for li in inv.line_items:
            line_items.append({
                "Invoice Number": inv.invoice_number,
                "Description": li.description,
                "Quantity": li.quantity,
                "Unit Price": li.unit_price,
                "Line Total": li.total,
            })
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        if line_items:
            pd.DataFrame(line_items).to_excel(writer, sheet_name="Line Items", index=False)
