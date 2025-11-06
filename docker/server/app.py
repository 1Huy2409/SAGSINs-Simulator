#!/usr/bin/env python3
"""
SAGSINs Server - Nhận packet từ Web App, tìm topology, tạo traffic và lưu CSV
"""
import os
import csv
import json
import math
import random
import subprocess
from datetime import datetime
from flask import Flask, request, jsonify
from collections import defaultdict
from traffic_adapter import TrafficAdapter  # ✅ Import adapter

app = Flask(__name__)

# ==============================
# Cấu hình
# ==============================
TOPOLOGY_FILE = "/app/topology_data.csv"
TRAFFIC_OUTPUT = "/data/traffic_data.csv"
DATA_DIR = "/data"

# Load topology data vào memory
topology_links = []
topology_map = {}  # Key: (source, destination) -> link_data

# ✅ Initialize Traffic Adapter
traffic_adapter = TrafficAdapter()

# ==============================
# Load topology từ CSV
# ==============================
def load_topology():
    global topology_links, topology_map
    
    if not os.path.exists(TOPOLOGY_FILE):
        print(f"⚠️ Topology file not found: {TOPOLOGY_FILE}")
        return
    
    try:
        with open(TOPOLOGY_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                link = {
                    "link_id": row["link_id"],
                    "source_node": row["source_node"].strip(),
                    "destination_node": row["destination_node"].strip(),
                    "source_layer": row.get("source_layer", "unknown"),
                    "destination_layer": row.get("destination_layer", "unknown"),
                    "capacity_bps": int(float(row.get("capacity_bps", 1e6))),
                    "base_latency_milliseconds": float(row.get("base_latency_milliseconds", 40.0)),
                    "min_capacity_bps": float(row.get("min_capacity_bps", row.get("capacity_bps", 1e6))),
                    "max_capacity_bps": float(row.get("max_capacity_bps", row.get("capacity_bps", 1e6))),
                    "reliability_score": float(row.get("reliability_score", 0.98)),
                }
                topology_links.append(link)
                
                # Map cho lookup nhanh
                key = (link["source_node"], link["destination_node"])
                topology_map[key] = link
        
        print(f"✅ Loaded {len(topology_links)} topology links")
        
    except Exception as e:
        print(f"❌ Error loading topology: {e}")

# ==============================
# Initialize traffic CSV với headers
# ==============================
def init_traffic_csv():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if not os.path.exists(TRAFFIC_OUTPUT):
        headers = [
            "timestamp", "bytes_sent", "bitrate_bps", "rtt_milliseconds",
            "loss_rate", "jitter_milliseconds", "link_latency_milliseconds",
            "capacity_bps", "source_layer", "destination_layer", "link_id",
            "hour", "day_of_week", "is_weekend", "hour_sin", "hour_cos",
            "day_sin", "day_cos", "utilization", "throughput_mbps",
            "quality_score", "efficiency"
        ]
        with open(TRAFFIC_OUTPUT, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
        print(f"✅ Initialized traffic CSV: {TRAFFIC_OUTPUT}")

# ==============================
# Tìm link từ topology
# ==============================
def find_link(source, destination):
    """Tìm link trực tiếp hoặc qua intermediate nodes"""
    # Direct link
    key = (source, destination)
    if key in topology_map:
        return topology_map[key]
    
    # Reverse direction (có thể bidirectional)
    reverse_key = (destination, source)
    if reverse_key in topology_map:
        link = topology_map[reverse_key].copy()
        link["source_node"] = source
        link["destination_node"] = destination
        return link
    
    return None

# ==============================
# Generate traffic metrics
# ==============================
def generate_traffic_metrics(link, content_length):
    """
    Generate realistic traffic metrics using TrafficAdapter
    (Replaces old random generation with training-matched patterns)
    """
    # ✅ Use adapter instead of random values
    metrics = traffic_adapter.generate_metrics(link, content_length)
    return metrics

# ==============================
# Save traffic data to CSV
# ==============================
def save_traffic_data(metrics):
    """Append traffic data to CSV file"""
    try:
        with open(TRAFFIC_OUTPUT, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                metrics["timestamp"], metrics["bytes_sent"], metrics["bitrate_bps"],
                metrics["rtt_milliseconds"], metrics["loss_rate"], metrics["jitter_milliseconds"],
                metrics["link_latency_milliseconds"], metrics["capacity_bps"],
                metrics["source_layer"], metrics["destination_layer"], metrics["link_id"],
                metrics["hour"], metrics["day_of_week"], metrics["is_weekend"],
                metrics["hour_sin"], metrics["hour_cos"], metrics["day_sin"], metrics["day_cos"],
                metrics["utilization"], metrics["throughput_mbps"],
                metrics["quality_score"], metrics["efficiency"]
            ])
        print(f"✅ Saved traffic data: {metrics['link_id']}")
    except Exception as e:
        print(f"❌ Error saving traffic data: {e}")

# ==============================
# Apply traffic shaping với tc
# ==============================
def apply_traffic_shaping(container_name, delay_ms, rate_mbps):
    """Apply tc qdisc shaping to container"""
    try:
        # Check if container exists
        result = subprocess.run(
            f"docker inspect {container_name} >/dev/null 2>&1",
            shell=True,
            capture_output=True
        )
        
        if result.returncode != 0:
            print(f"⚠️ Container {container_name} not found")
            return False
        
        # Remove old qdisc
        subprocess.run(
            f"docker exec {container_name} tc qdisc del dev eth0 root 2>/dev/null",
            shell=True
        )
        
        # Add netem (delay) + tbf (rate limit)
        subprocess.run(
            f"docker exec {container_name} tc qdisc add dev eth0 root handle 1: netem delay {int(delay_ms)}ms",
            shell=True,
            check=True
        )
        
        subprocess.run(
            f"docker exec {container_name} tc qdisc add dev eth0 parent 1:1 handle 10: "
            f"tbf rate {int(rate_mbps)}mbit burst 64kb latency 400ms",
            shell=True,
            check=True
        )
        
        print(f"✅ Applied shaping to {container_name}: delay={delay_ms}ms, rate={rate_mbps}mbps")
        return True
        
    except Exception as e:
        print(f"❌ Error applying shaping to {container_name}: {e}")
        return False

# ==============================
# API Endpoints
# ==============================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "SAGSINs Traffic Server",
        "status": "running",
        "topology_links": len(topology_links),
        "endpoints": {
            "POST /packet": "Receive packet from web app",
            "POST /ingest": "Receive traffic data from agents",
            "GET /topology": "Get topology information"
        }
    })

