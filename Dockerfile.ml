# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# 1. Install dependencies — BuildKit cache keeps downloaded wheels locally
#    so subsequent builds don't re-download 170 MB+ of onnxruntime etc.
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install --no-deps xgboost

# 2. RAG module
COPY rag/ ./rag/

# 3. Model files (local — no download needed)
COPY diabetes_model.pkl ./
COPY onnx_model/ ./onnx_model/
COPY faiss_index/ ./faiss_index/

# 5. Static config files
COPY feature_importance.json model_report.json ./

# 6. API code (changes most often — last layer for fast rebuilds)
COPY api.py ./

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
