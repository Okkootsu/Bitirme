FROM python:3.11-slim

WORKDIR /app

RUN pip install --upgrade pip && \
    pip install --no-cache-dir fastapi uvicorn "pandas<3" scikit-learn==1.6.1 joblib numpy

COPY model.py diabetes_risk_prediction_dataset.csv api.py ./

RUN python model.py

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
