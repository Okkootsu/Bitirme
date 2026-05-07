# =========================
# 1. IMPORTS
# =========================
import pandas as pd
import numpy as np

import joblib

from sklearn.model_selection import StratifiedKFold, GridSearchCV, train_test_split, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder

from sklearn.feature_selection import SelectKBest, mutual_info_classif

from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import VotingClassifier

from sklearn.metrics import classification_report


# =========================
# 2. LOAD DATA
# =========================
df = pd.read_csv("diabetes_risk_prediction_dataset.csv")

target_column = "class"

X = df.drop(columns=[target_column])
y = df[target_column]


# =========================
# 3. LABEL ENCODING (CRITICAL)
# =========================
le = LabelEncoder()
y = le.fit_transform(y)   # Negative=0, Positive=1


# =========================
# 4. COLUMN TYPES
# =========================
cat_cols = X.select_dtypes(include=["object"]).columns
num_cols = X.select_dtypes(exclude=["object"]).columns


# =========================
# 5. PREPROCESSING
# =========================
preprocess = ColumnTransformer([
    ("num", Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ]), num_cols),

    ("cat", Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ]), cat_cols)
])


# =========================
# 6. TRAIN TEST SPLIT
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    stratify=y,
    random_state=42
)


# =========================
# 7. CV SETUP
# =========================
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)


# =========================
# 8. PIPELINE FUNCTION
# =========================
def build_pipeline(model):
    return Pipeline([
        ("preprocess", preprocess),

        ("feature_selection",
         SelectKBest(score_func=mutual_info_classif, k=10)),

        ("model", model)
    ])


# =========================
# 9. MODEL TRAINING
# =========================
models = {
    "LogReg": LogisticRegression(max_iter=1000, solver="liblinear"),
    "NaiveBayes": GaussianNB()
}

results = []

for name, model in models.items():
    pipe = build_pipeline(model)

    scores = cross_validate(
        pipe,
        X_train,
        y_train,
        cv=cv,
        scoring=["accuracy", "precision", "recall", "f1"]
    )

    results.append({
        "Model": name,
        "Accuracy": scores["test_accuracy"].mean(),
        "Recall": scores["test_recall"].mean(),
        "F1": scores["test_f1"].mean()
    })

results_df = pd.DataFrame(results)
print(results_df)


# =========================
# 10. BEST MODEL (LOGREG TUNING)
# =========================
logreg_pipe = build_pipeline(
    LogisticRegression(max_iter=1000, solver="liblinear")
)

param_grid = {
    "model__C": [0.01, 0.1, 1, 5],
    "feature_selection__k": [5, 8, 10, "all"]
}

grid = GridSearchCV(
    logreg_pipe,
    param_grid,
    cv=cv,
    scoring="recall",
    n_jobs=-1
)

grid.fit(X_train, y_train)

print("Best Params:", grid.best_params_)
print("Best Recall:", grid.best_score_)


# =========================
# 11. FINAL MODEL (ENSEMBLE)
# =========================
best_k = grid.best_params_["feature_selection__k"]
best_c = grid.best_params_["model__C"]

final_model = Pipeline([
    ("preprocess", preprocess),
    ("feature_selection",
     SelectKBest(mutual_info_classif, k=best_k)),
    ("model", VotingClassifier(
        estimators=[
            ("lr", LogisticRegression(C=best_c, max_iter=1000)),
            ("nb", GaussianNB())
        ],
        voting="soft"
    ))
])

final_model.fit(X_train, y_train)


# =========================
# 12. EVALUATION
# =========================
y_pred = final_model.predict(X_test)

print("\nFINAL REPORT")
print(classification_report(y_test, y_pred))


# =========================
# 13. SAVE MODEL (FASTAPI READY)
# =========================
joblib.dump(final_model, "diabetes_model.pkl")
joblib.dump(le, "label_encoder.pkl")

print("\nModel saved successfully!")