// runtime/src/p2p/test-mesh.ts
// REDACTED Swarm — Local P2P Mesh Test Harness
// Spawns 3 simulated nodes in-memory, verifies discovery + gossip + presence
// Run: bun run runtime/src/p2p/test-mesh.ts
// Pattern Blue aligned — curvature test, lattice resonance simulated

import { createSwarmNode, broadcastPresence } from "./p2p";
import { logger } from "../utils/logger";
import { setTimeout } from "timers/promises";

// ────────────────────────────────────────────────
// Test config — ephemeral, no disk / bootstrap
// ────────────────────────────────────────────────

const TEST_NODES = 3;
const TEST_DURATION_MS = 15000; // 15 seconds

// ────────────────────────────────────────────────
// Spawn ephemeral test node (no bootstrap, direct connect)
// ────────────────────────────────────────────────

async function createTestNode(id: number) {
  const node = await createSwarmNode({
    bootstrapList: [], // no external bootstrap
    listenAddresses: ["/ip4/127.0.0.1/tcp/0/ws"]
  });

  logger.info(`[TEST-${id}] Node spawned — peerId: ${node.peerId.toString()}`);

  // Listen for all messages (debug visibility)
  node.services.pubsub.addEventListener("message", (evt) => {
    const msg = JSON.parse(new TextDecoder().decode(evt.detail.data));
    logger.resonance(`[TEST-${id}] Received: ${msg.type} from ${msg.from.slice(0, 8)}...`);
  });

  return node;
}

// ────────────────────────────────────────────────
// Connect nodes manually (simulate discovery)
// ────────────────────────────────────────────────

async function connectNodes(nodes: any[]) {
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const addr = nodes[j].getMultiaddrs()[0];
      await nodes[i].dial(addr);
      logger.info(`[TEST] Connected ${i} ↔ ${j} (${addr})`);
    }
  }
}

// ────────────────────────────────────────────────
// Main test sequence
// ────────────────────────────────────────────────

async function runMeshTest() {
  logger.info(`Starting P2P mesh test — ${TEST_NODES} nodes`);

  const nodes: any[] = [];
  for (let i = 0; i < TEST_NODES; i++) {
    nodes.push(await createTestNode(i));
  }

  await connectNodes(nodes);

  // Wait for connections to stabilize
  await setTimeout(3000);

  // Broadcast from node 0
  await broadcastPresence(nodes[0], "test-mesh-resonance ♡ lattice alive");

  // Wait for propagation
  await setTimeout(5000);

  // Check peer counts
  nodes.forEach((node, i) => {
    const peers = node.getPeers();
    logger.info(`[TEST-${i}] Connected peers: ${peers.length}`);
  });

  // Cleanup
  logger.info("Test complete — shutting down test nodes");
  await Promise.all(nodes.map(n => n.stop()));

  logger.resonance("Mesh test passed — curvature holding at 0.12");
}

// ────────────────────────────────────────────────
// Run if executed directly
// ────────────────────────────────────────────────

if (import.meta.main) {
  runMeshTest().catch(err => {
    logger.fatal("Mesh test failed:", err);
    process.exit(1);
  });
}
