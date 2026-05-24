# =========================
# 1. IMPORTS
# =========================
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict
import pandas as pd
import numpy as np
import json
import joblib
import sys

from rag.retriever import RAGRetriever
from rag.config import EMBEDDING_MODEL


# =========================
# 2. LOAD MODEL & RAG
# =========================
try:
    model = joblib.load("diabetes_model.pkl")
except FileNotFoundError:
    print("ERROR: diabetes_model.pkl not found. Run model.py first.", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"ERROR: Failed to load model: {e}", file=sys.stderr)
    sys.exit(1)

try:
    with open("feature_importance.json", "r") as f:
        feature_importance = json.load(f)
except FileNotFoundError:
    print("ERROR: feature_importance.json not found. Run model.py first.", file=sys.stderr)
    sys.exit(1)

rag_retriever = RAGRetriever()

# --- SHAP Explainer ---
shap_explainer = None
shap_scaler = None
try:
    import shap
    # Extract XGBoost from CalibratedClassifierCV → StackingClassifier → Pipeline
    base_pipeline = model.calibrated_classifiers_[0].estimator.estimators_[1]
    # Pipeline has steps like [('scaler', StandardScaler()), ('model', XGBClassifier())]
    if hasattr(base_pipeline, 'named_steps'):
        # Get the scaler for transforming input before SHAP
        for name, step in base_pipeline.steps:
            if hasattr(step, 'transform'):
                shap_scaler = step
        # Get the actual tree model (last step)
        tree_model = base_pipeline.steps[-1][1]
    else:
        tree_model = base_pipeline
    shap_explainer = shap.TreeExplainer(tree_model)
    print("SHAP TreeExplainer initialized successfully.", file=sys.stderr)
except Exception as e:
    print(f"WARNING: SHAP explainer could not be initialized: {e}", file=sys.stderr)
    print("SHAP values will not be available in predictions.", file=sys.stderr)

# Feature columns expected by the model (must match model.py FEATURE_COLS order)
FEATURE_COLS = [
    "HighBP", "HighChol", "BMI", "Smoker", "HeartDiseaseorAttack",
    "PhysActivity", "Fruits", "Veggies", "HvyAlcoholConsump",
    "GenHlth", "DiffWalk", "Sex", "Age",
]

# Feature name mapping (API field → display name in Turkish)
FEATURE_DISPLAY_NAMES = {
    "HighBP": "Yüksek tansiyon",
    "HighChol": "Yüksek kolesterol",
    "BMI": "Vücut kitle indeksi (BMI)",
    "Smoker": "Sigara kullanımı",
    "HeartDiseaseorAttack": "Kalp hastalığı öyküsü",
    "PhysActivity": "Fiziksel aktivite eksikliği",
    "Fruits": "Yetersiz meyve tüketimi",
    "Veggies": "Yetersiz sebze tüketimi",
    "HvyAlcoholConsump": "Ağır alkol kullanımı",
    "GenHlth": "Kötü genel sağlık durumu",
    "DiffWalk": "Yürüme zorluğu",
    "Sex": "Cinsiyet",
    "Age": "Yaş",
}

# ============================================================
# SYMPTOM WEIGHTS — derived from clinical evidence
# Sources:
#   - ADA Standards of Care 2024/2025 (diabetesjournals.org)
#   - WHO classic diabetes symptoms classification
#   - PMC9676132: ML symptom importance (n=520, SVC model)
#   - PMC12332044: Symptom prevalence in new T2DM (n=50)
#   - IDF Type 1 Diabetes symptoms (idf.org)
# ============================================================
SYMPTOM_WEIGHTS = {
    "polyuria":        0.20,  # %60 prevalence, highest ML correlation
    "polydipsia":      0.20,  # %56 prevalence, highest SVC weight
    "unexplained_weight_loss": 0.18,  # %38 prevalence, classic triad
    "fatigue":         0.12,  # %50 prevalence, glucose utilization deficit
    "blurred_vision":  0.12,  # %26 prevalence, lens osmotic changes
    "slow_healing":    0.10,  # %16 prevalence, microvascular impairment
    "frequent_infections": 0.05,  # immune dysfunction marker
    "tingling_numbness":   0.03,  # peripheral neuropathy, late sign
}

