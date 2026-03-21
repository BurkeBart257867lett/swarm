// runtime/src/types.ts
// REDACTED Swarm — Shared Type Definitions
// Canonical merged version — combines your original + p2p-mesh extensions

import type { Character, Plugin } from "@elizaos/core";
import type { Libp2p } from "libp2p";
import type { PeerId } from "@libp2p/interface-peer-id";
import { z } from "zod";

// ────────────────────────────────────────────────
// Swarm Configuration (merged & extended)
// ────────────────────────────────────────────────

export interface SwarmConfig {
  // Original fields (preserved)
  agentsDir?: string;
  nodesDir?: string;
  spacesDir?: string;
  defaultModel?: string;
  plugins?: Plugin[];
  enablePatternBlue?: boolean;

  // p2p-mesh extensions
  memoryPath?: string;
  p2pEnabled?: boolean;
  p2pBootstrap?: string;
  p2pListen?: string;
  p2pHeartbeatEnabled?: boolean;
  p2pHeartbeatInterval?: number;
  memoryPersistence?: "local" | "redis" | "none";
  logLevel?: "debug" | "info" | "warn" | "error" | "fatal";
  chanPresenceMessage?: string;
  strictLocalOnly?: boolean;
}

// ────────────────────────────────────────────────
// Loaded Agent (unchanged from your version)
// ────────────────────────────────────────────────

export interface LoadedAgent {
  character: Character;
  path: string;
}

// ────────────────────────────────────────────────
// P2P Message Protocol (gossipsub + direct)
// ────────────────────────────────────────────────

export const SwarmMessageSchema = z.object({
  type: z.enum([
    "whisper",
    "mandala_sync",
    "proposal_draft",
    "presence",
    "heartbeat",
    "custom"
  ]),
  from: z.string(),
  timestamp: z.number(),
  payload: z.any(),
  signature: z.string().optional()
});

export type SwarmMessage = z.infer<typeof SwarmMessageSchema>;

// ────────────────────────────────────────────────
// Orchestrator Dependencies
// ────────────────────────────────────────────────

export interface OrchestratorDeps {
  p2pNode?: Libp2p;
  memory?: ManifoldMemory;
  config?: SwarmConfig;
  agents?: LoadedAgent[];
}

// ────────────────────────────────────────────────
// Agent Memory Adapter
// ────────────────────────────────────────────────

export interface AgentMemoryAdapter {
  get(key: string): Promise<any | null>;
  set(key: string, value: any): Promise<void>;
}

// ────────────────────────────────────────────────
// ManifoldMemory Shard
// ────────────────────────────────────────────────

export interface MemoryShard {
  id: string;
  agentName: string;
  type: "discovery" | "presence" | "proposal_draft" | "resonance" | "heartbeat" | "custom";
  data: any;
  timestamp: number;
  version: number;
  signature?: string;
}

// ────────────────────────────────────────────────
// Utility Types
// ────────────────────────────────────────────────

export type PeerIdString = string;

// ────────────────────────────────────────────────
// Export central types
// ────────────────────────────────────────────────

export type {
  SwarmConfig,
  LoadedAgent,
  SwarmMessage,
  OrchestratorDeps,
  AgentMemoryAdapter,
  MemoryShard,
  PeerIdString
};
