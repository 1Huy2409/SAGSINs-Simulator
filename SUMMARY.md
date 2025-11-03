# 🌐 SAGSINs System - Traffic Generation for VAE Model

## ✨ Tính năng đã hoàn thành

### 1. **Web Application** ✅

- Giao diện đẹp với gradient design
- Chọn source & destination node từ dropdown
- Gửi packet real-time qua Socket.IO
- Nhận packet và hiển thị logs
- Queue management cho offline nodes

### 2. **Backend Server (Node.js)** ✅

- Socket.IO server cho real-time communication
- Forward packets đến Docker network
- REST API cho nodes và packet queue
- Logging đầy đủ với emoji indicators

### 3. **Docker Network** ✅

- SAGSINs Server (Flask) nhận packets
- Tìm topology link từ CSV
- Generate traffic metrics (22 features)
- Apply traffic shaping với TC command
- Lưu vào CSV format cho VAE model

### 4. **Traffic Data Generation** ✅

Format CSV đầy đủ 22 features:

```
timestamp, bytes_sent, bitrate_bps, rtt_milliseconds, loss_rate,
jitter_milliseconds, link_latency_milliseconds, capacity_bps,
source_layer, destination_layer, link_id, hour, day_of_week,
is_weekend, hour_sin, hour_cos, day_sin, day_cos, utilization,
throughput_mbps, quality_score, efficiency
```

## 🚀 Quick Start

### Bước 1: Khởi động Docker Network

```bash
# Windows
start-docker.bat

# Linux/Mac
chmod +x start-docker.sh
./start-docker.sh
```

### Bước 2: Khởi động Backend (Terminal 1)

```bash
cd wep-app/backend
npm install
npm start
```

### Bước 3: Khởi động Frontend (Terminal 2)

```bash
cd wep-app/frontend
npm install
npm run dev -- --host
```

### Bước 4: Mở Web App

Truy cập: **http://localhost:5173**

### Bước 5: Test hệ thống

```bash
node test-system.js
```

## 📊 Flow hoạt động

```
User sends packet in Web UI
         ↓
Frontend (React) → Socket.IO → Backend (Node.js)
                                    ↓
                            Forward via HTTP POST
                                    ↓
                        Docker Server (Flask:8080)
                                    ↓
                    ┌───────────────┴────────────────┐
                    ↓                                ↓
            Find Topology Link              Generate Metrics
            (topology_data.csv)         (22 features for VAE)
                    ↓                                ↓
            Apply TC Shaping ←──────────────→ Save to CSV
            (delay + rate limit)         (/data/traffic_data.csv)
```

## 📁 Cấu trúc thư mục

```
SAGSINs-System/
├── docker/
│   ├── server/
│   │   ├── app.py              ← Flask server (UPDATED)
│   │   ├── requirements.txt    ← Dependencies (UPDATED)
│   │   └── Dockerfile
│   ├── node/
│   │   ├── agent.py
│   │   └── Dockerfile
│   ├── data/
│   │   └── traffic_data.csv    ← OUTPUT FILE
│   ├── topology_data.csv       ← Topology configuration
│   ├── docker-compose.yml
│   └── apply-shaping.py
├── wep-app/
│   ├── backend/
│   │   ├── server.js           ← Socket.IO + Forward (UPDATED)
│   │   ├── package.json
│   │   └── .env
│   └── frontend/
│       ├── src/
│       │   ├── App.jsx         ← UI (UPDATED)
│       │   ├── components/
│       │   │   ├── PacketForm.jsx
│       │   │   └── PacketLog.jsx
│       │   └── socket.js
│       └── package.json
├── start-docker.bat            ← Windows startup script
├── start-docker.sh             ← Linux/Mac startup script
├── test-system.js              ← Verification script
├── SETUP_GUIDE.md              ← Detailed guide
└── SUMMARY.md                  ← This file
```

## 🎯 Các thay đổi chính

### 1. `docker/server/app.py` - Hoàn toàn mới

- Flask server nhận HTTP POST từ backend
- Load topology từ CSV
- Generate 22 features cho VAE model
- Apply TC shaping to containers
- Save traffic data to CSV

### 2. `wep-app/backend/server.js` - Enhanced

- Forward packets qua HTTP POST
- Logging đẹp với emoji
- Error handling tốt hơn
- Show metrics từ Docker response

