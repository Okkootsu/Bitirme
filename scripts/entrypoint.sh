#!/bin/bash
set -e

# Download model files if not present (first run only - volumes persist them)
if [ ! -f /app/model_cache/diabetes_model.pkl ] || [ ! -f /app/onnx_model/model.onnx ]; then
    echo "First run: downloading model files from GitHub Releases..."
    python /app/scripts/download_models.py
fi

# Symlink pkl from volume to where api.py expects it
if [ ! -f /app/diabetes_model.pkl ]; then
    ln -s /app/model_cache/diabetes_model.pkl /app/diabetes_model.pkl
fi

echo "Starting ML API server..."
exec uvicorn api:app --host 0.0.0.0 --port 8000
