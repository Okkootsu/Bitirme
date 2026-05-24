"""
Offline script to build the FAISS index from knowledge base documents.
Run: python scripts/build_index.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rag.config import KNOWLEDGE_BASE_DIR
from rag.document_loader import load_documents
from rag.chunker import chunk_documents
from rag.embeddings import EmbeddingService
from rag.vector_store import VectorStore


def main():
    print("=" * 60)
    print("RAG Index Builder")
    print("=" * 60)

    # 1. Load documents
    print(f"\n[1/4] Loading documents from: {KNOWLEDGE_BASE_DIR}")
    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        print(f"ERROR: Knowledge base directory not found: {KNOWLEDGE_BASE_DIR}")
        print("Skipping index build. RAG will start without an index.")
        return

    documents = load_documents(KNOWLEDGE_BASE_DIR)
    if not documents:
        print("WARNING: No documents found in knowledge base. Skipping index build.")
        return

    print(f"   Loaded {len(documents)} document pages.")

    # 2. Chunk documents
    print(f"\n[2/4] Chunking documents...")
    chunks = chunk_documents(documents)
    print(f"   Created {len(chunks)} chunks.")

    if not chunks:
        print("WARNING: No chunks created. Skipping index build.")
        return

    # 3. Generate embeddings
    print(f"\n[3/4] Generating embeddings...")
    embedding_service = EmbeddingService()
    texts = [chunk["text"] for chunk in chunks]
    embeddings = embedding_service.embed_texts(texts)
    print(f"   Generated {embeddings.shape[0]} embeddings (dim={embeddings.shape[1]}).")

    # 4. Build and save FAISS index
    print(f"\n[4/4] Building FAISS index...")
    vector_store = VectorStore()
    vector_store.build_index(chunks, embeddings)
    vector_store.save()

    print("\n" + "=" * 60)
    print(f"Index build complete! {len(chunks)} chunks indexed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
