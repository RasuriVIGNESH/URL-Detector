"""Train and save the URL classifier."""
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from src.feature_extractor import FEATURE_NAMES, feature_vector

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "urls.csv"
MODEL_DIR = ROOT / "models"
MODEL_PATH = MODEL_DIR / "phishing_model.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"


def train() -> dict:
    df = pd.read_csv(DATA_PATH).dropna(subset=["url", "label"])
    x = pd.DataFrame([feature_vector(url) for url in df["url"]], columns=FEATURE_NAMES)
    y = df["label"]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.25, random_state=42, stratify=y
    )
    model = RandomForestClassifier(
        n_estimators=200, random_state=42, class_weight="balanced", min_samples_leaf=1
    )
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    metrics = {
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "precision": round(float(precision_score(y_test, predictions, pos_label="phishing", zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, predictions, pos_label="phishing", zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, predictions, pos_label="phishing", zero_division=0)), 4),
        "feature_names": FEATURE_NAMES,
        "model_version": "1.0.0",
        "samples": int(len(df)),
        "classification_report": classification_report(y_test, predictions, zero_division=0),
    }
    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))
    return metrics


if __name__ == "__main__":
    result = train()
    print(json.dumps(result, indent=2))
