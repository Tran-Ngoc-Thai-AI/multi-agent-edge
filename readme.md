multi-agent-edge/
│
├── docker-compose.yml
│
├── agent1-sensor/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
│
├── agent2-analyzer/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py
│   └── train_model.py
│
├── agent3-decision/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
│
└── benchmark/
    └── benchmark.py

Command:
    docker compose build
    docker compose up -d
    docker compose ps
    curl http://localhost:8001/health
    curl http://localhost:8002/health
    curl http://localhost:8003/health

Test end to end:
    curl -X POST http://localhost:8001/process \
    -H "Content-Type: application/json" \
    -d "{\"temperature\":25,\"humidity\":55}"

    python benchmark/benchmark.py

    -----------

    PHASE 1 — MVP
────────────────────────
3 VM
3 Agent
REST
Scikit-learn
Fault tolerance
Benchmark
        ↓
        ↓
PHASE 2 — Edge AI
────────────────────────
Agent 2
Qwen2.5-0.5B Q4
llama.cpp
Benchmark ML vs LLM
        ↓
        ↓
PHASE 3 — Optimization
────────────────────────
Q4 vs Q8
CPU/RAM comparison
Latency comparison
Edge-only vs cloud
MQTT
Retry/Circuit breaker