### 3. `docker/server/requirements.txt` - Updated

```
flask
requests
pandas
```

### 4. Traffic CSV Output Location

```
docker/data/traffic_data.csv
```

## 📈 Ví dụ Traffic Data

```csv
2025-10-29 08:30:15,45232.18,36185.744,85.23,0.0082,11.45,170.12,12000000,space,air,LINK_SPACE_AIR_01,8,1,0,-0.7071,0.7071,0.433,0.9009,0.72,36.19,0.9654,0.6951
```

Features này phù hợp hoàn toàn với VAE model của bạn!

## 🧪 Testing

### Test 1: Docker Server

```bash
curl http://localhost:8080/
```

### Test 2: Topology Lookup

```bash
curl "http://localhost:8080/topology?source=SATELLITE_01&destination=UAV_01"
```

### Test 3: Send Test Packet

```bash
curl -X POST http://localhost:8080/packet \
  -H "Content-Type: application/json" \
  -d '{"source":"SATELLITE_01","destination":"UAV_01","content":"Test"}'
```

### Test 4: Full System Verification

```bash
node test-system.js
```

## 📊 Monitor Traffic Generation

### Real-time Docker logs:

```bash
docker logs sagsins-server -f
```

### Watch traffic CSV:

```bash
# Windows
type docker\data\traffic_data.csv

# Linux/Mac
tail -f docker/data/traffic_data.csv
```

### Count records:

```bash
# Windows
find /c /v "" docker\data\traffic_data.csv

# Linux/Mac
wc -l docker/data/traffic_data.csv
```

## 🎨 UI Features

- 🎨 Beautiful gradient design
- 📊 Real-time packet logs
- 📬 Receive packets button
- 🎯 Dropdown node selection
- ✅ Connection status indicator
- 📱 Responsive layout

## 🔧 Configuration

### Backend `.env`:

```env
PORT=3000
DOCKER_SERVER_URL=http://localhost:8080/packet
```

### Frontend `.env`:

```env
VITE_API_URL=http://localhost:3000
```

### Docker Network:

- Server: `10.10.0.100:8080`
- Nodes: `10.10.0.11-10.10.0.27`

## 🐛 Troubleshooting

### Issue: Backend không connect được Docker

**Solution**:

```bash
# Check Docker is running
docker ps | grep sagsins-server

# Check logs
docker logs sagsins-server

# Restart container
cd docker
docker-compose restart sagsins-server
```

### Issue: Không tìm thấy topology link

**Solution**: Kiểm tra tên node trong `topology_data.csv` khớp với web app (case-sensitive)

### Issue: Traffic CSV không được tạo

**Solution**:

```bash
# Check data directory exists
ls docker/data/

# Check container permissions
docker exec sagsins-server ls -la /data/
```

## ✅ Checklist hoàn thành

- [x] Web UI với dropdown selection
- [x] Real-time Socket.IO communication
- [x] Backend forward đến Docker
- [x] Docker server nhận và process packets
- [x] Tìm topology link từ CSV
- [x] Generate 22 features cho VAE
- [x] Apply TC traffic shaping
- [x] Lưu CSV format chuẩn
- [x] Logging và monitoring
- [x] Error handling
- [x] Test scripts
- [x] Documentation

## 🎓 Sử dụng với VAE Model

```python
import pandas as pd
import numpy as np

# Load traffic data
df = pd.read_csv('docker/data/traffic_data.csv')

# Select features for VAE
features = [
    'bitrate_bps', 'rtt_milliseconds', 'loss_rate',
    'jitter_milliseconds', 'utilization', 'throughput_mbps',
    'quality_score', 'efficiency', 'hour_sin', 'hour_cos',
    'day_sin', 'day_cos'
]

X = df[features].values

# Normalize if needed
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train VAE model
# your_vae_model.fit(X_scaled)
```

## 🎉 Kết luận

Hệ thống đã hoàn thiện với đầy đủ tính năng:

1. ✅ Web app gửi/nhận packets
2. ✅ Backend forward đến Docker network
3. ✅ Docker server tìm topology và tạo traffic
4. ✅ TC shaping cho realistic simulation
5. ✅ CSV output với 22 features cho VAE

**Bạn có thể bắt đầu thu thập dữ liệu traffic ngay bây giờ!** 🚀
