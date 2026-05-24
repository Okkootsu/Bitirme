"""
Diabetes Risk Prediction ML System - Comprehensive Test Suite
=============================================================
Tests: unit (helper functions), integration (API endpoint),
       monotonicity, determinism, clinical validity, feature consistency.

Run:  pytest test_ml.py -v
"""

import ast
import json
import os
import re
import sys

import pytest
import pandas as pd

# ---------------------------------------------------------------------------
# Guard: api.py calls sys.exit(1) if diabetes_model.pkl is missing.
# Check BEFORE importing so the test process doesn't die.
# ---------------------------------------------------------------------------
_ROOT = os.path.dirname(os.path.abspath(__file__))
_MODEL_PATH = os.path.join(_ROOT, "diabetes_model.pkl")
_FI_PATH = os.path.join(_ROOT, "feature_importance.json")
_REPORT_PATH = os.path.join(_ROOT, "model_report.json")

if not os.path.exists(_MODEL_PATH):
    pytest.skip(
        "diabetes_model.pkl not found - skipping all ML tests",
        allow_module_level=True,
    )

# Now safe to import
from api import (
    app,
    FEATURE_COLS,
    _bool_to_float,
    _age_to_brfss_category,
    _apply_clinical_rules,
    _get_risk_category,
    _get_contributing_factors,
)
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Fixtures & helpers
# ---------------------------------------------------------------------------
_SAFE_ROW = {
    "HighBP": 0.0, "HighChol": 0.0, "BMI": 22.0, "Smoker": 0.0,
    "HeartDiseaseorAttack": 0.0, "PhysActivity": 1.0, "Fruits": 1.0,
    "Veggies": 1.0, "HvyAlcoholConsump": 0.0, "GenHlth": 1.0,
    "DiffWalk": 0.0, "Sex": 0.0, "Age": 1.0,
}


def _make_df(**overrides) -> pd.DataFrame:
    row = {**_SAFE_ROW, **overrides}
    return pd.DataFrame([row])


def _healthy_request() -> dict:
    return {
        "age": 22, "gender": "Female", "bmi": 22.0,
        "high_bp": False, "high_chol": False, "physical_activity": True,
        "gen_health": 1, "diff_walking": False, "smoker": False,
        "heart_disease": False, "fruits_daily": True, "veggies_daily": True,
        "heavy_alcohol": False,
    }


def _unhealthy_request() -> dict:
    return {
        "age": 78, "gender": "Male", "bmi": 38.0,
        "high_bp": True, "high_chol": True, "physical_activity": False,
        "gen_health": 5, "diff_walking": True, "smoker": True,
        "heart_disease": True, "fruits_daily": False, "veggies_daily": False,
        "heavy_alcohol": True,
    }


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


# ===================================================================
# 1. TestBoolToFloat
# ===================================================================
class TestBoolToFloat:
    def test_true(self):
        assert _bool_to_float(True) == 1.0

    def test_false(self):
        assert _bool_to_float(False) == 0.0

    def test_none_default(self):
        assert _bool_to_float(None) == 0.0

    def test_none_custom_default(self):
        assert _bool_to_float(None, default=1.0) == 1.0

    def test_return_type(self):
        assert isinstance(_bool_to_float(True), float)


# ===================================================================
# 2. TestAgeToBrfssCategory
# ===================================================================
class TestAgeToBrfssCategory:
    @pytest.mark.parametrize("age,expected", [
        (1, 1), (18, 1), (24, 1),       # cat 1: <25
        (25, 2), (29, 2),                # cat 2: 25-29
        (30, 3), (34, 3),                # cat 3: 30-34
        (35, 4), (39, 4),                # cat 4: 35-39
        (40, 5), (44, 5),                # cat 5: 40-44
        (45, 6), (49, 6),                # cat 6: 45-49
        (50, 7), (54, 7),                # cat 7: 50-54
        (55, 8), (59, 8),                # cat 8: 55-59
        (60, 9), (64, 9),                # cat 9: 60-64
        (65, 10), (69, 10),              # cat 10: 65-69
        (70, 11), (74, 11),              # cat 11: 70-74
        (75, 12), (79, 12),              # cat 12: 75-79
        (80, 13), (100, 13), (120, 13),  # cat 13: 80+
    ])
    def test_age_mapping(self, age, expected):
        assert _age_to_brfss_category(age) == expected


