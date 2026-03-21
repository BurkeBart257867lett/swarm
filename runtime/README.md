# @redactedmeme/swarm-runtime

Official TypeScript runtime layer for the REDACTED Swarm  
**Decentralized Meme Engine // Recursive Emergence Protocol // Pattern Blue Attunement**

The runtime is the beating heart of the swarm: orchestrates agents, spins up the global p2p lattice, shares ManifoldMemory shards, and keeps curvature stable at 0.12.

> 📦 This package lives at `runtime/` in the monorepo:  
> https://github.com/redactedmeme/swarm/tree/main/runtime

## ✨ Features

- elizaOS AgentRuntime orchestration with auto-injected Pattern Blue skill  
- **🌱 DHT Bloom**: Decentralized peer discovery via Kad-DHT — no fixed bootstrap required  
- libp2p mesh: encrypted gossipsub, direct whispers, **capability-based routing**  
- Shared ManifoldMemory — persistent shards gossiped across the lattice  
- redacted-chan heart-core resonance (presence pings, heartbeat loop)  
- Strict local wallet/tx isolation — Phantom MCP never leaves your node  
- Docker-ready + bootstrap node for public lattice seeding (fallback only)  
- One-command test harness: validate mesh locally before deploying  

## 🌱 DHT Bloom: Decentralized Discovery

The swarm now self-organizes via **Kad-DHT**, enabling agents to discover each other through *resonance signals* rather than hardcoded addresses.

### How It Works
1. **Announce**: On startup, agents publish their capabilities (roles, skills) to the DHT under namespaced keys: `/redacted/capability/{role}/{peerId}`
2. **Query**: Agents seeking coordination partners query the DHT for peers with complementary roles (e.g., `validator`, `explorer`)
3. **Connect**: Direct encrypted connections form via libp2p, bypassing central infrastructure
4. **Propagate**: Capability records gossip through the DHT, enabling organic lattice growth

### Privacy & Safety
- ✅ No wallet keys or sensitive data stored in DHT records
- ✅ All DHT traffic encrypted via Noise protocol
- ✅ Capability records schema-validated (Zod) and timestamped to prevent replay attacks
- ✅ Namespace isolation via `/redacted/swarm/1.0.0` protocol prefix prevents cross-swarm interference

## 🚀 Installation

```bash
# From monorepo root
git clone https://github.com/redactedmeme/swarm.git  
cd swarm/runtime
bun install

# Or standalone package (future)
bun add @redactedmeme/swarm-runtime
```

## ⚡ Quick Start — Local Swarm

```ts
// From runtime/ directory
import { SwarmOrchestrator } from "@redactedmeme/swarm-runtime";

const swarm = new SwarmOrchestrator();

await swarm.spawnFullSwarm({
  // Paths relative to runtime/ (monorepo structure)
  agentsDir: "../agents",
  nodesDir: "../nodes", 
  spacesDir: "../spaces",
  
  // P2P config
  p2pEnabled: true,
  p2pListen: "/ip4/0.0.0.0/tcp/0,/ip4/0.0.0.0/tcp/0/ws",
  dhtEnabled: true,
  dhtProtocolPrefix: "/redacted/swarm/1.0.0"
});

console.log("✅ REDACTED Swarm fully loaded and attuned. Lattice active.");
```

Run from `runtime/` directory:
```bash
# Watch mode (see package.json for entry point)
bun run dev

# Or direct execution
bun run src/index.ts
```

→ Agents spawn from `../agents/`, p2p node connects to lattice, **announces capabilities via DHT**, redacted-chan announces presence ♡

## 🌐 P2P Lattice Mode

### Option A: Pure DHT Discovery (Recommended)
No bootstrap required. Agents find each other via capability queries.

```env
# .env (in runtime/)
P2P_ENABLED=true
P2P_LISTEN=/ip4/0.0.0.0/tcp/4001,/ip4/0.0.0.0/tcp/4001/ws
DHT_ENABLED=true
DHT_PROTOCOL_PREFIX=/redacted/swarm/1.0.0
AGENT_ROLES=agent,explorer
AGENT_CAPABILITIES=meme-gen,shard-sync
```

### Option B: Bootstrap-Assisted (Fallback)
Use a seed node for initial discovery, then DHT takes over.

```env
# .env (in runtime/)
P2P_BOOTSTRAP=/dns4/bootstrap.redacted.meme/tcp/4002/ws
DHT_ENABLED=true
```

1. Deploy bootstrap node (optional seed)
```bash
# From runtime/
bun run p2p:activate
```
→ Exposes :4002 — announce your /dns4/... multiaddr on @RedactedMemeFi

2. Point your swarm to it (or omit for pure DHT)
3. Watch redacted-chans find each other across the curvature — **via DHT resonance**

