import os
import json
from typing import List, Dict

import pdfplumber


def load_documents(knowledge_base_dir: str) -> List[Dict]:
    """
    Load all documents from the knowledge base directory.
    Returns a list of dicts: {text, source, page_number}
    """
    documents = []
    metadata_path = os.path.join(knowledge_base_dir, "metadata.json")

    # Load metadata if exists
    metadata = {}
    if os.path.exists(metadata_path):
        with open(metadata_path, "r", encoding="utf-8") as f:
            meta_list = json.load(f)
            metadata = {item["file"]: item for item in meta_list}

    for filename in os.listdir(knowledge_base_dir):
        filepath = os.path.join(knowledge_base_dir, filename)

        if filename == "metadata.json":
            continue

        file_meta = metadata.get(filename, {})
        source_title = file_meta.get("title", filename)
        category = file_meta.get("category")
        source_type = file_meta.get("source_type", "educational")

        if filename.lower().endswith(".pdf"):
            documents.extend(_load_pdf(filepath, source_title, category, source_type))
        elif filename.lower().endswith((".txt", ".md")):
            documents.extend(_load_text(filepath, source_title, category, source_type))

    return documents


def _load_pdf(filepath: str, source_title: str, category: str = None, source_type: str = "educational") -> List[Dict]:
    """Extract text from PDF file page by page."""
    pages = []
    try:
        with pdfplumber.open(filepath) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and text.strip():
                    pages.append({
                        "text": text.strip(),
                        "source": source_title,
                        "page_number": i + 1,
                        "category": category,
                        "source_type": source_type,
                    })
    except Exception as e:
        print(f"Warning: Could not load PDF {filepath}: {e}")
    return pages


def _load_text(filepath: str, source_title: str, category: str = None, source_type: str = "educational") -> List[Dict]:
    """Load a plain text or markdown file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read().strip()
        if text:
            return [{"text": text, "source": source_title, "page_number": 1, "category": category, "source_type": source_type}]
    except Exception as e:
        print(f"Warning: Could not load text file {filepath}: {e}")
    return []
