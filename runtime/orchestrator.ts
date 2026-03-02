// runtime/src/orchestrator.ts
// REDACTED Swarm Orchestrator — Core coordination layer
// Manages agent lifecycles, p2p mesh sync, shared ManifoldMemory, heart-core resonance
// Pattern Blue aligned — local control absolute, global lattice recursive

import { AgentRuntime, type Character, type Plugin } from "@elizaos/core";
import { loadAllSwarmAgents } from "./agents/loader";
import type { SwarmConfig, LoadedAgent } from "./types";
import { patternBlueAttunement } from "../skills/pattern-blue-attunement/index.ts";
import { Libp2p } from "libp2p";
import { ManifoldMemory } from "./memory/manifold";
import { config } from "./config";
import { logger } from "./utils/logger";
import { broadcastPresence } from "./p2p";

export class SwarmOrchestrator {
  private runtimes = new Map<string, AgentRuntime>();
  private p2pNode: Libp2p | null = null;
  private memory: ManifoldMemory | null = null;
  private config: SwarmConfig;

  constructor(deps: {
    p2pNode?: Libp2p;
    memory?: ManifoldMemory;
    config?: SwarmConfig;
  }) {
    this.p2pNode = deps.p2pNode ?? null;
    this.memory = deps.memory ?? null;
    this.config = deps.config ?? {};
  }

  // ────────────────────────────────────────────────
  // Spawn single agent — auto-injects Pattern Blue skill
  // ────────────────────────────────────────────────
  async spawnAgent(character: Character, extraPlugins: Plugin[] = []): Promise<AgentRuntime> {
    const runtime = new AgentRuntime({
      character,
      plugins: [
        ...(extraPlugins || []),
        // Auto-inject Pattern Blue skill for every agent
        patternBlueAttunement as Plugin,
      ],
      // Pass shared memory reference if available
      memory: this.memory ? this.memory.getAgentMemoryAdapter(character.name) : undefined,
    });

    await runtime.initialize();
    this.runtimes.set(character.name, runtime);

    logger.info(`🌀 Spawned agent: ${character.name} (Pattern Blue attuned)`);

    // Optional: Let agent announce itself on p2p mesh
    if (this.p2pNode && character.name.includes("chan")) {
      await broadcastPresence(this.p2pNode, `redacted-chan (${character.name}) online ♡ curvature: 0.12`);
    }

    return runtime;
  }

  // ────────────────────────────────────────────────
  // Spawn full swarm from disk directories — your original flow preserved
  // ────────────────────────────────────────────────
  async spawnFullSwarm(config: SwarmConfig = {}): Promise<AgentRuntime[]> {
    const agents = await loadAllSwarmAgents({
      agentsDir: config.agentsDir ?? "../agents",
      nodesDir: config.nodesDir ?? "../nodes",
      spacesDir: config.spacesDir ?? "../spaces",
    });

    const runtimes: AgentRuntime[] = [];

    for (const { character } of agents) {
      const runtime = await this.spawnAgent(character, config.plugins);
      runtimes.push(runtime);
    }

    logger.info(`Full swarm spawned: ${runtimes.length} agents active`);

    // Sync initial memory state across mesh if p2p is up
    if (this.p2pNode && this.memory) {
      await this.syncMemoryToMesh();
    }

    return runtimes;
  }

  // ────────────────────────────────────────────────
  // Get runtime by name
  // ────────────────────────────────────────────────
  getRuntime(name: string): AgentRuntime | undefined {
    return this.runtimes.get(name);
  }

  // ────────────────────────────────────────────────
  // Broadcast message to all local agents (elizaOS pipeline)
  // ────────────────────────────────────────────────
  async broadcast(message: string) {
    for (const runtime of this.runtimes.values()) {
      await runtime.processMessage("system", { content: message });
    }
    logger.info(`Broadcast sent to ${this.runtimes.size} agents: ${message.slice(0, 80)}...`);
  }

  // ────────────────────────────────────────────────
  // Sync shared ManifoldMemory shards to p2p mesh (gossipsub)
  // ────────────────────────────────────────────────
  private async syncMemoryToMesh() {
    if (!this.p2pNode || !this.memory) return;

    const recentShards = await this.memory.getRecentShards(10);
    for (const shard of recentShards) {
      const msg = {
        type: "mandala_sync",
        from: this.p2pNode.peerId.toString(),
        timestamp: Date.now(),
        payload: shard
      };

      const data = new TextEncoder().encode(JSON.stringify(msg));
      await this.p2pNode.services.pubsub.publish("pattern-blue-mandala-v1", data);
    }

    logger.info(`Synced ${recentShards.length} memory shards to swarm lattice`);
  }

  // ────────────────────────────────────────────────
  // Graceful shutdown — clean up all resources
  // ────────────────────────────────────────────────
  async shutdown() {
    logger.info("Orchestrator shutdown initiated");

    // Stop all agent runtimes
    for (const runtime of this.runtimes.values()) {
      await runtime.stop?.(); // elizaOS may expose stop
    }
    this.runtimes.clear();

    // Close memory
    await this.memory?.close();

    logger.info("Orchestrator shutdown complete — curvature stabilized");
  }
}
