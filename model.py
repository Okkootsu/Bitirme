# ==============================================================================
# DIABETES RISK PREDICTION - MODEL TRAINING PIPELINE
# Dataset: BRFSS Diabetes Health Indicators (CDC, 70K+ samples)
# Models: LogReg, NaiveBayes, DecisionTree, SVM, RandomForest, XGBoost
# Final: Stacking Ensemble (top 3 by AUC-ROC) + Isotonic Calibration
# ==============================================================================

import json
import time
import warnings
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, brier_score_loss,
    accuracy_score, precision_score, recall_score, f1_score
)
from xgboost import XGBClassifier

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

# ==============================================================================
# 1. DATA LOADING
# ==============================================================================
print("=" * 70)
print("DIABETES RISK PREDICTION - MODEL TRAINING")
print("=" * 70)

df = pd.read_csv("diabetes_brfss_dataset.csv")
print(f"\nDataset: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"Target distribution:\n{df['Diabetes_binary'].value_counts().to_string()}")

# ==============================================================================
# 2. FEATURE SELECTION & MAPPING
# ==============================================================================
# Select features that map to our API schema (user-reportable)
FEATURE_COLS = [
    "HighBP",               # high_bp
    "HighChol",             # high_chol
    "BMI",                  # bmi
    "Smoker",               # smoker
    "HeartDiseaseorAttack", # heart_disease
    "PhysActivity",         # physical_activity
    "Fruits",               # fruits_daily
    "Veggies",              # veggies_daily
    "HvyAlcoholConsump",    # heavy_alcohol
    "GenHlth",              # gen_health (1-5)
    "DiffWalk",             # diff_walking
    "Sex",                  # gender (0=Female, 1=Male)
    "Age",                  # age (categorical 1-13 in BRFSS)
]

TARGET_COL = "Diabetes_binary"

X = df[FEATURE_COLS].copy()
y = df[TARGET_COL].copy()

print(f"\nFeatures used: {len(FEATURE_COLS)}")
print(f"  {FEATURE_COLS}")

# ==============================================================================
# 3. TRAIN/TEST SPLIT
# ==============================================================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\nTrain: {X_train.shape[0]}, Test: {X_test.shape[0]}")

# ==============================================================================
# 4. MODEL DEFINITIONS
# ==============================================================================
models = {
    "LogisticRegression": Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(
            C=1.0, max_iter=1000, solver="lbfgs", class_weight="balanced"
        ))
    ]),
    "NaiveBayes": Pipeline([
        ("scaler", StandardScaler()),
        ("model", GaussianNB())
    ]),
    "DecisionTree": Pipeline([
        ("model", DecisionTreeClassifier(
            max_depth=8, min_samples_split=20, min_samples_leaf=10,
            class_weight="balanced", random_state=42
        ))
    ]),
    "SVM": Pipeline([
        ("scaler", StandardScaler()),
        ("model", SVC(
            C=1.0, kernel="rbf", gamma="scale",
            class_weight="balanced", probability=True, random_state=42,
            cache_size=500, max_iter=5000
        ))
    ]),
    "RandomForest": Pipeline([
        ("model", RandomForestClassifier(
            n_estimators=200, max_depth=12, min_samples_split=10,
            min_samples_leaf=5, class_weight="balanced",
            random_state=42, n_jobs=-1
        ))
    ]),
    "XGBoost": Pipeline([
        ("model", XGBClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            subsample=0.8, colsample_bytree=0.8,
            scale_pos_weight=1, eval_metric="logloss",
            random_state=42, n_jobs=-1, verbosity=0
        ))
    ]),
}

# ==============================================================================
# 5. TRAIN & EVALUATE ALL MODELS (5-Fold Stratified CV)
# ==============================================================================
print("\n" + "=" * 70)
print("MODEL COMPARISON (5-Fold Stratified Cross-Validation)")
print("=" * 70)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scoring = ["accuracy", "precision", "recall", "f1", "roc_auc"]

results = {}

for name, pipeline in models.items():
    print(f"\n  Training {name}...", end=" ")
    start = time.time()

    cv_results = cross_validate(
        pipeline, X_train, y_train, cv=cv, scoring=scoring, n_jobs=-1
    )

    elapsed = time.time() - start
    results[name] = {
        "accuracy": cv_results["test_accuracy"].mean(),
        "precision": cv_results["test_precision"].mean(),
        "recall": cv_results["test_recall"].mean(),
        "f1": cv_results["test_f1"].mean(),
        "auc_roc": cv_results["test_roc_auc"].mean(),
        "time": elapsed,
    }
    print(f"done ({elapsed:.1f}s) | AUC-ROC: {results[name]['auc_roc']:.4f}")

# Print comparison table
print("\n" + "-" * 70)
print(f"{'Model':<20} {'Accuracy':<10} {'Precision':<10} {'Recall':<10} {'F1':<10} {'AUC-ROC':<10}")
print("-" * 70)
for name, metrics in sorted(results.items(), key=lambda x: x[1]["auc_roc"], reverse=True):
    print(f"{name:<20} {metrics['accuracy']:.4f}    {metrics['precision']:.4f}    "
          f"{metrics['recall']:.4f}    {metrics['f1']:.4f}    {metrics['auc_roc']:.4f}")
print("-" * 70)

# ==============================================================================
# 6. SELECT TOP 3 MODELS BY AUC-ROC
# ==============================================================================
sorted_models = sorted(results.items(), key=lambda x: x[1]["auc_roc"], reverse=True)
top3_names = [name for name, _ in sorted_models[:3]]
print(f"\nTop 3 models for ensemble: {top3_names}")

