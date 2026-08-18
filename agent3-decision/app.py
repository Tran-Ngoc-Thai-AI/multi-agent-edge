import json
import os
import time
import requests
import psutil

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="Decision Agent")


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://phase2-ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
OLLAMA_TIMEOUT_SEC = float(os.getenv("OLLAMA_TIMEOUT_SEC", "15"))
ALERT_WEBHOOK_URL = os.getenv("ALERT_WEBHOOK_URL", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


class AnalysisData(BaseModel):
    temperature: float
    humidity: float
    anomaly_score: float
    status: str
    timestamp: float | None = None


@app.get("/health")
def health():
    return {
        "agent": "decision",
        "status": "UP",
        "ollama_url": OLLAMA_URL,
        "ollama_model": OLLAMA_MODEL
    }


@app.get("/metrics")
def metrics():
    process = psutil.Process()
    return {
        "agent": "decision",
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_mb": process.memory_info().rss / 1024 / 1024
    }


def build_structured_prompt(data: AnalysisData) -> str:
    return f"""
Bạn là trợ lý an toàn môi trường cho hệ thống giám sát cảm biến.

Dữ liệu đầu vào:
- temperature_c: {data.temperature}
- humidity_percent: {data.humidity}
- anomaly_score: {data.anomaly_score}
- timestamp_unix: {data.timestamp}

Quy tắc bắt buộc:
1) IsolationForest đã xác định đây là nhánh ANOMALY. Không được phủ nhận, không được giảm nhẹ, không được nói rằng mọi thứ vẫn bình thường.
2) Phản hồi phải hoàn toàn bằng tiếng Việt tự nhiên, rõ ràng, ngắn gọn.
3) Chỉ trả về MỘT đối tượng JSON hợp lệ, không có markdown, không có giải thích ngoài JSON.
4) JSON phải có đúng các khóa: summary, severity, recommendation, confidence
5) summary và recommendation phải là tiếng Việt.
6) severity chỉ được là một trong: LOW, MEDIUM, HIGH, CRITICAL
7) confidence là số từ 0 đến 1
8) Vì đây là nhánh ANOMALY, severity tối thiểu phải là HIGH; không được trả về LOW hoặc MEDIUM.
9) summary phải rất ngắn, tối đa 1 câu, dứt khoát, ưu tiên nêu rủi ro.
10) recommendation phải là mệnh lệnh trực tiếp, bắt đầu bằng động từ như: Kiểm tra, Cô lập, Dừng, Xác minh, Báo động.
11) Không được dùng giọng xin lỗi, vòng vo, giảm nhẹ, hoặc các cụm như: "xin lỗi", "vui lòng", "xem xét", "nên", "có thể".

Nếu là ANOMALY, hãy ưu tiên mô tả rủi ro và hành động xử lý ngay.
JSON only.
""".strip()


def _first_sentence(text: str) -> str:
    cleaned = " ".join(str(text).split()).strip()
    if not cleaned:
        return cleaned

    for separator in [".", "!", "?", "\n"]:
        if separator in cleaned:
            cleaned = cleaned.split(separator, 1)[0].strip()
            break

    return cleaned


def _normalize_recommendation(text: str, data: AnalysisData) -> str:
    normalized = " ".join(str(text).split()).strip()
    lowered = normalized.lower()

    banned_markers = [
        "xin lỗi",
        "vui lòng",
        "xem xét",
        "nên",
        "có thể",
        "tôi không thể",
        "không thể",
    ]

    if not normalized or any(marker in lowered for marker in banned_markers):
        return _build_contextual_recommendation(data)

    imperative_starts = ("kiểm tra", "cô lập", "dừng", "xác minh", "báo động", "khởi động", "ngắt")
    if len(normalized) < 18:
        return _build_contextual_recommendation(data)

    if not lowered.startswith(imperative_starts):
        return _build_contextual_recommendation(data)

    return normalized


def _build_contextual_recommendation(data: AnalysisData) -> str:
    return (
        f"Kiểm tra ngay khu vực có nhiệt độ {data.temperature}°C và độ ẩm {data.humidity}%, "
        f"cô lập nguồn gây bất thường và xác minh lại cảm biến trước khi tiếp tục vận hành."
    )


def normalize_ai_result(parsed: dict, data: AnalysisData) -> dict:
    severity = str(parsed.get("severity", "HIGH")).upper().strip()
    if severity not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
        severity = "HIGH"

    if severity in {"LOW", "MEDIUM"}:
        severity = "HIGH"

    try:
        confidence = float(parsed.get("confidence", 0.7))
    except (TypeError, ValueError):
        confidence = 0.7

    if confidence < 0:
        confidence = 0.0
    elif confidence > 1:
        confidence = 1.0

    return {
        "summary": _first_sentence(
            parsed.get("summary", "Phát hiện bất thường từ luồng cảm biến.")
        ) or "Phát hiện bất thường từ luồng cảm biến.",
        "severity": severity,
        "recommendation": _normalize_recommendation(
            parsed.get(
                "recommendation",
                "Kiểm tra khu vực ngay và kích hoạt quy trình xử lý sự cố."
            ),
            data,
        ),
        "confidence": confidence,
    }


def call_ollama_for_alert(data: AnalysisData):
    prompt = build_structured_prompt(data)
    start = time.perf_counter()

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1
        }
    }

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json=payload,
        timeout=OLLAMA_TIMEOUT_SEC
    )
    response.raise_for_status()

    body = response.json()
    raw = body.get("response", "{}")

    parsed = json.loads(raw)
    result = normalize_ai_result(parsed)

    llm_latency_ms = (time.perf_counter() - start) * 1000
    return result, round(llm_latency_ms, 2)


