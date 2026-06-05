# InvoiceIQ — Intelligent Document Processing Platform

> **From:** Automated Invoice Processing Application *(basic extractor)*  
> **To:** InvoiceIQ — open-source, local-first Intelligent Document Processing platform for invoices, receipts, and purchase documents.

Upload invoice PDFs or scans → extract vendor + line-item data → validate totals and tax consistency → flag low-confidence documents → route to review queue → export clean JSON/CSV/Excel for ERP/accounting.

---

## Product Vision

InvoiceIQ is not just an OCR script. It's a **document operations platform** that:

- Runs **fully locally** — no API keys, no data leaving your machine
- Uses **Phi-3 Vision** (VLM) for end-to-end extraction from images
- Validates business rules (totals, tax, duplicates) automatically
- Provides a **human-in-the-loop review queue** for edge cases
- Exports **ERP-ready structured data** (JSON, CSV, Excel)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit (multi-page dashboard) |
| OCR + Extraction | Ollama + Phi-3 Vision (end-to-end) |
| Validation | Python rule engine (heuristic) |
| Export | Pandas → Excel / CSV / JSON |
| Containerization | Docker + Docker Compose |

---

## Architecture

```
┌─────────────┐    ┌──────────────────┐    ┌────────────┐
│  Upload PDF │───▶│  Ollama Phi-3    │───▶│ Validation │
│  / Image    │    │  Vision (VLM)    │    │  Engine    │
└─────────────┘    └──────────────────┘    └─────┬──────┘
                                                              │
                    ┌─────────────────────────────────────────┘
                    ▼
        ┌──────────────────────┐
        │  Confidence ≥ 0.7?   │
        │  All fields present? │
        │  Tax math checks?    │
        └──────┬───────────┬───┘
               │           │
          Auto-pass    Needs Review
               │           │
               ▼           ▼
        ┌──────────┐ ┌──────────┐
        │  Export  │ │  Review  │
        │  CSV/XLSX│ │  Queue   │──▶ Approved → Export
        └──────────┘ └──────────┘
```

---

## Upgrade Roadmap (1-Day Build)

### Phase 1 — Foundation & Cleanup

| # | Task | Est. Time | Status |
|---|------|-----------|--------|
| 1.1 | Fix `requirements.txt` typo ("Flaask" → "Flask"), remove unused deps | 10 min | ⬜ |
| 1.2 | Remove dead `process_files` function, cleanup code | 10 min | ⬜ |
| 1.3 | Rename project to InvoiceIQ throughout | 10 min | ⬜ |
| 1.4 | Set up project structure: `app/`, `pages/`, `utils/`, `models/` | 20 min | ⬜ |

### Phase 2 — Streamlit Frontend

| # | Task | Est. Time | Status |
|---|------|-----------|--------|
| 2.1 | Build main upload page with batch PDF/image support | 45 min | ⬜ |
| 2.2 | Build extraction status dashboard with per-invoice confidence badges | 45 min | ⬜ |
| 2.3 | Build review queue page — filterable, editable fields | 1 hr | ⬜ |
| 2.4 | Build export page — download JSON / CSV / Excel | 30 min | ⬜ |

### Phase 3 — Ollama + Local LLM Integration

| # | Task | Est. Time | Status |
|---|------|-----------|--------|
| 3.1 | Install Ollama, pull Phi-3 Vision model | 20 min | ⬜ |
| 3.2 | Replace Gemini + Tesseract with Phi-3 Vision (image→JSON) | 30 min | ⬜ |
| 3.3 | Update prompt for structured JSON output (fields + confidence) | 20 min | ⬜ |
| 3.4 | Add line-item extraction (description, qty, unit price, total) | 20 min | ⬜ |

### Phase 4 — Validation Engine

| # | Task | Est. Time | Status |
|---|------|-----------|--------|
| 4.1 | Tax consistency check: `subtotal × tax_rate ≈ tax_amount` | 15 min | ⬜ |
| 4.2 | Total match check: `subtotal + tax ≈ total` | 10 min | ⬜ |
| 4.3 | Missing field detection + field-level confidence scoring | 20 min | ⬜ |
| 4.4 | Duplicate invoice detection (by invoice number + vendor) | 15 min | ⬜ |
| 4.5 | Overall document confidence score (0.0–1.0) | 15 min | ⬜ |

### Phase 5 — Export & Containerization

| # | Task | Est. Time | Status |
|---|------|-----------|--------|
| 5.1 | ERP-normalized CSV export (columns matching common ERP formats) | 20 min | ⬜ |
| 5.2 | JSON export with full metadata + confidence scores | 15 min | ⬜ |
| 5.3 | Excel export with summary + detailed sheets | 20 min | ⬜ |
| 5.4 | Dockerfile for the Streamlit app | 30 min | ⬜ |
| 5.5 | `docker-compose.yml` with app + Ollama service | 30 min | ⬜ |

### Phase 6 — Polish & Testing

| # | Task | Est. Time | Status |
|---|------|-----------|--------|
| 6.1 | End-to-end test with 10–20 sample invoices | 30 min | ⬜ |
| 6.2 | Edge case handling (corrupted PDFs, blank pages, unsupported formats) | 20 min | ⬜ |
| 6.3 | Final README polish with screenshots + demo GIF | 20 min | ⬜ |

**Total estimated time: ~9 hours**

---

## Getting Started (After Build)

```bash
# Option 1: Local
pip install -r requirements.txt
ollama pull phi3:vision
streamlit run app.py

# Option 2: Docker
docker-compose up --build
```

---

## Demo Storyline

1. Upload 20 mixed invoices (PDF + scanned images)
2. System processes → 15 pass validation, 5 flagged for review
3. Review dashboard shows low-confidence invoices with edit capability
4. Approve → export as CSV/JSON/Excel
5. Dashboard shows: vendor spend, processing time, exception rate

---

## Why This Stands Out

- **Useful:** Invoice automation is a real-world pain point
- **Modern:** Vision LM extraction (not regex scraping)
- **Private:** Fully local — no data leaves your machine
- **Productized:** Review workflows, auditability, ERP exports
- **Deployable:** Dockerized full pipeline — not a Jupyter notebook
