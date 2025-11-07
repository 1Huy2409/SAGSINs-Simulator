# 🔮 Auto Prediction System

## Quick Start

### 1️⃣ Start Prediction Service (Local)

```bash
cd D:\HuyCoding\PBL4\PBL4-Network-Traffic-Prediction
start-prediction-service.bat
```

**Keep this running!** ✅

### 2️⃣ Start Docker Containers

```bash
cd D:\HuyCoding\PBL4\SAGSINs-System\docker
docker-compose up -d
```

### 3️⃣ Send Packet & Watch

- Open Web App: http://localhost:5173
- Send packet from UI
- **Prediction runs automatically!** 🎯

---

## Architecture

```
Web App → Docker Server → HTTP → Prediction Service (Local)
                    ↓              ↓
               Save CSV      Run VAE + LSTM
                                   ↓
                              Return predictions
```

**Benefits:**

- ⚡ Fast (no Docker overhead)
- 🔧 Easy debug (Python script)
- 📦 Light Docker (no PyTorch)
- 🚀 Quick rebuild (1 min vs 10 min)

---

## Documentation

📖 **[PREDICTION_COMPLETE.md](./PREDICTION_COMPLETE.md)** - Complete guide

---

## Files

### Current Solution (v2.0):

- ✅ `PREDICTION_COMPLETE.md` - Main documentation
- ✅ `../PBL4-Network-Traffic-Prediction/prediction_service.py` - FastAPI service
- ✅ `../PBL4-Network-Traffic-Prediction/start-prediction-service.bat` - Start script

### Configuration:

- `docker/docker-compose.yml` - Docker config with prediction service URL
- `docker/server/app.py` - Calls prediction service via HTTP

---

**Version**: 2.0 (Separate Prediction Service)  
**Last Updated**: 2025-11-07
