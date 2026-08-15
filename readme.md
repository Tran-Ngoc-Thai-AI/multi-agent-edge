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
    curl -X POST http://localhost:8001/process -H "Content-Type: application/json" -d "{\"temperature\":38.5,\"humidity\":82}"
    Invoke-RestMethod -Uri "http://localhost:8001/process" -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"temperature":38.5,"humidity":82}'