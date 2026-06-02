"""
Diabetes Risk Prediction — ML Service Test Suite
=================================================
Tests the hybrid prediction API (ML + Symptom + Clinical layers).

Run against the live container:
    pytest test_ml.py -v

Requires: ML service running at localhost:8000
"""

import pytest
import requests

BASE = "http://localhost:8000"


def predict(payload: dict) -> dict:
    r = requests.post(f"{BASE}/predict", json=payload, timeout=10)
    assert r.status_code == 200, f"HTTP {r.status_code}: {r.text}"
    return r.json()


def prob(payload: dict) -> float:
    return predict(payload)["risk_probability"]


# ── Fixtures ──────────────────────────────────────────────────────────

def _healthy():
    return {
        "age": 25, "gender": "Female", "bmi": 22.0,
        "high_bp": False, "high_chol": False, "physical_activity": True,
        "gen_health": 1, "diff_walking": False, "smoker": False,
        "heart_disease": False, "fruits_daily": True, "veggies_daily": True,
        "heavy_alcohol": False,
    }


def _risky():
    return {
        "age": 65, "gender": "Male", "bmi": 38.0,
        "high_bp": True, "high_chol": True, "physical_activity": False,
        "gen_health": 5, "diff_walking": True, "smoker": True,
        "heart_disease": True, "fruits_daily": False, "veggies_daily": False,
        "heavy_alcohol": True,
    }


def _moderate():
    return {
        "age": 45, "gender": "Male", "bmi": 28.0,
        "high_bp": True, "gen_health": 3,
    }


# ═══════════════════════════════════════════════════════════════════════
# 1. HEALTH & SCHEMA
# ═══════════════════════════════════════════════════════════════════════

class TestHealth:
    def test_health_endpoint(self):
        r = requests.get(f"{BASE}/health", timeout=5)
        assert r.status_code == 200
        d = r.json()
        assert d["model_loaded"] is True
        assert d["rag_ready"] is True
        assert d["shap_available"] is True

    def test_root_endpoint(self):
        r = requests.get(f"{BASE}/", timeout=5)
        assert r.status_code == 200
        assert "running" in r.json()["status"].lower()


class TestResponseSchema:
    REQUIRED_FIELDS = [
        "risk_probability", "risk_category", "confidence_level",
        "contributing_factors", "shap_values",
        "ml_score", "symptom_score", "clinical_score",
        "active_symptoms", "risk_factor_cards",
    ]

    def test_all_fields_present(self):
        d = predict({"age": 40, "gender": "Male"})
        for f in self.REQUIRED_FIELDS:
            assert f in d, f"Missing: {f}"

    def test_probability_is_float_0_to_1(self):
        d = predict({"age": 40, "gender": "Male"})
        assert isinstance(d["risk_probability"], float)
        assert 0.0 <= d["risk_probability"] <= 1.0

    def test_category_is_valid(self):
        d = predict({"age": 40, "gender": "Male"})
        assert d["risk_category"] in ("Low", "Medium", "High")

    def test_layer_scores_are_floats(self):
        d = predict({"age": 40, "gender": "Male"})
        for key in ("ml_score", "symptom_score", "clinical_score"):
            assert isinstance(d[key], float)
            assert 0.0 <= d[key] <= 1.0

    def test_active_symptoms_is_list(self):
        d = predict({"age": 40, "gender": "Male"})
        assert isinstance(d["active_symptoms"], list)

    def test_risk_factor_cards_structure(self):
        d = predict({**_moderate(), "bmi": 32.0})
        cards = d["risk_factor_cards"]
        assert len(cards) > 0
        for card in cards:
            assert "name" in card
            assert "value" in card
            assert card["status"] in ("risk", "protective", "neutral")


# ═══════════════════════════════════════════════════════════════════════
# 2. RISK SEPARATION — model must differentiate profiles
# ═══════════════════════════════════════════════════════════════════════

