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

# Phase 2 — Distributed Edge Deployment

## 8. Mục tiêu

Chuyển MVP từ mô hình chạy tập trung trên một máy:

```text
1 Machine
   │
   ├── Docker Agent 1
   ├── Docker Agent 2
   └── Docker Agent 3
```

sang mô hình phân tán:

```text
Edge VM 1
2 vCPU / 4 GB
└── Agent 1


        HTTP Network


Edge VM 2
2 vCPU / 4 GB
└── Agent 2


        HTTP Network


Edge VM 3
2 vCPU / 4 GB
└── Agent 3
```

---

## 9. Mục tiêu chính Phase 2

* [ ] Tạo 3 Edge VM riêng biệt.
* [ ] Mỗi VM có 2 vCPU / 4 GB RAM.
* [ ] CPU-only.
* [ ] Deploy đúng 1 Agent trên mỗi VM.
* [ ] Các Agent giao tiếp thật qua IP/network.
* [ ] Không sử dụng shared memory giữa các Agent.
* [ ] Không sử dụng function call nội bộ thay cho network communication.
* [ ] Cấu hình network/security.
* [ ] Kiểm tra health giữa các VM.
* [ ] Chạy End-to-End test trên 3 VM.
* [ ] Test fault tolerance bằng cách shutdown một VM/container.
* [ ] Benchmark lại trên môi trường distributed.
* [ ] Đo CPU/RAM/latency/throughput trên từng Edge VM.
* [ ] So sánh Phase 2 với baseline Phase 1.

---

## 10. Kiến trúc Phase 2

```text
                         HTTP
┌────────────────┐ ───────────────> ┌────────────────┐
│ Edge VM 1      │                  │ Edge VM 2      │
│ 2 vCPU / 4 GB  │                  │ 2 vCPU / 4 GB  │
│                │                  │                │
│ Agent 1        │                  │ Agent 2        │
│ Sensor         │                  │ Analyzer       │
└────────────────┘                  └───────┬────────┘
                                            │
                                            │ HTTP
                                            ▼
                                    ┌────────────────┐
                                    │ Edge VM 3      │
                                    │ 2 vCPU / 4 GB  │
                                    │                │
                                    │ Agent 3        │
                                    │ Decision       │
                                    └────────────────┘
```

---

## 11. Nguyên tắc Phase 2

### Không tối ưu sớm

Không thay đổi logic Agent nếu không cần thiết.

Mục tiêu Phase 2 là chứng minh:

```text
Cùng một MVP
     ↓
3 Edge VM độc lập
     ↓
Real Network
     ↓
Distributed System
     ↓
Distributed Benchmark
```

Chỉ sau khi Phase 2 chạy ổn định mới thực hiện optimization.

---

# Phase 3 — Edge AI Optimization & Advanced Evaluation

## 12. Mục tiêu

Phase 3 tập trung vào tối ưu Edge AI và đánh giá các trade-off:

```text
Model Quality
      ↕
Latency
      ↕
CPU
      ↕
RAM
      ↕
Throughput
```

---

## 13. Các hướng nâng cấp

### 13.1 Local AI nâng cao

Có thể nghiên cứu:

* Thay hoặc bổ sung model AI nhẹ hơn/thực tế hơn.
* Local LLM nếu phù hợp.
* Chọn model có kích thước phù hợp với giới hạn 4 GB RAM.
* Quantization nếu sử dụng LLM.
* Ghi rõ model size.
* Ghi rõ parameter count.
* Ghi rõ quantization level.

---

### 13.2 Optimization

Thực hiện benchmark theo mô hình:

```text
Baseline Model
      ↓
Benchmark
      ↓
Optimized Model
      ↓
Benchmark
      ↓
Comparison
```

So sánh:

* CPU
* RAM
* Latency
* Throughput
* Model quality

Đánh giá ảnh hưởng của optimization tới chất lượng model.

---

### 13.3 Fault Tolerance nâng cao

Có thể bổ sung:

* Retry
* Exponential backoff
* Circuit breaker
* Health checking
* Automatic recovery

---

### 13.4 Communication Optimization

Sau khi HTTP ở Phase 2 ổn định, có thể nghiên cứu:

```text
HTTP
  vs
MQTT
```

So sánh:

* Latency
* Throughput
* CPU
* RAM
* Network overhead
* Reliability

Không thực hiện phần này trước khi Phase 2 HTTP hoàn chỉnh.

---

### 13.5 Benchmark nâng cao

Benchmark với nhiều mức tải:

```text
10 requests
100 requests
500 requests
1000 requests
```

Đo:

* p50 latency
* p95 latency
* p99 latency
* Throughput
* CPU average
* CPU peak
* RAM peak
* E2E latency
* Agent-level latency

---

### 13.6 So sánh Edge Architecture

