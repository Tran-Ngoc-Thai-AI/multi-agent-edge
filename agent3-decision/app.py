import time
import psutil

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="Decision Agent")


class AnalysisData(BaseModel):
    temperature: float
    humidity: float
    anomaly_score: float
    status: str


@app.get("/health")
def health():

    return {
        "agent": "decision",
        "status": "UP"
    }


@app.get("/metrics")
def metrics():

    process = psutil.Process()

    return {
        "agent": "decision",
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_mb": process.memory_info().rss / 1024 / 1024
    }


@app.post("/decide")
def decide(data: AnalysisData):

    start = time.perf_counter()

    if data.status == "ANOMALY":

        action = "HIGH_ENVIRONMENT_RISK"
        decision = "ALERT"

    else:

        action = "NO_ACTION"
        decision = "NORMAL"

    latency_ms = (
        time.perf_counter() - start
    ) * 1000

    return {
        "agent": "decision",
        "status": "SUCCESS",
        "decision": decision,
        "action": action,
        "latency_ms": round(
            latency_ms,
            2
        )
    }