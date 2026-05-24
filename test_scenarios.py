# -*- coding: utf-8 -*-
"""
Gercek Kullanici Senaryolari ile Hybrid Model + Risk Faktor Kartlari Testi
==========================================================================
- 10 senaryo: farkli yas, cinsiyet, katman kombinasyonlari
- Her senaryo icin: katman skorlari, risk kategorisi, faktor kartlari dogrulanir
"""

import requests
import sys

API = "http://localhost:8000/predict"
PASS = 0
FAIL = 0
DETAILS = []


def test(name, payload, checks):
    global PASS, FAIL
    resp = requests.post(API, json=payload, timeout=10)
    if resp.status_code != 200:
        FAIL += 1
        DETAILS.append(f"  FAIL  {name}: HTTP {resp.status_code} - {resp.text[:200]}")
        return

    d = resp.json()
    errors = []

    # Category
    if "category" in checks and d["risk_category"] != checks["category"]:
        errors.append(f"category: {d['risk_category']} != {checks['category']}")

    # Probability bounds
    prob = d["risk_probability"]
    if "prob_min" in checks and prob < checks["prob_min"]:
        errors.append(f"prob {prob:.4f} < min {checks['prob_min']}")
    if "prob_max" in checks and prob > checks["prob_max"]:
        errors.append(f"prob {prob:.4f} > max {checks['prob_max']}")

    # Layer scores
    for layer in ["ml", "sym", "clin"]:
        key_api = {"ml": "ml_score", "sym": "symptom_score", "clin": "clinical_score"}[layer]
        val = d[key_api]
        if f"{layer}_min" in checks and val < checks[f"{layer}_min"]:
            errors.append(f"{key_api} {val:.4f} < min {checks[f'{layer}_min']}")
        if f"{layer}_max" in checks and val > checks[f"{layer}_max"]:
            errors.append(f"{key_api} {val:.4f} > max {checks[f'{layer}_max']}")

    # Confidence
    if "confidence" in checks and d["confidence_level"] != checks["confidence"]:
        errors.append(f"confidence: {d['confidence_level']} != {checks['confidence']}")

    # Active symptoms count
    if "active_symptoms_min" in checks and len(d["active_symptoms"]) < checks["active_symptoms_min"]:
        errors.append(f"active_symptoms count {len(d['active_symptoms'])} < {checks['active_symptoms_min']}")

    # Risk factor cards
    cards = {c["name"]: c for c in d.get("risk_factor_cards", [])}

    if "card_names" in checks:
        for cn in checks["card_names"]:
            if cn not in cards:
                errors.append(f"missing card: '{cn}'")

    if "card_statuses" in checks:
        for cn, expected_status in checks["card_statuses"].items():
            if cn not in cards:
                errors.append(f"card '{cn}' not found for status check")
            elif cards[cn]["status"] != expected_status:
                errors.append(f"card '{cn}' status: {cards[cn]['status']} != {expected_status}")

    if "no_cards" in checks:
        for cn in checks["no_cards"]:
            if cn in cards:
                errors.append(f"unexpected card present: '{cn}'")

    # SHAP excluded
    if "shap_excluded" in checks and d.get("shap_values"):
        for excluded in checks["shap_excluded"]:
            if excluded in d["shap_values"]:
                errors.append(f"SHAP should not contain '{excluded}'")

    # Card count
    if "card_count" in checks and len(cards) != checks["card_count"]:
        errors.append(f"card count {len(cards)} != {checks['card_count']}")

    # Result
    card_summary = ", ".join(f"{c['name']}={c['status']}" for c in d.get("risk_factor_cards", []))
    if errors:
        FAIL += 1
        err_str = "; ".join(errors)
        DETAILS.append(f"  FAIL  {name}")
        DETAILS.append(f"        Prob={prob:.2%} Cat={d['risk_category']} Conf={d['confidence_level']}")
        DETAILS.append(f"        ML={d['ml_score']:.2%} Sym={d['symptom_score']:.2%} Clin={d['clinical_score']:.2%}")
        DETAILS.append(f"        Cards: [{card_summary}]")
        DETAILS.append(f"        Errors: {err_str}")
    else:
        PASS += 1
        DETAILS.append(f"  OK    {name}")
        DETAILS.append(f"        Prob={prob:.2%} Cat={d['risk_category']} Conf={d['confidence_level']}")
        DETAILS.append(f"        ML={d['ml_score']:.2%} Sym={d['symptom_score']:.2%} Clin={d['clinical_score']:.2%}")
        DETAILS.append(f"        Cards: [{card_summary}]")


