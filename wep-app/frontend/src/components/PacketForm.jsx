import React, { useState } from "react";

export default function PacketForm({ nodeId, nodes = [], onSend }) {
  const [dest, setDest] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!nodeId || !dest) {
      alert("⚠️ Vui lòng nhập Node ID và Destination!");
      return;
    }

    const packet = {
      source: nodeId,
      destination: dest,
      content: message,
    };
    onSend(packet);
    setMessage("");
  };

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        backgroundColor: "#f8f9fa",
        padding: "25px",
        borderRadius: "15px",
        border: "2px solid #e9ecef",
      }}
    >
      <h3
        style={{
          marginTop: 0,
          marginBottom: "20px",
          color: "#495057",
          fontSize: "1.3rem",
        }}
      >
        📤 Gửi Packet
      </h3>

      <div style={{ marginBottom: "20px" }}>
        <label
          style={{
            display: "block",
            marginBottom: "8px",
            fontWeight: "600",
            color: "#495057",
          }}
        >
          🎯 Destination Node:
        </label>
        <select
          value={dest}
          onChange={(e) => setDest(e.target.value)}
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
            color: "#495057",
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
            border: "2px solid #dee2e6",
            width: "100%",
            backgroundColor: "white",
            transition: "all 0.3s ease",
            outline: "none",
            boxSizing: "border-box",
          }}
          onFocus={(e) => (e.target.style.borderColor = "#667eea")}
          onBlur={(e) => (e.target.style.borderColor = "#dee2e6")}
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
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          color: "white",
          cursor: "pointer",
          width: "100%",
          boxShadow: "0 4px 15px rgba(102, 126, 234, 0.4)",
          transition: "all 0.3s ease",
          transform: "translateY(0)",
        }}
        onMouseOver={(e) => {
          e.target.style.transform = "translateY(-2px)";
          e.target.style.boxShadow = "0 6px 20px rgba(102, 126, 234, 0.6)";
        }}
        onMouseOut={(e) => {
          e.target.style.transform = "translateY(0)";
          e.target.style.boxShadow = "0 4px 15px rgba(102, 126, 234, 0.4)";
        }}
      >
        🚀 Gửi Packet
      </button>
    </form>
  );
}
