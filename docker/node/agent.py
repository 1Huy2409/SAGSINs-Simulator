import os
import time
import random
import requests
import csv
import sys
import math
from datetime import datetime

# ==============================
# Cấu hình môi trường
# ==============================
NODE_ID_RAW = os.getenv("NODE_ID", "unknown")
NODE_ID = NODE_ID_RAW.strip().lower()
SERVER = os.getenv("SERVER_IP", "10.10.0.100")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8080"))
SLEEP = float(os.getenv("SEND_INTERVAL", "3"))
TOPO_FILE = os.getenv("TOPOLOGY_FILE", "topology_data.csv")

# Control automatic traffic generation (NEW!)
AUTO_TRAFFIC = os.getenv("AUTO_TRAFFIC", "false").lower() == "true"

# ==============================
# Thêm logging tốt hơn
# ==============================
def log(msg):
    print(f"[{NODE_ID}] {msg}", flush=True)  # flush=True để log xuất hiện ngay
    sys.stdout.flush()

# ==============================
# Đọc danh sách link từ file topology
# ==============================
def load_links(node_id_lc: str):
    links = []
    
    # Kiểm tra file có tồn tại không
    if not os.path.exists(TOPO_FILE):
        log(f"ERROR: Topology file not found: {TOPO_FILE}")
        log(f"Current directory: {os.getcwd()}")
        log(f"Files in current directory: {os.listdir('.')}")
        return links
    
    try:
        with open(TOPO_FILE, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                src = (row.get("source_node") or "").strip()
                dst = (row.get("destination_node") or "").strip()
                
                if src.lower() == node_id_lc or dst.lower() == node_id_lc:
                    links.append({
                        "link_id": row["link_id"],
                        "source_node": src,
                        "destination_node": dst,
                        "source_layer": row.get("source_layer", "unknown"),
                        "destination_layer": row.get("destination_layer", "unknown"),
                        "min_capacity_bps": int(float(row.get("min_capacity_bps", row.get("capacity_bps", 1e6)))),
                        "max_capacity_bps": int(float(row.get("max_capacity_bps", row.get("capacity_bps", 1e6)))),
                        "capacity_bps": int(float(row.get("capacity_bps", 1e6))),
                        "base_latency_milliseconds": float(row.get("base_latency_milliseconds", 0.0)),
                    })
        
        log(f"Loaded {len(links)} links for node {node_id_lc}")
        if not links:
            log(f"WARN: No links found for node {node_id_lc} in {TOPO_FILE}")
            
    except Exception as e:
        log(f"ERROR reading {TOPO_FILE}: {e}")
        import traceback
        traceback.print_exc()
        
    return links

# ==============================
# Tạo payload dữ liệu giả lập traffic với features cho ML
# ==============================
def make_payload(link_data):
    bitrate_min = min(link_data["min_capacity_bps"], link_data["max_capacity_bps"])
    bitrate_max = max(link_data["min_capacity_bps"], link_data["max_capacity_bps"])
    
    # Generate bitrate with realistic variation
    bitrate_bps = random.randint(bitrate_min, bitrate_max)
    capacity_bps = link_data["capacity_bps"]
    
    # Calculate utilization (0-1)
    utilization = min(bitrate_bps / capacity_bps, 1.0) if capacity_bps > 0 else 0.0
    
    # Network quality metrics
    # Loss rate: tăng khi utilization cao
    loss_rate = random.uniform(0.001, 0.002) if utilization < 0.7 else random.uniform(0.002, 0.01)
    
    # Link latency
    link_latency_milliseconds = link_data["base_latency_milliseconds"]
    
    # Jitter: dao động delay (ms) - phụ thuộc utilization
    base_jitter = random.uniform(5.0, 25.0)
    jitter_milliseconds = base_jitter * (0.5 + utilization * 0.5)  # Tăng khi congestion
    
    # RTT: round-trip time (ms) - base latency + random variation
    rtt_milliseconds = link_latency_milliseconds + random.uniform(-5, 5)
    
    # Bytes sent in last 30s interval (for consistent format)
    bytes_sent = bitrate_bps * 30 / 8  # 30 seconds worth of data
    
    # Throughput in Mbps
    throughput_mbps = bitrate_bps / 1_000_000
    
    # Quality score: inversely related to loss rate and jitter, positively to utilization
    quality_score = (1 - loss_rate) * (1 - min(jitter_milliseconds / 100, 0.5)) * 0.98
    
    # Efficiency: how well the link is being used
    efficiency = utilization * quality_score
    
    # Temporal features
    now = datetime.utcnow()
    hour = now.hour
    day_of_week = now.weekday()  # 0=Monday, 6=Sunday
    
    # Cyclic encoding for time features
    hour_sin = math.sin(2 * math.pi * hour / 24)
    hour_cos = math.cos(2 * math.pi * hour / 24)
    day_sin = math.sin(2 * math.pi * day_of_week / 7)
    day_cos = math.cos(2 * math.pi * day_of_week / 7)
    
    # Weekend flag (0=weekday, 1=weekend)
    is_weekend = 1 if day_of_week >= 5 else 0
    
    payload = {
        # Core metrics
        "bytes_sent": round(bytes_sent, 2),
        "bitrate_bps": bitrate_bps,
        "rtt_milliseconds": round(rtt_milliseconds, 6),
        "loss_rate": round(loss_rate, 10),
        "jitter_milliseconds": round(jitter_milliseconds, 6),
        "link_latency_milliseconds": round(link_latency_milliseconds, 6),
        "capacity_bps": capacity_bps,
        
        # Layer information
        "source_layer": link_data["source_layer"],
        "destination_layer": link_data["destination_layer"],
        "link_id": link_data["link_id"],
        
        # Temporal features
        "hour": hour,
        "day_of_week": day_of_week,
        "is_weekend": is_weekend,
        "hour_sin": round(hour_sin, 10),
        "hour_cos": round(hour_cos, 10),
        "day_sin": round(day_sin, 10),
        "day_cos": round(day_cos, 10),
        
        # Derived metrics
        "utilization": round(utilization, 10),
        "throughput_mbps": round(throughput_mbps, 10),
        "quality_score": round(quality_score, 10),
        "efficiency": round(efficiency, 10),
        
        # Metadata
        "node_id": NODE_ID,
        "destination": link_data["destination_node"],
    }
    return payload

# ==============================
# Gửi payload đến server
# ==============================
def send(link_data):
    url = f"http://{SERVER}:{SERVER_PORT}/ingest"
    payload = make_payload(link_data)
    try:
        r = requests.post(url, json=payload, timeout=5)
        log(f"sent link={link_data['link_id']}, bitrate={payload['bitrate_bps']}bps -> {r.status_code}")
    except requests.exceptions.ConnectionError as e:
        log(f"Connection error to {url}: {e}")
    except Exception as e:
        log(f"Error sending: {e}")

# ==============================
# Main loop
# ==============================
if __name__ == "__main__":
    try:
        log("="*50)
        log(f"Node starting...")
        log(f"NODE_ID: {NODE_ID}")
        log(f"SERVER: {SERVER}:{SERVER_PORT}")
        log(f"AUTO_TRAFFIC: {AUTO_TRAFFIC}")
        log("="*50)
        
        # Check if automatic traffic generation is enabled
        if not AUTO_TRAFFIC:
            log("⚠️  AUTOMATIC TRAFFIC GENERATION: DISABLED")
            log("📌 Mode: MANUAL (Web UI only)")
            log("🔧 This node will only participate in traffic when triggered by Web UI")
            log("⏸️  Container running in idle mode...")
            log("="*50)
            
            # Keep container alive but do nothing
            while True:
                time.sleep(3600)  # Sleep 1 hour
        
        # Original automatic traffic code (only runs if AUTO_TRAFFIC=true)
        log("✅ AUTOMATIC TRAFFIC GENERATION: ENABLED")
        log(f"TOPOLOGY_FILE: {TOPO_FILE}")
        log(f"SEND_INTERVAL: {SLEEP}s")
        
        links = load_links(NODE_ID)
        
        if not links:
            log("ERROR: No links loaded. Agent will not send any data.")
            log("Check if NODE_ID matches source_node or destination_node in topology file")
            # Không exit, để container tiếp tục chạy để debug
        
        time.sleep(random.uniform(0, 2))
        
        log("Starting main loop...")
        
        while True:
            if links:
                link_data = random.choice(links)
                send(link_data)
            else:
                log("WARN: No link available, skipping...")
            time.sleep(SLEEP)
            
    except KeyboardInterrupt:
        log("Shutting down...")
    except Exception as e:
        log(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)