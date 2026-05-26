from typing import List, Dict

from .config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_documents(documents: List[Dict]) -> List[Dict]:
    """
    Split documents into smaller chunks with overlap.
    Each chunk retains source metadata.
    """
    all_chunks = []
    chunk_id = 0

    for doc in documents:
        text = doc["text"]
        source = doc["source"]
        page_number = doc["page_number"]
        category = doc.get("category")
        source_type = doc.get("source_type", "educational")

        chunks = _recursive_split(text, CHUNK_SIZE, CHUNK_OVERLAP)

        for chunk_text in chunks:
            all_chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text,
                "source": source,
                "page_number": page_number,
                "category": category,
                "source_type": source_type,
            })
            chunk_id += 1

    return all_chunks


def _recursive_split(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Split text by paragraph boundaries first, then by sentence,
    then by character count as fallback.
    """
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    # Try splitting by paragraphs
    separators = ["\n\n", "\n", ". ", " "]

    for sep in separators:
        parts = text.split(sep)
        if len(parts) > 1:
            chunks = []
            current_chunk = ""

            for part in parts:
                candidate = current_chunk + sep + part if current_chunk else part

                if len(candidate) <= chunk_size:
                    current_chunk = candidate
                else:
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    # Start new chunk with overlap from previous
                    if overlap > 0 and current_chunk:
                        overlap_text = current_chunk[-overlap:]
                        current_chunk = overlap_text + sep + part
                    else:
                        current_chunk = part

            if current_chunk.strip():
                chunks.append(current_chunk.strip())

            if chunks:
                return chunks

    # Fallback: hard split by character count
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start = end - overlap

    return [c for c in chunks if c]