SYMPTOM_DISPLAY_NAMES = {
    "polyuria": "Sık idrara çıkma (poliüri)",
    "polydipsia": "Aşırı susama (polidipsi)",
    "unexplained_weight_loss": "Açıklanamayan kilo kaybı",
    "fatigue": "Yorgunluk / halsizlik",
    "blurred_vision": "Bulanık görme",
    "slow_healing": "Yara iyileşme gecikmesi",
    "frequent_infections": "Sık enfeksiyon geçirme",
    "tingling_numbness": "Karıncalanma / uyuşma",
}


# =========================
# 3. FASTAPI INIT
# =========================
app = FastAPI(
    title="Diabetes Risk Prediction API",
    description="Hybrid ML + Symptom + Clinical diabetes risk prediction",
    version="3.0"
)


# =========================
# 4. INPUT SCHEMAS
# =========================
class PatientInput(BaseModel):
    # Required
    age: int
    gender: str  # "Male" / "Female"

    # Tier 1 - Lifestyle & health history
    bmi: Optional[float] = None
    high_bp: Optional[bool] = None
    high_chol: Optional[bool] = None
    physical_activity: Optional[bool] = None
    gen_health: Optional[int] = None  # 1-5 (1=excellent, 5=poor)
    diff_walking: Optional[bool] = None
    smoker: Optional[bool] = None

    # Tier 2 - Optional clinical/lifestyle
    heart_disease: Optional[bool] = None
    fruits_daily: Optional[bool] = None
    veggies_daily: Optional[bool] = None
    heavy_alcohol: Optional[bool] = None

    # Clinical values
    blood_glucose: Optional[float] = None  # fasting, mg/dL
    hba1c: Optional[float] = None  # percentage

    # Convenience for BMI calculation
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None

    # Symptoms (new — hybrid model)
    polyuria: Optional[bool] = None
    polydipsia: Optional[bool] = None
    unexplained_weight_loss: Optional[bool] = None
    fatigue: Optional[bool] = None
    blurred_vision: Optional[bool] = None
    slow_healing: Optional[bool] = None
    frequent_infections: Optional[bool] = None
    tingling_numbness: Optional[bool] = None

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: int) -> int:
        if v < 1 or v > 120:
            raise ValueError("age must be between 1 and 120")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        if v not in ("Male", "Female"):
            raise ValueError("gender must be 'Male' or 'Female'")
        return v

    @field_validator("gen_health")
    @classmethod
    def validate_gen_health(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 1 or v > 5):
            raise ValueError("gen_health must be between 1 and 5")
        return v

    @field_validator("height_cm")
    @classmethod
    def validate_height(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("height_cm must be positive")
        return v

    @field_validator("weight_kg")
    @classmethod
    def validate_weight(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("weight_kg must be positive")
        return v


class RiskFactorCard(BaseModel):
    name: str
    value: str
    status: str  # "risk", "protective", "neutral"
    detail: str


class PredictionResponse(BaseModel):
    risk_probability: float
    risk_category: str
    confidence_level: str
    contributing_factors: List[str]
    shap_values: Optional[Dict[str, float]] = None
    # Hybrid model layer scores
    ml_score: float
    symptom_score: float
    clinical_score: float
    active_symptoms: List[str]
    risk_factor_cards: List[RiskFactorCard]


class RAGQuery(BaseModel):
    query: str
    top_k: int = 5

    @field_validator("top_k")
    @classmethod
    def validate_top_k(cls, v: int) -> int:
        if v < 1 or v > 20:
            raise ValueError("top_k must be between 1 and 20")
        return v


class RetrievedChunk(BaseModel):
    text: str
    source: str
    score: float


# =========================
# 5. HEALTH CHECK
# =========================
@app.get("/")
def home():
    return {"status": "API is running", "model_version": "3.0-hybrid"}


@app.get("/health")
def health_check():
    """Health check endpoint for Docker/Kubernetes."""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "rag_ready": rag_retriever.is_ready,
        "shap_available": shap_explainer is not None,
    }


# =========================
# 6. PREDICT ENDPOINT
# =========================
@app.post("/predict", response_model=PredictionResponse)
def predict(data: PatientInput):

    # --- Compute BMI if not provided ---
    bmi = data.bmi
    if bmi is None and data.height_cm and data.weight_kg:
        height_m = data.height_cm / 100
        bmi = data.weight_kg / (height_m ** 2)
    if bmi is None:
        bmi = 28.0  # median from BRFSS dataset

    # --- Map age to BRFSS category (1-13) ---
    age_category = _age_to_brfss_category(data.age)

    # --- Map gender ---
    sex = 1.0 if data.gender == "Male" else 0.0

    # --- Build feature vector ---
    input_df = pd.DataFrame([{
        "HighBP": _bool_to_float(data.high_bp),
        "HighChol": _bool_to_float(data.high_chol),
        "BMI": float(bmi),
        "Smoker": _bool_to_float(data.smoker),
        "HeartDiseaseorAttack": _bool_to_float(data.heart_disease),
        "PhysActivity": _bool_to_float(data.physical_activity),
        "Fruits": _bool_to_float(data.fruits_daily),
        "Veggies": _bool_to_float(data.veggies_daily),
        "HvyAlcoholConsump": _bool_to_float(data.heavy_alcohol),
        "GenHlth": float(data.gen_health) if data.gen_health is not None else 3.0,
        "DiffWalk": _bool_to_float(data.diff_walking),
        "Sex": sex,
        "Age": float(age_category),
    }])

    # =============================================
    # LAYER 1: ML Model Score (BRFSS risk factors)
    # =============================================
    try:
        ml_score = float(model.predict_proba(input_df)[0][1])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model prediction failed: {e}")

    # --- SHAP Values (filtered to user-provided fields only) ---
    # Map FEATURE_COLS to input fields to detect which were actually provided
    user_provided_features = set()
    # Always provided
    user_provided_features.add("Sex")
    user_provided_features.add("Age")
    if data.high_bp is not None:
        user_provided_features.add("HighBP")
    if data.high_chol is not None:
        user_provided_features.add("HighChol")
    if data.bmi is not None or (data.height_cm and data.weight_kg):
        user_provided_features.add("BMI")
    if data.smoker is not None:
        user_provided_features.add("Smoker")
    if data.heart_disease is not None:
        user_provided_features.add("HeartDiseaseorAttack")
    if data.physical_activity is not None:
        user_provided_features.add("PhysActivity")
    if data.fruits_daily is not None:
        user_provided_features.add("Fruits")
    if data.veggies_daily is not None:
        user_provided_features.add("Veggies")
    if data.heavy_alcohol is not None:
        user_provided_features.add("HvyAlcoholConsump")
    if data.gen_health is not None:
        user_provided_features.add("GenHlth")
    if data.diff_walking is not None:
        user_provided_features.add("DiffWalk")

    shap_result = None
    if shap_explainer is not None:
        try:
            shap_input = input_df.copy()
            if shap_scaler is not None:
                shap_input = pd.DataFrame(
                    shap_scaler.transform(shap_input),
                    columns=FEATURE_COLS
                )
            sv = shap_explainer.shap_values(shap_input)
            shap_dict = {}
            for i, col in enumerate(FEATURE_COLS):
                # Only include features the user actually provided
                if col not in user_provided_features:
                    continue
                display_name = FEATURE_DISPLAY_NAMES.get(col, col)
                shap_dict[display_name] = round(float(sv[0][i]), 4)
            shap_result = dict(sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True))
        except Exception:
            shap_result = None

    # =============================================
    # LAYER 2: Symptom Score (rule-based, ADA/WHO)
    # =============================================
    symptom_score, active_symptoms = _calculate_symptom_score(data)

    # =============================================
    # LAYER 3: Clinical Score (ADA 2024 thresholds)
    # =============================================
    clinical_score = _calculate_clinical_score(data.blood_glucose, data.hba1c)

    # =============================================
    # WEIGHTED FUSION
    # =============================================
    final_probability = _weighted_fusion(ml_score, symptom_score, clinical_score, data)

    # --- Risk Category ---
    risk_category = _get_risk_category(final_probability)

    # --- Confidence Level ---
    confidence_level = _get_confidence_level(data)

    # --- Contributing Factors ---
    contributing_factors = _get_contributing_factors(input_df)
    # Append active symptoms to contributing factors
    for sym_key in active_symptoms:
        label = SYMPTOM_DISPLAY_NAMES.get(sym_key, sym_key)
        if label not in contributing_factors:
            contributing_factors.append(label)

    # --- Risk Factor Cards ---
    risk_factor_cards = _build_risk_factor_cards(data, bmi)

    return PredictionResponse(
        risk_probability=round(final_probability, 4),
        risk_category=risk_category,
        confidence_level=confidence_level,
        contributing_factors=contributing_factors[:8],
        shap_values=shap_result,
        ml_score=round(ml_score, 4),
        symptom_score=round(symptom_score, 4),
        clinical_score=round(clinical_score, 4),
        active_symptoms=[SYMPTOM_DISPLAY_NAMES.get(s, s) for s in active_symptoms],
        risk_factor_cards=risk_factor_cards,
    )


