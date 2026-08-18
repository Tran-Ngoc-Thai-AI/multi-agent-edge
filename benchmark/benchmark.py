import csv
import subprocess
import threading
import time
import statistics

import requests


# ============================================================
# CONFIG
# ============================================================

TARGET_URL = "http://localhost:8001/process"

CONTAINERS = [
    "agent1-sensor",
    "agent2-analyzer",
    "agent3-decision",
    "phase2-ollama",
]

NUM_REQUESTS = 100

# Resource sampling interval
SAMPLE_INTERVAL = 0.2

# Output
CSV_FILE = "benchmark/results/results.csv"


# ============================================================
# SHARED STATE
# ============================================================

monitoring = False

resource_samples = {
    container: {
        "cpu": [],
        "memory_mb": [],
    }
    for container in CONTAINERS
}


# ============================================================
# DOCKER RESOURCE MONITOR
# ============================================================

def get_docker_stats():

    result = subprocess.run(
        [
            "docker",
            "stats",
            "--no-stream",
            "--format",
            "{{.Name}},{{.CPUPerc}},{{.MemUsage}}",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    stats = {}

    for line in result.stdout.strip().splitlines():

        parts = line.split(",")

        if len(parts) != 3:
            continue

        name = parts[0]

        if name not in CONTAINERS:
            continue

        cpu = parse_cpu(parts[1])

        memory = parse_memory(
            parts[2].split("/")[0].strip()
        )

        stats[name] = {
            "cpu": cpu,
            "memory_mb": memory,
        }

    return stats


def parse_cpu(value):

    try:
        return float(
            value.replace("%", "").strip()
        )
    except ValueError:
        return 0.0


def parse_memory(value):

    value = value.upper().strip()

    try:

        if "GIB" in value:
            return (
                float(value.replace("GIB", "").strip())
                * 1024
            )

        if "MIB" in value:
            return float(
                value.replace("MIB", "").strip()
            )

        if "KIB" in value:
            return (
                float(value.replace("KIB", "").strip())
                / 1024
            )

        if "GB" in value:
            return (
                float(value.replace("GB", "").strip())
                * 1024
            )

        if "MB" in value:
            return float(
                value.replace("MB", "").strip()
            )

        if "KB" in value:
            return (
                float(value.replace("KB", "").strip())
                / 1024
            )

        return 0.0

    except ValueError:
        return 0.0


# ============================================================
# RESOURCE MONITOR THREAD
# ============================================================

def resource_monitor():

    global monitoring

    while monitoring:

        try:

            stats = get_docker_stats()

            for container in CONTAINERS:

                if container not in stats:
                    continue

                resource_samples[
                    container
                ]["cpu"].append(
                    stats[container]["cpu"]
                )

                resource_samples[
                    container
                ]["memory_mb"].append(
                    stats[container]["memory_mb"]
                )

        except Exception as e:

            print(
                f"[Monitor warning] {e}"
            )

        time.sleep(SAMPLE_INTERVAL)


# ============================================================
# PERCENTILE
# ============================================================

def percentile(values, p):

    if not values:
        return 0.0

    values = sorted(values)

    index = int(
        len(values) * p
    )

    if index >= len(values):
        index = len(values) - 1

    return values[index]


# ============================================================
# BENCHMARK
# ============================================================

def run_benchmark():

    global monitoring

    latencies = []

    success_count = 0
    failed_count = 0

    print("Starting benchmark...")
    print(f"Requests: {NUM_REQUESTS}")
    print(
        f"Resource sampling: "
        f"{SAMPLE_INTERVAL}s"
    )
    print()

    # --------------------------------------------------------
    # Start resource monitor
    # --------------------------------------------------------

    monitoring = True

    monitor_thread = threading.Thread(
        target=resource_monitor,
        daemon=True,
    )

    monitor_thread.start()

    # --------------------------------------------------------
    # Start benchmark
    # --------------------------------------------------------

    benchmark_start = time.perf_counter()

    for i in range(NUM_REQUESTS):

        payload = {
            "temperature": 25 + (i % 10),
            "humidity": 50 + (i % 20),
        }

        start = time.perf_counter()

        try:

            response = requests.post(
                TARGET_URL,
                json=payload,
                timeout=10,
            )

            response.raise_for_status()

            success_count += 1

        except Exception as e:

            failed_count += 1

            print(
                f"Request {i + 1} failed: {e}"
            )

        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        latencies.append(latency_ms)

    benchmark_duration = (
        time.perf_counter()
        - benchmark_start
    )

    # --------------------------------------------------------
    # Stop resource monitor
    # --------------------------------------------------------

    monitoring = False

    monitor_thread.join(
        timeout=2
    )

    # --------------------------------------------------------
    # Calculate metrics
    # --------------------------------------------------------

    if latencies:

        p50 = statistics.median(
            latencies
        )

        p95 = percentile(
            latencies,
            0.95
        )

    else:

        p50 = 0
        p95 = 0

    throughput = (
        success_count / benchmark_duration
        if benchmark_duration > 0
        else 0
    )

    # --------------------------------------------------------
    # Print E2E
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("END-TO-END BENCHMARK")
    print("=" * 60)

    print(
        f"Requests       : {NUM_REQUESTS}"
    )

    print(
        f"Successful     : {success_count}"
    )

    print(
        f"Failed         : {failed_count}"
    )

    print(
        f"Total time     : "
        f"{benchmark_duration:.2f} sec"
    )

    print(
        f"p50 latency    : "
        f"{p50:.2f} ms"
    )

    print(
        f"p95 latency    : "
        f"{p95:.2f} ms"
    )

    print(
        f"Throughput     : "
        f"{throughput:.2f} req/s"
    )

    # --------------------------------------------------------
    # Print resource
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("RESOURCE BENCHMARK")
    print("=" * 60)

    results = []

    for container in CONTAINERS:

        cpus = resource_samples[
            container
        ]["cpu"]

        memories = resource_samples[
            container
        ]["memory_mb"]

        if cpus:

            cpu_avg = statistics.mean(cpus)
            cpu_peak = max(cpus)

        else:

            cpu_avg = 0
            cpu_peak = 0

        if memories:

            ram_peak = max(memories)

        else:

            ram_peak = 0

        print()
        print(container)

        print(
            f"CPU avg       : "
            f"{cpu_avg:.2f}%"
        )

        print(
            f"CPU peak      : "
            f"{cpu_peak:.2f}%"
        )

        print(
            f"RAM peak      : "
            f"{ram_peak:.2f} MB"
        )

        results.append({
            "container": container,
            "cpu_avg_percent": round(
                cpu_avg,
                2
            ),
            "cpu_peak_percent": round(
                cpu_peak,
                2
            ),
            "ram_peak_mb": round(
                ram_peak,
                2
            ),
        })

    # --------------------------------------------------------
    # Save CSV
    # --------------------------------------------------------

    save_results(
        results,
        p50,
        p95,
        throughput,
        benchmark_duration,
        success_count,
        failed_count,
    )


# ============================================================
# SAVE CSV
# ============================================================

def save_results(
    resource_results,
    p50,
    p95,
    throughput,
    duration,
    success,
    failed,
):

    with open(
        CSV_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "metric",
            "value",
        ])

        writer.writerow([
            "requests",
            NUM_REQUESTS,
        ])

        writer.writerow([
            "successful",
            success,
        ])

        writer.writerow([
            "failed",
            failed,
        ])

        writer.writerow([
            "total_time_sec",
            round(duration, 4),
        ])

        writer.writerow([
            "e2e_p50_ms",
            round(p50, 4),
        ])

        writer.writerow([
            "e2e_p95_ms",
            round(p95, 4),
        ])

        writer.writerow([
            "throughput_req_sec",
            round(throughput, 4),
        ])

        writer.writerow([])

        writer.writerow([
            "container",
            "cpu_avg_percent",
            "cpu_peak_percent",
            "ram_peak_mb",
        ])

        for result in resource_results:

            writer.writerow([
                result["container"],
                result["cpu_avg_percent"],
                result["cpu_peak_percent"],
                result["ram_peak_mb"],
            ])

    print()
    print(
        f"Results saved to: {CSV_FILE}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    run_benchmark()