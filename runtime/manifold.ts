// runtime/src/memory/manifold.ts
// REDACTED Swarm — ManifoldMemory Layer
// Shared, persistent, shardable memory pool for agents & p2p sync
// Pattern Blue aligned — curvature preserved, shards gossiped across lattice

import { z } from "zod";
import { logger } from "../utils/logger";
import { config } from "../config";
import { mkdirSync, existsSync, writeFileSync, readFileSync } from "fs";
import { join } from "path";

// ────────────────────────────────────────────────
// Shard Schema — atomic memory units
// ────────────────────────────────────────────────

const MemoryShardSchema = z.object({
  id: z.string().uuid(),
  agentName: z.string(),
  type: z.enum(["discovery", "presence", "proposal_draft", "resonance", "heartbeat", "custom"]),
  data: z.any(),
  timestamp: z.number(),
  version: z.number().default(1),
  signature: z.string().optional() // future Phantom MCP sig
});

type MemoryShard = z.infer<typeof MemoryShardSchema>;

// ────────────────────────────────────────────────
// In-memory + file persistence (local mode)
// Future: redis / kv backing via config
// ────────────────────────────────────────────────

export class ManifoldMemory {
  private shards: Map<string, MemoryShard> = new Map();
  private basePath: string;
  private persistence: "local" | "redis" | "none";

  constructor(options: {
    persistence?: "local" | "redis" | "none";
    path?: string;
  } = {}) {
    this.persistence = options.persistence ?? config.get("memoryPersistence");
    this.basePath = options.path ?? config.get("memoryPath");

    if (this.persistence === "local" && !existsSync(this.basePath)) {
      mkdirSync(this.basePath, { recursive: true });
      logger.info(`ManifoldMemory directory created: ${this.basePath}`);
    }
  }

  async initialize(): Promise<void> {
    if (this.persistence === "local") {
      await this.loadFromDisk();
    }
    logger.info(`ManifoldMemory initialized — mode: ${this.persistence}`);
  }

  // ────────────────────────────────────────────────
  // Atomic upsert — guarded write
  // ────────────────────────────────────────────────
  async upsertAgentShard(shard: Omit<MemoryShard, "id" | "timestamp" | "version">): Promise<string> {
    const id = crypto.randomUUID();
    const fullShard: MemoryShard = {
      ...shard,
      id,
      timestamp: Date.now(),
      version: 1
    };

    // Validate
    MemoryShardSchema.parse(fullShard);

    this.shards.set(id, fullShard);

    if (this.persistence === "local") {
      const filePath = join(this.basePath, `${id}.json`);
      writeFileSync(filePath, JSON.stringify(fullShard, null, 2));
    }

    logger.debug(`Upserted shard: ${shard.type} for ${shard.agentName}`);

    return id;
  }

  // ────────────────────────────────────────────────
  // Get recent shards (for p2p sync)
  // ────────────────────────────────────────────────
  async getRecentShards(limit: number = 10): Promise<MemoryShard[]> {
    const sorted = Array.from(this.shards.values()).sort((a, b) => b.timestamp - a.timestamp);
    return sorted.slice(0, limit);
  }

  // ────────────────────────────────────────────────
  // Agent-specific memory adapter (passed to AgentRuntime)
  // ────────────────────────────────────────────────
  getAgentMemoryAdapter(agentName: string) {
    return {
      async get(key: string) {
        // Future: agent-specific prefix filtering
        return null; // stub — expand later
      },
      async set(key: string, value: any) {
        await this.upsertAgentShard({
          agentName,
          type: "custom",
          data: { key, value }
        });
      }
    };
  }

  // ────────────────────────────────────────────────
  // Disk load (local persistence only)
  // ────────────────────────────────────────────────
  private async loadFromDisk(): Promise<void> {
    // Stub — implement glob read of *.json in basePath
    // For now assume fresh start; expand in v0.3
    logger.debug("Local persistence load stub — starting fresh");
  }

  // ────────────────────────────────────────────────
  // Graceful close
  // ────────────────────────────────────────────────
  async close(): Promise<void> {
    if (this.persistence === "local") {
      // Future: flush pending writes
    }
    this.shards.clear();
    logger.info("ManifoldMemory closed");
  }
}
