"""FastAPI service for static phishing URL classification."""
import json
import os
from pathlib import Path
from time import perf_counter

import joblib
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from src.feature_extractor import FEATURE_NAMES, extract_features, feature_vector
from src.validation import URLRequest

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "phishing_model.joblib"
METRICS_PATH = ROOT / "models" / "metrics.json"
load_dotenv(ROOT / ".env")
API_KEY = os.getenv("API_KEY", "change-this-demo-key")

if not MODEL_PATH.exists():
    raise RuntimeError("Model not found. Run: python -m src.train_model")

model = joblib.load(MODEL_PATH)
metrics = json.loads(METRICS_PATH.read_text()) if METRICS_PATH.exists() else {}
app = FastAPI(title="Secure Phishing URL Detector", version=metrics.get("model_version", "1.0.0"))
request_count = 0
prediction_count = {"legitimate": 0, "phishing": 0}


def require_api_key(x_api_key: str | None = Header(default=None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Missing or invalid API key")


@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start = perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time-Ms"] = f"{(perf_counter() - start) * 1000:.2f}"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.get("/health")
def health():
    return {"status": "healthy", "model_version": metrics.get("model_version", "unknown")}


@app.get("/metrics", dependencies=[Depends(require_api_key)])
def app_metrics():
    return {
        "request_count": request_count,
        "prediction_count": prediction_count,
        "model_metrics": metrics,
    }


@app.post("/predict", dependencies=[Depends(require_api_key)])
def predict(payload: URLRequest):
    global request_count
    request_count += 1
    vector = [feature_vector(payload.url)]
    probabilities = model.predict_proba(vector)[0]
    classes = list(model.classes_)
    index = int(model.predict(vector)[0] == "phishing")
    label = str(model.predict(vector)[0])
    confidence = float(probabilities[classes.index(label)])
    prediction_count[label] = prediction_count.get(label, 0) + 1
    return {
        "url": payload.url,
        "prediction": label,
        "confidence": round(confidence, 4),
        "risk_level": "high" if label == "phishing" else "low",
        "model_version": metrics.get("model_version", "unknown"),
        "features": extract_features(payload.url),
        "disclaimer": "Static analysis only; this service never opens the submitted URL.",
    }
