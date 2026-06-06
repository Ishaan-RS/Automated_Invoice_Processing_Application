import streamlit as st
import os
import re

from utils.ocr import pdf_to_images, load_image, extract_text_pypdf2, resize_for_model, is_text_clean
from utils.extraction import extract_invoice_from_image, extract_invoice_from_text, regex_extract_invoice_from_text
from utils.validation import validate_invoice, find_duplicates


def secure_filename(filename):
    """Simple secure filename implementation without werkzeug dependency"""
    # Remove any path separators
    filename = os.path.basename(filename)
    # Keep only alphanumeric, dots, hyphens, and underscores
    filename = re.sub(r'[^\w\-_.]', '_', filename)
    # Limit length
    return filename[:255]

UPLOAD_FOLDER = "uploads"


def process_file(uploaded_file):
    filename = secure_filename(uploaded_file.name)
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())

    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        with open(filepath, "rb") as f:
            fallback_text = extract_text_pypdf2(f)
        if is_text_clean(fallback_text):
            inv = regex_extract_invoice_from_text(fallback_text, filename)
            inv.raw_text = fallback_text
            inv.extraction_method = "regex"
        else:
            with open(filepath, "rb") as f:
                images = pdf_to_images(f)
            if not images:
                st.error("No pages found in document")
                return None
            img = resize_for_model(images[0])
            inv = extract_invoice_from_image(img, filename, fallback_text)
            inv.raw_text = fallback_text
            inv.extraction_method = "vision"
    elif ext in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
        with open(filepath, "rb") as f:
            images = [load_image(f)]
        if not images:
            st.error("No pages found in document")
            return None
        img = resize_for_model(images[0])
        inv = extract_invoice_from_image(img, filename, "")
        inv.extraction_method = "vision"
    else:
        st.error(f"Unsupported file type: {ext}")
        return None

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
