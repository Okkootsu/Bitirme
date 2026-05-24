"""
Export embedding model to ONNX format for lightweight container deployment.
Requires torch + sentence-transformers (run locally or in existing container).

Usage:
    python scripts/export_onnx.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import torch
from sentence_transformers import SentenceTransformer
from rag.config import EMBEDDING_MODEL, ONNX_MODEL_DIR


def main():
    print(f"Loading model: {EMBEDDING_MODEL}")
    st_model = SentenceTransformer(EMBEDDING_MODEL)

    transformer = st_model[0].auto_model
    tokenizer = st_model[0].tokenizer

    os.makedirs(ONNX_MODEL_DIR, exist_ok=True)

    # Save tokenizer
    tokenizer.save_pretrained(ONNX_MODEL_DIR)
    print(f"Tokenizer saved to {ONNX_MODEL_DIR}")

    # Export to ONNX
    transformer.eval()
    dummy = tokenizer(
        "This is a test sentence",
        return_tensors="pt",
        padding="max_length",
        max_length=512,
        truncation=True,
    )

    onnx_path = os.path.join(ONNX_MODEL_DIR, "model.onnx")

    with torch.no_grad():
        torch.onnx.export(
            transformer,
            (dummy["input_ids"], dummy["attention_mask"]),
            onnx_path,
            input_names=["input_ids", "attention_mask"],
            output_names=["last_hidden_state"],
            dynamic_axes={
                "input_ids": {0: "batch", 1: "sequence"},
                "attention_mask": {0: "batch", 1: "sequence"},
                "last_hidden_state": {0: "batch", 1: "sequence"},
            },
            opset_version=14,
        )

    size_mb = os.path.getsize(onnx_path) / (1024 * 1024)
    print(f"ONNX model saved to {onnx_path} ({size_mb:.1f} MB)")
    print("Done!")


if __name__ == "__main__":
    main()
