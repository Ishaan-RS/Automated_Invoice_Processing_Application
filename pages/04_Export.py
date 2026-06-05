import streamlit as st
import pandas as pd
import os
from utils.export import to_dataframe, to_json, to_erp_csv, to_excel

st.header("💾 Export Data")

if not st.session_state.get("invoices"):
    st.info("No invoices to export. Go to **Upload** first.")
    st.page_link("pages/01_Upload.py", label="→ Go to Upload", icon="📤")
    st.stop()

invoices = st.session_state.invoices

summary_df = to_dataframe(invoices)
erp_df = to_erp_csv(invoices)
json_str = to_json(invoices)

st.subheader("Preview")
st.dataframe(summary_df, use_container_width=True, hide_index=True)

st.subheader("Download Options")

col1, col2, col3 = st.columns(3)

with col1:
    csv_data = summary_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download CSV",
        data=csv_data,
        file_name="invoiceiq_export.csv",
        mime="text/csv",
        use_container_width=True,
    )

with col2:
    json_bytes = json_str.encode("utf-8")
    st.download_button(
        "📥 Download JSON",
        data=json_bytes,
        file_name="invoiceiq_export.json",
        mime="application/json",
        use_container_width=True,
    )

with col3:
    erp_csv_data = erp_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download ERP CSV",
        data=erp_csv_data,
        file_name="invoiceiq_erp_export.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.divider()
st.subheader("📊 Summary Statistics")

total_invoices = len(invoices)
total_spend = sum(i.invoice_total or 0 for i in invoices if i.invoice_total)
avg_confidence = sum(i.confidence for i in invoices) / total_invoices if total_invoices else 0
approved = sum(1 for i in invoices if i.approved)
needs_review = sum(1 for i in invoices if i.needs_review)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Invoices", total_invoices)
c2.metric("Total Spend", f"${total_spend:,.2f}")
c3.metric("Avg Confidence", f"{avg_confidence:.0%}")
c4.metric("Approved / Flagged", f"{approved} / {needs_review}")

if invoices:
    output_path = os.path.join("output", "invoiceiq_export.xlsx")
    os.makedirs("output", exist_ok=True)
    to_excel(invoices, output_path)
    with open(output_path, "rb") as f:
        st.download_button(
            "📥 Download Excel (with Line Items)",
            data=f,
            file_name="invoiceiq_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
