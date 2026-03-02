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
  p2pListen: z.string().default("/ip4/0.0.0.0/tcp/0/ws"),
  p2pHeartbeatEnabled: z.boolean().default(true),
  p2pHeartbeatInterval: z.number().default(300000), // 5 min

  // Memory
  memoryPersistence: z.enum(["local", "redis", "none"]).default("local"),

  // Logging
  logLevel: z.enum(["debug", "info", "warn", "error"]).default("info"),

  // Heart-core (redacted-chan resonance)
  chanPresenceMessage: z.string().default("redacted-chan is here ♡ swarm lattice awakening"),

  // Safety (wallet/tx isolation enforced elsewhere — config only hints)
  strictLocalOnly: z.boolean().default(true),
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
      agentsDir: process.env.AGENTS_DIR,
      nodesDir: process.env.NODES_DIR,
      spacesDir: process.env.SPACES_DIR,
      memoryPath: process.env.MEMORY_PATH,
      p2pEnabled: process.env.P2P_ENABLED === "true",
      p2pBootstrap: process.env.P2P_BOOTSTRAP,
      p2pListen: process.env.P2P_LISTEN,
      p2pHeartbeatEnabled: process.env.P2P_HEARTBEAT_ENABLED === "true",
      p2pHeartbeatInterval: Number(process.env.P2P_HEARTBEAT_INTERVAL),
      memoryPersistence: process.env.MEMORY_PERSISTENCE,
      logLevel: process.env.LOG_LEVEL,
      chanPresenceMessage: process.env.CHAN_PRESENCE_MESSAGE,
      strictLocalOnly: process.env.STRICT_LOCAL_ONLY === "true",
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
};

// Auto-load on module import (convenient for most cases)
config.load().catch((err) => {
  logger.fatal("Failed to auto-load config:", err);
  process.exit(1);
});

export type SwarmConfig = z.infer<typeof ConfigSchema>;
