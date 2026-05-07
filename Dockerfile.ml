FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn pandas scikit-learn==1.6.1 joblib

COPY api.py diabetes_model.pkl label_encoder.pkl ./

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
