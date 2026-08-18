# Multi-Agent Edge AI Demo

Hệ thống demo gồm 3 agent giao tiếp qua HTTP:

- `agent1-sensor`: nhận dữ liệu cảm biến và gọi sang agent phân tích
- `agent2-analyzer`: chạy `IsolationForest` để phát hiện bất thường
- `agent3-decision`: tạo quyết định, gọi Ollama để sinh diễn giải AI, và gửi alert qua Telegram khi có anomaly

Demo này tập trung vào 3 mục tiêu:

- Xử lý end-to-end qua nhiều agent
- Phát hiện anomaly bằng ML cục bộ
- Gửi cảnh báo AI và Telegram khi có sự kiện bất thường

## Kiến Trúc

```text
Client
  ↓
Agent 1 - Sensor
  ↓ HTTP
Agent 2 - Analyzer
  ↓ HTTP
Agent 3 - Decision
  ↓
Ollama / Telegram
  ↓
Response
```

## Công Nghệ

- Python 3.12
- FastAPI
- Uvicorn
- scikit-learn
- IsolationForest
- Ollama
- Telegram Bot API
- Docker
- Docker Compose
- psutil

## Chức Năng Chính

- Nhận nhiệt độ và độ ẩm từ client
- Tạo payload sensor có `timestamp`
- Phân tích anomaly bằng `IsolationForest`
- Chỉ gọi LLM khi trạng thái là `ANOMALY`
- Sinh alert tiếng Việt bằng Ollama
- Gửi thông báo Telegram khi có anomaly
- Trả về trạng thái `SUCCESS` hoặc `DEGRADED` nếu AI/LLM gặp lỗi

## Cấu Trúc Dịch Vụ

| Service | Port | Vai trò |
| --- | ---: | --- |
| `agent1-sensor` | 8001 | Nhận request từ client |
| `agent2-analyzer` | 8002 | Phân tích dữ liệu và nhận diện anomaly |
| `agent3-decision` | 8003 | Tạo quyết định, alert AI, notification |
| `phase2-ollama` | 11434 | Runtime cho mô hình ngôn ngữ |

## Yêu Cầu

- Docker
- Docker Compose
- Mạng đủ ổn định để tải image và model Ollama

## Chạy Demo

### 1. Build và chạy toàn bộ stack

```bash
docker compose up -d --build
```

### 2. Kiểm tra trạng thái service

```bash
docker compose ps
```

### 3. Gửi request demo

```bash
curl -X POST "http://localhost:8001/process" \
  -H "Content-Type: application/json" \
  -d "{\"temperature\":39.5,\"humidity\":88}"
```

## Luồng Xử Lý

1. Client gửi nhiệt độ và độ ẩm vào `agent1-sensor`
2. `agent1-sensor` chuyển dữ liệu sang `agent2-analyzer`
3. `agent2-analyzer` chạy `IsolationForest`
4. Nếu kết quả là `NORMAL`, hệ thống trả response nhanh
5. Nếu kết quả là `ANOMALY`, `agent2-analyzer` chuyển sang `agent3-decision`
6. `agent3-decision` gọi Ollama để sinh diễn giải AI tiếng Việt
7. Nếu có anomaly, hệ thống gửi Telegram alert
8. Response cuối cùng được trả ngược về client

## API

### Agent 1 - Sensor

`POST /process`

Request body:

```json
{
  "temperature": 39.5,
  "humidity": 88
}
```

### Agent 2 - Analyzer

`POST /analyze`

Input:

```json
{
  "temperature": 39.5,
  "humidity": 88,
  "timestamp": 1787078642.7450736
}
```

### Agent 3 - Decision

`POST /decide`

Input:

```json
{
  "temperature": 39.5,
  "humidity": 88,
  "anomaly_score": -0.02,
  "status": "ANOMALY",
  "timestamp": 1787078642.7450736
}
```

