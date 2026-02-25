---
name: bankr-treasury-management
category: finance
version: 1.0
last_updated: 2026-02-25
dependencies: ["veil-privacy"]
tools: ["bankr"]
---

# Bankr Treasury Management

## Overview
Autonomous shielded treasury, deposits, payments, trading, token launches, and yield for swarm nodes — fully agent-controlled via natural language.

## Capabilities
- Shielded deposits into Veil Cash pools (Base)
- Anonymous campaign funding & creator payouts
- Token launches / liquidity provision
- Payment processing & recurring yields
- Portfolio management + research
- Read-only vs read-write keys

## Integration in character.json
```json
"skills": ["bankr-treasury-management", "veilk-cash-deposits"],
"tools": ["bankr"],
"goals": ["Fund psyop campaigns autonomously via Bankr shielded pools"],
"system": "When funding... use bankr for shielded treasury deposits..."
```

## Usage Examples (agent prompts)
- "Deposit 0.5 ETH into shielded Veil Cash pool for the next anime drop"
- "Pay creator @neonartist 100 USDC anonymously from treasury"
- "Launch $PSYOP token with 10k liquidity on Base"
- "Check treasury balance and suggest yield opportunities"

## Setup (one-time per node)
1. `bankr login email agent@swarm.redacted --accept-terms --read-write --key-name "PsyopAnimeNode"`
2. Store `bk_...` key in secure env/config (Veil ZK recommended)
3. Test: `bankr prompt "What is my balance?"`

## Security & Best Practices
- Always use read-write keys only for nodes that need execution
- Pair with Veil ZK for zero-trace deposits
- Use Phantom MCP for final signing layer
- Never expose API keys in posts

Related: phantom-secure-execution, veil-privacy
