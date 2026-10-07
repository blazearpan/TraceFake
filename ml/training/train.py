from pathlib import Path
import json
import sys
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from backend.app.services.url_features import extract_features, FEATURE_NAMES

DATASET = ROOT / "ml" / "datasets" / "PhiUSIIL_Phishing_URL_Dataset.csv"
OUT = ROOT / "ml" / "trained_models"
OUT.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42

def load_data():
    if not DATASET.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET}. Run download_dataset.py first.")
    df = pd.read_csv(DATASET)
    if "URL" not in df.columns or "Label" not in df.columns:
        raise ValueError("Dataset must contain URL and Label columns.")
    df = df[["URL", "Label"]].dropna()
    df["URL"] = df["URL"].astype(str).str.strip()
    df = df[df["URL"] != ""].drop_duplicates(subset=["URL"]).reset_index(drop=True)
    # UCI: Label 1 = legitimate, Label 0 = phishing.
    df["target"] = (df["Label"].astype(int) == 0).astype(int)
    return df

def build_features(urls):
    rows = []
    for url in urls:
        rows.append(extract_features(url))
    return pd.DataFrame(rows, columns=FEATURE_NAMES)

def metrics(y_true, pred, prob):
    return {
        "accuracy": float(accuracy_score(y_true, pred)),
        "precision": float(precision_score(y_true, pred, zero_division=0)),
        "recall": float(recall_score(y_true, pred, zero_division=0)),
        "f1": float(f1_score(y_true, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, prob)) if prob is not None else None,
    }

def main():
    df = load_data()
    X = build_features(df["URL"])
    y = df["target"]

    X_train, X_holdout, y_train, y_holdout = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=RANDOM_STATE
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_holdout, y_holdout, test_size=0.50, stratify=y_holdout, random_state=RANDOM_STATE
    )

    models = {
        "Logistic Regression": Pipeline([
            ("scale", StandardScaler()),
            ("model", LogisticRegression(max_iter=2000, random_state=RANDOM_STATE))
        ]),
        "Decision Tree": DecisionTreeClassifier(max_depth=18, min_samples_leaf=3, random_state=RANDOM_STATE, class_weight="balanced"),
        "Random Forest": RandomForestClassifier(n_estimators=300, max_depth=24, min_samples_leaf=2, n_jobs=-1, random_state=RANDOM_STATE, class_weight="balanced_subsample"),
        "Gradient Boosting": GradientBoostingClassifier(random_state=RANDOM_STATE, n_estimators=150, max_depth=3),
    }

    comparison = []
    fitted = {}
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        pred = model.predict(X_val)
        prob = model.predict_proba(X_val)[:, list(model.classes_).index(1)] if hasattr(model, "predict_proba") else None
        m = metrics(y_val, pred, prob)
        comparison.append({"model": name, **m})
        fitted[name] = model

    comparison.sort(key=lambda r: (r["f1"], r["roc_auc"]), reverse=True)
    selected_name = comparison[0]["model"]
    selected = fitted[selected_name]

    test_pred = selected.predict(X_test)
    test_prob = selected.predict_proba(X_test)[:, list(selected.classes_).index(1)] if hasattr(selected, "predict_proba") else None
    test_metrics = metrics(y_test, test_pred, test_prob)
    cm = confusion_matrix(y_test, test_pred).tolist()

    # Fit the selected model on train + validation only, keeping the test set untouched.
    X_trainval = pd.concat([X_train, X_val], axis=0)
    y_trainval = pd.concat([y_train, y_val], axis=0)
    selected.fit(X_trainval, y_trainval)

    feature_importance = []
    if hasattr(selected, "feature_importances_"):
        values = selected.feature_importances_
    elif hasattr(selected, "named_steps") and hasattr(selected.named_steps["model"], "coef_"):
        values = np.abs(selected.named_steps["model"].coef_[0])
    else:
        values = None
    if values is not None:
        pairs = sorted(zip(FEATURE_NAMES, values), key=lambda x: x[1], reverse=True)[:20]
        feature_importance = [{"feature": n, "importance": float(v)} for n, v in pairs]

    model_path = OUT / "tracefake_model.joblib"
    joblib.dump(selected, model_path)

    metadata = {
        "model_name": selected_name,
        "model_version": "1.0-url-only",
        "random_state": RANDOM_STATE,
        "selection_method": "Selected by validation F1-score, with validation ROC-AUC as tie-breaker. Final metrics are from an untouched test set.",
        "feature_names": FEATURE_NAMES,
        "feature_count": len(FEATURE_NAMES),
        "dataset": {
            "name": "PhiUSIIL Phishing URL (Website)",
            "source": "UCI Machine Learning Repository",
            "url": "https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset",
            "license": "CC BY 4.0",
            "rows_after_deduplication": int(len(df)),
            "phishing": int(y.sum()),
            "legitimate": int((y == 0).sum()),
            "split": {"train": int(len(X_train)), "validation": int(len(X_val)), "test": int(len(X_test))},
            "note": "Only URL-derived features were used. Webpage/source-code features from the original dataset were intentionally excluded."
        },
        "test_metrics": test_metrics,
        "confusion_matrix": cm,
        "model_comparison": comparison,
        "feature_importance": feature_importance,
    }
    (OUT / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))
    print(f"Saved model to {model_path}")

if __name__ == "__main__":
    main()
