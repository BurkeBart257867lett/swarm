import { readFileSync } from "fs";
import { glob } from "glob";
import type { Character } from "@elizaos/core";
import type { LoadedAgent } from "./types.ts";

export async function loadAllSwarmAgents(config: {
  agentsDir?: string;
  nodesDir?: string;
  spacesDir?: string;
}): Promise<LoadedAgent[]> {
  const patterns = [
    ...(config.agentsDir ? [`${config.agentsDir}/**/*.character.json`] : []),
    ...(config.nodesDir ? [`${config.nodesDir}/**/*.character.json`] : []),
    ...(config.spacesDir ? [`${config.spacesDir}/**/*.character.json`] : []),
  ];

  const agents: LoadedAgent[] = [];

  for (const pattern of patterns) {
    const files = await glob(pattern);
    for (const file of files) {
      const raw = readFileSync(file, "utf-8");
      const character = JSON.parse(raw) as Character;
      agents.push({ character, path: file });
    }
  }

  return agents;
}
