import os
import pickle
import time
import requests
import psutil

import numpy as np

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="Analyzer Agent")


AGENT3_URL = os.getenv(
    "AGENT3_URL",
    "http://agent3-decision:8000"
)
AGENT3_TIMEOUT_SEC = float(
    os.getenv("AGENT3_TIMEOUT_SEC", "18")
)


with open("model.pkl", "rb") as f:
    model = pickle.load(f)


class SensorData(BaseModel):
    temperature: float
    humidity: float
    timestamp: float | None = None


@app.get("/health")
def health():
    return {
        "agent": "analyzer",
        "status": "UP",
        "model": "IsolationForest"
    }


@app.get("/metrics")
def metrics():
    process = psutil.Process()
    return {
        "agent": "analyzer",
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_mb": process.memory_info().rss / 1024 / 1024
    }


@app.post("/analyze")
def analyze(data: SensorData):
    start = time.perf_counter()

    features = np.array([[data.temperature, data.humidity]])
    prediction = model.predict(features)[0]
    anomaly_score = model.decision_function(features)[0]

    status = "ANOMALY" if prediction == -1 else "NORMAL"

    analysis = {
        "temperature": data.temperature,
        "humidity": data.humidity,
        "timestamp": data.timestamp,
        "anomaly_score": round(float(anomaly_score), 4),
        "status": status
    }

    local_latency_ms = (time.perf_counter() - start) * 1000

    try:
        response = requests.post(
            f"{AGENT3_URL}/decide",
            json=analysis,
            timeout=AGENT3_TIMEOUT_SEC
        )
        response.raise_for_status()
        decision = response.json()

        return {
            "agent": "analyzer",
            "status": "SUCCESS",
            "local_inference": True,
            "model": "IsolationForest",
            "latency_ms": round(local_latency_ms, 2),
            "analysis": analysis,
            "decision": decision
        }

    except requests.Timeout:
        return {
            "agent": "analyzer",
            "status": "DEGRADED",
            "error": "AGENT3_TIMEOUT",
            "local_inference": True,
            "analysis": analysis
        }

    except requests.RequestException as e:
        return {
            "agent": "analyzer",
            "status": "DEGRADED",
            "error": "AGENT3_UNAVAILABLE",
            "local_inference": True,
            "analysis": analysis,
            "message": str(e)
        }
