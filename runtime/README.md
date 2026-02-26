# @redactedmeme/swarm-runtime

Official TypeScript runtime layer for the REDACTED Swarm.

## Usage

```ts
import { SwarmOrchestrator } from "@redactedmeme/swarm-runtime";

const swarm = new SwarmOrchestrator();

await swarm.spawnFullSwarm();           // loads everything + Pattern Blue
// or
await swarm.spawnAgent(myCustomCharacter);