@app.route("/packet", methods=["POST"])
def receive_packet():
    """
    Nhận packet từ Web App
    Expected: { "source": "SATELLITE_01", "destination": "UAV_01", "content": "Hello" }
    """
    try:
        data = request.json
        source = data.get("source", "").strip()
        destination = data.get("destination", "").strip()
        content = data.get("content", "")
        
        print(f"📦 Received packet: {source} -> {destination}: {content}")
        
        # 1. Tìm link trong topology
        link = find_link(source, destination)
        
        if not link:
            return jsonify({
                "status": "error",
                "message": f"No topology link found for {source} -> {destination}"
            }), 404
        
        print(f"🔗 Found link: {link['link_id']}")
        
        # 2. Generate traffic metrics
        content_length = len(content.encode('utf-8'))
        metrics = generate_traffic_metrics(link, content_length)
        
        # 3. Save to CSV
        save_traffic_data(metrics)
        
        # 4. Apply traffic shaping to containers
        source_container = source.lower()
        dest_container = destination.lower()
        
        rate_mbps = link["capacity_bps"] / 1_000_000
        delay_ms = link["base_latency_milliseconds"]
        
        apply_traffic_shaping(source_container, delay_ms, rate_mbps)
        apply_traffic_shaping(dest_container, delay_ms, rate_mbps)
        
        return jsonify({
            "status": "success",
            "link": link["link_id"],
            "metrics": metrics,
            "message": "Traffic data saved and shaping applied"
        })
        
    except Exception as e:
        print(f"❌ Error processing packet: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/ingest", methods=["POST"])
def ingest():
    """Receive traffic data from agent nodes"""
    try:
        data = request.json
        # Agent gửi đầy đủ metrics, chỉ cần append vào CSV
        save_traffic_data(data)
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"❌ Error ingesting data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/nodes", methods=["GET"])
def get_nodes():
    """Get list of all unique nodes from topology"""
    nodes = set()
    for link in topology_links:
        nodes.add(link["source_node"])
        nodes.add(link["destination_node"])
    
    return jsonify(sorted(list(nodes)))

@app.route("/topology", methods=["GET"])
def get_topology():
    """Get topology information"""
    source = request.args.get("source")
    destination = request.args.get("destination")
    
    if source and destination:
        link = find_link(source, destination)
        if link:
            return jsonify({"status": "success", "link": link})
        else:
            return jsonify({"status": "error", "message": "Link not found"}), 404
    
    return jsonify({
        "status": "success",
        "total_links": len(topology_links),
        "links": topology_links
    })

# ==============================
# Initialize & Run
# ==============================
if __name__ == "__main__":
    print("="*60)
    print("🚀 SAGSINs Traffic Server Starting...")
    print("="*60)
    
    load_topology()
    init_traffic_csv()
    
    print("✅ Server ready!")
    print("="*60)
    
    app.run(host="0.0.0.0", port=8080, debug=False)
