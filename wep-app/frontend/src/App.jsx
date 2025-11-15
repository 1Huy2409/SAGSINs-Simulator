import React, { useState, useEffect } from "react";
import socket from "./socket";
import PacketForm from "./components/PacketForm";
import PacketLog from "./components/PacketLog";
import TopologyViewer from "./components/TopologyViewer";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:3000";

export default function App() {
  const [logs, setLogs] = useState([]);
  const [nodeId, setNodeId] = useState("");
  const [nodes, setNodes] = useState([]);
  const [loading, setLoading] = useState(true);

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

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: "#0f1419",
        backgroundImage: "linear-gradient(135deg, #0f1419 0%, #1a2332 100%)",
        padding: "40px 20px",
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
      }}
    >
      {/* Header */}
      <div style={{ padding: "10px 20px 60px 20px", paddingBottom: "20px" }}>
        <h1
          style={{
            fontSize: "2.5rem",
            fontWeight: "bold",
            color: "#ffffff",
            marginBottom: "10px",
            display: "flex",
            justifyContent: "center"
          }}
        >
          🌐 Network Packet Simulator
        </h1>
        <p style={{ color: "#a0aec0", fontSize: "1rem", display: "flex", justifyContent: "center" }}>
          Satellite & UAV Communication System
        </p>
      </div>

      {/* Main Layout - Sidebar + Content */}
      <div style={{ display: "flex", gap: "20px" }}>
        {/* Left Sidebar - Network Topology (Full Height) */}
        <div style={{ flex: "0 0 380px", height: "100vh", overflow: "hidden", borderRadius: "10px"}}>
          <TopologyViewer />
        </div>

        {/* Right Content - Node Selection + Packet Form + Log */}
        <div
          style={{
            flex: "1",
            display: "flex",
            flexDirection: "column",
            gap: "20px",
          }}
        >
          {/* Node Selection */}
          <div
            style={{
              backgroundColor: "#243447",
              padding: "25px",
              borderRadius: "15px",
              border: "1px solid #2c3e50",
            }}
          >
            <label
              style={{
                display: "block",
                marginBottom: "10px",
                fontWeight: "600",
                fontSize: "1.1rem",
                color: "#e2e8f0",
              }}
            >
              🛰️ Chọn Node ID của bạn:
            </label>
            {loading ? (
              <p style={{ color: "#a0aec0", fontStyle: "italic" }}>
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
                  border: "2px solid #2c3e50",
                  backgroundColor: "#1a2332",
                  color: "#e2e8f0",
                  cursor: "pointer",
                  transition: "all 0.3s ease",
                  outline: "none",
                  width: "100%",
                }}
                onFocus={(e) => (e.target.style.borderColor = "#00d9ff")}
                onBlur={(e) => (e.target.style.borderColor = "#2c3e50")}
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
                  backgroundColor: "rgba(0, 217, 255, 0.1)",
                  border: "1px solid #00d9ff",
                  borderRadius: "8px",
                  color: "#00d9ff",
                  fontSize: "0.9rem",
                }}
              >
                ✅ Connected as: <strong>{nodeId}</strong>
              </div>
            )}
          </div>

          {/* Packet Form & Log */}
          <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            <PacketForm nodeId={nodeId} nodes={nodes} onSend={handleSendPacket} />
            <div style={{ overflow: "auto", maxHeight: "500px" }}>
              <PacketLog logs={logs} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
