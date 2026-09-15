# ============================================================
# FILE: ml/extract_regulations.py
# ============================================================
# Reads PDFs from data/regulations/ and breaks them into
# ~500-word chunks for embedding into the vector store.
#
# If no PDFs are found, creates demo chunks instead so the
# rest of the RAG pipeline can still be built and tested.
#
# HOW TO RUN:
#   python ml/extract_regulations.py
# ============================================================

import os
import json
import re

REGULATIONS_DIR = "data/regulations"
OUTPUT_FILE = "data/chunks.json"
CHUNK_WORD_SIZE = 500

DEMO_CHUNKS = [
    {
        "text": "RBI Master Direction on KYC 2023, Section 16(3): Regulated entities shall "
                "undertake Enhanced Due Diligence for any single transaction exceeding "
                "Rs. 5,00,000 where the customer's identity has not been verified in "
                "accordance with prescribed KYC norms.",
        "source": "RBI KYC Master Direction 2023",
        "section": "Section 16(3)",
        "status": "current",
    },
    {
        "text": "RBI Master Direction on KYC 2016, Section 16(3): Regulated entities shall "
                "undertake due diligence for high value transactions. (Superseded by the "
                "2023 Master Direction.)",
        "source": "RBI KYC Master Direction 2016",
        "section": "Section 16(3)",
        "status": "superseded",
    },
    {
        "text": "Prevention of Money Laundering Act 2002, Section 3: Whosoever directly or "
                "indirectly attempts to indulge, knowingly assists, or is a party to any "
                "process connected with the proceeds of crime, including structuring "
                "transactions to evade reporting thresholds, commits the offence of "
                "money laundering.",
        "source": "PMLA 2002",
        "section": "Section 3",
        "status": "current",
    },
    {
        "text": "Prevention of Money Laundering Act 2002, Rule 7: Every reporting entity "
                "shall furnish information to the Financial Intelligence Unit-India (FIU-IND) "
                "for all cash transactions of value more than Rs. 10,00,000 or its equivalent "
                "in foreign currency.",
        "source": "PMLA 2002",
        "section": "Rule 7",
        "status": "current",
    },
    {
        "text": "RBI Digital Lending Guidelines 2022, Section 8: Digital lending apps and "
                "their partner lenders must complete KYC verification before disbursal of "
                "any loan amount exceeding Rs. 50,000, regardless of the loan tenure.",
        "source": "RBI Digital Lending Guidelines 2022",
        "section": "Section 8",
        "status": "superseded",
    },
    {
        "text": "RBI Digital Lending Directions 2025 update and supersede the 2022 "
                "guidelines, extending KYC and disclosure requirements to all digital "
                "lending platforms including those operating via mobile applications.",
        "source": "RBI Digital Lending Directions 2025",
        "section": "General",
        "status": "current",
    },
    {
        "text": "RBI Fraud Circular 2016: Banks shall treat transactions occurring between "
                "midnight and 5 AM involving amounts above Rs. 5,00,000 as requiring "
                "additional scrutiny for potential fraudulent activity.",
        "source": "RBI Fraud Circular 2016",
        "section": "General",
        "status": "current",
    },
    {
        "text": "Digital Personal Data Protection Act 2023: Data fiduciaries must obtain "
                "verifiable consent before processing personal data, and must implement "
                "reasonable security safeguards to prevent personal data breaches. Rules "
                "notified in 2025 are being brought into force in phases.",
        "source": "DPDP Act 2023 (Rules 2025)",
        "section": "General",
        "status": "phased_commencement",
    },
]


def chunk_text(text: str, source_name: str) -> list[dict]:
    """Split raw text into ~500-word chunks."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), CHUNK_WORD_SIZE):
        chunk_words = words[i : i + CHUNK_WORD_SIZE]
        chunks.append({
            "text": " ".join(chunk_words),
            "source": source_name,
            "section": f"chunk_{i // CHUNK_WORD_SIZE + 1}",
            "status": "current",
        })
    return chunks


def extract_from_pdfs() -> list[dict]:
    """Extract and chunk text from every PDF in data/regulations/."""
    try:
        from pypdf import PdfReader
    except ImportError:
        print("  pypdf not installed — installing is required for real PDF extraction.")
        print("  Run: pip install pypdf")
        return []

    all_chunks = []
    pdf_files = [f for f in os.listdir(REGULATIONS_DIR) if f.lower().endswith(".pdf")]

    if not pdf_files:
        return []

    for filename in pdf_files:
        path = os.path.join(REGULATIONS_DIR, filename)
        try:
            reader = PdfReader(path)
            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception:
                    print(f"  Skipping {filename} — encrypted/password-protected, can't read.")
                    continue

            full_text = ""
            for page in reader.pages:
                full_text += (page.extract_text() or "") + " "
            full_text = re.sub(r"\s+", " ", full_text).strip()

            if len(full_text.split()) < 20:
                print(f"  Skipping {filename} — no extractable text found (scanned image?).")
                continue

            source_name = filename.replace(".pdf", "").replace("_", " ").title()
            chunks = chunk_text(full_text, source_name)
            all_chunks.extend(chunks)
            print(f"  Processing {filename}... {len(chunks)} chunks")
        except Exception as e:
            print(f"  Skipping {filename} — could not read ({e}).")
            continue

    return all_chunks


def main():
    os.makedirs(REGULATIONS_DIR, exist_ok=True)
    os.makedirs("data", exist_ok=True)

    chunks = extract_from_pdfs()

    if not chunks:
        print("  No PDFs found — creating demo chunks...")
        chunks = DEMO_CHUNKS
        print(f"  Created {len(chunks)} demo chunks")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)

    print(f"\nTotal: {len(chunks)} chunks")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
