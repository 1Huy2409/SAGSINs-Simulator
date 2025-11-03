#!/usr/bin/env python3
import csv, subprocess, sys, os
from collections import defaultdict

TOPO_CSV = "topology_data.csv"
# Cần cột: link_id, source_node, destination_node, capacity_bps, base_latency_milliseconds

def run(cmd: str):
    print("RUN:", cmd, flush=True)
    subprocess.run(cmd, shell=True, check=True)

def container_exists(container: str) -> bool:
    try:
        subprocess.run(
            f"docker inspect {container} >/dev/null 2>&1",
            shell=True, check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def ensure_tc(container: str) -> bool:
    if not container_exists(container):
        print(f"[WARN] Container '{container}' not found. Skip shaping.")
        return False
    try:
        # Kiểm tra 'tc' có sẵn không
        subprocess.run(
            f"docker exec {container} tc -v >/dev/null 2>&1",
            shell=True, check=True
        )
        return True
    except subprocess.CalledProcessError:
        print(f"[WARN] Container '{container}' missing 'tc' (iproute2). Skip shaping.")
        return False

def apply_on_container(container: str, delay_ms: int, rate_mbit: int):
    if not ensure_tc(container):
        return
    # Xóa qdisc cũ (nếu có)
    try:
        run(f"docker exec {container} tc qdisc del dev eth0 root")
    except subprocess.CalledProcessError:
        pass
    # netem (delay) + tbf (rate)
    run(f"docker exec {container} tc qdisc add dev eth0 root handle 1: netem delay {int(delay_ms)}ms")
    run(
        f"docker exec {container} tc qdisc add dev eth0 parent 1:1 handle 10: "
        f"tbf rate {int(rate_mbit)}mbit burst 64kb latency 400ms"
    )

def main():
    if not os.path.exists(TOPO_CSV):
        print("Missing", TOPO_CSV)
        sys.exit(1)

    # Gom theo container (lowercase tên container để khớp docker-compose)
    # rate = min(capacity_bps của mọi link mà container là src/dst)
    # delay = max(base_latency_ms ...)
    agg_rate = defaultdict(lambda: float("inf"))
    agg_delay = defaultdict(lambda: 0.0)

    with open(TOPO_CSV, newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            src_raw = (r.get("source_node") or r.get("source") or "").strip()
            dst_raw = (r.get("destination_node") or r.get("target") or "").strip()
            # ✅ chuyển lowercase để trùng tên service/container trong compose
            src = src_raw.lower()
            dst = dst_raw.lower()

            cap = float(r.get("capacity_bps") or r.get("capacity") or 1e6)
            delay = float(r.get("base_latency_milliseconds") or 0)

            if src:
                agg_rate[src] = min(agg_rate[src], cap)
                agg_delay[src] = max(agg_delay[src], delay)
            if dst:
                agg_rate[dst] = min(agg_rate[dst], cap)
                agg_delay[dst] = max(agg_delay[dst], delay)

    # Áp dụng shaping mỗi container đúng 1 lần
    for container, cap_bps in agg_rate.items():
        if not container:
            continue
        delay_ms = agg_delay[container]
        rate_mbit = max(int(cap_bps / 1e6), 1)
        print(f"Apply shaping on {container}: delay={delay_ms}ms, rate={rate_mbit}mbit")
        try:
            apply_on_container(container, delay_ms=int(delay_ms), rate_mbit=rate_mbit)
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] apply shaping on {container} failed: {e}")

if __name__ == "__main__":
    main()
