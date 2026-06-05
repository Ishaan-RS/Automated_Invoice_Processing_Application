import streamlit as st
import pandas as pd
from utils.export import to_dataframe

st.header("📊 Extraction Results")

if not st.session_state.get("invoices"):
    st.info("No invoices processed yet. Go to **Upload** to process files.")
    st.page_link("pages/01_Upload.py", label="→ Go to Upload", icon="📤")
    st.stop()

invoices = st.session_state.invoices
df = to_dataframe(invoices)

total = len(invoices)
passed = sum(1 for i in invoices if not i.needs_review)
flagged = sum(1 for i in invoices if i.needs_review)

col1, col2, col3 = st.columns(3)
col1.metric("Total", total)
col2.metric("✅ Auto-Passed", passed, f"{passed / total * 100:.0f}%" if total else "")
col3.metric("⚠️ Needs Review", flagged, f"{flagged / total * 100:.0f}%" if total else "")

st.subheader("Confidence Distribution")
import altair as alt
chart_df = pd.DataFrame({
    "Invoice": [f"#{i+1}" for i in range(total)],
    "Confidence": [round(i.confidence, 2) for i in invoices],
    "Status": ["✅ Pass" if not i.needs_review else "⚠️ Review" for i in invoices],
})
chart = alt.Chart(chart_df).mark_bar().encode(
    x="Invoice:N",
    y="Confidence:Q",
    color=alt.Color("Status:N", scale=alt.Scale(domain=["✅ Pass", "⚠️ Review"], range=["#27ae60", "#f39c12"])),
    tooltip=["Invoice", "Confidence", "Status"],
).properties(height=400)
st.altair_chart(chart, width='stretch')

st.subheader("Invoice Details")
display_cols = [
    "Scan ID", "Vendor Name", "Invoice Number", "Invoice Date",
    "Invoice Total", "Confidence", "Needs Review", "Validation Errors"
]
view_df = df[display_cols]
st.dataframe(view_df, width='stretch', hide_index=True)

st.page_link("pages/03_Review.py", label="→ Review Queue", icon="🔍")
