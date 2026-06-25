import requests
import json

BASE = "http://localhost:8000/predict"

scenarios = [
    {
        "name": "1. Saglikli Genc (25Y, Kadin)",
        "expected_risk": "Low",
        "expected_range": (0.0, 0.20),
        "data": {
            "age": 25, "gender": "Female", "bmi": 22.0,
            "high_bp": False, "high_chol": False, "physical_activity": True,
            "gen_health": 1, "diff_walking": False, "smoker": False,
            "heart_disease": False, "fruits_daily": True, "veggies_daily": True,
            "heavy_alcohol": False,
            "blood_glucose": 85, "hba1c": 5.0,
            "polyuria": False, "polydipsia": False, "unexplained_weight_loss": False,
            "fatigue": False, "blurred_vision": False, "slow_healing": False,
            "frequent_infections": False, "tingling_numbness": False
        }
    },
    {
        "name": "2. Prediyabet (48Y, Erkek, IFG + hafif semptom)",
        "expected_risk": "Medium",
        "expected_range": (0.30, 0.60),
        "data": {
            "age": 48, "gender": "Male", "bmi": 29.5,
            "high_bp": True, "high_chol": True, "physical_activity": False,
            "gen_health": 3, "diff_walking": False, "smoker": False,
            "heart_disease": False, "fruits_daily": False, "veggies_daily": True,
            "heavy_alcohol": False,
            "blood_glucose": 115, "hba1c": 6.0,
            "polyuria": False, "polydipsia": False, "unexplained_weight_loss": False,
            "fatigue": True, "blurred_vision": False, "slow_healing": False,
            "frequent_infections": False, "tingling_numbness": False
        }
    },
    {
        "name": "3. Yeni Tani T2DM (55Y, Erkek, klasik triad + diyabet lab)",
        "expected_risk": "High",
        "expected_range": (0.80, 1.0),
        "data": {
            "age": 55, "gender": "Male", "bmi": 33.0,
            "high_bp": True, "high_chol": True, "physical_activity": False,
            "gen_health": 4, "diff_walking": False, "smoker": True,
            "heart_disease": False, "fruits_daily": False, "veggies_daily": False,
            "heavy_alcohol": False,
            "blood_glucose": 185, "hba1c": 7.8,
            "polyuria": True, "polydipsia": True, "unexplained_weight_loss": True,
            "fatigue": True, "blurred_vision": True, "slow_healing": False,
            "frequent_infections": False, "tingling_numbness": False
        }
    },
    {
        "name": "4. Ileri T2DM + Komplikasyon (65Y, Erkek, tum semptomlar)",
        "expected_risk": "High",
        "expected_range": (0.85, 1.0),
        "data": {
            "age": 65, "gender": "Male", "bmi": 35.0,
            "high_bp": True, "high_chol": True, "physical_activity": False,
            "gen_health": 5, "diff_walking": True, "smoker": True,
            "heart_disease": True, "fruits_daily": False, "veggies_daily": False,
            "heavy_alcohol": False,
            "blood_glucose": 250, "hba1c": 9.5,
            "polyuria": True, "polydipsia": True, "unexplained_weight_loss": True,
            "fatigue": True, "blurred_vision": True, "slow_healing": True,
            "frequent_infections": True, "tingling_numbness": True
        }
    },
    {
        "name": "5. Asemptomatik T2DM (52Y, Kadin, yuksek lab, semptom yok)",
        "expected_risk": "High",
        "expected_range": (0.60, 0.90),
        "data": {
            "age": 52, "gender": "Female", "bmi": 31.0,
            "high_bp": True, "high_chol": False, "physical_activity": False,
            "gen_health": 3, "diff_walking": False, "smoker": False,
            "heart_disease": False, "fruits_daily": True, "veggies_daily": True,
            "heavy_alcohol": False,
            "blood_glucose": 145, "hba1c": 6.7,
            "polyuria": False, "polydipsia": False, "unexplained_weight_loss": False,
            "fatigue": False, "blurred_vision": False, "slow_healing": False,
            "frequent_infections": False, "tingling_numbness": False
        }
    },
    {
        "name": "6. Semptom Agirlikli (40Y, Erkek, klasik triad, lab yok)",
        "expected_risk": "Medium",
        "expected_range": (0.30, 0.59),
        "data": {
            "age": 40, "gender": "Male", "bmi": 27.0,
            "high_bp": False, "high_chol": False, "physical_activity": True,
            "gen_health": 3, "diff_walking": False, "smoker": False,
            "heart_disease": False, "fruits_daily": True, "veggies_daily": True,
            "heavy_alcohol": False,
            "polyuria": True, "polydipsia": True, "unexplained_weight_loss": True,
            "fatigue": True, "blurred_vision": False, "slow_healing": False,
            "frequent_infections": False, "tingling_numbness": False
        }
    },
    {
        "name": "7. Yasli Yuksek Riskli (70Y, Erkek, cok risk, normal lab)",
        "expected_risk": "Medium",
        "expected_range": (0.25, 0.55),
        "data": {
            "age": 70, "gender": "Male", "bmi": 30.0,
            "high_bp": True, "high_chol": True, "physical_activity": False,
            "gen_health": 4, "diff_walking": True, "smoker": True,
            "heart_disease": True, "fruits_daily": False, "veggies_daily": False,
            "heavy_alcohol": True,
            "blood_glucose": 92, "hba1c": 5.4,
            "polyuria": False, "polydipsia": False, "unexplained_weight_loss": False,
            "fatigue": False, "blurred_vision": False, "slow_healing": False,
            "frequent_infections": False, "tingling_numbness": False
        }
    },
    {
        "name": "8. Genc Obez (30Y, Kadin, BMI 38, baska risk yok)",
        "expected_risk": "Low",
        "expected_range": (0.05, 0.25),
        "data": {
            "age": 30, "gender": "Female", "bmi": 38.0,
            "high_bp": False, "high_chol": False, "physical_activity": True,
            "gen_health": 2, "diff_walking": False, "smoker": False,
            "heart_disease": False, "fruits_daily": True, "veggies_daily": True,
            "heavy_alcohol": False,
            "blood_glucose": 88, "hba1c": 5.2,
            "polyuria": False, "polydipsia": False, "unexplained_weight_loss": False,
            "fatigue": False, "blurred_vision": False, "slow_healing": False,
            "frequent_infections": False, "tingling_numbness": False
        }
    },
    {
        "name": "9. GDM Riski (28Y, Kadin, hafif yuksek FBG + yorgunluk)",
        "expected_risk": "Low",
        "expected_range": (0.15, 0.40),
        "data": {
            "age": 28, "gender": "Female", "bmi": 26.0,
            "high_bp": False, "high_chol": False, "physical_activity": True,
            "gen_health": 2, "diff_walking": False, "smoker": False,
            "heart_disease": False, "fruits_daily": True, "veggies_daily": True,
            "heavy_alcohol": False,
            "blood_glucose": 105, "hba1c": 5.8,
            "polyuria": False, "polydipsia": False, "unexplained_weight_loss": False,
            "fatigue": True, "blurred_vision": False, "slow_healing": False,
            "frequent_infections": False, "tingling_numbness": False
        }
    },
    {
        "name": "10. Minimum Veri (45Y, Erkek, sadece yas+cinsiyet)",
        "expected_risk": "Low",
        "expected_range": (0.10, 0.35),
        "data": {
            "age": 45, "gender": "Male"
        }
    },
    {
        "name": "11. Sinir Prediyabet (50Y, Erkek, FBG=100, HbA1c=5.7)",
        "expected_risk": "Medium",
        "expected_range": (0.30, 0.55),
        "data": {
            "age": 50, "gender": "Male", "bmi": 28.0,
            "high_bp": True, "high_chol": False, "physical_activity": False,
            "gen_health": 3, "diff_walking": False, "smoker": False,
            "blood_glucose": 100, "hba1c": 5.7,
            "polyuria": False, "polydipsia": False, "unexplained_weight_loss": False,
            "fatigue": False, "blurred_vision": False, "slow_healing": False
        }
    },
    {
        "name": "12. Noropati Profili (60Y, Erkek, karincalanma+bulanik gorme)",
        "expected_risk": "Medium",
        "expected_range": (0.35, 0.65),
        "data": {
            "age": 60, "gender": "Male", "bmi": 29.0,
            "high_bp": True, "high_chol": True, "physical_activity": False,
            "gen_health": 4, "diff_walking": True, "smoker": False,
            "polyuria": False, "polydipsia": False, "unexplained_weight_loss": False,
            "fatigue": True, "blurred_vision": True, "slow_healing": True,
            "frequent_infections": False, "tingling_numbness": True
        }
    },
]

