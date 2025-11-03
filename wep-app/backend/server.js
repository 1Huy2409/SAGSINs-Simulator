import express from "express";
import dotenv from "dotenv";
import { createServer } from "http";
import { Server } from "socket.io";
import axios from "axios";
import cors from "cors";

dotenv.config();
const app = express();
app.use(cors());
app.use(express.json());

const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: "*",
  },
});
const port = process.env.PORT || 3000;

const nodes = [
  "SATELLITE_01",
  "SATELLITE_02",
  "SATELLITE_03",
  "UAV_01",
  "UAV_02",
  "GROUND_GATEWAY_01",
  "GROUND_GATEWAY_02",
  "GROUND_GATEWAY_03",
  "SHIP_01",
  "SHIP_02",
];

app.get("/nodes", (req, res) => res.json(nodes));

// Lưu trữ packet queue cho mỗi node
const packetQueues = new Map();

// API để lấy danh sách packet của một node
app.get("/packets/:nodeId", (req, res) => {
  const { nodeId } = req.params;
  const packets = packetQueues.get(nodeId) || [];
  res.json(packets);
});

// API để xóa packet queue sau khi đã nhận
app.delete("/packets/:nodeId", (req, res) => {
  const { nodeId } = req.params;
  packetQueues.delete(nodeId);
  res.json({ message: "Packets cleared" });
});

const clients = new Map();

io.on("connection", (socket) => {
  console.log("Client connected:", socket.id);

  socket.on("register", (node_id) => {
    clients.set(node_id, socket);
    console.log(`Registered node: ${node_id}`);
  });

  socket.on("send_packet", async ({ source, destination, content }) => {
    console.log(`📦 ${source} -> ${destination}: ${content}`);

    // Lưu packet vào queue của node đích
    if (!packetQueues.has(destination)) {
      packetQueues.set(destination, []);
    }
    packetQueues.get(destination).push({
      from: source,
      content,
      timestamp: new Date().toISOString(),
    });

    // Forward tới Docker Server để tạo traffic data
    const dockerServerUrl =
      process.env.DOCKER_SERVER_URL || "http://localhost:8080/packet";

    try {
      console.log(`🚀 Forwarding to Docker server...`);

      const response = await axios.post(
        dockerServerUrl,
        {
          source,
          destination,
          content,
        },
        {
          timeout: 15000, // Tăng timeout lên 15s
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      console.log(`✅ Traffic data saved: ${response.data.link || "unknown"}`);

      if (response.data.metrics) {
        console.log(
          `   📊 Bitrate: ${(response.data.metrics.bitrate_bps / 1e6).toFixed(
            2
          )} Mbps, Quality: ${(
            response.data.metrics.quality_score * 100
          ).toFixed(1)}%`
        );
      }
    } catch (error) {
      if (error.code === "ECONNREFUSED") {
        console.log("❌ Docker server not reachable (connection refused)");
        console.log("   Make sure Docker containers are running:");
        console.log("   cd docker && docker-compose up -d");
      } else if (
        error.code === "ETIMEDOUT" ||
        error.message.includes("timeout")
      ) {
        console.log("❌ Docker server timeout - server may be overloaded");
        console.log("   Check server logs: docker logs sagsins-server");
      } else if (error.response) {
        console.log(
          `❌ Docker server error: ${error.response.status} - ${
            error.response.data?.message || "Unknown"
          }`
        );
      } else {
        console.log(`❌ Failed to forward to Docker: ${error.message}`);
      }
    }

    // Gửi tới node đích nếu đang online
    const destSocket = clients.get(destination);
    if (destSocket) {
      destSocket.emit("receive_packet", { from: source, content });
      console.log(`✅ Delivered to ${destination}`);
    } else {
      console.log(`⚠️  ${destination} is offline, packet queued`);
    }
  });

  socket.on("disconnect", () => {
    for (let [node, sock] of clients.entries()) {
      if (sock.id === socket.id) clients.delete(node);
    }
    console.log(`Client disconnected: ${socket.id}`);
  });
});

httpServer.listen(port, "0.0.0.0", () => {
  console.log(`Socket.IO backend running on:`);
  console.log(`  - Local:   http://localhost:${port}`);
  console.log(`  - Network: http://0.0.0.0:${port}`);
  console.log(`Allow connections from any network interface`);
});
