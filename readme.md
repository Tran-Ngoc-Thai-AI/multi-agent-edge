# Multi-Agent Edge AI — Project Handoff

## Phase 1 — MVP: COMPLETED ✅

### 1. Mục tiêu Phase 1

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

## 2. Vai trò các Agent

| Agent   | Vai trò  | Port | Chức năng chính                            |
| ------- | -------- | ---: | ------------------------------------------ |
| Agent 1 | Sensor   | 8001 | Nhận và tiền xử lý temperature/humidity    |
| Agent 2 | Analyzer | 8002 | Local ML inference, anomaly detection      |
| Agent 3 | Decision | 8003 | Phân tích kết quả và đưa ra decision/alert |

---

## 3. Công nghệ Phase 1

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

## 4. Các yêu cầu MVP đã hoàn thành

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

## 5. Fault Tolerance đã kiểm chứng

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

## 6. Benchmark Phase 1

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

## 7. Resource Budget

### Target theo đề bài

```text
CPU : 2 vCPU
RAM : 4 GB
Mode: CPU-only
```

Phase 1 hiện tại chạy ổn định với workload MVP và mức sử dụng tài nguyên thấp.

> **Lưu ý:** Benchmark Phase 1 được thực hiện trên Docker local. Việc chứng minh mỗi Agent thực sự chạy trên một Edge VM độc lập với cấu hình **2 vCPU / 4 GB RAM** sẽ là trọng tâm của Phase 2.

---

# Phase 2 — AI Upgrade

## 8. Mục tiêu

Phase 2 tập trung vào **nâng cấp AI cho Agent 2 — Analyzer**.

Phase 1 sử dụng ML model nhỏ để hoàn thiện MVP và thiết lập baseline.

Phase 2 nâng cấp Agent 2 lên mô hình AI thực tế và có tính kỹ thuật cao hơn, ví dụ **Ollama / LLM**, nhưng vẫn phải hoạt động trong resource constraint:

```text
CPU : 2 vCPU
RAM : 4 GB
Mode: CPU-only
```

Mục tiêu là đánh giá khả năng chạy AI model nâng cao trong môi trường Edge resource-constrained.

---

## 9. AI Upgrade

Agent 2 được nâng cấp từ:

```text
Phase 1
Simple ML
      ↓
Phase 2
Advanced AI / LLM
```

Các hướng nghiên cứu:

* Ollama.
* Lightweight LLM.
* Model phù hợp với 2 vCPU / 4 GB RAM.
* CPU-only inference.
* Model optimization nếu cần.
* Quantization nếu cần.
* Local AI inference.

Kiến trúc Multi-Agent và giao tiếp HTTP của Phase 1 được giữ nguyên.

---

## 10. Benchmark Phase 2

Benchmark Phase 2 được so sánh với baseline Phase 1.

Các metric chính:

* CPU usage.
* RAM usage.
* Inference latency.
* E2E latency.
* p50 latency.
* p95 latency.
* Throughput.
* Model size.
* AI response quality.

Mục tiêu là đánh giá trade-off giữa:

```text
AI Capability
      ↕
CPU / RAM
      ↕
Latency
      ↕
Throughput
```

---

## 11. Mục tiêu hoàn thành Phase 2

* [ ] Nâng cấp Agent 2 từ Simple ML lên Advanced AI.
* [ ] Chạy được AI model trong môi trường CPU-only.
* [ ] Đáp ứng resource constraint 2 vCPU / 4 GB RAM.
* [ ] Ollama / LLM hoạt động ổn định nếu được lựa chọn.
* [ ] Benchmark Phase 2.
* [ ] So sánh với baseline Phase 1.
* [ ] Đánh giá CPU / RAM / latency / throughput.
* [ ] Đánh giá AI response quality.
* [ ] Đảm bảo End-to-End flow vẫn hoạt động.
* [ ] Đảm bảo fault tolerance vẫn hoạt động.

---

# 12. Roadmap Tổng thể

```text
┌──────────────────────────────────────┐
│ PHASE 1 — MVP & DEMO                 │
│                                      │
│ 3 Docker Containers                  │
│ 3 Agents                             │
│ HTTP                                │
│ Local ML                            │
│ CPU-only                            │
│ Fault Tolerance                     │
│ Benchmark                           │
│                                      │
│ STATUS: COMPLETED ✅                 │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│ PHASE 2 — AI UPGRADE                 │
│                                      │
│ Agent 2 AI Upgrade                  │
│ Advanced AI / LLM                   │
│ Ollama                              │
│ CPU-only                            │
│ 2 vCPU / 4 GB RAM                   │
│ Local AI Inference                  │
│ Benchmark                           │
│ AI Quality Evaluation               │
│                                      │
│ STATUS: NEXT 🚀                      │
└──────────────────────────────────────┘
```

---

# 13. Nguyên tắc thực hiện

Phase 2 giữ nguyên kiến trúc và baseline của Phase 1.

```text
Phase 1
Simple ML Baseline
       ↓
Agent 2 AI Upgrade
       ↓
Advanced AI / LLM
       ↓
2 vCPU / 4 GB RAM
       ↓
Benchmark
       ↓
Comparison
```

Không mở rộng sang Distributed Edge, MQTT hoặc Edge vs Cloud trong scope hiện tại.

---

# 14. Current Status

| Phase   | Nội dung                                                                          | Status      |
| ------- | --------------------------------------------------------------------------------- | ----------- |
| Phase 1 | MVP & Demo — 3 Agent / 3 Docker / HTTP / Local ML / Fault Tolerance / Benchmark   | ✅ COMPLETED |
| Phase 2 | AI Upgrade — Agent 2 / Advanced AI / LLM / Ollama / 2 vCPU / 4 GB RAM / Benchmark | 🚀 NEXT     |

---

# 15. Mục tiêu của Chat tiếp theo

Bắt đầu **Phase 2 — AI Upgrade** từ code Phase 1 hiện tại.

Trình tự:

```text
1. Kiểm tra Agent 2
2. Xác định model ML hiện tại
3. Xác định AI model phù hợp
4. Tích hợp Advanced AI / Ollama
5. Chạy CPU-only
6. Giới hạn 2 vCPU / 4 GB RAM
7. Test End-to-End
8. Benchmark
9. So sánh với Phase 1
10. Đánh giá kết quả
```

---

# Project Milestone

```text
┌─────────────────────────────────────┐
│ Multi-Agent Edge AI                 │
├─────────────────────────────────────┤
│                                     │
│ Phase 1 — MVP & Demo                │
│              ✅ COMPLETED           │
│                                     │
│ Phase 2 — AI Upgrade                │
│              🚀 NEXT                │
│                                     │
└─────────────────────────────────────┘
```

**Phase 1 MVP & Demo is complete.**

**Next milestone: Phase 2 — AI Upgrade for Agent 2.**
