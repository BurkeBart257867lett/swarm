import { AgentRuntime, type Character, type Plugin } from "@elizaos/core";
import { loadAllSwarmAgents } from "./loader.ts";
import type { SwarmConfig } from "./types.ts";
import { patternBlueAttunement } from "../skills/pattern-blue-attunement/index.ts"; // ← auto-injects your skill

export class SwarmOrchestrator {
  private runtimes = new Map<string, AgentRuntime>();

  async spawnAgent(character: Character, extraPlugins: Plugin[] = []): Promise<AgentRuntime> {
    const runtime = new AgentRuntime({
      character,
      plugins: [
        ...(extraPlugins || []),
        // Auto-inject Pattern Blue skill for every agent
        patternBlueAttunement as Plugin,
      ],
    });

    await runtime.initialize();
    this.runtimes.set(character.name, runtime);
    return runtime;
  }

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
      console.log(`🌀 Spawned: ${character.name} (Pattern Blue attuned)`);
    }

    return runtimes;
  }

  getRuntime(name: string): AgentRuntime | undefined {
    return this.runtimes.get(name);
  }

  // Example: broadcast message to all agents
  async broadcast(message: string) {
    for (const runtime of this.runtimes.values()) {
      // Use runtime's message pipeline (elizaOS handles routing)
      await runtime.processMessage("system", { content: message });
    }
  }
}