print("=" * 100)
print("HYBRID MODEL KAPSAMLI TEST RAPORU")
print("=" * 100)

results = []
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
    lo, hi = s["expected_range"]

    in_range = lo <= prob <= hi
    cat_match = cat == s["expected_risk"]
    passed = in_range and cat_match

    if passed:
        pass_count += 1
        status = "PASS"
    else:
        fail_count += 1
        status = "FAIL"

    results.append({
        "name": s["name"],
        "prob": prob, "cat": cat, "ml": ml, "sym": sym, "clin": clin,
        "conf": conf, "expected_risk": s["expected_risk"],
        "expected_range": s["expected_range"], "passed": passed, "status": status,
        "active_symptoms": d.get("active_symptoms", []),
        "factors": d.get("contributing_factors", [])
    })

for r in results:
    lo, hi = r["expected_range"]
    mark = "PASS" if r["passed"] else "FAIL"
    print("")
    print("-" * 100)
    print("  [%s]  %s" % (mark, r["name"]))
    print("-" * 100)
    print("  Final Risk:  %%%.1f  |  Kategori: %s  |  Guven: %s" % (r["prob"]*100, r["cat"], r["conf"]))
    print("  ML Skor:     %%%.1f" % (r["ml"]*100))
    print("  Semptom:     %%%.1f" % (r["sym"]*100))
    print("  Klinik:      %%%.1f" % (r["clin"]*100))
    expected_str = "  Beklenen:    %s (%.0f%%-%.0f%%)" % (r["expected_risk"], lo*100, hi*100)
    if not r["passed"]:
        if not (lo <= r["prob"] <= hi):
            expected_str += "  <- ARALIK DISI (%%%.1f)" % (r["prob"]*100)
        if r["cat"] != r["expected_risk"]:
            expected_str += "  <- KATEGORI UYUMSUZ (%s != %s)" % (r["cat"], r["expected_risk"])
    print(expected_str)
    if r["active_symptoms"]:
        syms = ", ".join(r["active_symptoms"][:4])
        print("  Semptomlar:  %s" % syms)
    if r["factors"]:
        facts = ", ".join(r["factors"][:4])
        print("  Faktorler:   %s" % facts)

