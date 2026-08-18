# Multi-Agent Edge AI — Project Handoff

## Phase 1 — MVP: COMPLETED ✅

### Mục tiêu Phase 1

Phase 1 đã hoàn thành MVP của hệ thống **Multi-Agent Edge AI** với:

* 3 Agent độc lập.
* 3 Docker container riêng biệt.
* Giao tiếp giữa các Agent bằng HTTP/REST.
* Local AI/ML inference.
* CPU-only.
* Fault tolerance cơ bản.
* Benchmark hiệu năng và tài nguyên.

### Kiến trúc Phase 1

```text
Client
  │
  ▼
Agent 1 — Sensor
  │ HTTP
  ▼
Agent 2 — Analyzer
  │ HTTP
  ▼
Agent 3 — Decision
  │
  ▼
Response
```

---

## Vai trò các Agent

| Agent   | Vai trò  | Port | Chức năng chính                            |
| ------- | -------- | ---: | ------------------------------------------ |
| Agent 1 | Sensor   | 8001 | Nhận và tiền xử lý temperature/humidity    |
| Agent 2 | Analyzer | 8002 | Local ML inference, anomaly detection      |
| Agent 3 | Decision | 8003 | Phân tích kết quả và đưa ra decision/alert |

---

## Công nghệ Phase 1

* Python 3.12
* FastAPI
* Uvicorn
* scikit-learn
* Isolation Forest
* REST/HTTP
* Docker
* Docker Compose
* psutil / Docker Stats
* Python Benchmark

---

## Các yêu cầu MVP đã hoàn thành

* [x] 3 Agent
* [x] 3 Docker container
* [x] Agent có vai trò khác nhau
* [x] Network communication
* [x] Local AI/ML inference
* [x] CPU-only
* [x] Fault tolerance cơ bản
* [x] Timeout handling
* [x] CPU average measurement
* [x] CPU peak measurement
* [x] RAM peak measurement
* [x] E2E latency measurement
* [x] p50 latency
* [x] p95 latency
* [x] Throughput measurement
* [x] Benchmark CSV
* [x] Agent failure test

---

## Fault Tolerance đã kiểm chứng

Fault tolerance đã được kiểm tra bằng cách dừng Agent 3:

```bash
docker stop agent3-decision
```

Sau đó gửi request vào Agent 1:

```bash
curl -X POST http://localhost:8001/process \
  -H "Content-Type: application/json" \
  -d "{\"temperature\":38.5,\"humidity\":82}"
```

Hệ thống vẫn phản hồi và chuyển sang trạng thái:

```text
DEGRADED
```

với lỗi timeout thay vì crash toàn bộ hệ thống.

Sau đó Agent 3 được restart:

```bash
docker start agent3-decision
```

Hệ thống hoạt động trở lại bình thường.

### Kết luận

Phase 1 đã chứng minh được:

```text
Agent Failure
      ↓
Timeout Handling
      ↓
DEGRADED State
      ↓
System vẫn phản hồi
      ↓
Agent Recovery
      ↓
System hoạt động bình thường
```

---

## Benchmark Phase 1

### Test Configuration

```text
Requests       : 100
Successful     : 100
Failed         : 0
Total time     : 3.19 sec
p50 latency    : 31.88 ms
p95 latency    : 42.69 ms
Throughput     : 31.37 req/s
```

### Resource Usage

| Agent              | CPU Avg | CPU Peak |  RAM Peak |
| ------------------ | ------: | -------: | --------: |
| Agent 1 — Sensor   |  10.60% |   13.43% |  40.80 MB |
| Agent 2 — Analyzer |  31.79% |   43.36% | 111.00 MB |
| Agent 3 — Decision |   4.11% |    5.15% |  36.81 MB |

### Benchmark Output

Kết quả benchmark được lưu tại:

```text
benchmark/results/results.csv
```

---

## Resource Budget

### Target theo đề bài

```text
CPU : 2 vCPU
RAM : 4 GB
Mode: CPU-only
```

Phase 1 hiện tại chạy ổn định với workload MVP và mức sử dụng tài nguyên thấp.

> **Lưu ý:** Benchmark Phase 1 được thực hiện trên Docker local. Việc chứng minh mỗi Agent thực sự chạy trên một Edge VM độc lập với cấu hình **2 vCPU / 4 GB RAM** sẽ là trọng tâm của Phase 2.

