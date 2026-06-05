import streamlit as st
import os
from werkzeug.utils import secure_filename

from utils.ocr import extract_text_from_pdf, extract_text_from_image
from utils.extraction import extract_invoice
from utils.validation import validate_invoice, find_duplicates

UPLOAD_FOLDER = "uploads"


def process_file(uploaded_file):
    filename = secure_filename(uploaded_file.name)
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())

    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        with open(filepath, "rb") as f:
            text = extract_text_from_pdf(f)
    elif ext in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
        with open(filepath, "rb") as f:
            text = extract_text_from_image(f)
    else:
        st.error(f"Unsupported file type: {ext}")
        return None

    inv = extract_invoice(text, filename)
    inv = validate_invoice(inv)
    return inv


st.header("📤 Upload Documents")

uploaded_files = st.file_uploader(
    "Choose PDF or image files",
    type=["pdf", "png", "jpg", "jpeg", "tiff", "bmp"],
    accept_multiple_files=True,
    help="Upload invoices, receipts, or purchase documents (max 50 files).",
)

if uploaded_files:
    if st.button("🚀 Process Files", type="primary"):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        progress_bar = st.progress(0)
        status_text = st.empty()

        invoices = []
        total = len(uploaded_files)

        for i, file in enumerate(uploaded_files):
            status_text.text(f"Processing {file.name} ({i + 1}/{total})...")
            inv = process_file(file)
            if inv:
                invoices.append(inv)
            progress_bar.progress((i + 1) / total)

        duplicates = find_duplicates(invoices)
        if duplicates:
            st.warning(f"⚠️ Found {len(duplicates)} duplicate invoice(s)!")

        st.session_state.invoices = invoices
        st.session_state.processed = True
        status_text.text("Done!")

        passed = sum(1 for i in invoices if not i.needs_review)
        flagged = sum(1 for i in invoices if i.needs_review)
        st.success(
            f"✅ Processed {len(invoices)} invoices. "
            f"{passed} passed, {flagged} flagged for review."
        )
        if duplicates:
            for orig, dup in duplicates:
                st.info(f"🔁 Duplicate: {orig.invoice_number} — {orig.vendor_name}")

        st.page_link("pages/02_Results.py", label="→ View Results", icon="📊")

if st.session_state.get("processed"):
    st.divider()
    st.subheader("Previously Processed")
    invs = st.session_state.invoices
    passed = sum(1 for i in invs if not i.needs_review)
    flagged = sum(1 for i in invs if i.needs_review)
    st.metric("Total Invoices", len(invs))
    col1, col2 = st.columns(2)
    col1.metric("✅ Passed", passed)
    col2.metric("⚠️ Needs Review", flagged)
