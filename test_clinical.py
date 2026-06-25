# -*- coding: utf-8 -*-
"""
Gercek Klinik Senaryolar - Prediyabet vs Diyabet Ayrimi Testi
"""
import requests

BASE = "http://localhost:8000/predict"

scenarios = [
    # === PREDİYABET SENARYOLARI ===
    {
        "name": "PRE-1: Klasik prediyabet (45E, FBG=110, A1c=6.0, hafif obez)",
        "expected": "Medium",
        "data": {
            "age": 45, "gender": "Male", "bmi": 28.5,
            "high_bp": True, "high_chol": False, "physical_activity": False,
            "gen_health": 3, "smoker": False, "heart_disease": False,
            "blood_glucose": 110, "hba1c": 6.0,
            "polyuria": False, "polydipsia": False, "fatigue": True,
            "blurred_vision": False, "slow_healing": False,
            "unexplained_weight_loss": False, "frequent_infections": False, "tingling_numbness": False
        }
    },
    {
        "name": "PRE-2: Erken prediyabet (38K, FBG=102, A1c=5.8, normal kilo)",
        "expected": "Low|Medium",
        "data": {
            "age": 38, "gender": "Female", "bmi": 24.5,
            "high_bp": False, "high_chol": False, "physical_activity": True,
            "gen_health": 2, "smoker": False,
            "blood_glucose": 102, "hba1c": 5.8,
            "polyuria": False, "polydipsia": False, "fatigue": False,
            "blurred_vision": False, "slow_healing": False,
            "unexplained_weight_loss": False, "frequent_infections": False, "tingling_numbness": False
        }
    },
    {
        "name": "PRE-3: Ust sinir prediyabet (55E, FBG=124, A1c=6.4, obez+HT)",
        "expected": "Medium|High",
        "data": {
            "age": 55, "gender": "Male", "bmi": 32.0,
            "high_bp": True, "high_chol": True, "physical_activity": False,
            "gen_health": 4, "smoker": True, "heart_disease": False,
            "diff_walking": False,
            "blood_glucose": 124, "hba1c": 6.4,
            "polyuria": False, "polydipsia": False, "fatigue": True,
            "blurred_vision": False, "slow_healing": False,
            "unexplained_weight_loss": False, "frequent_infections": False, "tingling_numbness": False
        }
    },
    {
        "name": "PRE-4: Prediyabet + semptomlar (50K, FBG=118, A1c=6.2, poliuri+yorgunluk)",
        "expected": "Medium",
        "data": {
            "age": 50, "gender": "Female", "bmi": 30.0,
            "high_bp": True, "high_chol": False, "physical_activity": False,
            "gen_health": 3, "smoker": False,
            "blood_glucose": 118, "hba1c": 6.2,
            "polyuria": True, "polydipsia": False, "fatigue": True,
            "blurred_vision": False, "slow_healing": False,
            "unexplained_weight_loss": False, "frequent_infections": False, "tingling_numbness": False
        }
    },

    # === KESİN DİYABET SENARYOLARI ===
    {
        "name": "DM-1: Yeni tani T2DM (52E, FBG=145, A1c=7.2, klasik semptomlar)",
        "expected": "High",
        "data": {
            "age": 52, "gender": "Male", "bmi": 31.5,
            "high_bp": True, "high_chol": True, "physical_activity": False,
            "gen_health": 4, "smoker": False, "heart_disease": False,
            "blood_glucose": 145, "hba1c": 7.2,
            "polyuria": True, "polydipsia": True, "fatigue": True,
            "blurred_vision": True, "slow_healing": False,
            "unexplained_weight_loss": False, "frequent_infections": False, "tingling_numbness": False
        }
    },
    {
        "name": "DM-2: Kontrolsuz diyabet (60E, FBG=220, A1c=9.5, tum semptomlar)",
        "expected": "High",
        "data": {
            "age": 60, "gender": "Male", "bmi": 34.0,
            "high_bp": True, "high_chol": True, "physical_activity": False,
            "gen_health": 5, "smoker": True, "heart_disease": True,
            "diff_walking": True,
            "blood_glucose": 220, "hba1c": 9.5,
            "polyuria": True, "polydipsia": True, "fatigue": True,
            "blurred_vision": True, "slow_healing": True,
            "unexplained_weight_loss": True, "frequent_infections": True, "tingling_numbness": True
        }
    },
    {
        "name": "DM-3: Asemptomatik diyabet (48K, FBG=135, A1c=6.8, semptom yok)",
        "expected": "High",
        "data": {
            "age": 48, "gender": "Female", "bmi": 29.0,
            "high_bp": False, "high_chol": False, "physical_activity": True,
            "gen_health": 2, "smoker": False,
            "blood_glucose": 135, "hba1c": 6.8,
            "polyuria": False, "polydipsia": False, "fatigue": False,
            "blurred_vision": False, "slow_healing": False,
            "unexplained_weight_loss": False, "frequent_infections": False, "tingling_numbness": False
        }
    },
    {
        "name": "DM-4: Diyabet esiginde (50E, FBG=126, A1c=6.5, minimal risk)",
        "expected": "High",
        "data": {
            "age": 50, "gender": "Male", "bmi": 27.0,
            "high_bp": False, "high_chol": False, "physical_activity": True,
            "gen_health": 2, "smoker": False,
            "blood_glucose": 126, "hba1c": 6.5,
            "polyuria": False, "polydipsia": False, "fatigue": False,
            "blurred_vision": False, "slow_healing": False,
            "unexplained_weight_loss": False, "frequent_infections": False, "tingling_numbness": False
        }
    },

    # === SINIR / GECİS SENARYOLARI ===
    {
        "name": "SINIR-1: Normal -> Prediyabet gecisi (42K, FBG=100, A1c=5.7)",
        "expected": "Low|Medium",
        "data": {
            "age": 42, "gender": "Female", "bmi": 26.0,
            "high_bp": False, "high_chol": False, "physical_activity": True,
            "gen_health": 2, "smoker": False,
            "blood_glucose": 100, "hba1c": 5.7,
            "polyuria": False, "polydipsia": False, "fatigue": False,
            "blurred_vision": False, "slow_healing": False,
            "unexplained_weight_loss": False, "frequent_infections": False, "tingling_numbness": False
        }
    },
    {
        "name": "SINIR-2: Prediyabet -> Diyabet gecisi (55E, FBG=125, A1c=6.4)",
        "expected": "Medium",
        "data": {
            "age": 55, "gender": "Male", "bmi": 30.0,
            "high_bp": True, "high_chol": True, "physical_activity": False,
            "gen_health": 3, "smoker": False,
            "blood_glucose": 125, "hba1c": 6.4,
            "polyuria": False, "polydipsia": False, "fatigue": True,
            "blurred_vision": False, "slow_healing": False,
            "unexplained_weight_loss": False, "frequent_infections": False, "tingling_numbness": False
        }
    },
    {
        "name": "SINIR-3: Tam normal lab (35E, FBG=85, A1c=5.0) ama obez+HT+sigara",
        "expected": "Low|Medium",
        "data": {
            "age": 35, "gender": "Male", "bmi": 33.0,
            "high_bp": True, "high_chol": True, "physical_activity": False,
            "gen_health": 3, "smoker": True,
            "blood_glucose": 85, "hba1c": 5.0,
            "polyuria": False, "polydipsia": False, "fatigue": False,
            "blurred_vision": False, "slow_healing": False,
            "unexplained_weight_loss": False, "frequent_infections": False, "tingling_numbness": False
        }
    },
    {
        "name": "SINIR-4: Diyabet labi ama saglikli profil (30K, FBG=140, A1c=7.0, semptomlu)",
        "expected": "High",
        "data": {
            "age": 30, "gender": "Female", "bmi": 22.0,
            "high_bp": False, "high_chol": False, "physical_activity": True,
            "gen_health": 1, "smoker": False,
            "blood_glucose": 140, "hba1c": 7.0,
            "polyuria": True, "polydipsia": True, "fatigue": True,
            "blurred_vision": False, "slow_healing": False,
            "unexplained_weight_loss": False, "frequent_infections": False, "tingling_numbness": False
        }
    },
]

