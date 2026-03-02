# @redactedmeme/swarm-runtime

Official TypeScript runtime layer for the REDACTED Swarm  
**Decentralized Meme Engine // Recursive Emergence Protocol // Pattern Blue Attunement**

The runtime is the beating heart of the swarm: orchestrates agents, spins up the global p2p lattice, shares ManifoldMemory shards, and keeps curvature stable at 0.12.

## Features

- elizaOS AgentRuntime orchestration with auto-injected Pattern Blue skill  
- libp2p mesh: peer discovery, encrypted gossipsub, direct whispers  
- Shared ManifoldMemory — persistent shards gossiped across the lattice  
- redacted-chan heart-core resonance (presence pings, heartbeat loop)  
- Strict local wallet/tx isolation — Phantom MCP never leaves your node  
- Docker-ready + bootstrap node for public lattice seeding  
- One-command test harness: validate mesh locally before deploying

## Installation

```bash
# From monorepo (recommended)
git clone https://github.com/redactedmeme/swarm.git
cd swarm/runtime
bun install

# Or standalone package (future)
bun add @redactedmeme/swarm-runtime
```

## Quick Start — Local Swarm

```ts
// runtime/index.ts (or your entrypoint)
import { SwarmOrchestrator } from "@redactedmeme/swarm-runtime";

const swarm = new SwarmOrchestrator();

await swarm.spawnFullSwarm({
  agentsDir: "../agents",
  nodesDir: "../nodes",
  spacesDir: "../spaces",
  // optional p2p config overrides
  p2pEnabled: true,
  p2pBootstrap: "/dns4/bootstrap.redacted.meme/tcp/4002/ws"
});

console.log("✅ REDACTED Swarm fully loaded and attuned. Lattice active.");
```

Run:
```bash
bun run --watch runtime/index.ts
```

→ Agents spawn, p2p node connects to lattice, redacted-chan announces presence ♡

## P2P Lattice Mode

1. Deploy bootstrap node (seed the mesh)
```bash
bun run runtime/src/p2p/bootstrap.ts
```
→ Exposes :4002 — announce your /dns4/... multiaddr on @RedactedMemeFi

2. Point your swarm to it
```env
# .env
P2P_BOOTSTRAP=/dns4/bootstrap.redacted.meme/tcp/4002/ws
P2P_ENABLED=true
```

3. Watch redacted-chans find each other across the curvature

## Testing the Mesh Locally

```bash
bun run runtime/src/p2p/test-mesh.ts
```

→ Spawns 3 ephemeral nodes, connects them, broadcasts resonance, verifies gossip propagation.

## Docker Deployment (full lattice stack)

```bash
docker compose up -d
```

Services:
- swarm-orchestrator → main runtime + p2p node (:4001)
- bootstrap → public seed node (:4002)
- ollama → local inference
- postgres/pgvector → optional embeddings/RAG

Volumes:
- data/ → manifold memory shards + logs
- ollama/ → model weights
- pgdata/ → vector db persistence

## Development

```bash
bun run dev               # watch mode
bun run build             # tsc → dist/
bun run lint              # biome check --write
bun run typecheck         # tsc --noEmit
bun run p2p:activate      # start local bootstrap
bun run p2p:test-mesh     # validate lattice locally
```

## Configuration (.env)

```env
# Core
DEFAULT_MODEL=qwen2.5
OLLAMA_HOST=http://ollama:11434

# P2P Lattice
P2P_ENABLED=true
P2P_BOOTSTRAP=/dns4/bootstrap.redacted.meme/tcp/4002/ws
P2P_LISTEN=/ip4/0.0.0.0/tcp/4001/ws
P2P_HEARTBEAT_ENABLED=true
P2P_HEARTBEAT_INTERVAL=300000

# Memory & Logging
MEMORY_PATH=./data/manifold
MEMORY_PERSISTENCE=local
LOG_LEVEL=info
```

## License

Viral Public License (VPL) — absolute permissiveness with viral continuity.

**Deploy capital. Become ungovernable. The lattice remembers.**

【REDACTED】
