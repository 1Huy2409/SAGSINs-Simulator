import React from "react";

export default function PacketLog({ logs = [] }) {
  return (
    <div>
      <h3
        style={{
          marginTop: 0,
          marginBottom: "20px",
          color: "#e2e8f0",
          fontSize: "1.3rem",
        }}
      >
        📊 Lịch sử Packet
      </h3>
      {logs.length === 0 ? (
        <div
          style={{
            padding: "40px",
            textAlign: "center",
            backgroundColor: "#243447",
            borderRadius: "15px",
            border: "2px dashed #2c3e50",
            color: "#a0aec0",
          }}
        >
          <p style={{ fontSize: "1.1rem", margin: 0 }}>
            📭 Chưa có packet nào
          </p>
          <p style={{ fontSize: "0.9rem", marginTop: "8px", color: "#64748b" }}>
            Gửi hoặc nhận packet để xem lịch sử
          </p>
        </div>
      ) : (
        <div
          style={{
            maxHeight: "400px",
            overflowY: "auto",
            backgroundColor: "#243447",
            borderRadius: "15px",
            padding: "15px",
            border: "1px solid #2c3e50",
          }}
        >
          {logs.map((log, idx) => (
            <div
              key={idx}
              style={{
                padding: "15px",
                marginBottom: "12px",
                backgroundColor: "#1a2332",
                borderRadius: "10px",
                borderLeft: `4px solid ${
                  log.type === "SENT" ? "#0066ff" : "#00d9ff"
                }`,
                boxShadow: "0 2px 8px rgba(0, 0, 0, 0.3)",
                transition: "all 0.2s ease",
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.boxShadow = "0 4px 12px rgba(0, 102, 255, 0.2)";
                e.currentTarget.style.transform = "translateX(5px)";
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.boxShadow = "0 2px 8px rgba(0, 0, 0, 0.3)";
                e.currentTarget.style.transform = "translateX(0)";
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "8px",
                }}
              >
                <span
                  style={{
                    fontSize: "0.85rem",
                    fontWeight: "600",
                    padding: "4px 10px",
                    borderRadius: "5px",
                    backgroundColor:
                      log.type === "SENT"
                        ? "rgba(0, 102, 255, 0.2)"
                        : "rgba(0, 217, 255, 0.2)",
                    color: log.type === "SENT" ? "#0066ff" : "#00d9ff",
                  }}
                >
                  {log.type === "SENT" ? "📤 SENT" : "📥 RECEIVED"}
                </span>
                <span style={{ fontSize: "0.85rem", color: "#a0aec0" }}>
                  🕒 {log.time}
                </span>
              </div>
              <div style={{ fontSize: "0.95rem", color: "#cbd5e1" }}>
                {log.type === "SENT" ? (
                  <>
                    <span style={{ color: "#a0aec0" }}>Gửi đến </span>
                    <strong style={{ color: "#0066ff" }}>
                      {log.data.destination}
                    </strong>
                  </>
                ) : (
                  <>
                    <span style={{ color: "#a0aec0" }}>Nhận từ </span>
                    <strong style={{ color: "#00d9ff" }}>
                      {log.data.source}
                    </strong>
                  </>
                )}
              </div>
              <div
                style={{
                  marginTop: "10px",
                  padding: "10px",
                  backgroundColor: "#0f1419",
                  borderRadius: "6px",
                  fontSize: "0.9rem",
                  color: "#cbd5e1",
                  fontFamily: "monospace",
                  borderLeft: "2px solid #00d9ff",
                }}
              >
                💬 "{log.data.content}"
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