def send_notification(message_payload: dict):
    if not ALERT_WEBHOOK_URL:
        return {
            "sent": False,
            "channel": "none",
            "reason": "ALERT_WEBHOOK_URL_NOT_SET"
        }

    try:
        resp = requests.post(ALERT_WEBHOOK_URL, json=message_payload, timeout=3)
        resp.raise_for_status()
        return {
            "sent": True,
            "channel": "webhook",
            "http_status": resp.status_code
        }
    except requests.RequestException as e:
        return {
            "sent": False,
            "channel": "webhook",
            "reason": "WEBHOOK_SEND_FAILED",
            "message": str(e)
        }


def build_telegram_message(data: AnalysisData, ai_result: dict) -> str:
    summary = ai_result.get("summary", "Phát hiện bất thường.")
    severity = ai_result.get("severity", "HIGH")
    recommendation = ai_result.get("recommendation", "Kiểm tra hiện trường ngay.")

    return (
        "CẢNH BÁO KHẨN: ANOMALY\n"
        f"- Nhiệt độ: {data.temperature}°C\n"
        f"- Độ ẩm: {data.humidity}%\n"
        f"- Điểm bất thường: {data.anomaly_score}\n"
        f"- Mức độ: {severity}\n"
        f"- Tóm tắt: {summary}\n"
        f"- Hành động: {recommendation}"
    )


def send_telegram_alert(data: AnalysisData, ai_result: dict):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return {
            "sent": False,
            "channel": "telegram",
            "reason": "TELEGRAM_BOT_TOKEN_OR_CHAT_ID_NOT_SET"
        }

    message = build_telegram_message(data, ai_result)

    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "disable_web_page_preview": True
            },
            timeout=5
        )
        resp.raise_for_status()
        return {
            "sent": True,
            "channel": "telegram",
            "http_status": resp.status_code
        }
    except requests.RequestException as e:
        return {
            "sent": False,
            "channel": "telegram",
            "reason": "TELEGRAM_SEND_FAILED",
            "message": str(e)
        }


def build_fallback_ai_result() -> dict:
    return {
        "summary": "Phát hiện bất thường, cần xử lý ngay.",
        "severity": "HIGH",
        "recommendation": "Kiểm tra hiện trường ngay, cô lập khu vực và xác minh nguyên nhân.",
        "confidence": 0.0
    }


@app.post("/decide")
def decide(data: AnalysisData):
    start = time.perf_counter()

    if data.status == "ANOMALY":
        decision = "ALERT"
        action = "HIGH_ENVIRONMENT_RISK"

        ai_result = None
        ai_degraded = False
        ai_error = None
        llm_latency_ms = None

        try:
            ai_result, llm_latency_ms = call_ollama_for_alert(data)
        except Exception as e:
            ai_degraded = True
            ai_error = "OLLAMA_TIMEOUT"
            ai_result = build_fallback_ai_result()

        notify_payload = {
            "event": "ANOMALY_ALERT",
            "temperature": data.temperature,
            "humidity": data.humidity,
            "anomaly_score": data.anomaly_score,
            "timestamp": data.timestamp,
            "ai_alert": ai_result
        }

        notification = send_notification(notify_payload)
        telegram_alert = send_telegram_alert(data, ai_result)
        latency_ms = (time.perf_counter() - start) * 1000

        return {
            "agent": "decision",
            "status": "DEGRADED" if ai_degraded else "SUCCESS",
            "decision": decision,
            "action": action,
            "latency_ms": round(latency_ms, 2),
            "ai": {
                "invoked": True,
                "degraded": ai_degraded,
                "error": ai_error,
                "llm_latency_ms": llm_latency_ms,
                "model": OLLAMA_MODEL,
                "alert": ai_result
            },
            "notification": notification,
            "telegram": telegram_alert
        }

    decision = "NORMAL"
    action = "NO_ACTION"
    latency_ms = (time.perf_counter() - start) * 1000

    return {
        "agent": "decision",
        "status": "SUCCESS",
        "decision": decision,
        "action": action,
        "latency_ms": round(latency_ms, 2),
        "ai": {
            "invoked": False
        }
    }
