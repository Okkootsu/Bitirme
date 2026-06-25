#!/bin/bash
set -e

# Verify model files are present (mounted from local ./models/)
if [ ! -f /app/model_cache/diabetes_model.pkl ]; then
    echo "ERROR: diabetes_model.pkl not found. Place model files in ./models/ directory." >&2
    exit 1
fi
if [ ! -f /app/onnx_model/model.onnx ]; then
    echo "ERROR: model.onnx not found. Place model files in ./models/ directory." >&2
    exit 1
fi
if [ ! -f /app/faiss_index/index.faiss ]; then
    echo "ERROR: index.faiss not found. Place model files in ./models/ directory." >&2
    exit 1
fi

echo "All model files found locally."

# Symlink pkl to where api.py expects it
if [ ! -f /app/diabetes_model.pkl ]; then
    ln -s /app/model_cache/diabetes_model.pkl /app/diabetes_model.pkl
fi

echo "Starting ML API server..."
exec uvicorn api:app --host 0.0.0.0 --port 8000
