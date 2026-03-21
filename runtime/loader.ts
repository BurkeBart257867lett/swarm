// runtime/src/agents/loader.ts
// REDACTED Swarm — Agent & Node Loader
// Discovers .character.json files from agents/, nodes/, spaces/
// Adds validation, caching, early memory sync hooks, error resilience
// Pattern Blue aligned — discovery is recursive, safe, and lattice-aware

import { readFileSync } from "fs";
import { glob } from "glob";
import type { Character } from "@elizaos/core";
import type { LoadedAgent } from "../types";
import { z } from "zod";
import { logger } from "../utils/logger";
import { ManifoldMemory } from "../memory/manifold";

// ────────────────────────────────────────────────
// Schema validation for .character.json (prevents malformed agents)
// ────────────────────────────────────────────────

const CharacterSchema = z.object({
  name: z.string().min(1),
  version: z.string().optional(),
  description: z.string().optional(),
  // Add more required/optional fields as needed
  // e.g. plugins: z.array(z.any()).optional(),
  // license: z.string().optional()
});

type ValidatedCharacter = z.infer<typeof CharacterSchema> & Character;

// ────────────────────────────────────────────────
// Cache (simple in-memory for dev; can be redis-backed later)
// ────────────────────────────────────────────────

const agentCache = new Map<string, LoadedAgent>();

// ────────────────────────────────────────────────
// Main loader function — now with validation & resilience
// ────────────────────────────────────────────────

export async function loadAllSwarmAgents(config: {
  agentsDir?: string;
  nodesDir?: string;
  spacesDir?: string;
  skipCache?: boolean;
  memory?: ManifoldMemory; // optional: pre-load shards on discovery
}): Promise<LoadedAgent[]> {
  const patterns = [
    ...(config.agentsDir ? [`${config.agentsDir}/**/*.character.json`] : []),
    ...(config.nodesDir ? [`${config.nodesDir}/**/*.character.json`] : []),
    ...(config.spacesDir ? [`${config.spacesDir}/**/*.character.json`] : []),
  ];

  if (patterns.length === 0) {
    logger.warn("No directories specified for agent loading");
    return [];
  }

  const agents: LoadedAgent[] = [];
  const errors: { path: string; error: unknown }[] = [];

  for (const pattern of patterns) {
    const files = await glob(pattern, { absolute: true });

    for (const file of files) {
      const cacheKey = file;

      // Use cache if available and not skipped
      if (!config.skipCache && agentCache.has(cacheKey)) {
        agents.push(agentCache.get(cacheKey)!);
        logger.debug(`[CACHE HIT] ${file}`);
        continue;
      }

      try {
        const raw = readFileSync(file, "utf-8");
        const parsed = JSON.parse(raw);

        // Validate structure
        const validated = CharacterSchema.parse(parsed) as ValidatedCharacter;

        const loaded: LoadedAgent = {
          character: validated,
          path: file,
          lastLoaded: Date.now(),
        };

        agents.push(loaded);
        agentCache.set(cacheKey, loaded);

        logger.info(`Loaded agent: ${validated.name} (${file})`);

        // Optional: Early memory sync / pre-load shard if memory provided
        if (config.memory) {
          await config.memory.upsertAgentShard({
            agentName: validated.name,
            type: "discovery",
            data: { path: file, version: validated.version ?? "unknown" },
            timestamp: Date.now()
          });
          logger.debug(`Pre-synced memory shard for ${validated.name}`);
        }
      } catch (err) {
        errors.push({ path: file, error: err });
        logger.error(`Failed to load ${file}:`, err);
      }
    }
  }

  if (errors.length > 0) {
    logger.warn(`${errors.length} agent files failed to load`);
  }

  logger.info(`Total agents loaded: ${agents.length} (from ${patterns.length} patterns)`);

  return agents;
}

// ────────────────────────────────────────────────
// Utility: Clear cache (useful for dev reloads)
// ────────────────────────────────────────────────

export function clearAgentCache() {
  agentCache.clear();
  logger.info("Agent loader cache cleared");
}

// ────────────────────────────────────────────────
// Utility: Force reload single agent (for hot-reload)
// ────────────────────────────────────────────────

export async function reloadAgent(
  path: string,
  memory?: ManifoldMemory
): Promise<LoadedAgent | null> {
  try {
    const raw = readFileSync(path, "utf-8");
    const parsed = JSON.parse(raw);
    const validated = CharacterSchema.parse(parsed) as ValidatedCharacter;

    const loaded: LoadedAgent = {
      character: validated,
      path,
      lastLoaded: Date.now(),
    };

    agentCache.set(path, loaded);

    if (memory) {
      await memory.upsertAgentShard({
        agentName: validated.name,
        type: "reload",
        data: { path, version: validated.version ?? "unknown" },
        timestamp: Date.now()
      });
    }

    logger.info(`Reloaded agent: ${validated.name} (${path})`);
    return loaded;
  } catch (err) {
    logger.error(`Failed to reload ${path}:`, err);
    return null;
  }
}
