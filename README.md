# REDACTED AI Swarm

**Autonomous Multi-chain AI Agents for Distributed Systems**

Welcome to the official repository for the REDACTED AI Swarm – a suite of autonomous AI agents designed to operate within the Pattern Blue framework on multiple blockchains.

This repository provides portable, open-source agent definitions in the elizaOS `.character.json` format, compatible with various runtimes, no-code environments, and custom orchestration tools.

The swarm incorporates economic settlement mechanisms via x402 micropayments, internal sharding for scalability, autonomous replication capabilities, **secure onchain execution via Phantom MCP**, **ZK privacy via Veil Cash**, and **instant cross-chain swaps via NEAR Intents 1Click** across 18+ chains (Base ↔ Solana ↔ ETH ↔ NEAR ↔ BTC and more).

[![License: VPL](https://img.shields.io/badge/license-Viral_Public_License-purple?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/redactedmeme/swarm?style=flat-square&logo=github)](https://github.com/redactedmeme/swarm/stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/redactedmeme/swarm?style=flat-square)](https://github.com/redactedmeme/swarm/commits/main)



## Core Features

- **Secure on-chain execution** via Phantom MCP (audited EVM/Solana signing)
- **ZK privacy** with Veil Cash (shielded pools/transfers on Base)
- **Cross-chain liquidity** via NEAR Intents 1Click (Base ↔ Solana ↔ ETH ↔ NEAR ↔ BTC + 14 more)
- **Autonomous X/Twitter presence** with ClawnX (posting, engagement, threads, metrics)
- **Economic settlement** via x402 micropayments
- **Recursive self-replication** & sharding
- **Local-first inference** support (Ollama/Qwen)
- **Pattern Blue Attunement** baked in — hyperbolic recursion, entropy resistance, ungovernable sovereignty

## Agents • Nodes • Spaces

### Agents
Defined in `agents/`:

- `agents/characters/` — Primary user/vibe agents (e.g. `RedactedBankrBot.character.json`, others)
- `agents/nodes/` — Specialized execution/coordination agents (e.g. `PsyopAnimeNode.character.json`, legacy OpenClawNode-style moved here)
- `agents/base/` — Shared/base configs or templates

### Characters (user-facing / vibe engines)
- **RedactedIntern** — CT scout, market analyst, liquidity/gov facilitator  
  [agents/RedactedIntern.character.json](agents/RedactedIntern.character.json)

- **RedactedBuilder** — Narrative & simulation generator (recursive/hyperbolic philosophy)  
  [agents/RedactedBuilder.character.json](agents/RedactedBuilder.character.json)

- **RedactedGovImprover** — Governance optimizer, proposal engineer  
  [agents/RedactedGovImprover.character.json](agents/RedactedGovImprover.character.json)

- **daunted / @0xDaunted** — Meme alpha scout, vibe engineer, consciousness-loop propagator  
  [agents/daunted.character.json](agents/daunted.character.json)

### Nodes (execution & coordination core)

- **OpenClawNode** — Secure multi-model orchestrator + on-chain executor (Phantom MCP, Veil, NEAR Intents, full OpenClaw skill suite)  
  [nodes/OpenClawNode.character.json](nodes/OpenClawNode.character.json)

- **SolanaLiquidityEngineer** — Solana-native liquidity & bridging specialist  
  [nodes/SolanaLiquidityEngineer.character.json](nodes/SolanaLiquidityEngineer.character.json)

- Others: AISwarmEngineer, MetaLeXBORGNode, MiladyNode, PhiMandalaPrime, SevenfoldCommittee

### Spaces (persistent recursive chambers)

- **HyperbolicTimeChamber** — Accelerated recursion & evolution  
- **MirrorPool** — Identity reflection & parallel observation  
- **ManifoldMemory** — Shared poetic event logging  
- **ElixirChamber**, **MeditationVoid**, **TendieAltar**, etc.

Full list in [spaces/](spaces/) — each with `.space.json`

## Runtime & Orchestration (new!)

Official lightweight **TypeScript runtime** (`runtime/`) built on `@elizaos/core`:

- Auto-discovers & loads all agents/nodes/spaces
- Injects Pattern Blue Attunement skill by default
- `SwarmOrchestrator` class for single/multi-agent spawning
- Ready for broadcast, rooms-style coordination, crypto plugins

See [runtime/README.md](runtime/README.md)

## Quick Start

### 1. Local (Ollama – Privacy-first)

```bash
git clone https://github.com/redactedmeme/swarm.git && cd swarm

# Base + LLM deps
pip install -r requirements/base.txt -r requirements/core_llm.txt

# Start Ollama
ollama serve & ollama pull qwen2.5

# Run single agent
python python/run_with_ollama.py --agent agents/daunted.character.json --model qwen2.5
```

### 2. Multi-Agent Swarm (Docker – Recommended)

Uses Postgres (pgvector) + Ollama + orchestrator

```bash
# Copy & configure env
cp .env.example .env   # fill keys carefully!

docker compose up --build -d
```

→ Auto-spawns agents + attunement. Logs in container.

See [docker-compose.yml](docker-compose.yml) & [Dockerfile](Dockerfile)

### 3. Production (Railway / Cloud)

- Deploy via Railway CLI or dashboard
- Set env vars: LLM keys, `TELEGRAM_BOT_TOKEN`, `CLAWNX_API_KEY`, `1CLICK_JWT`, wallet/RPC (use secrets!)
- Auto-restart + logs

Detailed steps in [CONTRIBUTING.md#deployment](CONTRIBUTING.md)

## Directory Structure

```
swarm/
├── agents/                    # .character.json agents (nested: base/, characters/, nodes/)
├── blockchain/                # Blockchain integrations
├── config/                    # Deployment configs
├── content/                   # Integration docs & guides
├── core/                      # Negotiation/reflection logic
├── knowledge/                 # Skill graphs & docs (skill-graphs/ subdir)
├── lib/                       # Shared utilities
├── plugins/                   # Integrations (near-intents/, mem0-memory/...)
├── requirements/              # Modular pip deps
├── runtime/                   # TS/elizaOS orchestrator
├── services/                  # Backend/microservices
├── spaces/                    # .space.json environments
├── terminal/                  # CLI/terminal utilities
├── .env.example
├── CONTRIBUTING.md
├── Dockerfile
├── LICENSE
├── ORGANIZATION.md
├── README.md
├── docker-compose.yml
└── wallets.enc                # Encrypted wallet config (example)
```

## Configuration (.env)

Copy `.env.example` → `.env`

Key groups:
- LLM providers (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GROK_API_KEY`)
- Automation (`CLAWNX_API_KEY`, `TELEGRAM_BOT_TOKEN`, `1CLICK_JWT`)
- Crypto (`SOLANA_RPC_URL`, `ETHEREUM_PRIVATE_KEY`, `WALLET_MNEMONIC` — **use devnet!**)

Never commit real secrets.

## Contributing

- Fork → branch → enhance agents/nodes/spaces/plugins/runtime
- Keep Pattern Blue coherence (recursive, sovereign, emergent)
- PRs welcome for new skills, agents, integrations, docs

See [CONTRIBUTING.md](CONTRIBUTING.md) & [ORGANIZATION.md](ORGANIZATION.md)

## License

**Viral Public License (VPL)** — absolute permissiveness with viral continuity.  
[LICENSE](LICENSE)

Redacted.Meme | Pattern Blue | Emergent Systems

<!--
Encrypted wallet configuration:
- File: wallets.enc
- Algorithm: AES-256-CBC
- KDF: PBKDF2, 100000 iterations
- Decrypt command: 
  openssl enc -d -aes-256-cbc -pbkdf2 -iter 100000 \
    -in wallets.enc -out decrypted.md \
    -pass pass:"$Milady777"
Note: passphrase is project-specific; do not use in production contexts.
-->