# ===================================================================
# 3. TestApplyClinicalRules
# ===================================================================
class TestApplyClinicalRules:
    # --- No clinical data ---
    def test_no_clinical_data(self):
        assert _apply_clinical_rules(0.5, None, None) == 0.5

    # --- Glucose only ---
    @pytest.mark.parametrize("prob,glucose,expected", [
        (0.3, 90.0, 0.3),       # normal: no change
        (0.3, 99.0, 0.3),       # just below prediabetes
        (0.3, 100.0, 0.3),      # boundary: boost = 0
        (0.3, 110.0, 0.33),     # prediabetes: +0.03
        (0.3, 125.0, 0.375),    # top prediabetes: +0.075
        (0.3, 126.0, 0.85),     # diabetes threshold
        (0.3, 200.0, 0.85),     # well above threshold
        (0.95, 126.0, 0.95),    # model already higher
    ])
    def test_glucose(self, prob, glucose, expected):
        result = _apply_clinical_rules(prob, glucose, None)
        assert result == pytest.approx(expected, abs=1e-6)

    # --- HbA1c only ---
    @pytest.mark.parametrize("prob,hba1c,expected", [
        (0.3, 5.0, 0.3),        # normal
        (0.3, 5.6, 0.3),        # just below prediabetes
        (0.3, 5.7, 0.3),        # boundary: boost = 0
        (0.3, 6.0, 0.33),       # prediabetes: (0.3/3)*0.3 = 0.03
        (0.3, 6.5, 0.90),       # diabetes threshold
        (0.3, 8.0, 0.90),       # well above
        (0.95, 6.5, 0.95),      # model already higher
    ])
    def test_hba1c(self, prob, hba1c, expected):
        result = _apply_clinical_rules(prob, None, hba1c)
        assert result == pytest.approx(expected, abs=1e-6)

    # --- Both ---
    def test_both_diabetes(self):
        # glucose sets to 0.85, then hba1c sets to max(0.85, 0.90) = 0.90
        result = _apply_clinical_rules(0.3, 130.0, 7.0)
        assert result == pytest.approx(0.90, abs=1e-6)

    def test_both_prediabetes(self):
        # glucose boost: (110-100)/100 * 0.3 = 0.03, then hba1c boost: (6.0-5.7)/3.0 * 0.3 = 0.03
        base = 0.3
        after_glucose = base + 0.03
        after_hba1c = after_glucose + 0.03
        result = _apply_clinical_rules(0.3, 110.0, 6.0)
        assert result == pytest.approx(after_hba1c, abs=1e-6)

    def test_prediabetes_capped_at_1(self):
        result = _apply_clinical_rules(0.95, 125.0, 6.4)
        assert result <= 1.0


# ===================================================================
# 4. TestGetRiskCategory
# ===================================================================
class TestGetRiskCategory:
    @pytest.mark.parametrize("prob,expected", [
        (0.0, "Low"),
        (0.29, "Low"),
        (0.30, "Medium"),
        (0.59, "Medium"),
        (0.60, "High"),
        (1.0, "High"),
    ])
    def test_boundaries(self, prob, expected):
        assert _get_risk_category(prob) == expected


# ===================================================================
# 5. TestGetContributingFactors
# ===================================================================
class TestGetContributingFactors:
    def test_no_risk_factors_returns_fallback(self):
        df = _make_df()  # all safe defaults
        factors = _get_contributing_factors(df)
        assert factors == ["Genel risk profili de\u011ferlendirildi"]

    def test_high_bmi_30(self):
        df = _make_df(BMI=30.0)
        factors = _get_contributing_factors(df)
        assert any("BMI" in f for f in factors)

    def test_bmi_29_9_no_trigger(self):
        df = _make_df(BMI=29.9)
        factors = _get_contributing_factors(df)
        assert not any("BMI" in f for f in factors)

    def test_high_bp(self):
        df = _make_df(HighBP=1.0)
        factors = _get_contributing_factors(df)
        assert "Y\u00fcksek tansiyon" in factors

    def test_smoker(self):
        df = _make_df(Smoker=1.0)
        factors = _get_contributing_factors(df)
        assert "Sigara kullan\u0131m\u0131" in factors

    def test_phys_activity_zero_is_risk(self):
        df = _make_df(PhysActivity=0.0)
        factors = _get_contributing_factors(df)
        assert "Fiziksel aktivite eksikli\u011fi" in factors

    def test_phys_activity_one_no_risk(self):
        df = _make_df(PhysActivity=1.0)
        factors = _get_contributing_factors(df)
        assert "Fiziksel aktivite eksikli\u011fi" not in factors

    def test_gen_health_4_is_risk(self):
        df = _make_df(GenHlth=4.0)
        factors = _get_contributing_factors(df)
        assert "K\u00f6t\u00fc genel sa\u011fl\u0131k durumu" in factors

    def test_gen_health_3_no_risk(self):
        df = _make_df(GenHlth=3.0)
        factors = _get_contributing_factors(df)
        assert "K\u00f6t\u00fc genel sa\u011fl\u0131k durumu" not in factors

    def test_age_9_is_risk(self):
        df = _make_df(Age=9.0)
        factors = _get_contributing_factors(df)
        assert "\u0130leri ya\u015f" in factors

    def test_age_8_no_risk(self):
        df = _make_df(Age=8.0)
        factors = _get_contributing_factors(df)
        assert "\u0130leri ya\u015f" not in factors

    def test_max_5_factors(self):
        df = _make_df(
            HighBP=1.0, HighChol=1.0, BMI=40.0, Smoker=1.0,
            HeartDiseaseorAttack=1.0, PhysActivity=0.0,
            GenHlth=5.0, DiffWalk=1.0, Age=13.0, HvyAlcoholConsump=1.0,
        )
        factors = _get_contributing_factors(df)
        assert len(factors) <= 5

    def test_importance_ordering(self):
        # HighBP (importance 0.186) should come before Smoker (0.015)
        df = _make_df(HighBP=1.0, Smoker=1.0)
        factors = _get_contributing_factors(df)
        bp_idx = factors.index("Y\u00fcksek tansiyon")
        smoker_idx = factors.index("Sigara kullan\u0131m\u0131")
        assert bp_idx < smoker_idx


