import React, { useState, useEffect } from "react";
import socket from "./socket";
import PacketForm from "./components/PacketForm";
import PacketLog from "./components/PacketLog";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:3000";

export default function App() {
  const [logs, setLogs] = useState([]);
  const [nodeId, setNodeId] = useState("");
  const [nodes, setNodes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [fetchingPackets, setFetchingPackets] = useState(false);

  // Fetch danh sách nodes từ API
  useEffect(() => {
    const fetchNodes = async () => {
      try {
        const response = await fetch(`${API_URL}/nodes`);
        const data = await response.json();
        setNodes(data);
        setLoading(false);
      } catch (error) {
        console.error("Failed to fetch nodes:", error);
        setLoading(false);
      }
    };

    fetchNodes();
  }, []);

  // Đăng ký node với backend khi user chọn node ID
  useEffect(() => {
    if (nodeId) {
      socket.emit("register", nodeId);
      console.log(`Registered as ${nodeId}`);
    }
  }, [nodeId]);

  // Lắng nghe packet đến
  useEffect(() => {
    socket.on("receive_packet", (data) => {
      console.log("Received packet:", data);
      setLogs((prev) => [
        ...prev,
        {
          type: "RECEIVED",
          data: {
            source: data.from,
            destination: nodeId,
            content: data.content,
          },
          time: new Date().toLocaleTimeString(),
        },
      ]);
    });

    return () => socket.off("receive_packet");
  }, [nodeId]);

  const handleSendPacket = (payload) => {
    socket.emit("send_packet", payload);
    setLogs((prev) => [
      ...prev,
      {
        type: "SENT",
        data: payload,
        time: new Date().toLocaleTimeString(),
      },
    ]);
  };

  const handleReceivePackets = async () => {
    if (!nodeId) {
      alert("⚠️ Vui lòng chọn Node ID trước!");
      return;
    }

    setFetchingPackets(true);
    try {
      const response = await fetch(`${API_URL}/packets/${nodeId}`);
      const packets = await response.json();

      if (packets.length === 0) {
        alert("📭 Không có packet nào đang chờ!");
      } else {
        // Thêm các packet vào logs
        packets.forEach((packet) => {
          setLogs((prev) => [
            ...prev,
            {
              type: "RECEIVED",
              data: {
                source: packet.from,
                destination: nodeId,
                content: packet.content,
              },
              time: new Date(packet.timestamp).toLocaleTimeString(),
            },
          ]);
        });

        // Xóa packet queue sau khi đã nhận
        await fetch(`${API_URL}/packets/${nodeId}`, {
          method: "DELETE",
        });

        alert(`📬 Đã nhận ${packets.length} packet(s)!`);
      }
    } catch (error) {
      console.error("Failed to fetch packets:", error);
      alert("❌ Lỗi khi nhận packets!");
    } finally {
      setFetchingPackets(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        padding: "40px 20px",
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
      }}
    >
      <div
        style={{
          maxWidth: "900px",
          margin: "0 auto",
          backgroundColor: "rgba(255, 255, 255, 0.95)",
          borderRadius: "20px",
          padding: "40px",
          boxShadow: "0 20px 60px rgba(0, 0, 0, 0.3)",
        }}
      >
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: "40px" }}>
          <h1
            style={{
              fontSize: "2.5rem",
              fontWeight: "bold",
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              marginBottom: "10px",
            }}
          >
            🌐 Network Packet Simulator
          </h1>
          <p style={{ color: "#666", fontSize: "1rem" }}>
            Satellite & UAV Communication System
          </p>
        </div>

        {/* Node Selection Card */}
        <div
          style={{
            backgroundColor: "#f8f9fa",
            padding: "25px",
            borderRadius: "15px",
            marginBottom: "25px",
            border: "2px solid #e9ecef",
          }}
        >
          <label
            style={{
              display: "block",
              marginBottom: "10px",
              fontWeight: "600",
              fontSize: "1.1rem",
              color: "#495057",
            }}
          >
            🛰️ Chọn Node ID của bạn:
          </label>
          {loading ? (
            <p style={{ color: "#6c757d", fontStyle: "italic" }}>
              ⏳ Đang tải danh sách nodes...
            </p>
          ) : (
            <select
              value={nodeId}
              onChange={(e) => setNodeId(e.target.value)}
              style={{
                padding: "12px 16px",
                fontSize: "1rem",
                borderRadius: "10px",
                border: "2px solid #dee2e6",
                width: "100%",
                backgroundColor: "white",
                cursor: "pointer",
                transition: "all 0.3s ease",
                outline: "none",
              }}
              onFocus={(e) => (e.target.style.borderColor = "#667eea")}
              onBlur={(e) => (e.target.style.borderColor = "#dee2e6")}
            >
              <option value="">-- Chọn một node --</option>
              {nodes.map((node) => (
                <option key={node} value={node}>
                  {node}
                </option>
              ))}
            </select>
          )}
          {nodeId && (
            <div
              style={{
                marginTop: "15px",
                padding: "12px",
                backgroundColor: "#d4edda",
                border: "1px solid #c3e6cb",
                borderRadius: "8px",
                color: "#155724",
                fontSize: "0.9rem",
              }}
            >
              ✅ Connected as: <strong>{nodeId}</strong>
            </div>
          )}
        </div>

        {/* Receive Packets Button */}
        <div style={{ marginBottom: "30px", textAlign: "center" }}>
          <button
            onClick={handleReceivePackets}
            disabled={!nodeId || fetchingPackets}
            style={{
              padding: "15px 40px",
              fontSize: "1.1rem",
              fontWeight: "bold",
              borderRadius: "12px",
              border: "none",
              background: nodeId && !fetchingPackets
                ? "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)"
                : "#e9ecef",
              color: nodeId && !fetchingPackets ? "white" : "#adb5bd",
              cursor: nodeId && !fetchingPackets ? "pointer" : "not-allowed",
              boxShadow: nodeId && !fetchingPackets
                ? "0 4px 15px rgba(17, 153, 142, 0.4)"
                : "none",
              transition: "all 0.3s ease",
              transform: "translateY(0)",
            }}
            onMouseOver={(e) => {
              if (nodeId && !fetchingPackets) {
                e.target.style.transform = "translateY(-2px)";
                e.target.style.boxShadow = "0 6px 20px rgba(17, 153, 142, 0.6)";
              }
            }}
            onMouseOut={(e) => {
              e.target.style.transform = "translateY(0)";
              e.target.style.boxShadow = nodeId && !fetchingPackets
                ? "0 4px 15px rgba(17, 153, 142, 0.4)"
                : "none";
            }}
          >
            {fetchingPackets ? "⏳ Đang nhận..." : "📬 Receive Packets"}
          </button>
          {!nodeId && (
            <p style={{ fontSize: "0.9rem", color: "#6c757d", marginTop: "10px" }}>
              💡 Vui lòng chọn Node ID để nhận packets
            </p>
          )}
        </div>

        {/* Packet Form */}
        <PacketForm nodeId={nodeId} nodes={nodes} onSend={handleSendPacket} />

        {/* Divider */}
        <div
          style={{
            height: "2px",
            background: "linear-gradient(90deg, transparent, #dee2e6, transparent)",
            margin: "40px 0",
          }}
        />

        {/* Packet Log */}
        <PacketLog logs={logs} />
      </div>
    </div>
  );
}
