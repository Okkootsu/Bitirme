import json
import os
from typing import List, Dict, Tuple

import numpy as np
import faiss

from .config import FAISS_INDEX_PATH, CHUNKS_PATH, EMBEDDING_DIM


class VectorStore:
    """FAISS-based vector store for document chunks."""

    def __init__(self):
        self._index: faiss.IndexFlatIP = None
        self._chunks: List[Dict] = []

    @property
    def chunk_count(self) -> int:
        return len(self._chunks)

    def build_index(self, chunks: List[Dict], embeddings: np.ndarray) -> None:
        """Build FAISS index from chunk embeddings."""
        self._index = faiss.IndexFlatIP(EMBEDDING_DIM)
        self._index.add(embeddings)
        self._chunks = chunks

    def save(self) -> None:
        """Persist index and chunks to disk."""
        os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)

        faiss.write_index(self._index, FAISS_INDEX_PATH)

        with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
            json.dump(self._chunks, f, ensure_ascii=False, indent=2)

        print(f"Saved FAISS index ({self._index.ntotal} vectors) to {FAISS_INDEX_PATH}")

    def load(self) -> bool:
        """Load index and chunks from disk. Returns True if successful."""
        if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(CHUNKS_PATH):
            return False

        try:
            self._index = faiss.read_index(FAISS_INDEX_PATH)
            with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
                self._chunks = json.load(f)
        except Exception as e:
            print(f"Error loading FAISS index or chunks: {e}")
            self._index = None
            self._chunks = []
            return False

        print(f"Loaded FAISS index ({self._index.ntotal} vectors)")
        return True

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """
        Search for top-k similar chunks.
        Returns list of (chunk_dict, similarity_score) tuples.
        """
        if self._index is None or self._index.ntotal == 0:
            return []

        scores, indices = self._index.search(query_embedding, min(top_k, self._index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            results.append((self._chunks[idx], float(score)))

        return results