Có thể thực hiện hai mô hình.

#### Case A — Edge-only

```text
Agent 1 → Agent 2 → Agent 3
```

#### Case B — Edge + Cloud

```text
Agent 1 → Agent 2 → Cloud/Server
                         ↓
                      Agent 3
```

Phân tích trade-off:

* Latency
* Resource usage
* Network dependency
* Accuracy
* Cost

---

# 14. Roadmap Tổng thể

```text
┌──────────────────────────────────────┐
│ PHASE 1 — MVP                        │
│                                      │
│ 3 Docker Containers                 │
│ 3 Agents                            │
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
│ PHASE 2 — DISTRIBUTED EDGE           │
│                                      │
│ 3 Edge VM                            │
│ 2 vCPU / 4 GB mỗi VM                │
│ 1 Agent / VM                        │
│ Real Network                        │
│ Fault Tolerance                     │
│ Distributed Benchmark               │
│                                      │
│ STATUS: NEXT 🚀                      │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│ PHASE 3 — OPTIMIZATION               │
│                                      │
│ Model Optimization                   │
│ Quantization                         │
│ Advanced Benchmark                   │
│ Retry / Circuit Breaker             │
│ HTTP vs MQTT                         │
│ Edge vs Cloud                        │
│ Trade-off Analysis                   │
│                                      │
│ STATUS: PLANNED                      │
└──────────────────────────────────────┘
```

---

# 15. Nguyên tắc thực hiện

## Phase 2

Không tối ưu sớm.

Giữ nguyên MVP hiện tại càng nhiều càng tốt.

Tập trung theo thứ tự:

```text
Local Docker MVP
      ↓
3 Edge VM
      ↓
Real Network
      ↓
Distributed System
      ↓
Distributed Benchmark
```

Mục tiêu chính là chứng minh hệ thống **thực sự chạy phân tán trên 3 Edge node độc lập**.

---

## Phase 3

Chỉ bắt đầu sau khi Phase 2 hoàn chỉnh và ổn định.

Trình tự:

```text
Phase 2 Stable
      ↓
Optimization
      ↓
Benchmark
      ↓
Comparison
      ↓
Trade-off Analysis
      ↓
Final Evaluation
```

---

# 16. Current Status

| Phase   | Nội dung                                                                  | Status      |
| ------- | ------------------------------------------------------------------------- | ----------- |
| Phase 1 | MVP — 3 Agent / 3 Docker / HTTP / Local ML / Fault Tolerance / Benchmark  | ✅ COMPLETED |
| Phase 2 | Distributed Edge Deployment — 3 VM / Real Network / Distributed Benchmark | 🚀 NEXT     |
| Phase 3 | Edge AI Optimization & Advanced Evaluation                                | 📋 PLANNED  |

---

# 17. Mục tiêu của Chat tiếp theo

Bắt đầu **Phase 2 — Distributed Edge Deployment** từ code Phase 1 hiện tại.

Trình tự thực hiện:

```text
1. Kiểm tra cấu trúc code Phase 1
            ↓
2. Xác định IP / PORT và các biến cấu hình cần thay đổi
            ↓
3. Chuẩn bị 3 Edge VM
            ↓
4. Cấu hình network giữa 3 VM
            ↓
5. Deploy Agent 1 lên VM1
            ↓
6. Deploy Agent 2 lên VM2
            ↓
7. Deploy Agent 3 lên VM3
            ↓
8. Test health
            ↓
9. Test End-to-End
            ↓
10. Test fault tolerance
            ↓
11. Benchmark distributed
            ↓
12. So sánh với baseline Phase 1
```

### Điều kiện chuyển sang Phase 3

Chỉ chuyển sang Phase 3 khi Phase 2 đã hoàn thành:

* [ ] 3 Agent chạy trên 3 Edge VM độc lập.
* [ ] Network communication hoạt động ổn định.
* [ ] End-to-End flow hoạt động.
* [ ] Fault tolerance được kiểm chứng.
* [ ] Distributed benchmark hoàn tất.
* [ ] CPU/RAM/latency/throughput đã được đo.
* [ ] Kết quả Phase 2 đã được so sánh với baseline Phase 1.

---

# Project Milestone

```text
┌─────────────────────────────────────┐
│ Multi-Agent Edge AI                 │
├─────────────────────────────────────┤
│                                     │
│ Phase 1 — MVP                       │
│              ✅ COMPLETED           │
│                                     │
│ Phase 2 — Distributed Edge          │
│              🚀 NEXT                │
│                                     │
│ Phase 3 — Optimization              │
│              📋 PLANNED             │
│                                     │
└─────────────────────────────────────┘
```

**Phase 1 MVP is complete.**

**Next milestone: Phase 2 — Distributed Edge Deployment.**
