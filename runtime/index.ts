export { SwarmOrchestrator } from "./orchestrator.ts";
export { loadAllSwarmAgents } from "./loader.ts";
export type { SwarmConfig, LoadedAgent } from "./types.ts";

// Quick demo (run with: bun runtime/index.ts)
if (import.meta.main) {
  const orchestrator = new SwarmOrchestrator();
  
  await orchestrator.spawnFullSwarm({
    agentsDir: "../agents",
    nodesDir: "../nodes",
  });

  console.log("✅ REDACTED Swarm fully loaded and attuned.");
}