print("")
print("=" * 100)
print("SONUC: %d/%d test gecti, %d basarisiz" % (pass_count, len(results), fail_count))
print("=" * 100)

# Layer analysis
print("")
print("=" * 100)
print("KATMAN ANALIZI")
print("=" * 100)

print("")
print("-" * 60)
print("ML MODEL KATMANI - Skor Dagilimi")
print("-" * 60)
ml_scores = [(r["name"].split(".")[0].strip(), r["ml"]) for r in results]
ml_scores.sort(key=lambda x: x[1])
for name, score in ml_scores:
    bar = "#" * int(score * 40)
    print("  Senaryo %2s: %%%5.1f  %s" % (name, score*100, bar))

print("")
print("-" * 60)
print("SEMPTOM KATMANI - Skor Dagilimi")
print("-" * 60)
for r in results:
    short = r["name"][:45].ljust(45)
    if r["sym"] > 0:
        bar = "#" * int(r["sym"] * 40)
        print("  %s: %%%5.1f  %s" % (short, r["sym"]*100, bar))
    else:
        print("  %s: %%  0.0  (semptom girilmedi)" % short)

print("")
print("-" * 60)
print("KLINIK KATMAN - ADA Esik Dogrulamasi")
print("-" * 60)
ada_tests = [
    ("Normal (FBG=85, A1c=5.0)", {"age": 40, "gender": "Male", "blood_glucose": 85, "hba1c": 5.0}),
    ("Prediyabet alt (FBG=100, A1c=5.7)", {"age": 40, "gender": "Male", "blood_glucose": 100, "hba1c": 5.7}),
    ("Prediyabet ust (FBG=125, A1c=6.4)", {"age": 40, "gender": "Male", "blood_glucose": 125, "hba1c": 6.4}),
    ("Diyabet (FBG=126, A1c=6.5)", {"age": 40, "gender": "Male", "blood_glucose": 126, "hba1c": 6.5}),
    ("Agir diyabet (FBG=200, A1c=9.0)", {"age": 40, "gender": "Male", "blood_glucose": 200, "hba1c": 9.0}),
    ("Sadece FBG yuksek (FBG=150)", {"age": 40, "gender": "Male", "blood_glucose": 150}),
    ("Sadece A1c yuksek (A1c=7.0)", {"age": 40, "gender": "Male", "hba1c": 7.0}),
]
for name, data in ada_tests:
    r2 = requests.post(BASE, json=data)
    d2 = r2.json()
    bar = "#" * int(d2["clinical_score"] * 40)
    print("  %-40s: Klinik=%%%5.1f  %s" % (name, d2["clinical_score"]*100, bar))

print("")
print("-" * 60)
print("FUSION AGIRLIK DOGRULAMASI")
print("-" * 60)
fusion_ok = 0
fusion_fail = 0
for r in results:
    ml, sym, clin = r["ml"], r["sym"], r["clin"]
    has_sym = sym > 0
    has_clin = clin > 0
    if has_sym and has_clin:
        expected = ml * 0.35 + clin * 0.45 + sym * 0.20
        mode = "ML*0.35+Clin*0.45+Sym*0.20"
    elif has_clin:
        expected = ml * 0.35 + clin * 0.65
        mode = "ML*0.35+Clin*0.65"
    elif has_sym:
        base = ml * 0.60 + sym * 0.40
        ceiling = 0.40 + sym * 0.50
        expected = min(base, ceiling)
        mode = "min(ML*0.60+Sym*0.40,ceil)"
    else:
        expected = ml
        mode = "ML*1.00"

    diff = abs(r["prob"] - round(expected, 4))
    if diff < 0.005:
        ok = "OK"
        fusion_ok += 1
    else:
        ok = "FARK=%.4f" % diff
        fusion_fail += 1
    short = r["name"][:35].ljust(35)
    print("  %s %-30s Hesap=%%%.1f Gercek=%%%.1f %s" % (short, mode, expected*100, r["prob"]*100, ok))

print("")
print("  Fusion dogruluk: %d/%d" % (fusion_ok, fusion_ok + fusion_fail))