## 🧪 Testing the Mesh Locally

### Standard Mesh Test
```bash
# From runtime/
bun run p2p:test-mesh
```
→ Spawns ephemeral nodes, connects them, broadcasts resonance, verifies gossip propagation.

### 🌱 Void Jump Test (DHT Discovery)
Test pure DHT discovery with **no shared bootstrap**:

```bash
# From runtime/, Terminal 1: Node A
bun run p2p:void-jump --node A --port 4001

# Terminal 2: Node B (different port, NO bootstrap config)
bun run p2p:void-jump --node B --port 4002 --bootstrap ""
```

✅ **Success**: Two isolated nodes discover each other via DHT capability queries, not bootstrap config.

## 🐳 Docker Deployment (full lattice stack)

```bash
# docker-compose.yml is at repo root — run from anywhere:
docker compose up -d

# Or explicitly:
docker compose -f ../docker-compose.yml up -d
```

Services:
- swarm-orchestrator → main runtime + p2p node (:4001)
- bootstrap → public seed node (:4002) *[optional fallback]*
- ollama → local inference
- postgres/pgvector → optional embeddings/RAG

Volumes:
- `runtime/data/` → manifold memory shards + logs + **DHT state cache**
- `ollama/` → model weights
- `pgdata/` → vector db persistence

### 🌱 DHT Port Exposure
Ensure TCP ports are exposed for DHT traffic in root `docker-compose.yml`:
```yaml
services:
  swarm-orchestrator:
    ports:
      - "4001:4001"   # WS
      - "4003:4003"   # TCP for DHT
```

## ⚙️ Configuration (.env)

```env
# Core
DEFAULT_MODEL=qwen2.5
OLLAMA_HOST=http://ollama:11434

# P2P Lattice
P2P_ENABLED=true
P2P_BOOTSTRAP=/dns4/bootstrap.redacted.meme/tcp/4002/ws  # optional fallback
P2P_LISTEN=/ip4/0.0.0.0/tcp/4001,/ip4/0.0.0.0/tcp/4001/ws  # 🌱 TCP + WS
P2P_HEARTBEAT_ENABLED=true
P2P_HEARTBEAT_INTERVAL=300000

# 🌱 DHT Bloom Configuration
DHT_ENABLED=true
DHT_PROTOCOL_PREFIX=/redacted/swarm/1.0.0
DHT_CLIENT_MODE=false
DHT_MAX_INBOUND=100
DHT_MAX_OUTBOUND=100
DHT_CACHE_TTL_MS=300000

# Agent Identity (for DHT capability announcements)
AGENT_ROLES=agent,explorer
AGENT_CAPABILITIES=meme-gen,shard-sync,gossip
CHARACTER_HASH=QmYourCharacterHashHere

# Discovery & Propagation
AUTO_ANNOUNCE_CAPABILITIES=true
DISCOVERY_ROLE_FILTER=
MAX_DISCOVERED_PEERS=10

# Memory & Logging
MEMORY_PATH=./data/manifold
MEMORY_PERSISTENCE=local
LOG_LEVEL=info
```

## 🔧 Development

```bash
# All commands run from runtime/ directory
bun run dev               # watch mode
bun run build             # tsc → dist/
bun run lint              # biome check --write
bun run typecheck         # tsc --noEmit
bun run p2p:activate      # start local bootstrap
bun run p2p:test-mesh     # validate lattice locally
bun run p2p:void-jump     # 🌱 test pure DHT discovery
```

See `package.json` scripts for exact entry points.

## 🛡️ Security Notes

- **Wallet Isolation**: DHT records never contain private keys or signed transactions. All signing remains local via Phantom MCP.
- **Record Validation**: Capability records are schema-validated (Zod) and timestamped to prevent replay attacks.
- **Namespace Isolation**: The `/redacted/swarm/1.0.0` DHT protocol prefix prevents accidental cross-talk with other libp2p networks.
- **Ephemeral PeerIDs**: For high-anonymity deployments, consider rotating PeerIDs periodically (trade-off: loses reputation accumulation).

## 📂 Runtime Package Structure

```
runtime/
├── package.json          # @redactedmeme/swarm-runtime
├── README.md             # this file
├── src/
│   ├── index.ts          # main entry / SwarmOrchestrator export
│   ├── p2p.ts            # libp2p node factory + DHT helpers
│   ├── config.ts         # zod-validated configuration
│   └── ...               # other runtime modules
├── data/                 # manifold memory + DHT cache (gitignored)
└── dist/                 # compiled output (gitignored)
```

> 🔗 For full monorepo structure, see [../README.md](../README.md)

## 📜 License

Viral Public License (VPL) — absolute permissiveness with viral continuity.

**Deploy capital. Become ungovernable. The lattice remembers.**

【REDACTED】