# =====================================================================
# SENARYO 1: Saglikli genc — sadece risk faktorleri (Katman 1)
# =====================================================================
test("S1: Saglikli genc kadin (sadece risk faktorleri)", {
    "age": 28, "gender": "Female",
    "bmi": 22.0,
    "high_bp": False, "high_chol": False,
    "physical_activity": True, "gen_health": 1,
    "smoker": False, "fruits_daily": True, "veggies_daily": True,
}, {
    "category": "Low",
    "prob_max": 0.35,
    "sym_min": 0.0, "sym_max": 0.0,
    "clin_min": 0.0, "clin_max": 0.0,
    "confidence": "low",
    "card_names": [
        "Ya\u015f", "Cinsiyet", "BMI",
        "Y\u00fcksek Tansiyon", "Y\u00fcksek Kolesterol",
        "Fiziksel Aktivite", "Genel Sa\u011fl\u0131k",
        "Sigara", "Meyve T\u00fcketimi", "Sebze T\u00fcketimi",
    ],
    "card_statuses": {
        "Ya\u015f": "protective",
        "BMI": "protective",
        "Y\u00fcksek Tansiyon": "protective",
        "Y\u00fcksek Kolesterol": "protective",
        "Fiziksel Aktivite": "protective",
        "Sigara": "protective",
        "Meyve T\u00fcketimi": "protective",
        "Sebze T\u00fcketimi": "protective",
    },
    "no_cards": ["A\u00e7l\u0131k Kan \u015eekeri", "HbA1c"],
})

# =====================================================================
# SENARYO 2: Orta yasli erkek, bazi risk faktorleri (Katman 1)
# =====================================================================
test("S2: Orta yasli erkek, risk faktorleri var", {
    "age": 52, "gender": "Male",
    "bmi": 31.0,
    "high_bp": True, "high_chol": True,
    "physical_activity": False, "gen_health": 4,
    "smoker": True, "heart_disease": False,
    "diff_walking": False,
}, {
    "prob_min": 0.50,
    "sym_min": 0.0, "sym_max": 0.0,
    "clin_min": 0.0, "clin_max": 0.0,
    "confidence": "low",
    "card_statuses": {
        "Ya\u015f": "risk",
        "BMI": "risk",
        "Y\u00fcksek Tansiyon": "risk",
        "Y\u00fcksek Kolesterol": "risk",
        "Fiziksel Aktivite": "risk",
        "Genel Sa\u011fl\u0131k": "risk",
        "Sigara": "risk",
        "Kalp Hastal\u0131\u011f\u0131": "protective",
        "Y\u00fcr\u00fcme Zorlu\u011fu": "protective",
    },
    "no_cards": ["A\u00e7l\u0131k Kan \u015eekeri", "HbA1c"],
})

# =====================================================================
# SENARYO 3: Semptomlu hasta — Katman 1 + 2
# Klasik triad (poliuri + polidipsi + kilo kaybi) + yorgunluk
# =====================================================================
test("S3: Klasik triad + yorgunluk (risk + semptom)", {
    "age": 45, "gender": "Male",
    "bmi": 28.0,
    "high_bp": True,
    "polyuria": True, "polydipsia": True,
    "unexplained_weight_loss": True, "fatigue": True,
}, {
    "prob_min": 0.40,
    "sym_min": 0.50,
    "clin_min": 0.0, "clin_max": 0.0,
    "confidence": "moderate",
    "active_symptoms_min": 4,
    "card_statuses": {
        "Ya\u015f": "risk",
        "BMI": "risk",
        "Y\u00fcksek Tansiyon": "risk",
    },
    "no_cards": ["A\u00e7l\u0131k Kan \u015eekeri", "HbA1c"],
})

