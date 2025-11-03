import React from "react";

export default function PacketLog({ logs }) {
  return (
    <div>
      <h3
        style={{
          marginTop: 0,
          marginBottom: "20px",
          color: "#495057",
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
            backgroundColor: "#f8f9fa",
            borderRadius: "15px",
            border: "2px dashed #dee2e6",
            color: "#6c757d",
          }}
        >
          <p style={{ fontSize: "1.1rem", margin: 0 }}>
            📭 Chưa có packet nào
          </p>
          <p style={{ fontSize: "0.9rem", marginTop: "8px", color: "#adb5bd" }}>
            Gửi hoặc nhận packet để xem lịch sử
          </p>
        </div>
      ) : (
        <div
          style={{
            maxHeight: "400px",
            overflowY: "auto",
            backgroundColor: "#f8f9fa",
            borderRadius: "15px",
            padding: "15px",
            border: "2px solid #e9ecef",
          }}
        >
          {logs.map((log, idx) => (
            <div
              key={idx}
              style={{
                padding: "15px",
                marginBottom: "12px",
                backgroundColor: "white",
                borderRadius: "10px",
                borderLeft: `4px solid ${
                  log.type === "SENT" ? "#667eea" : "#38ef7d"
                }`,
                boxShadow: "0 2px 8px rgba(0, 0, 0, 0.05)",
                transition: "all 0.2s ease",
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.boxShadow = "0 4px 12px rgba(0, 0, 0, 0.1)";
                e.currentTarget.style.transform = "translateX(5px)";
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.boxShadow = "0 2px 8px rgba(0, 0, 0, 0.05)";
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
                        ? "rgba(102, 126, 234, 0.1)"
                        : "rgba(56, 239, 125, 0.1)",
                    color: log.type === "SENT" ? "#667eea" : "#11998e",
                  }}
                >
                  {log.type === "SENT" ? "📤 SENT" : "📥 RECEIVED"}
                </span>
                <span style={{ fontSize: "0.85rem", color: "#6c757d" }}>
                  🕒 {log.time}
                </span>
              </div>
              <div style={{ fontSize: "0.95rem", color: "#495057" }}>
                {log.type === "SENT" ? (
                  <>
                    <span style={{ color: "#6c757d" }}>Gửi đến </span>
                    <strong style={{ color: "#667eea" }}>
                      {log.data.destination}
                    </strong>
                  </>
                ) : (
                  <>
                    <span style={{ color: "#6c757d" }}>Nhận từ </span>
                    <strong style={{ color: "#11998e" }}>
                      {log.data.source}
                    </strong>
                  </>
                )}
              </div>
              <div
                style={{
                  marginTop: "10px",
                  padding: "10px",
                  backgroundColor: "#f8f9fa",
                  borderRadius: "6px",
                  fontSize: "0.9rem",
                  color: "#212529",
                  fontFamily: "monospace",
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