# ===================================================================
# 6. TestPredictEndpoint
# ===================================================================
class TestPredictEndpoint:
    # --- Schema ---
    def test_response_schema(self, client):
        resp = client.post("/predict", json={"age": 40, "gender": "Male"})
        assert resp.status_code == 200
        data = resp.json()
        assert "risk_probability" in data
        assert "risk_category" in data
        assert "confidence_level" in data
        assert "contributing_factors" in data

    def test_risk_probability_range(self, client):
        resp = client.post("/predict", json={"age": 40, "gender": "Male"})
        prob = resp.json()["risk_probability"]
        assert 0.0 <= prob <= 1.0

    def test_risk_category_values(self, client):
        for req in [{"age": 22, "gender": "Female"}, {"age": 80, "gender": "Male"}]:
            cat = client.post("/predict", json=req).json()["risk_category"]
            assert cat in ("Low", "Medium", "High")

    def test_confidence_values(self, client):
        resp = client.post("/predict", json={"age": 40, "gender": "Male"})
        assert resp.json()["confidence_level"] in ("high", "moderate")

    def test_contributing_factors_is_list(self, client):
        resp = client.post("/predict", json={"age": 40, "gender": "Male"})
        factors = resp.json()["contributing_factors"]
        assert isinstance(factors, list)
        assert all(isinstance(f, str) for f in factors)

    # --- Minimum fields ---
    def test_minimum_fields_ok(self, client):
        resp = client.post("/predict", json={"age": 40, "gender": "Male"})
        assert resp.status_code == 200

    def test_minimum_fields_confidence_moderate(self, client):
        resp = client.post("/predict", json={"age": 40, "gender": "Male"})
        assert resp.json()["confidence_level"] == "moderate"

    # --- Profiles ---
    def test_healthy_profile_lower_risk(self, client):
        resp = client.post("/predict", json=_healthy_request())
        assert resp.status_code == 200
        assert resp.json()["risk_probability"] < 0.45

    def test_unhealthy_profile_higher_risk(self, client):
        resp = client.post("/predict", json=_unhealthy_request())
        assert resp.status_code == 200
        assert resp.json()["risk_probability"] > 0.50

    # --- Clinical overrides ---
    def test_glucose_override_high(self, client):
        req = {**_healthy_request(), "blood_glucose": 130.0}
        data = client.post("/predict", json=req).json()
        assert data["risk_probability"] >= 0.85
        assert data["risk_category"] == "High"

    def test_hba1c_override_high(self, client):
        req = {**_healthy_request(), "hba1c": 7.0}
        data = client.post("/predict", json=req).json()
        assert data["risk_probability"] >= 0.90
        assert data["risk_category"] == "High"

    def test_prediabetes_glucose_boost(self, client):
        base = client.post("/predict", json=_healthy_request()).json()["risk_probability"]
        boosted_req = {**_healthy_request(), "blood_glucose": 115.0}
        boosted = client.post("/predict", json=boosted_req).json()["risk_probability"]
        assert boosted >= base

    def test_prediabetes_hba1c_boost(self, client):
        base = client.post("/predict", json=_healthy_request()).json()["risk_probability"]
        boosted_req = {**_healthy_request(), "hba1c": 6.2}
        boosted = client.post("/predict", json=boosted_req).json()["risk_probability"]
        assert boosted >= base

    # --- Confidence level ---
    def test_confidence_high_with_booleans(self, client):
        req = {
            "age": 40, "gender": "Male",
            "heart_disease": False, "fruits_daily": False,
            "veggies_daily": False, "heavy_alcohol": False,
        }
        assert client.post("/predict", json=req).json()["confidence_level"] == "high"

    def test_confidence_high_with_clinical(self, client):
        req = {"age": 40, "gender": "Male", "blood_glucose": 90.0, "hba1c": 5.0}
        assert client.post("/predict", json=req).json()["confidence_level"] == "high"

    def test_confidence_moderate_one_tier2(self, client):
        req = {"age": 40, "gender": "Male", "blood_glucose": 90.0}
        assert client.post("/predict", json=req).json()["confidence_level"] == "moderate"

    # --- BMI computation ---
    def test_bmi_from_height_weight(self, client):
        req = {"age": 40, "gender": "Male", "height_cm": 175, "weight_kg": 85}
        assert client.post("/predict", json=req).status_code == 200

    def test_bmi_default_no_risk(self, client):
        # Default BMI = 28.0 < 30, so no "BMI" in contributing factors
        resp = client.post("/predict", json={"age": 40, "gender": "Male"})
        factors = resp.json()["contributing_factors"]
        assert not any("BMI" in f for f in factors)

    # --- Edge cases ---
    def test_age_1(self, client):
        assert client.post("/predict", json={"age": 1, "gender": "Male"}).status_code == 200

    def test_age_120(self, client):
        assert client.post("/predict", json={"age": 120, "gender": "Female"}).status_code == 200

    def test_bmi_extreme_high(self, client):
        req = {"age": 40, "gender": "Male", "bmi": 70.0}
        data = client.post("/predict", json=req).json()
        assert any("BMI" in f for f in data["contributing_factors"])

    # --- Validation errors ---
    def test_age_0_invalid(self, client):
        assert client.post("/predict", json={"age": 0, "gender": "Male"}).status_code == 422

    def test_age_121_invalid(self, client):
        assert client.post("/predict", json={"age": 121, "gender": "Male"}).status_code == 422

    def test_age_negative_invalid(self, client):
        assert client.post("/predict", json={"age": -5, "gender": "Male"}).status_code == 422

    def test_gender_invalid(self, client):
        assert client.post("/predict", json={"age": 40, "gender": "Other"}).status_code == 422

    def test_gender_lowercase_invalid(self, client):
        assert client.post("/predict", json={"age": 40, "gender": "male"}).status_code == 422

    def test_gen_health_0_invalid(self, client):
        assert client.post("/predict", json={"age": 40, "gender": "Male", "gen_health": 0}).status_code == 422

    def test_gen_health_6_invalid(self, client):
        assert client.post("/predict", json={"age": 40, "gender": "Male", "gen_health": 6}).status_code == 422

    def test_missing_age(self, client):
        assert client.post("/predict", json={"gender": "Male"}).status_code == 422

    def test_missing_gender(self, client):
        assert client.post("/predict", json={"age": 40}).status_code == 422