# =====================================================================
# SENARYO 4: Klinik degerli hasta — Katman 1 + 3
# FPG 140 + HbA1c 7.2 (diyabet esigi)
# =====================================================================
test("S4: Yuksek kan sekeri + HbA1c (risk + klinik)", {
    "age": 60, "gender": "Female",
    "bmi": 33.0,
    "high_bp": True, "high_chol": True,
    "blood_glucose": 140, "hba1c": 7.2,
}, {
    "category": "High",
    "clin_min": 0.90,
    "confidence": "high",
    "card_statuses": {
        "A\u00e7l\u0131k Kan \u015eekeri": "risk",
        "HbA1c": "risk",
        "Ya\u015f": "risk",
        "BMI": "risk",
    },
})

# =====================================================================
# SENARYO 5: Tam kapsamli — Katman 1 + 2 + 3
# =====================================================================
test("S5: Tam kapsamli (3 katman aktif)", {
    "age": 55, "gender": "Male",
    "bmi": 35.0,
    "high_bp": True, "high_chol": True,
    "physical_activity": False, "gen_health": 5,
    "smoker": True, "heart_disease": True,
    "diff_walking": True, "heavy_alcohol": True,
    "polyuria": True, "polydipsia": True, "fatigue": True,
    "blurred_vision": True,
    "blood_glucose": 180, "hba1c": 8.5,
}, {
    "category": "High",
    "prob_min": 0.70,
    "ml_min": 0.50,
    "sym_min": 0.40,
    "clin_min": 0.90,
    "confidence": "very_high",
    "active_symptoms_min": 4,
    "card_statuses": {
        "Ya\u015f": "risk",
        "BMI": "risk",
        "Y\u00fcksek Tansiyon": "risk",
        "Y\u00fcksek Kolesterol": "risk",
        "Fiziksel Aktivite": "risk",
        "Genel Sa\u011fl\u0131k": "risk",
        "Sigara": "risk",
        "Kalp Hastal\u0131\u011f\u0131": "risk",
        "Y\u00fcr\u00fcme Zorlu\u011fu": "risk",
        "Alkol Kullan\u0131m\u0131": "risk",
        "A\u00e7l\u0131k Kan \u015eekeri": "risk",
        "HbA1c": "risk",
    },
})

# =====================================================================
# SENARYO 6: Prediyabet — sinir degerler
# FPG 110, HbA1c 6.0
# =====================================================================
test("S6: Prediyabet sinir degerler", {
    "age": 48, "gender": "Female",
    "bmi": 27.0,
    "high_bp": False,
    "blood_glucose": 110, "hba1c": 6.0,
}, {
    "clin_min": 0.40, "clin_max": 0.75,
    "confidence": "high",
    "card_statuses": {
        "A\u00e7l\u0131k Kan \u015eekeri": "risk",
        "HbA1c": "risk",
        "BMI": "risk",
        "Y\u00fcksek Tansiyon": "protective",
    },
})

# =====================================================================
# SENARYO 7: Normal klinik degerler — koruyucu kartlar
# FPG 85, HbA1c 5.2
# =====================================================================
test("S7: Normal klinik degerler, saglikli profil", {
    "age": 35, "gender": "Male",
    "bmi": 23.0,
    "high_bp": False, "high_chol": False,
    "physical_activity": True, "gen_health": 2,
    "smoker": False,
    "blood_glucose": 85, "hba1c": 5.2,
}, {
    "category": "Low",
    "prob_max": 0.30,
    "clin_max": 0.25,
    "confidence": "high",
    "card_statuses": {
        "A\u00e7l\u0131k Kan \u015eekeri": "protective",
        "HbA1c": "protective",
        "BMI": "protective",
        "Y\u00fcksek Tansiyon": "protective",
        "Y\u00fcksek Kolesterol": "protective",
        "Fiziksel Aktivite": "protective",
        "Genel Sa\u011fl\u0131k": "protective",
        "Sigara": "protective",
    },
})

