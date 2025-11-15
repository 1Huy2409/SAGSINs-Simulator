import React, { useState } from "react";
import { TOPOLOGY_DATA } from "../data/topology_data";

export default function PacketForm({ nodeId, nodes = [], onSend }) {
  const [dest, setDest] = useState("");
  const [message, setMessage] = useState("");
  const [validationError, setValidationError] = useState("");

  const parseTopologyData = () => {
    const lines = TOPOLOGY_DATA.trim().split("\n");
    const headers = lines[0].split(",");
    const links = [];
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(",");
      const link = {};
      headers.forEach((header, index) => {
        link[header] = values[index];
      });
      links.push(link);
    }
    return links;
  };

  const links = parseTopologyData();

  const isValidRoute = (source, destination) => {
    const validLink = links.find(
      (link) => link.source_node === source && link.destination_node === destination
    );
    return !!validLink;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setValidationError("");

    if (!nodeId) {
      setValidationError("⚠️ Vui lòng chọn Node ID của bạn trước!");
      return;
    }

    if (!dest) {
      setValidationError("⚠️ Vui lòng chọn Destination Node!");
      return;
    }

    if (nodeId === dest) {
      setValidationError("❌ Bạn không thể gửi packet cho chính mình!");
      return;
    }

    if (!isValidRoute(nodeId, dest)) {
      setValidationError(
        `❌ Không có đường liên kết trực tiếp từ ${nodeId} đến ${dest}. Vui lòng chọn một destination hợp lệ!`
      );
      return;
    }

    const packet = {
      source: nodeId,
      destination: dest,
      content: message,
    };
    onSend(packet);
    setMessage("");
    setDest("");
  };

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        backgroundColor: "#243447",
        padding: "25px",
        borderRadius: "15px",
        border: "1px solid #2c3e50",
      }}
    >
      <h3
        style={{
          marginTop: 0,
          marginBottom: "20px",
          color: "#e2e8f0",
          fontSize: "1.3rem",
        }}
      >
        📤 Gửi Packet
      </h3>

      {validationError && (
        <div
          style={{
            padding: "12px 14px",
            backgroundColor: "rgba(255, 59, 48, 0.15)",
            border: "1px solid #ff3b30",
            borderRadius: "8px",
            color: "#ff6b63",
            marginBottom: "15px",
            fontSize: "0.85rem",
            fontWeight: "500",
            borderLeft: "4px solid #ff3b30",
          }}
        >
          {validationError}
        </div>
      )}

      <div style={{ marginBottom: "20px" }}>
        <label
          style={{
            display: "block",
            marginBottom: "8px",
            fontWeight: "600",
            color: "#a0aec0",
          }}
        >
          🎯 Destination Node:
        </label>
        <select
          value={dest}
          onChange={(e) => {
            setDest(e.target.value);
            setValidationError("");
          }}
          style={{
            padding: "12px 16px",
            fontSize: "1rem",
            borderRadius: "10px",
            border: "2px solid #2c3e50",
            width: "100%",
            backgroundColor: "#1a2332",
            color: "#e2e8f0",
            cursor: "pointer",
            transition: "all 0.3s ease",
            outline: "none",
          }}
          onFocus={(e) => (e.target.style.borderColor = "#0066ff")}
          onBlur={(e) => (e.target.style.borderColor = "#2c3e50")}
        >
          <option value="">-- Chọn destination node --</option>
          {nodes
            .filter((node) => node !== nodeId)
            .map((node) => (
              <option key={node} value={node}>
                {node}
              </option>
            ))}
        </select>
      </div>

      <div style={{ marginBottom: "25px" }}>
        <label
          style={{
            display: "block",
            marginBottom: "8px",
            fontWeight: "600",
            color: "#a0aec0",
          }}
        >
          💬 Nội dung packet:
        </label>
        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="VD: Hello from satellite!"
          style={{
            padding: "12px 16px",
            fontSize: "1rem",
            borderRadius: "10px",
            border: "2px solid #2c3e50",
            width: "100%",
            backgroundColor: "#1a2332",
            color: "#e2e8f0",
            transition: "all 0.3s ease",
            outline: "none",
            boxSizing: "border-box",
          }}
          onFocus={(e) => (e.target.style.borderColor = "#0066ff")}
          onBlur={(e) => (e.target.style.borderColor = "#2c3e50")}
        />
      </div>

      <button
        type="submit"
        style={{
          padding: "12px 30px",
          fontSize: "1.1rem",
          fontWeight: "bold",
          borderRadius: "10px",
          border: "none",
          background: "linear-gradient(135deg, #0066ff 0%, #00d9ff 100%)",
          color: "white",
          cursor: "pointer",
          width: "100%",
          boxShadow: "0 4px 15px rgba(0, 102, 255, 0.4)",
          transition: "all 0.3s ease",
          transform: "translateY(0)",
        }}
        onMouseOver={(e) => {
          e.target.style.transform = "translateY(-2px)";
          e.target.style.boxShadow = "0 6px 20px rgba(0, 102, 255, 0.6)";
        }}
        onMouseOut={(e) => {
          e.target.style.transform = "translateY(0)";
          e.target.style.boxShadow = "0 4px 15px rgba(0, 102, 255, 0.4)";
        }}
      >
        🚀 Gửi Packet
      </button>
    </form>
  );
}
