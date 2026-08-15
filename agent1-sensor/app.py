import os
import time
import random
import requests
import psutil

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="Sensor Agent")

AGENT2_URL = os.getenv(
    "AGENT2_URL",
    "http://agent2-analyzer:8000"
)


class SensorInput(BaseModel):
    temperature: float | None = None
    humidity: float | None = None


@app.get("/health")
def health():
    return {
        "agent": "sensor",
        "status": "UP"
    }


@app.get("/metrics")
def metrics():
    process = psutil.Process()

    return {
        "agent": "sensor",
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_mb": process.memory_info().rss / 1024 / 1024
    }


@app.post("/process")
def process_sensor(data: SensorInput):

    start = time.perf_counter()

    temperature = (
        data.temperature
        if data.temperature is not None
        else random.uniform(20, 40)
    )

    humidity = (
        data.humidity
        if data.humidity is not None
        else random.uniform(40, 90)
    )

    payload = {
        "temperature": temperature,
        "humidity": humidity,
        "timestamp": time.time()
    }

    try:

        response = requests.post(
            f"{AGENT2_URL}/analyze",
            json=payload,
            timeout=2
        )

        response.raise_for_status()

        result = response.json()

        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        return {
            "agent": "sensor",
            "status": "SUCCESS",
            "latency_ms": round(latency_ms, 2),
            "sensor_data": payload,
            "analysis": result
        }

    except requests.Timeout:

        return {
            "agent": "sensor",
            "status": "DEGRADED",
            "error": "AGENT2_TIMEOUT",
            "sensor_data": payload
        }

    except requests.RequestException as e:

        return {
            "agent": "sensor",
            "status": "DEGRADED",
            "error": "AGENT2_UNAVAILABLE",
            "message": str(e),
            "sensor_data": payload
        }