import os

EMBEDDING_MODEL = "intfloat/multilingual-e5-base"
EMBEDDING_DIM = 768

CHUNK_SIZE = 1024
CHUNK_OVERLAP = 128

TOP_K = 5
MIN_SCORE_THRESHOLD = 0.45

# Hybrid search: semantic skor ağırlığı (kalan keyword'e gider)
SEMANTIC_WEIGHT = 0.55
KEYWORD_WEIGHT = 0.45

FAISS_INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "faiss_index", "index.faiss")
CHUNKS_PATH = os.path.join(os.path.dirname(__file__), "..", "faiss_index", "chunks.json")
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge_base")
ONNX_MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "onnx_model")
