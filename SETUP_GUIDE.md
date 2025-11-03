# SAGSINs System - Setup Guide

## 🚀 Hệ thống hoàn chỉnh

Hệ thống bao gồm 3 phần chính:

1. **Web App** (Frontend + Backend) - Giao diện người dùng
2. **Docker Network** - Mạng mô phỏng với topology
3. **Traffic Generation** - Thu thập dữ liệu cho AI model

## 📋 Yêu cầu

- Docker & Docker Compose
- Node.js 18+
- Python 3.9+

## 🔧 Cài đặt

### 1. Khởi động Docker Network

```bash
cd docker
docker-compose up -d
```

Kiểm tra containers đang chạy:

```bash
docker ps
```

### 2. Khởi động Backend

```bash
cd wep-app/backend
npm install
npm start
```

Backend sẽ chạy tại: `http://localhost:3000`

### 3. Khởi động Frontend

```bash
cd wep-app/frontend
npm install
npm run dev -- --host
```

Frontend sẽ chạy tại: `http://localhost:5173`

## 📊 Flow hoạt động

```
┌─────────────┐         ┌──────────────┐         ┌─────────────────┐
│  Web App    │ Socket  │   Backend    │  HTTP   │  Docker Server  │
│  (Browser)  ├────────▶│   (Node.js)  ├────────▶│   (Flask)       │
└─────────────┘         └──────────────┘         └─────────────────┘
                                                           │
                                                           ▼
                                                  ┌─────────────────┐
                                                  │  1. Find Link   │
                                                  │  2. Gen Traffic │
                                                  │  3. Apply TC    │
                                                  │  4. Save CSV    │
                                                  └─────────────────┘
                                                           │
                                                           ▼
                                                  /data/traffic_data.csv
                                                  (Ready for VAE model)
```

## 🎯 Sử dụng

1. **Mở Web App** tại `http://localhost:5173`

2. **Chọn Source Node** - Node của bạn (VD: `SATELLITE_01`)

3. **Chọn Destination Node** - Node đích (VD: `UAV_01`)

4. **Nhập nội dung** và nhấn **"Gửi Packet"**

5. **Hệ thống tự động:**
   - ✅ Tìm topology link từ CSV
   - ✅ Tạo traffic metrics (bitrate, latency, loss, jitter, etc.)
   - ✅ Apply traffic shaping với `tc` command
   - ✅ Lưu vào `/data/traffic_data.csv`

## 📁 File CSV Output

File `traffic_data.csv` được tạo tại `docker/data/traffic_data.csv` với format:

```csv
timestamp,bytes_sent,bitrate_bps,rtt_milliseconds,loss_rate,jitter_milliseconds,
link_latency_milliseconds,capacity_bps,source_layer,destination_layer,link_id,
hour,day_of_week,is_weekend,hour_sin,hour_cos,day_sin,day_cos,utilization,
throughput_mbps,quality_score,efficiency
```

✅ **Phù hợp với VAE model của bạn!**

## 🔍 Kiểm tra dữ liệu

### Xem logs của Docker server:

```bash
docker logs sagsins-server -f
```

### Xem traffic data:

```bash
cat docker/data/traffic_data.csv
# hoặc
tail -f docker/data/traffic_data.csv
```

### Kiểm tra topology:

```bash
curl http://localhost:8080/topology
```

### Test forward packet:

```bash
curl -X POST http://localhost:8080/packet \
  -H "Content-Type: application/json" \
  -d '{"source":"SATELLITE_01","destination":"UAV_01","content":"Test message"}'
```

## 🐛 Troubleshooting

### Backend không kết nối được Docker server:

1. Kiểm tra Docker server đang chạy:

   ```bash
   docker ps | grep sagsins-server
   ```

2. Kiểm tra logs:

   ```bash
   docker logs sagsins-server
   ```

3. Test kết nối:
   ```bash
   curl http://localhost:8080/
   ```

### Không tìm thấy topology link:

- Kiểm tra tên node trong `topology_data.csv` khớp với tên trong web app
- Node names phải viết hoa chính xác (VD: `SATELLITE_01`, không phải `satellite_01`)

### Traffic shaping không hoạt động:

- Container cần có capability `NET_ADMIN`
- Kiểm tra trong `docker-compose.yml`:
  ```yaml
  cap_add:
    - NET_ADMIN
  ```

## 📈 Sử dụng dữ liệu cho VAE Model

File CSV đã sẵn sàng để đưa vào model VAE:

```python
import pandas as pd

# Load traffic data
df = pd.read_csv('docker/data/traffic_data.csv')

# Features cho VAE
features = [
    'bitrate_bps', 'rtt_milliseconds', 'loss_rate', 'jitter_milliseconds',
    'utilization', 'throughput_mbps', 'quality_score', 'efficiency',
    'hour_sin', 'hour_cos', 'day_sin', 'day_cos'
]

X = df[features].values
# Train VAE model...
```

## 🎨 Web App Features

- ✅ Real-time packet sending/receiving
- ✅ Node selection với dropdown
- ✅ Packet queue management
- ✅ Beautiful UI với gradients
- ✅ Packet history log
- ✅ Auto-registration với backend

## 🔐 Environment Variables

### Backend (.env):

```
PORT=3000
DOCKER_SERVER_URL=http://localhost:8080/packet
```

### Frontend (.env):

```
VITE_API_URL=http://localhost:3000
```

## 📝 Notes

- Traffic data được append vào CSV, không overwrite
- Mỗi packet tạo 1 record trong CSV
- Metrics được simulate realistic dựa trên topology
- TC shaping chỉ apply khi container tồn tại

## 🆘 Support

Nếu có vấn đề, check logs:

- Backend: Terminal where `npm start` is running
- Docker: `docker logs sagsins-server -f`
- Frontend: Browser console (F12)