---

# Phase 2 — Hybrid Edge AI 🚀

## Mục tiêu Phase 2

Nâng cấp hệ thống từ **Simple ML** lên **Hybrid Edge AI**, giữ nguyên kiến trúc Multi-Agent và baseline của Phase 1.

```text
Agent 1 — Sensor
      ↓
Agent 2 — ML Analyzer
      ↓
IsolationForest
      ↓
   ANOMALY?
    │    │
   NO   YES
    │    ↓
    │  Ollama
    │    ↓
    │ Local LLM
    │    ↓
    └→ Agent 3
         ↓
   Decision + Notification
```

### Thành phần

| Component | Role                                 |
| --------- | ------------------------------------ |
| Agent 1   | Sensor                               |
| Agent 2   | ML Analyzer + IsolationForest        |
| Agent 3   | Decision + Notification              |
| Ollama    | Local AI Runtime của Agent 3         |
| Local LLM | AI interpretation / Alert generation |
| Messaging | Alert delivery                       |

**Ollama không phải Agent độc lập.**

---

## AI Upgrade

IsolationForest tiếp tục là **source of truth** cho anomaly detection.

LLM chỉ được gọi khi:

```text
IsolationForest → ANOMALY → Ollama → AI Alert
```

LLM không thay thế hoặc override IsolationForest.

---

## Edge Constraint

```text
CPU : 2 vCPU
RAM : 4 GB
GPU : None
Execution : CPU-only
```

Model thử nghiệm:

```text
Qwen2.5 0.5B
```

Preliminary standalone inference:

```text
Warm ≈ 0.93s
Cold-ish ≈ 1.34s
RAM ≈ 599MB
```

Benchmark chính thức thực hiện sau khi tích hợp End-to-End.

---

## Benchmark

So sánh **Phase 1 Baseline vs Phase 2 Hybrid AI**.

Metrics chính:

* CPU / RAM
* Model memory
* Inference latency
* E2E latency
* p50 / p95
* Throughput
* Notification latency
* AI response quality
* Fault tolerance

Mục tiêu:

```text
AI Capability ↔ Resource ↔ Latency ↔ Throughput
```

---

## Fault Tolerance

LLM là **AI Enhancement**, không phải thành phần bắt buộc.

Nếu Ollama unavailable:

```text
ANOMALY → Ollama unavailable → Agent 3 → FALLBACK / DEGRADED
```

IsolationForest vẫn phải hoạt động độc lập.

---

# Roadmap

```text
PHASE 1 — MVP
3 Agents / 3 Docker / HTTP
IsolationForest / CPU-only
Fault Tolerance / Benchmark

STATUS: COMPLETED ✅
        │
        ▼
PHASE 2 — HYBRID EDGE AI
IsolationForest
+
Ollama / Local LLM
+
AI Alert
+
Messaging
+
Benchmark

STATUS: NEXT 🚀
```

---

## Nguyên tắc Phase 2

* Agent 1 = Sensor
* Agent 2 = ML Analyzer
* Agent 3 = Decision + Notification
* IsolationForest = Core Detection / Source of Truth
* Ollama = Local AI Runtime của Agent 3
* LLM chỉ xử lý `ANOMALY`
* CPU-only
* 2 vCPU / 4 GB RAM
* Giữ HTTP architecture
* Giữ fault tolerance
* Không mở rộng MQTT / Distributed Edge / Edge vs Cloud trong Phase 2

---

## Handoff — New Chat

Bắt đầu **Phase 2 — Hybrid Edge AI** từ code Phase 1 hiện tại.

Thứ tự thực hiện:

```text
1. Kiểm tra code Agent 3 hiện tại
2. Xác định Agent 2 → Agent 3 HTTP contract
3. Tích hợp Ollama
4. Chỉ gọi LLM khi ANOMALY
5. Structured prompt + JSON output
6. AI-generated Alert
7. Messaging
8. End-to-End Test
9. Fault Tolerance Test
10. Benchmark Phase 2
11. So sánh với Phase 1
12. Đánh giá AI quality
```

**Phase 1 = COMPLETED ✅**

**Next milestone = Phase 2 — Hybrid Edge AI 🚀**
