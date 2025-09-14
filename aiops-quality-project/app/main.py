from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import os, json, time

app = FastAPI(title="AIOps API")

# --- Prometheus ---
REQS = Counter("inference_requests_total", "Total inference requests")
LAT = Histogram("inference_latency_seconds", "Inference latency seconds")

# --- "Модель" (MVP): сума фіч ---
MODEL_PATH = os.getenv("MODEL_PATH", "/app/model/model.pkl")  # не використовується у мок-логіці
REF = {"mean": 0.0, "std": 1.0}  # референс для простого дрейф-чеку
try:
    REF = json.load(open(os.getenv("REF_STATS_PATH", "model/ref_stats.json")))
except Exception:
    pass

class Item(BaseModel):
    features: list[float]

def predict(vec: list[float]) -> float:
    # мок: сума як “прогноз”
    return float(sum(vec))

def check_drift(vec: list[float]) -> bool:
    if not vec:
        return False
    mean = sum(vec) / len(vec)
    # дуже простий критерій: >3σ від референсу = дрейф
    return abs(mean - REF.get("mean", 0.0)) > 3 * max(REF.get("std", 1.0), 1e-6)

@app.get("/healthz")
def health():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/predict")
def do_predict(item: Item):
    REQS.inc()
    t0 = time.time()

    y = predict(item.features)
    drift = check_drift(item.features)
    if drift:
        print({"event": "drift_detected", "input": item.features})

    LAT.observe(time.time() - t0)
    print({"event": "prediction", "input": item.features, "output": y})
    return {"prediction": y, "drift": drift}
