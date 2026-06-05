import streamlit as st

st.set_page_config(
    page_title="InvoiceIQ",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📄 InvoiceIQ — Intelligent Document Processing")
st.markdown(
    """
    **Upload invoices, extract data, validate, review, and export.**
    Fully local — no data leaves your machine.
    """
)

st.sidebar.title("Navigation")
st.sidebar.markdown(
    """
    - **Upload** — Upload PDFs and images
    - **Results** — Extraction results & confidence
    - **Review** — Approve or edit invoices
    - **Export** — Download as CSV / JSON / Excel
    """
)

if "invoices" not in st.session_state:
    st.session_state.invoices = []

if "processed" not in st.session_state:
    st.session_state.processed = False

st.sidebar.info(
    f"Processed: {len(st.session_state.invoices)} invoices\n\n"
    f"Needs review: {sum(1 for i in st.session_state.invoices if i.needs_review)}"
)
