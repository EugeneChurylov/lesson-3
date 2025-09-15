# app/main.py
from __future__ import annotations

import json
import os
import time
import logging
import requests
from typing import List, Dict, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator

from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram

# ------------ Logging ------------
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",  # чистий JSON рядок нижче
)

def log_json(event: str, **kwargs: Any) -> None:
    payload = {"event": event, **kwargs}
    try:
        logging.info(json.dumps(payload, ensure_ascii=False))
    except Exception:
        logging.info(str(payload))


# ------------ Pydantic models ------------
class PredictRequest(BaseModel):
    features: List[float] = Field(..., description="Vector of numeric features")

    @validator("features")
    def non_empty(cls, v: List[float]) -> List[float]:
        if not v:
            raise ValueError("features must be non-empty")
        return v


class PredictResponse(BaseModel):
    prediction: float
    drift: bool


# ------------ “Model” & drift utils ------------
MODEL_PATH = os.getenv("MODEL_PATH", "/app/model/model.pkl")
REF_STATS_PATH = os.getenv("REF_STATS_PATH", "/app/model/ref_stats.json")

_ref_stats: Dict[str, Any] | None = None

def load_ref_stats(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {"mean": 0.0, "count": 0}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def simple_model(features: List[float]) -> float:
    return float(sum(features))

def detect_drift(features: List[float], ref_stats: Dict[str, Any]) -> bool:
    if not ref_stats or ref_stats.get("count", 0) == 0:
        return False
    x_mean = sum(features) / len(features)
    ref_mean = float(ref_stats.get("mean", 0.0))
    if ref_mean == 0:
        return False
    return abs(x_mean - ref_mean) / abs(ref_mean) > 0.5


# ------------ Metrics ------------
PREDICTIONS = Counter(
    "aiops_predictions_total",
    "Total number of predictions",
)

DRIFT_EVENTS = Counter(
    "aiops_drift_events_total",
    "Total number of detected drift events",
)

PREDICTION_LATENCY = Histogram(
    "aiops_prediction_latency_seconds",
    "Latency of the /predict handler in seconds",
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)


# ------------ GitLab retrain trigger ------------
GITLAB_TRIGGER_URL = os.getenv("GITLAB_TRIGGER_URL")
GITLAB_TRIGGER_TOKEN = os.getenv("GITLAB_TRIGGER_TOKEN")
GITLAB_REF = os.getenv("GITLAB_REF", "main")

def trigger_gitlab_retrain() -> None:
    if not (GITLAB_TRIGGER_URL and GITLAB_TRIGGER_TOKEN):
        return
    try:
        resp = requests.post(
            GITLAB_TRIGGER_URL,
            data={
                "token": GITLAB_TRIGGER_TOKEN,
                "ref": GITLAB_REF,
                "variables[RETRAIN]": "true",
            },
            timeout=5,
        )
        log_json("gitlab_trigger", status=resp.status_code, body=resp.text[:200])
    except Exception as e:
        log_json("gitlab_trigger_error", error=str(e))


# ------------ FastAPI app ------------
app = FastAPI(title="AIOps API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.on_event("startup")
def _startup() -> None:
    global _ref_stats
    _ref_stats = load_ref_stats(REF_STATS_PATH)
    log_json("startup", ref_stats=_ref_stats)


@app.get("/healthz")
def healthz() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest, request: Request) -> PredictResponse:
    t0 = time.perf_counter()

    y = simple_model(req.features)
    drift = detect_drift(req.features, _ref_stats or {})

    PREDICTIONS.inc()
    if drift:
        DRIFT_EVENTS.inc()
        trigger_gitlab_retrain()

    elapsed = time.perf_counter() - t0
    PREDICTION_LATENCY.observe(elapsed)

    log_json(
        "prediction",
        input=req.features,
        output=y,
        drift=drift,
        latency_s=round(elapsed, 6),
        client=str(request.client.host) if request.client else None,
    )

    return PredictResponse(prediction=y, drift=drift)
