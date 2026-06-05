import streamlit as st
from models.invoice import Invoice

st.header("🔍 Review Queue")

if not st.session_state.get("invoices"):
    st.info("No invoices to review. Go to **Upload** first.")
    st.page_link("pages/01_Upload.py", label="→ Go to Upload", icon="📤")
    st.stop()

invoices = st.session_state.invoices
flagged = [inv for inv in invoices if inv.needs_review]
passed = [inv for inv in invoices if not inv.needs_review]

tab1, tab2 = st.tabs(["⚠️ Needs Review", "✅ Auto-Passed"])

with tab1:
    if not flagged:
        st.success("All invoices passed validation! 🎉")
    else:
        st.write(f"{len(flagged)} invoice(s) flagged for review.")
        for idx, inv in enumerate(flagged):
            _render_invoice_card(inv, idx, needs_review=True)

with tab2:
    if not passed:
        st.info("No auto-passed invoices.")
    else:
        st.write(f"{len(passed)} invoice(s) passed automatically.")
        for idx, inv in enumerate(passed):
            _render_invoice_card(inv, idx, needs_review=False)


def _render_invoice_card(inv: Invoice, idx: int, needs_review: bool):
    with st.expander(
        f"{'⚠️' if needs_review else '✅'} "
        f"{inv.scan_id} — {inv.vendor_name or 'Unknown'} "
        f"(Confidence: {inv.confidence:.2f})",
        expanded=needs_review,
    ):
        if inv.validation_errors:
            st.error(" | ".join(inv.validation_errors))

        col1, col2 = st.columns(2)

        with col1:
            inv.vendor_name = st.text_input(
                "Vendor Name", value=inv.vendor_name, key=f"vendor_{idx}"
            )
            inv.invoice_number = st.text_input(
                "Invoice #", value=inv.invoice_number, key=f"invnum_{idx}"
            )
            inv.invoice_date = st.text_input(
                "Date", value=inv.invoice_date, key=f"date_{idx}"
            )
            inv.currency = st.text_input(
                "Currency", value=inv.currency, key=f"cur_{idx}"
            )
            inv.po_number = st.text_input(
                "PO Number", value=inv.po_number, key=f"po_{idx}"
            )

        with col2:
            inv.net_amount = st.number_input(
                "Net Amount", value=inv.net_amount or 0.0, key=f"net_{idx}"
            )
            inv.tax_rate = st.number_input(
                "Tax Rate (%)", value=inv.tax_rate or 0.0, key=f"taxr_{idx}"
            )
            inv.tax_amount = st.number_input(
                "Tax Amount", value=inv.tax_amount or 0.0, key=f"taxa_{idx}"
            )
            inv.invoice_total = st.number_input(
                "Total", value=inv.invoice_total or 0.0, key=f"total_{idx}"
            )

        inv.bill_to_name = st.text_input(
            "Bill To", value=inv.bill_to_name, key=f"bill_{idx}"
        )
        inv.vendor_email = st.text_input(
            "Vendor Email", value=inv.vendor_email, key=f"email_{idx}"
        )
        inv.vendor_address = st.text_area(
            "Vendor Address", value=inv.vendor_address, key=f"addr_{idx}",
            height=60,
        )

        if st.button(f"✅ Approve {inv.scan_id}", key=f"approve_{idx}"):
            inv.approved = True
            inv.validation_errors = []
            inv.confidence = 1.0
            st.success(f"{inv.scan_id} approved!")
            st.rerun()

st.page_link("pages/04_Export.py", label="→ Export Data", icon="💾")
