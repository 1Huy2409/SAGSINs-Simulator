# 🔧 Rebuild Docker Containers

## Các thay đổi đã thực hiện:

✅ **Đã TẮT automatic traffic generation** từ tất cả node containers

### Thay đổi:

1. **agent.py**: Thêm check `AUTO_TRAFFIC` environment variable
2. **docker-compose.yml**: Set `AUTO_TRAFFIC=false` cho tất cả 10 nodes

### Kết quả:

❌ **TRƯỚC**: Nodes tự động gửi traffic mỗi 3 giây  
✅ **SAU**: Nodes chỉ idle, chờ commands từ Web UI

---

## 🚀 Cách rebuild containers:

```bash
# 1. Stop tất cả containers
cd docker
docker-compose down

# 2. Rebuild images với code mới
docker-compose build

# 3. Start lại containers
docker-compose up -d

# 4. Kiểm tra logs
docker logs satellite_01 -f
```

**Bạn sẽ thấy:**

```
[SATELLITE_01] ==================================================
[SATELLITE_01] Node starting...
[SATELLITE_01] NODE_ID: satellite_01
[SATELLITE_01] SERVER: 10.10.0.100:8080
[SATELLITE_01] AUTO_TRAFFIC: False
[SATELLITE_01] ==================================================
[SATELLITE_01] ⚠️  AUTOMATIC TRAFFIC GENERATION: DISABLED
[SATELLITE_01] 📌 Mode: MANUAL (Web UI only)
[SATELLITE_01] 🔧 This node will only participate in traffic when triggered by Web UI
[SATELLITE_01] ⏸️  Container running in idle mode...
[SATELLITE_01] ==================================================
```

---

## ✅ Verify hệ thống:

### 1. Check tất cả nodes đã idle:

```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### 2. Check logs của nhiều nodes:

```bash
docker logs satellite_01 | grep "AUTO_TRAFFIC"
docker logs uav_01 | grep "AUTO_TRAFFIC"
docker logs ground_gateway_01 | grep "AUTO_TRAFFIC"
```

Tất cả phải hiển thị: `AUTO_TRAFFIC: False`

### 3. Test gửi packet từ Web UI:

- Mở http://localhost:5173
- Chọn Source: SATELLITE_01
- Chọn Destination: UAV_01
- Gửi packet

### 4. Check Docker server nhận được:

```bash
docker logs sagsins-server -f
```

Bạn sẽ thấy:

```
📦 Received packet: SATELLITE_01 -> UAV_01: Hello
🔗 Found link: LINK_SPACE_AIR_01
✅ Saved traffic data: LINK_SPACE_AIR_01
✅ Applied shaping to satellite_01: delay=170ms, rate=12mbps
```

### 5. Check traffic CSV:

```bash
tail -f docker/data/traffic_data.csv
```

Chỉ có data khi bạn gửi từ Web UI! ✅

---

## 🔄 Nếu muốn BẬT LẠI automatic traffic:

Chỉ cần đổi trong `docker-compose.yml`:

```yaml
environment:
  - NODE_ID=SATELLITE_01
  - SERVER_IP=10.10.0.100
  - AUTO_TRAFFIC=true # ← Đổi thành true
```

Sau đó rebuild lại!

---

## 📊 Flow hiện tại:

```
User gửi packet từ Web UI (SATELLITE_01 → UAV_01)
         ↓
Backend forward to Docker Server (:8080/packet)
         ↓
Docker Server:
  1. Find topology link
  2. Generate traffic metrics (22 features)
  3. Apply TC shaping on satellite_01 container
  4. Save to /data/traffic_data.csv
         ↓
Done! ✅
```

**Không còn background traffic từ nodes nữa!**

---

## 🎯 Summary:

✅ Nodes chỉ idle, không tự gửi traffic  
✅ Traffic chỉ được tạo khi user gửi từ Web UI  
✅ Docker server vẫn apply shaping và lưu CSV  
✅ File CSV chỉ chứa traffic do user trigger

**Perfect cho testing và control chính xác! 🎉**