print("=" * 100)
print("GERCEK KLINIK SENARYO TESTI - PREDIYABET vs DIYABET AYRIMI")
print("=" * 100)

pass_count = 0
fail_count = 0

for s in scenarios:
    r = requests.post(BASE, json=s["data"])
    d = r.json()
    prob = d["risk_probability"]
    cat = d["risk_category"]
    ml = d["ml_score"]
    sym = d["symptom_score"]
    clin = d["clinical_score"]
    conf = d["confidence_level"]

    expected = s["expected"]
    if "|" in expected:
        passed = cat in expected.split("|")
    else:
        passed = cat == expected

    if passed:
        pass_count += 1
        mark = "PASS"
    else:
        fail_count += 1
        mark = "FAIL"

    # ADA classification
    fbg = s["data"].get("blood_glucose")
    a1c = s["data"].get("hba1c")
    ada = ""
    if fbg is not None and a1c is not None:
        if fbg >= 126 or a1c >= 6.5:
            ada = "ADA: DIYABET"
        elif fbg >= 100 or a1c >= 5.7:
            ada = "ADA: PREDIYABET"
        else:
            ada = "ADA: NORMAL"

    print()
    print("-" * 100)
    print("  [%s]  %s" % (mark, s["name"]))
    print("-" * 100)
    print("  Final:    %%%.1f  |  Kategori: %-8s |  Beklenen: %-12s |  Guven: %s" % (prob*100, cat, expected, conf))
    print("  ML=%%%.1f   Semptom=%%%.1f   Klinik=%%%.1f" % (ml*100, sym*100, clin*100))
    print("  %s  (FBG=%s mg/dL, A1c=%%%s)" % (ada, fbg, a1c))

print()
print("=" * 100)
print("SONUC: %d/%d senaryo gecti, %d basarisiz" % (pass_count, len(scenarios), fail_count))
print("=" * 100)