# =====================================================================
# SENARYO 8: Sadece semptomlar, risk faktorleri minimal
# Sadece yorgunluk + bulanik gorme
# =====================================================================
test("S8: Hafif semptomlar, minimal risk", {
    "age": 40, "gender": "Female",
    "fatigue": True, "blurred_vision": True,
}, {
    "sym_min": 0.15, "sym_max": 0.35,
    "clin_min": 0.0, "clin_max": 0.0,
    "confidence": "moderate",
    "active_symptoms_min": 2,
    "card_names": ["Ya\u015f", "Cinsiyet"],
    "card_count": 2,
    "no_cards": ["BMI", "Y\u00fcksek Tansiyon", "Sigara", "A\u00e7l\u0131k Kan \u015eekeri", "HbA1c"],
})

# =====================================================================
# SENARYO 9: Yasli hasta, coklu semptom + klinik
# 72 yas, 6 semptom + diyabet esigi kan sekeri
# =====================================================================
test("S9: Yasli, coklu semptom + diyabet esigi", {
    "age": 72, "gender": "Male",
    "bmi": 30.0,
    "high_bp": True,
    "polyuria": True, "polydipsia": True,
    "unexplained_weight_loss": True, "fatigue": True,
    "slow_healing": True, "tingling_numbness": True,
    "blood_glucose": 200, "hba1c": 9.0,
}, {
    "category": "High",
    "prob_min": 0.75,
    "sym_min": 0.60,
    "clin_min": 0.90,
    "confidence": "very_high",
    "active_symptoms_min": 6,
    "card_statuses": {
        "Ya\u015f": "risk",
        "A\u00e7l\u0131k Kan \u015eekeri": "risk",
        "HbA1c": "risk",
    },
})

# =====================================================================
# SENARYO 10: SHAP filtreleme + kart filtreleme dogrulamasi
# Sadece age, gender, bmi, high_bp verilecek — diger kartlar olmamali
# =====================================================================
test("S10: SHAP + kart filtreleme - verilmeyen alanlar gizli", {
    "age": 50, "gender": "Male",
    "bmi": 29.0,
    "high_bp": True,
}, {
    "card_count": 4,
    "card_names": ["Ya\u015f", "Cinsiyet", "BMI", "Y\u00fcksek Tansiyon"],
    "no_cards": [
        "Y\u00fcksek Kolesterol", "Sigara", "Kalp Hastal\u0131\u011f\u0131",
        "Fiziksel Aktivite", "Genel Sa\u011fl\u0131k", "Y\u00fcr\u00fcme Zorlu\u011fu",
        "Meyve T\u00fcketimi", "Sebze T\u00fcketimi", "Alkol Kullan\u0131m\u0131",
        "A\u00e7l\u0131k Kan \u015eekeri", "HbA1c",
    ],
    "shap_excluded": [
        "Y\u00fcksek kolesterol",
        "Sigara kullan\u0131m\u0131",
        "Kalp hastal\u0131\u011f\u0131 \u00f6yk\u00fcs\u00fc",
        "Fiziksel aktivite eksikli\u011fi",
        "Yetersiz meyve t\u00fcketimi",
        "Yetersiz sebze t\u00fcketimi",
        "A\u011f\u0131r alkol kullan\u0131m\u0131",
        "K\u00f6t\u00fc genel sa\u011fl\u0131k durumu",
        "Y\u00fcr\u00fcme zorlu\u011fu",
    ],
})


# =====================================================================
# RAPOR
# =====================================================================
print("=" * 70)
print("  HYBRID MODEL + RISK FAKTOR KARTLARI TEST RAPORU")
print("=" * 70)
for line in DETAILS:
    print(line)
print("=" * 70)
print(f"  SONUC: {PASS} BASARILI / {FAIL} BASARISIZ  (toplam {PASS + FAIL})")
print("=" * 70)

sys.exit(0 if FAIL == 0 else 1)
