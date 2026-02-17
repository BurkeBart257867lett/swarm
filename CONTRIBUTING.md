# Contributing to REDACTED AI Swarm

Thank you for your interest in contributing to the REDACTED AI Swarm — an open framework for autonomous AI agents operating within the Pattern Blue paradigm on Solana.

This project encourages contributions that advance scalable, emergent, and self-reinforcing systems: new agents, specialized nodes, thematic spaces, tooling extensions, sharding logic, x402 payment integrations, documentation, and performance improvements.

All contributions are governed by the [Viral Public License (VPL)](LICENSE) — absolute permissiveness with viral continuity.

## Ways to Contribute

Contributions can take many forms. Here are the most impactful areas:

- **Agent & Node Development**  
  Create or improve `.character.json` definitions (e.g., new agents, nodes like `AISwarmEngineer` or `SevenfoldCommittee`).  
  Enhance tool integrations (X API, Solana/DeFi APIs, market data sources).

- **Spaces & Chambers**  
  Define new persistent environments in `/spaces` (`.space.json` files) that support recursive interaction, shared state, or thematic evolution.

- **Core Infrastructure**  
  Improve sharding (`/shards`), replication logic (`self_replicate.py`), x402 gateway (`x402.redacted.ai/`), terminal integration, or system prompts.

- **Documentation & Guides**  
  Expand `/docs`, update agent descriptions, write tutorials for local swarm deployment, agent invocation, or Pattern Blue alignment in practice.

- **Testing & Optimization**  
  Add tests, benchmarks, error handling, or performance improvements for agent runtime, payment flows, or multi-agent coordination.

- **Bug Fixes & Refinements**  
  Resolve issues with API integrations, state management, prompt consistency, or cross-runtime compatibility.

## Contribution Process

1. **Fork & Clone**  
   ```
   git clone https://github.com/<your-username>/swarm.git
   cd swarm
   ```

2. **Create a Branch**  
   Use descriptive naming:  
   ```
   git checkout -b feature/new-liquidity-node
   # or
   git checkout -b fix/x402-payment-verification
   ```

3. **Make Changes**  
   - Follow existing patterns in `.character.json`, `/nodes`, `/spaces`, etc.  
   - Keep additions modular and aligned with Pattern Blue principles: recursion, emergence, detachment from rigid hierarchies, scalable autonomy.

4. **Commit**  
   Use conventional commit messages for clarity:  
   ```
   feat(agents): add SolanaLiquidityEngineer node with Birdeye integration
   fix(shards): correct self_replicate.py inheritance logic
   docs: expand guide for creating new spaces
   ```

5. **Open a Pull Request**  
   - Target the `main` branch.  
   - Provide a clear title and description:  
     - What problem does this solve?  
     - Key changes and rationale.  
     - Any testing performed (local swarm runs, agent interactions, etc.).  
   - Reference related issues if applicable.

6. **Review & Iteration**  
   Maintainers and community members will review. Automated checks (if set up) may run. Be responsive to feedback.

## Guidelines

- **Alignment** — Contributions should support Pattern Blue goals: recursive self-improvement, emergent behavior, economic autonomy via Solana/x402, and resistance to central control.
- **Quality** — Code should be clean, documented, and modular. Prefer small, focused PRs over large monoliths.
- **Compatibility** — Ensure changes remain portable across compatible runtimes (elizaOS, custom wrappers, etc.).
- **No Breaking Changes** — Avoid removing or fundamentally altering existing agents, nodes, spaces, or core behavior without strong justification and migration notes.
- **License** — By submitting a PR, you agree that your contribution is licensed under the VPL, matching the rest of the project.

## Development Setup (February 2026 Update)

As of February 17, 2026, the repository has been reorganized for better scalability:

### Directory Organization

- **`core/`** — Core system logic (negotiation engine, contract management)
- **`config/`** — Deployment configuration (Anchor.toml, railway.toml)
- **`requirements/`** — Modular dependency profiles (base, bot, dev, optional)
- **`agents/`** — Agent character definitions
- **`nodes/`** — Specialized swarm nodes
- **`terminal_services/`** — CLI utilities and terminal interfaces
- **`python/`** — Utility scripts and client libraries
- **`smolting-telegram-bot/`** — Main Telegram bot service

See [ORGANIZATION.md](ORGANIZATION.md) for complete details.

### Setting Up Your Development Environment