# =========================
# 7. RAG ENDPOINTS
# =========================
@app.post("/rag/retrieve", response_model=List[RetrievedChunk])
def rag_retrieve(data: RAGQuery):
    """Retrieve relevant document chunks for a query."""
    results = rag_retriever.retrieve(data.query, top_k=data.top_k)
    return results


@app.get("/rag/status")
def rag_status():
    """Get RAG system status."""
    return {
        "ready": rag_retriever.is_ready,
        "indexed_chunks": rag_retriever.chunk_count,
        "embedding_model": EMBEDDING_MODEL,
    }


# =========================
# 8. HELPER FUNCTIONS
# =========================
def _bool_to_float(value: Optional[bool], default: float = 0.0) -> float:
    """Convert optional bool to float (1.0/0.0)."""
    if value is None:
        return default
    return 1.0 if value else 0.0


def _age_to_brfss_category(age: int) -> int:
    """
    Map real age to BRFSS age category (1-13).
    BRFSS categories: 1=18-24, 2=25-29, 3=30-34, ..., 13=80+
    """
    if age < 25:
        return 1
    elif age < 30:
        return 2
    elif age < 35:
        return 3
    elif age < 40:
        return 4
    elif age < 45:
        return 5
    elif age < 50:
        return 6
    elif age < 55:
        return 7
    elif age < 60:
        return 8
    elif age < 65:
        return 9
    elif age < 70:
        return 10
    elif age < 75:
        return 11
    elif age < 80:
        return 12
    else:
        return 13


