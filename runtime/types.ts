import type { Character, Plugin } from "@elizaos/core";

export interface SwarmConfig {
  agentsDir?: string;
  nodesDir?: string;
  spacesDir?: string;
  defaultModel?: string;
  plugins?: Plugin[];
  enablePatternBlue?: boolean;
}

export interface LoadedAgent {
  character: Character;
  path: string;
}
