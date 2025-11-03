#!/usr/bin/env node

/**
 * Test script để verify SAGSINs System
 */

import axios from "axios";

const BACKEND_URL = "http://localhost:3000";
const DOCKER_URL = "http://localhost:8080";

const colors = {
  reset: "\x1b[0m",
  green: "\x1b[32m",
  red: "\x1b[31m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
};

function log(message, color = "reset") {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

async function testBackend() {
  log("\n📡 Testing Backend...", "blue");

  try {
    const response = await axios.get(`${BACKEND_URL}/nodes`);
    log(`✅ Backend is running`, "green");
    log(`   Found ${response.data.length} nodes`, "green");
    return true;
  } catch (error) {
    log(`❌ Backend is not reachable: ${error.message}`, "red");
    return false;
  }
}

async function testDockerServer() {
  log("\n🐳 Testing Docker Server...", "blue");

  try {
    const response = await axios.get(DOCKER_URL);
    log(`✅ Docker Server is running`, "green");
    log(`   Service: ${response.data.service}`, "green");
    log(`   Topology links: ${response.data.topology_links}`, "green");
    return true;
  } catch (error) {
    log(`❌ Docker Server is not reachable: ${error.message}`, "red");
    return false;
  }
}

async function testTopology() {
  log("\n🔗 Testing Topology...", "blue");

  try {
    const response = await axios.get(`${DOCKER_URL}/topology`, {
      params: {
        source: "SATELLITE_01",
        destination: "UAV_01",
      },
    });

    if (response.data.status === "success" && response.data.link) {
      log(`✅ Topology lookup successful`, "green");
      log(`   Link ID: ${response.data.link.link_id}`, "green");
      log(
        `   Capacity: ${response.data.link.capacity_bps / 1e6} Mbps`,
        "green"
      );
      log(
        `   Latency: ${response.data.link.base_latency_milliseconds} ms`,
        "green"
      );
      return true;
    } else {
      log(`⚠️  Topology link not found`, "yellow");
      return false;
    }
  } catch (error) {
    log(`❌ Topology test failed: ${error.message}`, "red");
    return false;
  }
}

async function testPacketForwarding() {
  log("\n📦 Testing Packet Forwarding...", "blue");

  try {
    const testPacket = {
      source: "SATELLITE_01",
      destination: "UAV_01",
      content: "Test packet from verification script",
    };

    const response = await axios.post(`${DOCKER_URL}/packet`, testPacket);

    if (response.data.status === "success") {
      log(`✅ Packet forwarding successful`, "green");
      log(`   Link: ${response.data.link}`, "green");
      log(
        `   Bitrate: ${(response.data.metrics.bitrate_bps / 1e6).toFixed(
          2
        )} Mbps`,
        "green"
      );
      log(
        `   RTT: ${response.data.metrics.rtt_milliseconds.toFixed(2)} ms`,
        "green"
      );
      log(
        `   Utilization: ${(response.data.metrics.utilization * 100).toFixed(
          1
        )}%`,
        "green"
      );
      return true;
    } else {
      log(`⚠️  Packet forwarding failed`, "yellow");
      return false;
    }
  } catch (error) {
    log(`❌ Packet forwarding test failed: ${error.message}`, "red");
    if (error.response) {
      log(`   Server response: ${JSON.stringify(error.response.data)}`, "red");
    }
    return false;
  }
}

async function main() {
  log("========================================", "blue");
  log("🧪 SAGSINs System Verification", "blue");
  log("========================================", "blue");

  const results = {
    backend: await testBackend(),
    dockerServer: await testDockerServer(),
    topology: await testTopology(),
    packetForwarding: await testPacketForwarding(),
  };

  log("\n========================================", "blue");
  log("📊 Test Results:", "blue");
  log("========================================", "blue");

  const total = Object.keys(results).length;
  const passed = Object.values(results).filter((r) => r).length;

  for (const [test, result] of Object.entries(results)) {
    const status = result ? "✅ PASS" : "❌ FAIL";
    const color = result ? "green" : "red";
    log(`${status} - ${test}`, color);
  }

  log("\n========================================", "blue");
  log(
    `Final Score: ${passed}/${total} tests passed`,
    passed === total ? "green" : "yellow"
  );
  log("========================================", "blue");

  if (passed === total) {
    log("\n🎉 All systems operational!", "green");
    log("\nYou can now:", "blue");
    log("1. Open Web App at http://localhost:5173", "blue");
    log("2. Select source and destination nodes", "blue");
    log("3. Send packets and watch traffic data being generated", "blue");
    log("4. Check traffic_data.csv in docker/data/ directory", "blue");
  } else {
    log("\n⚠️  Some tests failed. Please check the logs above.", "yellow");
    log("\nTroubleshooting:", "yellow");
    log("- Make sure Docker containers are running: docker ps", "yellow");
    log("- Check Docker logs: docker logs sagsins-server", "yellow");
    log(
      "- Verify backend is running: cd wep-app/backend && npm start",
      "yellow"
    );
  }

  process.exit(passed === total ? 0 : 1);
}

main().catch((error) => {
  log(`\n❌ Fatal error: ${error.message}`, "red");
  process.exit(1);
});
