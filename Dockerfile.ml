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

# 3. Helper scripts (model download + entrypoint)
COPY scripts/ ./scripts/
RUN chmod +x ./scripts/entrypoint.sh

# 4. Static config files
COPY feature_importance.json model_report.json ./

# 5. API code (changes most often — last layer for fast rebuilds)
COPY api.py ./

# Model files are downloaded at first start from GitHub Releases
CMD ["./scripts/entrypoint.sh"]