# ==============================================================================
# 7. BUILD STACKING ENSEMBLE
# ==============================================================================
print("\n" + "=" * 70)
print("BUILDING STACKING ENSEMBLE")
print("=" * 70)

# Get base estimators for top 3
estimators = [(name, models[name]) for name in top3_names]

stacking_ensemble = StackingClassifier(
    estimators=estimators,
    final_estimator=LogisticRegression(max_iter=1000),
    cv=5,
    stack_method="predict_proba",
    n_jobs=-1,
)

print("  Training stacking ensemble...")
start = time.time()
stacking_ensemble.fit(X_train, y_train)
print(f"  done ({time.time() - start:.1f}s)")

# ==============================================================================
# 8. PROBABILITY CALIBRATION (Isotonic Regression)
# ==============================================================================
print("\n  Calibrating probabilities (Isotonic Regression)...")

calibrated_model = CalibratedClassifierCV(
    stacking_ensemble, method="isotonic", cv=5
)
calibrated_model.fit(X_train, y_train)
print("  Calibration complete.")

# ==============================================================================
# 9. FINAL EVALUATION ON TEST SET
# ==============================================================================
print("\n" + "=" * 70)
print("FINAL MODEL EVALUATION (Test Set)")
print("=" * 70)

# Predictions
y_pred = calibrated_model.predict(X_test)
y_proba = calibrated_model.predict_proba(X_test)[:, 1]

# Metrics
acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_proba)
brier = brier_score_loss(y_test, y_proba)

print(f"\n  Accuracy:  {acc:.4f}")
print(f"  Precision: {prec:.4f}")
print(f"  Recall:    {rec:.4f}")
print(f"  F1-Score:  {f1:.4f}")
print(f"  AUC-ROC:   {auc:.4f}")
print(f"  Brier:     {brier:.4f}")

print(f"\n  Classification Report:")
print(classification_report(y_test, y_pred, target_names=["Negative", "Positive"]))

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()
print(f"  Confusion Matrix:")
print(f"                 Predicted Neg  Predicted Pos")
print(f"  Actual Neg     {tn:>12}  {fp:>12}")
print(f"  Actual Pos     {fn:>12}  {tp:>12}")
print(f"\n  TN={tn}, FP={fp}, FN={fn}, TP={tp}")

print(f"\n  Probability distribution: min={y_proba.min():.4f}, max={y_proba.max():.4f}, "
      f"mean={y_proba.mean():.4f}")

# ==============================================================================
# 10. FEATURE IMPORTANCE (from best tree-based model)
# ==============================================================================
print("\n" + "=" * 70)
print("FEATURE IMPORTANCE")
print("=" * 70)

# Extract feature importance from ensemble's RandomForest base estimator
rf_estimator = None
for name, estimator in stacking_ensemble.named_estimators_.items():
    if "RandomForest" in name:
        rf_model = estimator.named_steps.get("model") if hasattr(estimator, "named_steps") else estimator
        if hasattr(rf_model, "feature_importances_"):
            rf_estimator = rf_model
            break

if rf_estimator is None:
    # Fallback: use XGBoost or any tree-based model
    for name, estimator in stacking_ensemble.named_estimators_.items():
        model_step = estimator.named_steps.get("model") if hasattr(estimator, "named_steps") else estimator
        if hasattr(model_step, "feature_importances_"):
            rf_estimator = model_step
            break

importances = rf_estimator.feature_importances_
importance_df = pd.DataFrame({
    "feature": FEATURE_COLS,
    "importance": importances
}).sort_values("importance", ascending=False)

print("\n  Feature Importance Ranking:")
for _, row in importance_df.iterrows():
    bar = "#" * int(row["importance"] * 50)
    print(f"  {row['feature']:<25} {row['importance']:.4f} {bar}")

# ==============================================================================
# 11. SAVE MODEL & METADATA
# ==============================================================================
print("\n" + "=" * 70)
print("SAVING MODEL")
print("=" * 70)

# Save calibrated model
joblib.dump(calibrated_model, "diabetes_model.pkl")
print("  Saved: diabetes_model.pkl")

# Save feature importance as JSON (used by api.py)
fi_dict = {row["feature"]: row["importance"] for _, row in importance_df.iterrows()}
with open("feature_importance.json", "w", encoding="utf-8") as f:
    json.dump(fi_dict, f, indent=2, ensure_ascii=False)
print("  Saved: feature_importance.json")

# Save model report as JSON
model_report = {
    "dataset": "BRFSS Diabetes Health Indicators 2015 (50/50 split)",
    "dataset_size": len(df),
    "features": FEATURE_COLS,
    "ensemble_models": top3_names,
    "calibration": "isotonic",
    "test_metrics": {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "auc_roc": round(auc, 4),
        "brier_score": round(brier, 4),
    },
    "confusion_matrix": {
        "true_negative": int(tn),
        "false_positive": int(fp),
        "false_negative": int(fn),
        "true_positive": int(tp),
    },
    "all_model_comparison": {
        name: {k: round(v, 4) for k, v in metrics.items()}
        for name, metrics in results.items()
    },
    "feature_importance": {
        row["feature"]: round(row["importance"], 4)
        for _, row in importance_df.iterrows()
    },
    "risk_categories": {
        "low": "probability < 0.30",
        "medium": "0.30 <= probability < 0.60",
        "high": "probability >= 0.60",
    },
}

with open("model_report.json", "w", encoding="utf-8") as f:
    json.dump(model_report, f, indent=2, ensure_ascii=False)
print("  Saved: model_report.json")

print("\n" + "=" * 70)
print("MODEL TRAINING COMPLETE!")
print("=" * 70)