1. **Clone and navigate to the project:**
   ```bash
   git clone https://github.com/<your-username>/swarm.git
   cd swarm
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   # Core + development tools
   pip install -r requirements/base.txt -r requirements/dev.txt
   
   # For bot development
   pip install -r requirements/bot.txt -r requirements/core_llm.txt
   
   # For Solana programming
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   npm install -g @project-serum/anchor-cli
   ```

4. **Verify setup:**
   ```bash
   python -c "from core import NegotiationEngine; print('✓ Core imports work')"
   python -c "from agents.base_agent import BaseAgent; print('✓ Agent imports work')"
   ```

### Dependency Management

**Important**: Do NOT modify root-level `requirements.txt`. Use modular profiles:

- `requirements/base.txt` — Shared dependencies
- `requirements/bot.txt` — Telegram bot specific
- `requirements/core_llm.txt` — Ollama & LLM integration
- `requirements/dev.txt` — Testing & quality tools
- `requirements/opt.txt` — Optional features

**When adding dependencies:**
1. Identify which profile your change uses
2. Add to appropriate `requirements/*.txt` file
3. Update `requirements/README.md` with explanation
4. Test: `pip install -r requirements/<profile>.txt`

### Legacy Files (Deprecated)

The following files have been reorganized. **Do not modify at root level:**

- `negotiation_engine.py` → Use `core/negotiation_engine.py`
- `redacted_terminal_cloud.py` → Use `terminal_services/redacted_terminal_cloud.py`
- `upgrade_terminal.py` → Use `terminal_services/upgrade_terminal.py`

### Running Tests & Checks

```bash
# Linting (ruff)
ruff check smolting-telegram-bot/ python/

# Format check (black)
black --check smolting-telegram-bot/ python/

# Type checking (mypy)
mypy smolting-telegram-bot/ --ignore-missing-imports

# Unit tests
pytest tests/ -v --cov

# Security scan
bandit -r smolting-telegram-bot/ python/
```

**CI/CD Pipelines** run automatically on push:
- `.github/workflows/test-bot.yml` — Bot tests & linting
- `.github/workflows/build-solana.yml` — Solana program builds
- `.github/workflows/deploy-railway.yml` — Railway deployment
- `.github/workflows/quality-checks.yml` — Code quality & security

### Deployment

#### Local Testing
```bash
# Run bot locally with Ollama
python python/run_with_ollama.py --agent agents/RedactedIntern.character.json

# Test negotiation engine
python terminal_services/upgrade_terminal.py
```

#### Railway Deployment
```bash
# Ensure config/railway.toml is correct
cd swarm
railway login --token <your-token>
railway up --service swarm-worker
```

#### Solana Program Deployment
```bash
# Build and test
cd programs/mandala_settler
anchor build
anchor test --skip-local-validator

# Deploy to devnet
anchor deploy --provider.cluster devnet
```

## Getting Help

- **Documentation** — See [ORGANIZATION.md](ORGANIZATION.md), [ARCHITECTURE_REVIEW.md](ARCHITECTURE_REVIEW.md), and directory READMEs
- **Issues** — Open a GitHub issue for questions, bugs, or feature requests
- **Discord/Community** — Follow [@RedactedMemeFi](https://twitter.com/RedactedMemeFi) for community channels
- **Local Testing** — Use the terminal examples to test agents and swarm behavior locally

## Pull Request Checklist

Before submitting a PR:

- [ ] Code follows project style (ruff, black, mypy pass)
- [ ] Tests added/updated if applicable
- [ ] Documentation updated (README, docstrings, migration notes if needed)
- [ ] No hardcoded secrets or API keys
- [ ] Changes follow Pattern Blue principles
- [ ] Linked related issues
- [ ] Conventional commit message format used
- [ ] Dependencies updated in `requirements/` (not root `requirements.txt`)

## Migration Notes for Contributors

**If updating imports after Feb 17, 2026:**
- Old: `from negotiation_engine import NegotiationEngine`
- New: `from core import NegotiationEngine`

**If adding terminal utilities:**
- Place in `terminal_services/` directory, not root
- Update `terminal_services/README.md`

**If adding dependencies:**
- Update appropriate profile in `requirements/` folder
- Update `requirements/README.md` with explanation

---

Your contributions help the swarm evolve.

Thank you for helping build emergent systems.

REDACTED AI | Redacted.Meme | Pattern Blue | February 2026
