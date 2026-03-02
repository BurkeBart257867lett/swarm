// runtime/src/p2p/bootstrap.ts
// REDACTED Swarm — Standalone Bootstrap Node
// Lightweight seed node for libp2p mesh discovery
// Run separately on Railway/VPS: bun run p2p/bootstrap.ts
// Pattern Blue aligned — eternal lattice anchor, curvature stable

import { createLibp2p } from "libp2p";
import { webSockets } from "@libp2p/websockets";
import { noise } from "@chainsafe/libp2p-noise";
import { yamux } from "@chainsafe/libp2p-yamux";
import { identify } from "@libp2p/identify";
import { kadDHT } from "@libp2p/kad-dht";
import { multiaddr } from "@multiformats/multiaddr";
import { logger } from "../utils/logger";

// ────────────────────────────────────────────────
// Bootstrap node config — minimal & public-facing
// ────────────────────────────────────────────────

const LISTEN_ADDR = ["/ip4/0.0.0.0/tcp/4002/ws"];
const PROTOCOL_PREFIX = "redacted/bootstrap";

async function startBootstrapNode() {
  logger.info("Starting REDACTED Swarm Bootstrap Node...");

  const node = await createLibp2p({
    addresses: {
      listen: LISTEN_ADDR
    },

    transports: [webSockets()],

    connectionEncrypters: [noise()],

    streamMuxers: [yamux()],

    services: {
      identify: identify({
        protocolPrefix: PROTOCOL_PREFIX
      }),

      dht: kadDHT({
        clientMode: false, // full DHT node
        randomWalk: {
          enabled: true,
          interval: 10000 // aggressive for bootstrap
        }
      })
    }
  });

  await node.start();

  const listenAddrs = node.getMultiaddrs();
  logger.info("Bootstrap node online");
  logger.info("Listen addresses:");
  listenAddrs.forEach(addr => {
    console.log(`  ${addr.toString()}`);
    logger.info(`  ${addr.toString()}`);
  });

  logger.resonance("Bootstrap node ready — lattice peers may now connect");

  // Keep alive + periodic status
  setInterval(() => {
    const peers = node.getPeers();
    logger.info(`Current connected peers: ${peers.length}`);
    if (peers.length > 0) {
      logger.debug("Connected peer IDs:", peers.map(p => p.toString()));
    }
  }, 60000); // 1 min status

  // Graceful shutdown
  process.on("SIGINT", async () => {
    logger.info("SIGINT received — shutting down bootstrap node");
    await node.stop();
    logger.info("Bootstrap node offline — curvature preserved");
    process.exit(0);
  });
}

// ────────────────────────────────────────────────
// Run if executed directly: bun run p2p/bootstrap.ts
// ────────────────────────────────────────────────

if (import.meta.main) {
  startBootstrapNode().catch(err => {
    logger.fatal("Bootstrap node failed:", err);
    process.exit(1);
  });
}

export { startBootstrapNode };