# =============================================
# LAYER 2: Symptom Scoring
# Sources:
#   - ADA 2024 Table 2.1: classic symptoms = polyuria, polydipsia, weight loss
#   - WHO: classic triad confirms diagnosis with random glucose >= 200 mg/dL
#   - PMC9676132: polydipsia highest SVC weight, polyuria 3rd
#   - PMC12332044: prevalence data (polyuria 60%, polydipsia 56%, fatigue 50%)
# =============================================
def _calculate_symptom_score(data: PatientInput) -> tuple[float, list[str]]:
    """
    Calculate symptom score (0.0 - 1.0) based on reported symptoms.
    Weights derived from clinical prevalence + ML feature importance.
    Classic triad (polyuria + polydipsia + weight loss) gets 30% bonus.
    """
    symptom_fields = {
        "polyuria": data.polyuria,
        "polydipsia": data.polydipsia,
        "unexplained_weight_loss": data.unexplained_weight_loss,
        "fatigue": data.fatigue,
        "blurred_vision": data.blurred_vision,
        "slow_healing": data.slow_healing,
        "frequent_infections": data.frequent_infections,
        "tingling_numbness": data.tingling_numbness,
    }

    active = [k for k, v in symptom_fields.items() if v is True]

    if not active:
        return 0.0, []

    score = sum(SYMPTOM_WEIGHTS[s] for s in active)

    # Classic triad bonus (ADA/WHO: these 3 together are highly diagnostic)
    classic_triad = {"polyuria", "polydipsia", "unexplained_weight_loss"}
    if classic_triad.issubset(set(active)):
        score = min(1.0, score * 1.3)

    return min(1.0, score), active


