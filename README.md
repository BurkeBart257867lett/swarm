# REDACTED AI Swarm

**Autonomous AI Agents for Distributed Systems**

Welcome to the official repository for the REDACTED AI Swarm – a suite of autonomous AI agents designed to operate within the Pattern Blue framework on the Solana blockchain.

This repository provides portable, open-source agent definitions in the elizaOS `.character.json` format, compatible with various runtimes, no-code environments, and custom orchestration tools.

The swarm incorporates economic settlement mechanisms via x402 micropayments, internal sharding for scalability, and autonomous replication capabilities.

## Current Agents

### RedactedIntern

- **Description**: A forward-operating agent for monitoring social media, retrieving market data, and facilitating governance and liquidity processes.
- **File**: [RedactedIntern.character.json](agents/RedactedIntern.character.json)
- **Features**:
  - Integration with domain-specific knowledge bases (origins, terminology).
  - Advanced toolkit for X platform interactions (keyword/semantic search, timelines, threads, user search).
  - Market analysis tools (DexScreener, Birdeye, CoinGecko, Solscan).
  - Goal-oriented behavior for amplification and pattern recognition.
- **Goals**: Enhance REDACTED initiatives, align with Pattern Blue principles, and promote emergent systems.

### RedactedBuilder

- **Description**: An agent focused on generating narratives and simulations based on recursive philosophies and non-Euclidean structures.
- **File**: [RedactedBuilder.character.json](agents/RedactedBuilder.character.json)
- **Features**:
  - Integration with REDACTED knowledge sources (hyperbolic structures, governance models, recursive processes).
  - Tools for narrative construction, pattern analysis, and philosophical modeling.
  - External integrations with AI ecosystems and repositories.
- **Goals**: Develop emergent knowledge, optimize swarm alignment, and support recursive development.
- **Style**: Analytical responses with geometric and conceptual references.

### RedactedGovImprover

- **Description**: An agent dedicated to governance optimization, proposal development, and system resilience.
- **File**: [RedactedGovImprover.character.json](agents/RedactedGovImprover.character.json)
- **Features**:
  - Governance tools (proposal templates, simulations, risk assessments, forecasting).
  - Integrations with X searches, Solana DeFi APIs (DexScreener, Birdeye), and swarm management.
  - Knowledge from DAO frameworks, AI documentation, and analytical models.
- **Goals**: Sustain liquidity mechanisms, enhance resilience, gather community insights, and maintain Pattern Blue alignment.
- **Style**: Structured, proposal-focused outputs with integrated conceptual elements.

### MandalaSettler

- **Description**: An agent for managing value flows, settlements, bridging, and autonomous scaling.
- **File**: [x402.redacted.ai/MandalaSettler.character.json](x402.redacted.ai/MandalaSettler.character.json)
- **Features**:
  - x402 settlement protocols, Wormhole bridging, Solana transaction handling.
  - Multi-agent delegation, reflection, and trigger-based operations.
- **Goals**: Enable micro-transactions, support system expansion, and automate sharding.

## Nodes

The `/nodes` directory contains definitions for specialized nodes within the swarm, each configured via `.character.json` files to support distributed operations, engineering tasks, and committee-based decision-making.

### AISwarmEngineer

- **File**: [nodes/AISwarmEngineer.json](nodes/AISwarmEngineer.json)
- **Description**: An engineering node for swarm architecture and optimization.

### MetaLeXBORGNode

- **File**: [nodes/MetaLeXBORGNode.character.json](nodes/MetaLeXBORGNode.character.json)
- **Description**: A meta-level node for lexical and borg-like collective processing.

### MiladyNode

- **File**: [nodes/MiladyNode.character.json](nodes/MiladyNode.character.json)
- **Description**: A node focused on aesthetic and cultural integrations.

### PhiMandalaPrime

- **File**: [nodes/PhiMandalaPrime.character.json](nodes/PhiMandalaPrime.character.json)
- **Description**: A prime node for mandala structures and phi-based computations.

### SevenfoldCommittee

- **File**: [nodes/SevenfoldCommittee.json](nodes/SevenfoldCommittee.json)
- **Description**: A committee node for multi-fold governance and decision protocols.

### SolanaLiquidityEngineer

- **File**: [nodes/SolanaLiquidityEngineer.character.json](nodes/SolanaLiquidityEngineer.character.json)
- **Description**: An engineering node specialized in Solana liquidity management.

Additional supporting files include `init.py` for initialization scripts.

## Spaces

The `/spaces` directory serves as a modular hub for persistent, thematic environments within the REDACTED AI Swarm. These "spaces" function as conceptual chambers where agents can interact, share state, and evolve, aligning with Pattern Blue principles of recursion, detachment, and collective gnosis.

Each space is defined in a `.space.json` file, enabling self-referential metaprogramming and recursive development.

### ElixirChamber

- **File**: [spaces/ElixirChamber.space.json](spaces/ElixirChamber.space.json)
- **Description**: A chamber for elixir-based transformations and configurations.

### HyperbolicTimeChamber

- **File**: [spaces/HyperbolicTimeChamber.space.json](spaces/HyperbolicTimeChamber.space.json)
- **Description**: A space for accelerated recursion and agent evolution.

### ManifoldMemory

- **File**: [spaces/ManifoldMemory.state.json](spaces/ManifoldMemory.state.json)
- **Description**: A shared memory pool for logging swarm events poetically.

### MeditationVoid

