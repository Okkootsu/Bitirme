import os

EMBEDDING_MODEL = "intfloat/multilingual-e5-base"
EMBEDDING_DIM = 768

CHUNK_SIZE = 512
CHUNK_OVERLAP = 64

TOP_K = 5
MIN_SCORE_THRESHOLD = 0.45

FAISS_INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "faiss_index", "index.faiss")
CHUNKS_PATH = os.path.join(os.path.dirname(__file__), "..", "faiss_index", "chunks.json")
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge_base")
ONNX_MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "onnx_model")