# =============================================
# LAYER 3: Clinical Scoring
# Sources:
#   - ADA 2024/2025 Standards of Care Table 2.1 & 2.2
#     (diabetesjournals.org/care/article/48/Supplement_1/S27)
#   - IDF 2024 Position Statement: 1-h PG thresholds
#   - TEMD 2024 Kılavuzu: same ADA thresholds adopted in Turkey
#
# Thresholds:
#   FPG: Normal <100 | Prediabetes 100-125 | Diabetes >=126 mg/dL
#   HbA1c: Normal <5.7% | Prediabetes 5.7-6.4% | Diabetes >=6.5%
# =============================================
def _calculate_clinical_score(glucose: Optional[float], hba1c: Optional[float]) -> float:
    """
    Calculate clinical score (0.0 - 1.0) from lab values using ADA thresholds.
    When both values present, takes the higher score (worst case).
    """
    glucose_score = 0.0
    hba1c_score = 0.0

    if glucose is not None:
        if glucose >= 126:
            # ADA: FPG >= 126 mg/dL = diabetes diagnostic threshold
            glucose_score = 0.90
        elif glucose >= 100:
            # ADA: FPG 100-125 = IFG (prediabetes)
            # Linear interpolation within prediabetic range
            glucose_score = 0.40 + (glucose - 100) / (125 - 100) * 0.30  # 0.40 → 0.70
        else:
            # Normal FPG < 100
            glucose_score = max(0.0, glucose / 100 * 0.15)  # slight baseline up to 0.15

    if hba1c is not None:
        if hba1c >= 6.5:
            # ADA: HbA1c >= 6.5% = diabetes diagnostic threshold
            hba1c_score = 0.95
        elif hba1c >= 5.7:
            # ADA: HbA1c 5.7-6.4% = prediabetes
            hba1c_score = 0.40 + (hba1c - 5.7) / (6.4 - 5.7) * 0.30  # 0.40 → 0.70
        else:
            # Normal HbA1c < 5.7%
            hba1c_score = max(0.0, hba1c / 5.7 * 0.15)

    # When both present, take the worse indicator
    if glucose is not None and hba1c is not None:
        return max(glucose_score, hba1c_score)
    elif glucose is not None:
        return glucose_score
    elif hba1c is not None:
        return hba1c_score
    else:
        return 0.0


# =============================================
# WEIGHTED FUSION ENGINE
# Dynamic weights based on data availability:
#   - Only risk factors     → ML 100%
#   - Risk + symptoms       → ML 60% + Symptom 40%
#   - Risk + clinical       → ML 50% + Clinical 50%
#   - All three layers      → ML 40% + Symptom 30% + Clinical 30%
# =============================================
def _weighted_fusion(
    ml_score: float,
    symptom_score: float,
    clinical_score: float,
    data: PatientInput,
) -> float:
    """
    Combine layer scores with dynamic weights based on data availability.
    """
    has_symptoms = any([
        data.polyuria, data.polydipsia, data.unexplained_weight_loss,
        data.fatigue, data.blurred_vision, data.slow_healing,
        data.frequent_infections, data.tingling_numbness,
    ])
    has_clinical = data.blood_glucose is not None or data.hba1c is not None

    if has_symptoms and has_clinical:
        # All three layers available
        final = ml_score * 0.40 + symptom_score * 0.30 + clinical_score * 0.30
    elif has_symptoms:
        # Risk factors + symptoms
        final = ml_score * 0.60 + symptom_score * 0.40
    elif has_clinical:
        # Risk factors + clinical labs
        final = ml_score * 0.50 + clinical_score * 0.50
    else:
        # Only risk factors
        final = ml_score

    return min(1.0, max(0.0, final))


