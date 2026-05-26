from typing import List

import numpy as np

from .config import EMBEDDING_MODEL, ONNX_MODEL_DIR

# Lokal: sentence-transformers (index building + query)
# Container: onnxruntime + tokenizers (sadece query)
try:
    from sentence_transformers import SentenceTransformer
    _BACKEND = "sentence-transformers"
except ImportError:
    import os
    import onnxruntime as ort
    from tokenizers import Tokenizer
    _BACKEND = "onnx"


class EmbeddingService:
    """Singleton wrapper — sentence-transformers (local) veya ONNX (container)."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._model = None
            cls._instance._ort_session = None
            cls._instance._tokenizer = None
        return cls._instance

    def _load(self):
        if _BACKEND == "sentence-transformers":
            print(f"Loading embedding model (sentence-transformers): {EMBEDDING_MODEL}...")
            self._model = SentenceTransformer(EMBEDDING_MODEL)
        else:
            import os as _os
            model_path = _os.path.join(ONNX_MODEL_DIR, "model.onnx")
            tokenizer_path = _os.path.join(ONNX_MODEL_DIR, "tokenizer.json")
            print(f"Loading embedding model (ONNX): {model_path}...")
            self._ort_session = ort.InferenceSession(
                model_path, providers=["CPUExecutionProvider"]
            )
            self._tokenizer = Tokenizer.from_file(tokenizer_path)
            self._tokenizer.enable_padding(pad_id=1, pad_token="<pad>")
            self._tokenizer.enable_truncation(max_length=512)
        print("Embedding model loaded.")

    @property
    def _ready(self) -> bool:
        return self._model is not None or self._ort_session is not None

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Embed document passages (index building).
        Requires sentence-transformers — run locally, not in container.
        """
        if _BACKEND != "sentence-transformers":
            raise RuntimeError(
                "embed_texts requires sentence-transformers. "
                "Run index building locally: python scripts/build_index.py"
            )
        if not self._ready:
            self._load()
        prefixed = [f"passage: {t}" for t in texts]
        embeddings = self._model.encode(prefixed, normalize_embeddings=True, show_progress_bar=True)
        return np.array(embeddings, dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a search query.
        Works with both backends.
        """
        if not self._ready:
            self._load()

        if _BACKEND == "sentence-transformers":
            prefixed = f"query: {query}"
            embedding = self._model.encode([prefixed], normalize_embeddings=True)
            return np.array(embedding, dtype=np.float32)

        return self._onnx_embed(f"query: {query}")

    def _onnx_embed(self, text: str) -> np.ndarray:
        """ONNX inference with mean pooling + L2 normalization."""
        encoded = self._tokenizer.encode(text)
        input_ids = np.array([encoded.ids], dtype=np.int64)
        attention_mask = np.array([encoded.attention_mask], dtype=np.int64)

        outputs = self._ort_session.run(
            None, {"input_ids": input_ids, "attention_mask": attention_mask}
        )

        # Mean pooling
        token_embeddings = outputs[0]  # (1, seq_len, hidden_dim)
        mask = attention_mask[:, :, np.newaxis].astype(np.float32)
        pooled = (token_embeddings * mask).sum(axis=1) / mask.sum(axis=1).clip(min=1e-9)

        # L2 normalize
        norm = np.linalg.norm(pooled, axis=1, keepdims=True).clip(min=1e-9)
        return (pooled / norm).astype(np.float32)
