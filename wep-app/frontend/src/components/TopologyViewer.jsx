import React, { useState } from "react";
import { TOPOLOGY_DATA } from "../data/topology_data";
import { NODE_DATA } from "../data/nodes_data";

const Dialog = ({ isOpen, title, data, type, onClose }) => {
  if (!isOpen) return null;

  const getGradient = () => {
    return type === "link" ? "#0066ff" : "#00d9ff";
  };

  return (
    <>
      <div
        onClick={onClose}
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: "rgba(0, 0, 0, 0.8)",
          zIndex: 999,
          animation: "fadeIn 0.3s ease",
        }}
      />
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          position: "fixed",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          backgroundColor: "#1a2332",
          borderRadius: "15px",
          padding: "25px",
          maxWidth: "600px",
          maxHeight: "75vh",
          overflowY: "auto",
          zIndex: 1000,
          boxShadow: `0 20px 60px rgba(0, 217, 255, 0.3), 0 0 30px rgba(0, 217, 255, 0.1)`,
          border: `2px solid ${getGradient()}`,
          animation: "slideUp 0.3s ease",
        }}
      >
        {/* Header */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "20px",
            paddingBottom: "12px",
            borderBottom: `2px solid ${getGradient()}`,
          }}
        >
          <h2
            style={{
              fontSize: "1.3rem",
              fontWeight: "bold",
              color: getGradient(),
              margin: 0,
            }}
          >
            {type === "link" ? "🔗 Link Details" : "🖥️ Node Details"}
          </h2>
          <button
            onClick={onClose}
            style={{
              background: "none",
              border: "none",
              fontSize: "1.8rem",
              color: "#a0aec0",
              cursor: "pointer",
              transition: "color 0.2s",
              padding: "0",
              lineHeight: "1",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
            onMouseEnter={(e) => (e.target.style.color = "#ff3b30")}
            onMouseLeave={(e) => (e.target.style.color = "#a0aec0")}
          >
            ✕
          </button>
        </div>

        {/* Title */}
        <div
          style={{
            fontSize: "1rem",
            fontWeight: "bold",
            color: "#e2e8f0",
            marginBottom: "15px",
            padding: "8px 10px",
            backgroundColor: `rgba(0, ${type === "link" ? "102" : "217"}, 255, 0.15)`,
            borderRadius: "8px",
            borderLeft: `4px solid ${getGradient()}`,
          }}
        >
          {title}
        </div>

        {/* Content Grid */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "10px",
          }}
        >
          {Object.entries(data).map(([key, value]) => (
            <div
              key={key}
              style={{
                padding: "10px 12px",
                backgroundColor: "#243447",
                borderRadius: "8px",
                border: "1px solid #2c3e50",
                transition: "all 0.2s ease",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = "rgba(0, 217, 255, 0.1)";
                e.currentTarget.style.borderColor = getGradient();
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = "#243447";
                e.currentTarget.style.borderColor = "#2c3e50";
              }}
            >
              <div
                style={{
                  fontSize: "0.65rem",
                  color: "#a0aec0",
                  marginBottom: "4px",
                  textTransform: "uppercase",
                  fontWeight: "700",
                  letterSpacing: "0.5px",
                }}
              >
                {key.replace(/_/g, " ")}
              </div>
              <div
                style={{
                  fontSize: "0.85rem",
                  fontWeight: "600",
                  color: "#e2e8f0",
                  wordBreak: "break-word",
                }}
              >
                {value}
              </div>
            </div>
          ))}
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slideUp {
          from { transform: translate(-50%, -40%); opacity: 0; }
          to { transform: translate(-50%, -50%); opacity: 1; }
        }
      `}</style>
    </>
  );
};

export default function TopologyViewer() {
  const [selectedLink, setSelectedLink] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [error, setError] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogType, setDialogType] = useState(null);

  // Parse CSV data
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

  const parseNodeData = () => {
    const lines = NODE_DATA.trim().split("\n");
    const headers = lines[0].split(",");
    const nodes = [];

    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(",");
      const node = {};
      headers.forEach((header, index) => {
        node[header] = values[index];
      });
      nodes.push(node);
    }

    return nodes;
  };

  const links = parseTopologyData();
  const nodes = parseNodeData();

  // Extract unique node IDs
  const nodeIds = Array.from(
    new Set([
      ...links.map((l) => l.source_node),
      ...links.map((l) => l.destination_node),
    ])
  ).sort();

  // Handle link selection with error handling
  const handleLinkSelect = (link) => {
    try {
      if (!link.link_id || !link.source_node || !link.destination_node) {
        throw new Error("Invalid link data: Missing required fields");
      }
      setSelectedLink(link);
      setError(null);
      setDialogType("link");
      setDialogOpen(true);
    } catch (err) {
      setError(err.message);
      setSelectedLink(null);
    }
  };

  const handleNodeSelect = (nodeId) => {
    try {
      const node = nodes.find((n) => n.node_id === nodeId);
      if (!node) {
        throw new Error(`Node ${nodeId} not found in data`);
      }
      setSelectedNode(node);
      setError(null);
      setDialogType("node");
      setDialogOpen(true);
    } catch (err) {
      setError(err.message);
      setSelectedNode(null);
    }
  };

  const closeDialog = () => {
    setDialogOpen(false);
    setSelectedLink(null);
    setSelectedNode(null);
    setDialogType(null);
  };

  const formatNodeData = (node) => ({
    "Node ID": node.node_id,
    Layer: node.layer,
    "Node Type": node.node_type,
    "Movement Pattern": node.movement_pattern,
    Capacity: node.capacity,
    Latitude: node.latitude,
    Longitude: node.longitude,
    "Altitude (km)": node.altitude_km,
    "Max Throughput": node.max_throughput_gbps + " Gbps",
    "Power (W)": node.power_consumption_watts,
    "Speed (km/h)": node.mobility_speed_kmh,
    "Weather Sens.": node.weather_sensitivity,
  });

  return (
    <div
      style={{
        backgroundColor: "#243447",
        padding: "20px",
        borderRadius: "15px",
        border: "1px solid #2c3e50",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
      }}
    >
      <h2
        style={{
          fontSize: "1.3rem",
          fontWeight: "bold",
          color: "#00d9ff",
          marginBottom: "15px",
          margin: "0 0 15px 0",
        }}
      >
        Network Topology
      </h2>

      {error && (
        <div
          style={{
            padding: "10px",
            backgroundColor: "rgba(255, 59, 48, 0.15)",
            border: "1px solid #ff3b30",
            borderRadius: "6px",
            color: "#ff3b30",
            marginBottom: "12px",
            fontSize: "0.8rem",
            fontWeight: "500",
          }}
        >
          ❌ {error}
        </div>
      )}

      <div style={{ flex: "1", overflowY: "auto", paddingRight: "8px" }} className="custom-scrollbar">
        {/* Nodes Section */}
        <div style={{ marginBottom: "15px" }}>
          <h3
            style={{
              fontSize: "0.9rem",
              fontWeight: "600",
              color: "#e2e8f0",
              marginBottom: "8px",
              display: "flex",
              alignItems: "center",
              gap: "6px",
              margin: "0 0 8px 0",
            }}
          >
            <span style={{ color: "#00d9ff" }}>●</span> Nodes ({nodeIds.length})
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "5px" }}>
            {nodeIds.map((nodeId) => (
              <button
                key={nodeId}
                onClick={() => handleNodeSelect(nodeId)}
                style={{
                  padding: "8px 10px",
                  backgroundColor: "#1a2332",
                  border: "1px solid #2c3e50",
                  borderRadius: "6px",
                  color: "#e2e8f0",
                  cursor: "pointer",
                  fontSize: "0.8rem",
                  textAlign: "left",
                  transition: "all 0.2s ease",
                }}
                onMouseEnter={(e) => {
                  e.target.style.borderColor = "#00d9ff";
                  e.target.style.backgroundColor = "rgba(0, 217, 255, 0.1)";
                }}
                onMouseLeave={(e) => {
                  e.target.style.borderColor = "#2c3e50";
                  e.target.style.backgroundColor = "#1a2332";
                }}
              >
                {nodeId}
              </button>
            ))}
          </div>
        </div>

        {/* Links Section */}
        <div>
          <h3
            style={{
              fontSize: "0.9rem",
              fontWeight: "600",
              color: "#e2e8f0",
              marginBottom: "8px",
              display: "flex",
              alignItems: "center",
              gap: "6px",
              margin: "0 0 8px 0",
            }}
          >
            <span style={{ color: "#0066ff" }}>→</span> Links ({links.length})
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "5px" }}>
            {links.map((link) => (
              <button
                key={link.link_id}
                onClick={() => handleLinkSelect(link)}
                style={{
                  padding: "8px 10px",
                  backgroundColor: "#1a2332",
                  border: "1px solid #2c3e50",
                  borderRadius: "6px",
                  color: "#a0aec0",
                  cursor: "pointer",
                  fontSize: "0.7rem",
                  textAlign: "left",
                  transition: "all 0.2s ease",
                }}
                onMouseEnter={(e) => {
                  e.target.style.borderColor = "#00d9ff";
                  e.target.style.backgroundColor = "rgba(0, 217, 255, 0.1)";
                  e.target.style.color = "#00d9ff";
                  e.target.style.boxShadow = "0 0 12px rgba(0, 217, 255, 0.3)";
                }}
                onMouseLeave={(e) => {
                  e.target.style.borderColor = "#2c3e50";
                  e.target.style.backgroundColor = "#1a2332";
                  e.target.style.color = "#a0aec0";
                  e.target.style.boxShadow = "none";
                }}
              >
                <div style={{ fontWeight: "600", color: "#e2e8f0" }}>
                  {link.link_id}
                </div>
                <div style={{ fontSize: "0.65rem", color: "#8892a8" }}>
                  {link.source_node} → {link.destination_node}
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Dialogs */}
      {dialogType === "link" && (
        <Dialog
          isOpen={dialogOpen}
          title={`Link: ${selectedLink?.link_id}`}
          type="link"
          data={{
            "Link ID": selectedLink?.link_id,
            Source: selectedLink?.source_node,
            Destination: selectedLink?.destination_node,
            "Source Layer": selectedLink?.source_layer,
            "Dest Layer": selectedLink?.destination_layer,
            "Capacity": (selectedLink?.capacity_bps / 1000000).toFixed(2) + " Mbps",
            "Latency": selectedLink?.base_latency_milliseconds + " ms",
            "Reliability": (selectedLink?.reliability_score * 100).toFixed(1) + "%",
            "Distance": selectedLink?.distance_km + " km",
            Priority: selectedLink?.priority_level,
          }}
          onClose={closeDialog}
        />
      )}

      {dialogType === "node" && (
        <Dialog
          isOpen={dialogOpen}
          title={`Node: ${selectedNode?.node_id}`}
          type="node"
          data={formatNodeData(selectedNode)}
          onClose={closeDialog}
        />
      )}

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: linear-gradient(180deg, rgba(0, 102, 255, 0.1) 0%, rgba(0, 217, 255, 0.1) 100%);
          borderRadius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: linear-gradient(180deg, #0066ff 0%, #00d9ff 100%);
          borderRadius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: linear-gradient(180deg, #0052cc 0%, #00b8d4 100%);
        }
      `}</style>
    </div>
  );
}