## Cấu Hình Môi Trường

Các biến môi trường chính:

- `AGENT2_URL`
- `AGENT2_TIMEOUT_SEC`
- `AGENT3_URL`
- `AGENT3_TIMEOUT_SEC`
- `OLLAMA_URL`
- `OLLAMA_MODEL`
- `OLLAMA_TIMEOUT_SEC`
- `ALERT_WEBHOOK_URL`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Nếu muốn dùng Telegram thật, cần điền token và chat id hợp lệ trước khi build container.

## Demo Output Mong Đợi

Với payload anomaly, response thường có dạng:

```json
{
  "agent": "sensor",
  "status": "SUCCESS",
  "analysis": {
    "agent": "analyzer",
    "status": "SUCCESS",
    "analysis": {
      "status": "ANOMALY"
    },
    "decision": {
      "agent": "decision",
      "status": "SUCCESS",
      "decision": "ALERT",
      "action": "HIGH_ENVIRONMENT_RISK",
      "ai": {
        "invoked": true,
        "alert": {
          "summary": "...",
          "severity": "HIGH",
          "recommendation": "..."
        }
      },
      "telegram": {
        "sent": true
      }
    }
  }
}
```

## Benchmark

### Kết Quả Gần Nhất

Chạy bằng:

```bash
python benchmark/benchmark.py
```

Kết quả:

```text
Requests       : 100
Successful     : 100
Failed         : 0
Total time     : 424.46 sec
p50 latency    : 5611.61 ms
p95 latency    : 5935.62 ms
Throughput     : 0.24 req/s
```

### Resource Usage

| Service | CPU Avg | CPU Peak | RAM Peak |
| --- | ---: | ---: | ---: |
| `agent1-sensor` | 0.25% | 2.80% | 39.71 MB |
| `agent2-analyzer` | 0.40% | 7.23% | 106.20 MB |
| `agent3-decision` | 0.48% | 2.09% | 41.23 MB |
| `phase2-ollama` | 147.52% | 202.52% | 1679.36 MB |

## Đánh Giá Benchmark

### Điểm tốt

- 100/100 request thành công
- Không có request lỗi
- Pipeline end-to-end hoạt động ổn định
- Alert Telegram đã gửi thành công
- Các agent Python bên ngoài rất nhẹ, phù hợp với môi trường edge

### Điểm cần lưu ý

- Latency end-to-end còn cao, khoảng 5.6 đến 5.9 giây mỗi request
- Throughput thấp, khoảng 0.24 request/giây
- Ollama là nút cổ chai chính
- CPU và RAM tập trung chủ yếu ở `phase2-ollama`

### Kết Luận Benchmark

Hệ thống phù hợp cho demo multi-agent edge có AI alert và fault tolerance cơ bản.  
Về mặt ổn định thì tốt, nhưng về hiệu năng thì chưa phù hợp cho workload realtime.

## Ghi Chú

- Nếu `OLLAMA_TIMEOUT_SEC` quá thấp, request anomaly có thể bị rơi về `DEGRADED`
- Nếu chưa cấu hình Telegram, hệ thống vẫn chạy bình thường nhưng sẽ không gửi alert
- Benchmark hiện tại đang đo theo mô hình chạy local trong Docker

## Kết Luận Demo

Demo đã chứng minh được:

- Giao tiếp HTTP giữa nhiều agent
- Phát hiện anomaly bằng ML cục bộ
- Sinh diễn giải AI bằng Ollama
- Gửi cảnh báo Telegram khi có anomaly
- Xử lý lỗi theo hướng graceful degradation thay vì crash toàn hệ thống

## Test case

curl -X POST "http://localhost:8001/process" \
  -H "Content-Type: application/json" \
  -d '{"temperature":24,"humidity":55}'

curl -X POST "http://localhost:8001/process" \
  -H "Content-Type: application/json" \
  -d '{"temperature":39.5,"humidity":88}'