class TestRiskSeparation:
    def test_healthy_is_low(self):
        d = predict(_healthy())
        assert d["risk_probability"] < 0.15
        assert d["risk_category"] == "Low"

    def test_risky_is_high(self):
        d = predict(_risky())
        assert d["risk_probability"] > 0.70
        assert d["risk_category"] == "High"

    def test_high_much_greater_than_low(self):
        low = prob(_healthy())
        high = prob(_risky())
        assert high - low > 0.50

    def test_moderate_is_between(self):
        p = prob(_moderate())
        assert 0.15 < p < 0.70


# ═══════════════════════════════════════════════════════════════════════
# 3. FUSION MONOTONICITY — symptoms/clinical NEVER reduce risk
#    (This was the root cause of the "always 20-30%" bug)
# ═══════════════════════════════════════════════════════════════════════

class TestFusionMonotonicity:
    """Adding symptoms or clinical data must increase or maintain risk,
    never decrease it below the ML-only baseline."""

    def test_single_mild_symptom_does_not_reduce(self):
        """Regression: fatigue alone used to dilute ML score from 44%→31%."""
        base = prob(_moderate())
        with_fatigue = prob({**_moderate(), "fatigue": True})
        assert with_fatigue >= base, (
            f"Fatigue reduced risk: {base:.1%} → {with_fatigue:.1%}"
        )

    def test_single_mild_symptom_increases(self):
        base = prob(_moderate())
        with_fatigue = prob({**_moderate(), "fatigue": True})
        assert with_fatigue > base

    def test_multiple_symptoms_increase(self):
        base = prob(_moderate())
        with_syms = prob({
            **_moderate(),
            "polyuria": True, "polydipsia": True, "fatigue": True,
        })
        assert with_syms > base + 0.10

    def test_glucose_does_not_reduce(self):
        base = prob(_moderate())
        with_glucose = prob({**_moderate(), "blood_glucose": 110.0})
        assert with_glucose >= base

    def test_hba1c_does_not_reduce(self):
        base = prob(_moderate())
        with_hba1c = prob({**_moderate(), "hba1c": 6.0})
        assert with_hba1c >= base

    def test_symptoms_plus_clinical_does_not_reduce(self):
        base = prob(_moderate())
        full = prob({
            **_moderate(),
            "fatigue": True, "polyuria": True,
            "blood_glucose": 120.0,
        })
        assert full >= base

    @pytest.mark.parametrize("symptom", [
        "polyuria", "polydipsia", "unexplained_weight_loss",
        "fatigue", "blurred_vision", "slow_healing",
        "frequent_infections", "tingling_numbness",
    ])
    def test_each_symptom_individually(self, symptom):
        base = prob(_moderate())
        with_sym = prob({**_moderate(), symptom: True})
        assert with_sym >= base, f"{symptom} reduced risk"


# ═══════════════════════════════════════════════════════════════════════
# 4. ML MODEL MONOTONICITY — risk factors directionally correct
# ═══════════════════════════════════════════════════════════════════════

class TestMLMonotonicity:
    BASE = {
        "age": 40, "gender": "Male", "bmi": 25.0,
        "high_bp": False, "high_chol": False, "physical_activity": True,
        "gen_health": 3, "diff_walking": False, "smoker": False,
    }

    def _p(self, **kw):
        return prob({**self.BASE, **kw})

    def test_high_bp_increases(self):
        assert self._p(high_bp=True) >= self._p(high_bp=False)

    def test_high_chol_increases(self):
        assert self._p(high_chol=True) >= self._p(high_chol=False)

    def test_higher_bmi_increases(self):
        assert self._p(bmi=40.0) > self._p(bmi=22.0)

    def test_worse_health_increases(self):
        assert self._p(gen_health=5) > self._p(gen_health=1)

    def test_older_age_increases(self):
        assert self._p(age=75) > self._p(age=25)

    def test_no_activity_increases(self):
        assert self._p(physical_activity=False) >= self._p(physical_activity=True)

    def test_smoker_increases(self):
        assert self._p(smoker=True) >= self._p(smoker=False)


