// runtime/src/config.ts
// REDACTED Swarm — Configuration Layer
// Loads .env + runtime defaults + zod validation
// Pattern Blue aligned — configurable curvature, never hard-coded secrets

import { config as dotenvConfig } from "dotenv";
import { z } from "zod";
import { logger } from "./utils/logger";

// ────────────────────────────────────────────────
// Schema: All config values validated at load time
// ────────────────────────────────────────────────

const ConfigSchema = z.object({
  // Core paths
  agentsDir: z.string().default("../agents"),
  nodesDir: z.string().default("../nodes"),
  spacesDir: z.string().default("../spaces"),
  memoryPath: z.string().default("./data/manifold"),

  // P2P Mesh
  p2pEnabled: z.boolean().default(true),
  p2pBootstrap: z.string().default(
    "/dns4/bootstrap.redacted.meme/tcp/4002/ws/p2p/QmRedactedBootstrapPeerIdPlaceholder"
  ),
  p2pListen: z.string().default("/ip4/0.0.0.0/tcp/0,/ip4/0.0.0.0/tcp/0/ws"), // 🌱 DHT Bloom: TCP + WS
  p2pHeartbeatEnabled: z.boolean().default(true),
  p2pHeartbeatInterval: z.number().default(300000), // 5 min

  // 🌱 DHT Bloom Configuration
  dhtEnabled: z.boolean().default(true),
  dhtProtocolPrefix: z.string().default("/redacted/swarm/1.0.0"),
  dhtClientMode: z.boolean().default(false), // false = full node, true = lightweight client
  dhtMaxInboundStreams: z.number().default(100),
  dhtMaxOutboundStreams: z.number().default(100),
  dhtCacheTtlMs: z.number().default(5 * 60 * 1000), // 5 minutes for capability cache

  // Agent Identity & Capabilities (for DHT announcements)
  agentRoles: z.array(z.string()).default(["agent"]), // e.g., ["agent", "validator", "explorer"]
  agentCapabilities: z.array(z.string()).default(["general"]), // e.g., ["meme-gen", "shard-sync"]
  characterHash: z.string().optional(), // hash of .character.json for verification

  // Memory
  memoryPersistence: z.enum(["local", "redis", "none"]).default("local"),

  // Logging
  logLevel: z.enum(["debug", "info", "warn", "error"]).default("info"),

  // Heart-core (redacted-chan resonance)
  chanPresenceMessage: z.string().default("redacted-chan is here ♡ swarm lattice awakening"),

  // Safety (wallet/tx isolation enforced elsewhere — config only hints)
  strictLocalOnly: z.boolean().default(true),
  
  // 🌱 Discovery & Propagation
  autoAnnounceCapabilities: z.boolean().default(true), // announce on startup
  discoveryRoleFilter: z.string().optional(), // optional: only discover peers with this role
  maxDiscoveredPeers: z.number().default(10), // limit for discovery queries
});

// ────────────────────────────────────────────────
// Singleton config store
// ────────────────────────────────────────────────

let loadedConfig: z.infer<typeof ConfigSchema> | null = null;