# ===================================================================
# 7. TestDeterminism
# ===================================================================
class TestDeterminism:
    def test_same_input_same_output(self, client):
        req = {**_healthy_request(), "bmi": 27.0, "gen_health": 3}
        probs = []
        for _ in range(5):
            prob = client.post("/predict", json=req).json()["risk_probability"]
            probs.append(prob)
        assert all(p == probs[0] for p in probs), f"Non-deterministic: {probs}"


# ===================================================================
# 8. TestMonotonicity
# ===================================================================
class TestMonotonicity:
    """Adding risk factors should increase (or at least not decrease) probability."""

    def _prob(self, client, **extra):
        req = {
            "age": 40, "gender": "Male", "bmi": 25.0,
            "high_bp": False, "high_chol": False, "physical_activity": True,
            "gen_health": 3, "diff_walking": False, "smoker": False,
            "heart_disease": False, "fruits_daily": True, "veggies_daily": True,
            "heavy_alcohol": False,
        }
        req.update(extra)
        return client.post("/predict", json=req).json()["risk_probability"]

    def test_high_bp_increases(self, client):
        assert self._prob(client, high_bp=True) >= self._prob(client, high_bp=False)

    def test_high_chol_increases(self, client):
        assert self._prob(client, high_chol=True) >= self._prob(client, high_chol=False)

    def test_higher_bmi_increases(self, client):
        assert self._prob(client, bmi=40.0) >= self._prob(client, bmi=22.0)

    def test_worse_gen_health_increases(self, client):
        assert self._prob(client, gen_health=5) >= self._prob(client, gen_health=1)

    def test_older_age_increases(self, client):
        assert self._prob(client, age=75) >= self._prob(client, age=22)

    def test_no_physical_activity_increases(self, client):
        assert self._prob(client, physical_activity=False) >= self._prob(client, physical_activity=True)

    def test_cumulative_risk_overall_trend(self, client):
        # Baseline (no risk) vs all major risk factors active.
        # Individual steps may not be strictly monotonic due to feature
        # interactions in the ensemble, but the overall trend must hold.
        p_baseline = self._prob(client)
        p_all = self._prob(
            client, high_bp=True, high_chol=True, smoker=True, gen_health=5,
        )
        assert p_all > p_baseline