# ═══════════════════════════════════════════════════════════════════════
# 5. CLINICAL THRESHOLDS (ADA 2024)
# ═══════════════════════════════════════════════════════════════════════

class TestClinicalThresholds:
    def test_normal_glucose_low_score(self):
        d = predict({**_moderate(), "blood_glucose": 85.0})
        assert d["clinical_score"] < 0.15

    def test_prediabetic_glucose_moderate_score(self):
        d = predict({**_moderate(), "blood_glucose": 115.0})
        assert 0.30 < d["clinical_score"] < 0.75

    def test_diabetic_glucose_high_score(self):
        d = predict({**_moderate(), "blood_glucose": 200.0})
        assert d["clinical_score"] >= 0.85

    def test_normal_hba1c_low_score(self):
        d = predict({**_moderate(), "hba1c": 5.0})
        assert d["clinical_score"] < 0.15

    def test_prediabetic_hba1c_moderate_score(self):
        d = predict({**_moderate(), "hba1c": 6.0})
        assert 0.30 < d["clinical_score"] < 0.75

    def test_diabetic_hba1c_high_score(self):
        d = predict({**_moderate(), "hba1c": 7.5})
        assert d["clinical_score"] >= 0.90

    def test_diabetic_clinical_pushes_risk_high(self):
        d = predict({**_moderate(), "blood_glucose": 200.0})
        assert d["risk_probability"] > 0.60
        assert d["risk_category"] == "High"


# ═══════════════════════════════════════════════════════════════════════
# 6. SYMPTOM SCORING
# ═══════════════════════════════════════════════════════════════════════

class TestSymptomScoring:
    def test_no_symptoms_zero(self):
        d = predict({"age": 40, "gender": "Male"})
        assert d["symptom_score"] == 0.0
        assert d["active_symptoms"] == []

    def test_single_symptom_nonzero(self):
        d = predict({"age": 40, "gender": "Male", "fatigue": True})
        assert d["symptom_score"] > 0.0
        assert len(d["active_symptoms"]) == 1

    def test_classic_triad_high(self):
        d = predict({
            "age": 40, "gender": "Male",
            "polyuria": True, "polydipsia": True,
            "unexplained_weight_loss": True,
        })
        assert d["symptom_score"] > 0.55

    def test_all_symptoms_near_max(self):
        d = predict({
            "age": 40, "gender": "Male",
            "polyuria": True, "polydipsia": True,
            "unexplained_weight_loss": True, "fatigue": True,
            "blurred_vision": True, "slow_healing": True,
            "frequent_infections": True, "tingling_numbness": True,
        })
        assert d["symptom_score"] > 0.85

    def test_symptom_count_matches_active(self):
        d = predict({
            "age": 40, "gender": "Male",
            "polyuria": True, "fatigue": True, "blurred_vision": True,
        })
        assert len(d["active_symptoms"]) == 3


# ═══════════════════════════════════════════════════════════════════════
# 7. CONFIDENCE LEVEL
# ═══════════════════════════════════════════════════════════════════════

class TestConfidenceLevel:
    def test_only_risk_factors_is_low(self):
        d = predict(_moderate())
        assert d["confidence_level"] == "low"

    def test_with_symptoms_is_moderate(self):
        d = predict({**_moderate(), "fatigue": True})
        assert d["confidence_level"] == "moderate"

    def test_with_clinical_is_high(self):
        d = predict({**_moderate(), "blood_glucose": 100.0})
        assert d["confidence_level"] == "high"

    def test_symptoms_and_clinical_is_very_high(self):
        d = predict({
            **_moderate(), "fatigue": True, "blood_glucose": 100.0,
        })
        assert d["confidence_level"] == "very_high"