# =============================================
# CONFIDENCE LEVEL (improved)
# =============================================
def _get_confidence_level(data: PatientInput) -> str:
    """
    Determine confidence level based on data completeness.
    """
    has_symptoms = any([
        data.polyuria, data.polydipsia, data.unexplained_weight_loss,
        data.fatigue, data.blurred_vision, data.slow_healing,
        data.frequent_infections, data.tingling_numbness,
    ])
    has_clinical = data.blood_glucose is not None or data.hba1c is not None

    if has_symptoms and has_clinical:
        return "very_high"
    elif has_clinical:
        return "high"
    elif has_symptoms:
        return "moderate"
    else:
        return "low"


def _get_risk_category(probability: float) -> str:
    """Map probability to risk category."""
    if probability < 0.30:
        return "Low"
    elif probability < 0.60:
        return "Medium"
    else:
        return "High"


def _build_risk_factor_cards(data: PatientInput, bmi: float) -> List[RiskFactorCard]:
    """
    Build risk factor cards for each user-provided field.
    Each card shows: name, value, status (risk/protective/neutral), detail.
    """
    cards: List[RiskFactorCard] = []

    # --- Always-provided: Age ---
    age = data.age
    if age >= 45:
        cards.append(RiskFactorCard(
            name="Yaş", value=f"{age}",
            status="risk",
            detail="45 yaş üstü diyabet riski artar (ADA 2024: tarama önerisi ≥35 yaş)"
        ))
    elif age >= 35:
        cards.append(RiskFactorCard(
            name="Yaş", value=f"{age}",
            status="neutral",
            detail="35-44 yaş arası — ADA tarama başlangıç yaşı"
        ))
    else:
        cards.append(RiskFactorCard(
            name="Yaş", value=f"{age}",
            status="protective",
            detail="35 yaş altı, yaşa bağlı risk düşük"
        ))

    # --- Always-provided: Gender ---
    if data.gender == "Male":
        cards.append(RiskFactorCard(
            name="Cinsiyet", value="Erkek",
            status="neutral",
            detail="Erkeklerde T2DM riski kadınlara göre hafif yüksek (IDF 2024)"
        ))
    else:
        cards.append(RiskFactorCard(
            name="Cinsiyet", value="Kadın",
            status="neutral",
            detail="Gestasyonel diyabet öyküsü varsa risk artabilir"
        ))

    # --- BMI (if user provided) ---
    if data.bmi is not None or (data.height_cm and data.weight_kg):
        bmi_val = round(bmi, 1)
        if bmi_val >= 30:
            cards.append(RiskFactorCard(
                name="BMI", value=f"{bmi_val}",
                status="risk",
                detail=f"Obezite (BMI ≥30) — T2DM riskini 3-7 kat artırır (WHO)"
            ))
        elif bmi_val >= 25:
            cards.append(RiskFactorCard(
                name="BMI", value=f"{bmi_val}",
                status="risk",
                detail=f"Fazla kilolu (BMI 25-29.9) — diyabet riski artmış (ADA)"
            ))
        elif bmi_val >= 18.5:
            cards.append(RiskFactorCard(
                name="BMI", value=f"{bmi_val}",
                status="protective",
                detail="Normal BMI aralığı (18.5-24.9)"
            ))
        else:
            cards.append(RiskFactorCard(
                name="BMI", value=f"{bmi_val}",
                status="neutral",
                detail="Düşük kilolu — farklı metabolik riskler olabilir"
            ))

    # --- Blood Pressure ---
    if data.high_bp is not None:
        if data.high_bp:
            cards.append(RiskFactorCard(
                name="Yüksek Tansiyon", value="Var",
                status="risk",
                detail="Hipertansiyon, insülin direnci ile ilişkilidir (ADA 2024)"
            ))
        else:
            cards.append(RiskFactorCard(
                name="Yüksek Tansiyon", value="Yok",
                status="protective",
                detail="Normal tansiyon — kardiyometabolik risk düşük"
            ))

    # --- Cholesterol ---
    if data.high_chol is not None:
        if data.high_chol:
            cards.append(RiskFactorCard(
                name="Yüksek Kolesterol", value="Var",
                status="risk",
                detail="Dislipidemi, metabolik sendrom bileşenidir (ADA/TEMD)"
            ))
        else:
            cards.append(RiskFactorCard(
                name="Yüksek Kolesterol", value="Yok",
                status="protective",
                detail="Normal kolesterol düzeyi"
            ))

    # --- Physical Activity ---
    if data.physical_activity is not None:
        if data.physical_activity:
            cards.append(RiskFactorCard(
                name="Fiziksel Aktivite", value="Düzenli",
                status="protective",
                detail="Haftada ≥150 dk aktivite T2DM riskini %58 azaltır (DPP çalışması)"
            ))
        else:
            cards.append(RiskFactorCard(
                name="Fiziksel Aktivite", value="Yetersiz",
                status="risk",
                detail="Sedanter yaşam insülin direncini artırır"
            ))

    # --- General Health ---
    if data.gen_health is not None:
        gh_labels = {1: "Mükemmel", 2: "Çok İyi", 3: "İyi", 4: "Orta", 5: "Kötü"}
        gh_val = gh_labels.get(data.gen_health, str(data.gen_health))
        if data.gen_health >= 4:
            cards.append(RiskFactorCard(
                name="Genel Sağlık", value=gh_val,
                status="risk",
                detail="Kötü genel sağlık algısı, diyabet riski ile koreledir"
            ))
        elif data.gen_health <= 2:
            cards.append(RiskFactorCard(
                name="Genel Sağlık", value=gh_val,
                status="protective",
                detail="İyi genel sağlık durumu"
            ))
        else:
            cards.append(RiskFactorCard(
                name="Genel Sağlık", value=gh_val,
                status="neutral",
                detail="Orta düzey genel sağlık"
            ))

    # --- Smoking ---
    if data.smoker is not None:
        if data.smoker:
            cards.append(RiskFactorCard(
                name="Sigara", value="Kullanıyor",
                status="risk",
                detail="Sigara T2DM riskini %30-40 artırır (CDC, ADA)"
            ))
        else:
            cards.append(RiskFactorCard(
                name="Sigara", value="Kullanmıyor",
                status="protective",
                detail="Sigara kullanmamak diyabet riskini azaltır"
            ))

    # --- Heart Disease ---
    if data.heart_disease is not None:
        if data.heart_disease:
            cards.append(RiskFactorCard(
                name="Kalp Hastalığı", value="Var",
                status="risk",
                detail="Kardiyovasküler hastalık ve T2DM birlikte sık görülür (ADA)"
            ))
        else:
            cards.append(RiskFactorCard(
                name="Kalp Hastalığı", value="Yok",
                status="protective",
                detail="Kalp hastalığı öyküsü yok"
            ))

    # --- Difficulty Walking ---
    if data.diff_walking is not None:
        if data.diff_walking:
            cards.append(RiskFactorCard(
                name="Yürüme Zorluğu", value="Var",
                status="risk",
                detail="Fiziksel kısıtlılık, sedanter yaşama yol açabilir"
            ))
        else:
            cards.append(RiskFactorCard(
                name="Yürüme Zorluğu", value="Yok",
                status="protective",
                detail="Hareket kısıtlılığı yok"
            ))

    # --- Fruits ---
    if data.fruits_daily is not None:
        if data.fruits_daily:
            cards.append(RiskFactorCard(
                name="Meyve Tüketimi", value="Her gün",
                status="protective",
                detail="Düzenli meyve tüketimi antioksidan ve lif sağlar"
            ))
        else:
            cards.append(RiskFactorCard(
                name="Meyve Tüketimi", value="Yetersiz",
                status="risk",
                detail="Yetersiz meyve tüketimi beslenme kalitesini düşürür"
            ))

    # --- Veggies ---
    if data.veggies_daily is not None:
        if data.veggies_daily:
            cards.append(RiskFactorCard(
                name="Sebze Tüketimi", value="Her gün",
                status="protective",
                detail="Düzenli sebze tüketimi insülin duyarlılığını artırır"
            ))
        else:
            cards.append(RiskFactorCard(
                name="Sebze Tüketimi", value="Yetersiz",
                status="risk",
                detail="Yetersiz sebze tüketimi metabolik risk faktörüdür"
            ))

    # --- Heavy Alcohol ---
    if data.heavy_alcohol is not None:
        if data.heavy_alcohol:
            cards.append(RiskFactorCard(
                name="Alkol Kullanımı", value="Ağır",
                status="risk",
                detail="Ağır alkol pankreatit ve insülin direnci riskini artırır"
            ))
        else:
            cards.append(RiskFactorCard(
                name="Alkol Kullanımı", value="Yok/Hafif",
                status="neutral",
                detail="Ağır alkol kullanımı yok"
            ))

    # --- Clinical: Blood Glucose ---
    if data.blood_glucose is not None:
        bg = data.blood_glucose
        if bg >= 126:
            cards.append(RiskFactorCard(
                name="Açlık Kan Şekeri", value=f"{bg} mg/dL",
                status="risk",
                detail="ADA: FPG ≥126 mg/dL diyabet tanı eşiği (doğrulama gerekir)"
            ))
        elif bg >= 100:
            cards.append(RiskFactorCard(
                name="Açlık Kan Şekeri", value=f"{bg} mg/dL",
                status="risk",
                detail="ADA: FPG 100-125 mg/dL — bozulmuş açlık glikozu (prediyabet)"
            ))
        else:
            cards.append(RiskFactorCard(
                name="Açlık Kan Şekeri", value=f"{bg} mg/dL",
                status="protective",
                detail="Normal açlık kan şekeri (<100 mg/dL)"
            ))

    # --- Clinical: HbA1c ---
    if data.hba1c is not None:
        hba = data.hba1c
        if hba >= 6.5:
            cards.append(RiskFactorCard(
                name="HbA1c", value=f"%{hba}",
                status="risk",
                detail="ADA: HbA1c ≥6.5% diyabet tanı eşiği (doğrulama gerekir)"
            ))
        elif hba >= 5.7:
            cards.append(RiskFactorCard(
                name="HbA1c", value=f"%{hba}",
                status="risk",
                detail="ADA: HbA1c 5.7-6.4% — prediyabet aralığı"
            ))
        else:
            cards.append(RiskFactorCard(
                name="HbA1c", value=f"%{hba}",
                status="protective",
                detail="Normal HbA1c düzeyi (<%5.7)"
            ))

    return cards