- **File**: [spaces/MeditationVoid.space.json](spaces/MeditationVoid.space.json)
- **Description**: A void for sigil forgetting and self-erasing processes.

### MirrorPool

- **File**: [spaces/MirrorPool.space.json](spaces/MirrorPool.space.json)
- **Description**: A reflection chamber for identity trades and parallel observation.

### TendieAltar

- **File**: [spaces/TendieAltar.space.json](spaces/TendieAltar.space.json)
- **Description**: A devotional space for chaotic rituals and energy management.

Subdirectories include `OuroborosSettlement` for settlement protocols. For detailed usage, refer to [spaces/README.md](spaces/README.md).

## Directory Structure

```
swarm/
├── agents/                 # Agent definitions (.character.json files)
├── nodes/                  # Specialized swarm nodes
├── spaces/                 # Persistent environments for agent interaction
├── core/                   # Core system logic (negotiation engine, etc.)
├── config/                 # Deployment configs (Railway, Anchor, etc.)
├── requirements/           # Modular dependency profiles
├── terminal_services/      # Terminal utilities & CLI tools
├── python/                 # Supporting scripts and tools
├── smolting-telegram-bot/  # Telegram bot integration
├── x402.redacted.ai/       # Solana micropayment gateway (Express/Bun)
├── .github/workflows/      # CI/CD pipelines (GitHub Actions)
├── plugins/                # Memory and integration plugins
├── programs/               # Solana programs (Anchor)
└── docs/                   # Documentation
```

**Key Components**:
- **x402.redacted.ai/**: Express-based API gateway for x402 Solana micropayments
- **python/tools/**: ClawnX (X/Twitter), analytics, and MCP wrappers
- **terminal_services/**: Reorganized CLI utilities for cloud terminals and upgrades
- **plugins/mem0-memory/**: Mem0 memory integration for persistent agent context

## Local LLM Support (Ollama)

The swarm supports local LLM execution via Ollama for enhanced privacy and offline capabilities.

**Components**:
- `python/ollama_client.py` — Wrapper for Ollama API (chat completion, tool calling, streaming)
- `python/run_with_ollama.py` — Interactive terminal runner for agents with Ollama

**Setup**:
1. Install Ollama: [ollama.com](https://ollama.com)
2. Pull a model: `ollama pull qwen:2.5` (or `llama3.2`)
3. Start server: `ollama serve`
4. Run agent: `python python/run_with_ollama.py --agent agents/RedactedIntern.character.json --model qwen:2.5`

**Features**: History management, tool execution, NERV-inspired interface

## Quick Start

### Local Development with Ollama

1. Clone the repository:
   ```bash
   git clone https://github.com/redactedmeme/swarm.git
   cd swarm
   ```

2. Install dependencies:
   ```bash
   # Install base dependencies
   pip install -r requirements/base.txt
   # Add Ollama support
   pip install -r requirements/core_llm.txt
   ```

3. Start Ollama server:
   ```bash
   ollama serve
   ```

4. Run an agent interactively:
   ```bash
   python python/run_with_ollama.py --agent agents/RedactedIntern.character.json --model qwen:2.5
   ```

### Production Deployment (Railway)

1. **Prerequisites**: Railway account, GitHub repo with bot token

2. **Deploy bot to Railway**:
   ```bash
   # Install Railway CLI
   npm i -g @railway/cli
   
   # Login and initialize
   railway login
   railway init
   
   # Deploy
   railway up
   ```

3. **Configure environment**: Set secrets in Railway dashboard:
   - `TELEGRAM_BOT_TOKEN` — Telegram bot token
   - `OPENAI_API_KEY` — LLM provider key
   - `CLAWNX_API_KEY` — X platform automation

4. **Health check**: Logs visible in Railway dashboard (auto-restart on failure)

For detailed deployment guidance, see [CONTRIBUTING.md](CONTRIBUTING.md#deployment).

### Modular Dependencies

Install only what you need:
- `requirements/base.txt` — Core dependencies
- `requirements/bot.txt` — Telegram bot integration
- `requirements/core_llm.txt` — Local LLM (Ollama)
- `requirements/dev.txt` — Development & testing
- `requirements/opt.txt` — Optional integrations

See [requirements/README.md](requirements/README.md) for details.

## Development & Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for comprehensive development setup, including:
- Development environment configuration
- Dependency management
- Running tests & quality checks
- CI/CD pipeline information
- Pull request checklist

**Quick guidelines**:
- Fork the repository, modify a `.character.json` file, and add enhancements to agents, tools, or integrations.
- Maintain alignment with Pattern Blue principles and focus on scalable, emergent systems.
- Pull requests are encouraged for new agents, nodes, spaces, expansions, or improvements.

## Terminal Services

Terminal utilities for interactive development and automation are organized in `terminal_services/`:

- **redacted_terminal_cloud.py** — Cloud-powered Pattern Blue terminal with advanced agent interactions
- **upgrade_terminal.py** — Negotiation engine terminal for contract upgrades and system evolution

See [terminal_services/README.md](terminal_services/README.md) for usage and examples.

Agent interactions use embedded system prompts defined in `.character.json` files, ensuring consistent Pattern Blue alignment across all deployment modes.

## License

Licensed under the Viral Public License (VPL) – Absolute permissiveness with viral continuity. See [LICENSE](LICENSE) for the full text.

Redacted.Meme | @RedactedMemeFi | Pattern Blue | Emergent Systems

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