# ═══════════════════════════════════════════════════════════════════════
# 8. RISK CATEGORY ALIGNMENT
# ═══════════════════════════════════════════════════════════════════════

class TestRiskCategoryAlignment:
    """Category must be consistent with probability thresholds."""

    @pytest.mark.parametrize("payload", [
        {"age": 25, "gender": "Female", "bmi": 21.0, "gen_health": 1},
        _moderate(),
        _risky(),
        {**_moderate(), "polyuria": True, "polydipsia": True, "fatigue": True},
        {**_moderate(), "blood_glucose": 200.0, "hba1c": 8.0},
    ])
    def test_category_matches_probability(self, payload):
        d = predict(payload)
        p = d["risk_probability"]
        cat = d["risk_category"]
        if p < 0.30:
            assert cat == "Low", f"p={p:.2f} should be Low, got {cat}"
        elif p < 0.60:
            assert cat == "Medium", f"p={p:.2f} should be Medium, got {cat}"
        else:
            assert cat == "High", f"p={p:.2f} should be High, got {cat}"


# ═══════════════════════════════════════════════════════════════════════
# 9. DETERMINISM
# ═══════════════════════════════════════════════════════════════════════

class TestDeterminism:
    def test_same_input_same_output(self):
        payload = {**_moderate(), "fatigue": True, "blood_glucose": 110.0}
        results = [prob(payload) for _ in range(5)]
        assert all(r == results[0] for r in results), f"Non-deterministic: {results}"


# ═══════════════════════════════════════════════════════════════════════
# 10. SHAP VALUES
# ═══════════════════════════════════════════════════════════════════════

class TestShapValues:
    def test_shap_present_with_features(self):
        d = predict({**_moderate(), "bmi": 32.0, "smoker": True})
        assert d["shap_values"] is not None
        assert len(d["shap_values"]) > 0

    def test_shap_only_for_provided_features(self):
        """Only age+gender → should have exactly 2 SHAP entries."""
        d = predict({"age": 40, "gender": "Male"})
        assert d["shap_values"] is not None
        assert len(d["shap_values"]) == 2


# ═══════════════════════════════════════════════════════════════════════
# 11. INPUT VALIDATION
# ═══════════════════════════════════════════════════════════════════════

class TestValidation:
    def test_invalid_gender(self):
        r = requests.post(f"{BASE}/predict", json={"age": 40, "gender": "other"})
        assert r.status_code == 422

    def test_age_zero(self):
        r = requests.post(f"{BASE}/predict", json={"age": 0, "gender": "Male"})
        assert r.status_code == 422

    def test_age_over_120(self):
        r = requests.post(f"{BASE}/predict", json={"age": 121, "gender": "Male"})
        assert r.status_code == 422

    def test_missing_gender(self):
        r = requests.post(f"{BASE}/predict", json={"age": 40})
        assert r.status_code == 422

    def test_missing_age(self):
        r = requests.post(f"{BASE}/predict", json={"gender": "Male"})
        assert r.status_code == 422

    def test_gen_health_out_of_range(self):
        r = requests.post(f"{BASE}/predict", json={"age": 40, "gender": "Male", "gen_health": 6})
        assert r.status_code == 422


# ═══════════════════════════════════════════════════════════════════════
# 12. RAG ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════

class TestRAG:
    def test_rag_status_ready(self):
        r = requests.get(f"{BASE}/rag/status", timeout=5)
        assert r.status_code == 200
        d = r.json()
        assert d["ready"] is True
        assert d["indexed_chunks"] > 0

    def test_rag_retrieve_returns_results(self):
        r = requests.post(
            f"{BASE}/rag/retrieve",
            json={"query": "diyabet belirtileri nelerdir", "top_k": 3},
            timeout=10,
        )
        assert r.status_code == 200
        results = r.json()
        assert len(results) > 0
        assert "text" in results[0]
        assert "source" in results[0]
        assert "score" in results[0]
