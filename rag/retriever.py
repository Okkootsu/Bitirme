from typing import List, Dict

from .config import TOP_K, MIN_SCORE_THRESHOLD
from .embeddings import EmbeddingService
from .vector_store import VectorStore


class RAGRetriever:
    """Orchestrates the RAG retrieval pipeline."""

    def __init__(self):
        self._embedding_service = EmbeddingService()
        self._vector_store = VectorStore()
        self._loaded = self._vector_store.load()

        if self._loaded:
            print(f"RAG retriever ready: {self._vector_store.chunk_count} chunks indexed.")
        else:
            print("WARNING: No FAISS index found. RAG retrieval will return empty results.")

    @property
    def chunk_count(self) -> int:
        return self._vector_store.chunk_count

    @property
    def is_ready(self) -> bool:
        return self._loaded and self._vector_store.chunk_count > 0

    def retrieve(self, query: str, top_k: int = TOP_K) -> List[Dict]:
        """
        Retrieve relevant document chunks for a query.
        Returns list of dicts: {text, source, score}
        """
        if not self.is_ready:
            return []

        query_embedding = self._embedding_service.embed_query(query)
        results = self._vector_store.search(query_embedding, top_k)

        retrieved = []
        for chunk, score in results:
            if score < MIN_SCORE_THRESHOLD:
                continue
            retrieved.append({
                "text": chunk["text"],
                "source": chunk["source"],
                "score": round(score, 4),
            })

        return retrieved