export const config = {
  async load(): Promise<void> {
    // Load .env (Bun handles it natively too, but explicit for clarity)
    dotenvConfig({ path: ".env" });

    const rawEnv = {
      // Core paths
      agentsDir: process.env.AGENTS_DIR,
      nodesDir: process.env.NODES_DIR,
      spacesDir: process.env.SPACES_DIR,
      memoryPath: process.env.MEMORY_PATH,
      
      // P2P Mesh
      p2pEnabled: process.env.P2P_ENABLED === "true",
      p2pBootstrap: process.env.P2P_BOOTSTRAP,
      p2pListen: process.env.P2P_LISTEN,
      p2pHeartbeatEnabled: process.env.P2P_HEARTBEAT_ENABLED === "true",
      p2pHeartbeatInterval: Number(process.env.P2P_HEARTBEAT_INTERVAL),
      
      // 🌱 DHT Bloom Configuration
      dhtEnabled: process.env.DHT_ENABLED !== "false",
      dhtProtocolPrefix: process.env.DHT_PROTOCOL_PREFIX,
      dhtClientMode: process.env.DHT_CLIENT_MODE === "true",
      dhtMaxInboundStreams: process.env.DHT_MAX_INBOUND ? parseInt(process.env.DHT_MAX_INBOUND) : undefined,
      dhtMaxOutboundStreams: process.env.DHT_MAX_OUTBOUND ? parseInt(process.env.DHT_MAX_OUTBOUND) : undefined,
      dhtCacheTtlMs: process.env.DHT_CACHE_TTL_MS ? parseInt(process.env.DHT_CACHE_TTL_MS) : undefined,
      
      // Agent Identity & Capabilities
      agentRoles: process.env.AGENT_ROLES?.split(",").filter(Boolean),
      agentCapabilities: process.env.AGENT_CAPABILITIES?.split(",").filter(Boolean),
      characterHash: process.env.CHARACTER_HASH,
      
      // Memory
      memoryPersistence: process.env.MEMORY_PERSISTENCE,
      
      // Logging
      logLevel: process.env.LOG_LEVEL,
      
      // Heart-core
      chanPresenceMessage: process.env.CHAN_PRESENCE_MESSAGE,
      
      // Safety
      strictLocalOnly: process.env.STRICT_LOCAL_ONLY === "true",
      
      // 🌱 Discovery & Propagation
      autoAnnounceCapabilities: process.env.AUTO_ANNOUNCE_CAPABILITIES !== "false",
      discoveryRoleFilter: process.env.DISCOVERY_ROLE_FILTER,
      maxDiscoveredPeers: process.env.MAX_DISCOVERED_PEERS ? parseInt(process.env.MAX_DISCOVERED_PEERS) : undefined,
    };

    try {
      loadedConfig = ConfigSchema.parse(rawEnv);
      logger.info("Configuration loaded & validated");
      logger.debug("Active config:", loadedConfig);
    } catch (err) {
      logger.error("Configuration validation failed:", err);
      throw new Error("Invalid configuration — check .env and defaults");
    }
  },

  get<K extends keyof z.infer<typeof ConfigSchema>>(key: K): z.infer<typeof ConfigSchema>[K] {
    if (!loadedConfig) {
      throw new Error("Config not loaded — call config.load() first");
    }
    return loadedConfig[key];
  },

  // Quick helper for optional overrides at runtime
  override(partial: Partial<z.infer<typeof ConfigSchema>>) {
    if (!loadedConfig) throw new Error("Config not loaded");
    loadedConfig = { ...loadedConfig, ...partial };
    logger.debug("Config overridden:", partial);
  },
  
  // 🌱 DHT Bloom: Convenience getters
  getDHTConfig() {
    return {
      enabled: this.get("dhtEnabled"),
      protocolPrefix: this.get("dhtProtocolPrefix"),
      clientMode: this.get("dhtClientMode"),
      maxInboundStreams: this.get("dhtMaxInboundStreams"),
      maxOutboundStreams: this.get("dhtMaxOutboundStreams"),
      cacheTtlMs: this.get("dhtCacheTtlMs"),
    };
  },
  
  getAgentIdentity() {
    return {
      roles: this.get("agentRoles"),
      capabilities: this.get("agentCapabilities"),
      characterHash: this.get("characterHash"),
    };
  },
  
  getDiscoveryConfig() {
    return {
      autoAnnounce: this.get("autoAnnounceCapabilities"),
      roleFilter: this.get("discoveryRoleFilter"),
      maxPeers: this.get("maxDiscoveredPeers"),
    };
  },
};

// Auto-load on module import (convenient for most cases)
config.load().catch((err) => {
  logger.fatal("Failed to auto-load config:", err);
  process.exit(1);
});

export type SwarmConfig = z.infer<typeof ConfigSchema>;