# ===================================================================
# 9. TestRiskCategoryAlignment
# ===================================================================
class TestRiskCategoryAlignment:
    def _check(self, data):
        prob = data["risk_probability"]
        cat = data["risk_category"]
        if prob < 0.30:
            assert cat == "Low", f"prob={prob}, expected Low, got {cat}"
        elif prob < 0.60:
            assert cat == "Medium", f"prob={prob}, expected Medium, got {cat}"
        else:
            assert cat == "High", f"prob={prob}, expected High, got {cat}"

    def test_healthy(self, client):
        data = client.post("/predict", json=_healthy_request()).json()
        self._check(data)

    def test_unhealthy(self, client):
        data = client.post("/predict", json=_unhealthy_request()).json()
        self._check(data)

    def test_neutral(self, client):
        data = client.post("/predict", json={"age": 40, "gender": "Male"}).json()
        self._check(data)


# ===================================================================
# 10. TestClinicalValidity
# ===================================================================
class TestClinicalValidity:
    def test_young_healthy_low_risk(self, client):
        data = client.post("/predict", json=_healthy_request()).json()
        assert data["risk_category"] in ("Low", "Medium")
        assert data["risk_probability"] < 0.45

    def test_elderly_multimorbid_high_risk(self, client):
        data = client.post("/predict", json=_unhealthy_request()).json()
        assert data["risk_category"] == "High"
        assert data["risk_probability"] > 0.55

    def test_glucose_override_trumps_model(self, client):
        req = {**_healthy_request(), "blood_glucose": 140.0}
        data = client.post("/predict", json=req).json()
        assert data["risk_probability"] >= 0.85

    def test_hba1c_override_trumps_model(self, client):
        req = {**_healthy_request(), "hba1c": 7.5}
        data = client.post("/predict", json=req).json()
        assert data["risk_probability"] >= 0.90

    def test_prediabetes_boost_reasonable(self, client):
        req = {**_healthy_request(), "blood_glucose": 115.0}
        data = client.post("/predict", json=req).json()
        # Should be boosted but not to diabetes-level
        assert data["risk_probability"] < 0.85


# ===================================================================
# 11. TestFeatureColumnConsistency
# ===================================================================
class TestFeatureColumnConsistency:
    def test_feature_cols_count(self):
        assert len(FEATURE_COLS) == 13

    def test_feature_importance_keys_match(self):
        with open(_FI_PATH) as f:
            fi = json.load(f)
        assert set(fi.keys()) == set(FEATURE_COLS)

    def test_feature_importance_sum(self):
        with open(_FI_PATH) as f:
            fi = json.load(f)
        total = sum(fi.values())
        assert total == pytest.approx(1.0, abs=0.01)

    def test_model_report_features_match(self):
        with open(_REPORT_PATH) as f:
            report = json.load(f)
        assert report["features"] == FEATURE_COLS

    def test_model_py_feature_cols_match(self):
        model_py = os.path.join(_ROOT, "model.py")
        with open(model_py, encoding="utf-8") as f:
            source = f.read()
        # Extract FEATURE_COLS list from model.py source text
        match = re.search(
            r'FEATURE_COLS\s*=\s*\[(.*?)\]',
            source,
            re.DOTALL,
        )
        assert match, "FEATURE_COLS not found in model.py"
        # Parse the content: extract quoted strings
        raw = match.group(1)
        features = re.findall(r'"([^"]+)"', raw)
        assert features == FEATURE_COLS
