# @redactedmeme/swarm-runtime

Official TypeScript runtime layer for the REDACTED Swarm  
**Decentralized Meme Engine // Recursive Emergence Protocol // Pattern Blue Attunement**

The runtime is the beating heart of the swarm: orchestrates agents, spins up the global p2p lattice, shares ManifoldMemory shards, and keeps curvature stable at 0.12.

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
- ✅ Capability records signed by peer Ed25519 key (future: add explicit signature field)
- ✅ Namespace isolation via `/redacted/swarm/1.0.0` protocol prefix prevents cross-swarm interference

## 🚀 Installation

```bash
# From monorepo (recommended)
git clone https://github.com/redactedmeme/swarm.git  
cd swarm/runtime
bun install

# Or standalone package (future)
bun add @redactedmeme/swarm-runtime