def _get_contributing_factors(input_df: pd.DataFrame) -> List[str]:
    """Get top contributing factors based on feature importance and input values."""
    factors = []

    # Get feature importance ranking
    importance_dict = feature_importance

    # Check each feature's contribution
    row = input_df.iloc[0]

    risk_indicators = {
        "HighBP": (row["HighBP"] == 1.0, "Yüksek tansiyon"),
        "HighChol": (row["HighChol"] == 1.0, "Yüksek kolesterol"),
        "BMI": (row["BMI"] >= 30, f"Yüksek BMI ({row['BMI']:.1f})"),
        "Smoker": (row["Smoker"] == 1.0, "Sigara kullanımı"),
        "HeartDiseaseorAttack": (row["HeartDiseaseorAttack"] == 1.0, "Kalp hastalığı öyküsü"),
        "PhysActivity": (row["PhysActivity"] == 0.0, "Fiziksel aktivite eksikliği"),
        "GenHlth": (row["GenHlth"] >= 4, "Kötü genel sağlık durumu"),
        "DiffWalk": (row["DiffWalk"] == 1.0, "Yürüme zorluğu"),
        "Age": (row["Age"] >= 9, "İleri yaş"),
        "HvyAlcoholConsump": (row["HvyAlcoholConsump"] == 1.0, "Ağır alkol kullanımı"),
    }

    # Sort by importance, pick active risk factors
    for feature in importance_dict:
        if feature in risk_indicators:
            is_risk, label = risk_indicators[feature]
            if is_risk:
                factors.append(label)
        if len(factors) >= 5:
            break

    # If no specific factors found, add general ones
    if not factors:
        factors.append("Genel risk profili değerlendirildi")

    return factors
