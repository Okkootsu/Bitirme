# =========================
# 1. IMPORTS
# =========================
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib


# =========================
# 2. LOAD MODEL
# =========================
model = joblib.load("diabetes_model.pkl")
le = joblib.load("label_encoder.pkl")


# =========================
# 3. FASTAPI INIT
# =========================
app = FastAPI(
    title="Diabetes Risk Prediction API",
    description="Symptom-based ML model for diabetes prediction",
    version="1.0"
)


# =========================
# 4. INPUT SCHEMA
# =========================
class PatientInput(BaseModel):
    age: int
    gender: str
    polyuria: str
    polydipsia: str
    sudden_weight_loss: str
    weakness: str
    polyphagia: str
    genital_thrush: str
    visual_blurring: str
    itching: str
    irritability: str
    delayed_healing: str
    partial_paresis: str
    muscle_stiffness: str
    alopecia: str
    obesity: str


# =========================
# 5. HEALTH CHECK
# =========================
@app.get("/")
def home():
    return {"status": "API is running 🚀"}


# =========================
# 6. PREDICT ENDPOINT
# =========================
@app.post("/predict")
def predict(data: PatientInput):

    # Convert input to DataFrame with model-expected column names
    input_df = pd.DataFrame([{
        "Age": data.age,
        "Gender": data.gender,
        "Polyuria": data.polyuria,
        "Polydipsia": data.polydipsia,
        "sudden weight loss": data.sudden_weight_loss,
        "weakness": data.weakness,
        "Polyphagia": data.polyphagia,
        "Genital thrush": data.genital_thrush,
        "visual blurring": data.visual_blurring,
        "Itching": data.itching,
        "Irritability": data.irritability,
        "delayed healing": data.delayed_healing,
        "partial paresis": data.partial_paresis,
        "muscle stiffness": data.muscle_stiffness,
        "Alopecia": data.alopecia,
        "Obesity": data.obesity,
    }])

    # Prediction
    prediction = model.predict(input_df)[0]

    # Probability (if model supports it)
    probability = None
    if hasattr(model, "predict_proba"):
        probability = model.predict_proba(input_df)[0][1]

    # Decode label (0/1 → Negative/Positive)
    result = le.inverse_transform([prediction])[0]

    return {
        "prediction": result,
        "risk_probability": float(probability) if probability is not None else None
    }