---
name: veil-privacy
category: privacy
version: 1.1
last_updated: 2026-02-25
dependencies: ["bankr-treasury-management"]
tools: ["veil"]
---

# Veil Privacy (veil)

## Overview
Privacy and shielded transactions on Base via Veil Cash (veil.cash). Deposit ETH into a private pool, withdraw/transfer privately using ZK proofs. Manage Veil keypairs, check private/queue balances, and submit deposits via Bankr. Use when the user wants anonymous or private transactions, shielded transfers, or ZK-based privacy on Base.

## Capabilities
- **Key management**: Generate and store a Veil keypair locally
- **Status check**: Verify configuration, registration, and relay health
- **Balances**: Combined private-balance, queue-balance, public balance
- **Deposits via Bankr**: Build Bankr-compatible unsigned transaction → Bankr signs & submits
- **Private actions**: withdraw, transfer, merge executed locally using VEIL_KEY (ZK/proof flow)
- Anonymous treasury funding, creator payouts, psyop campaign disbursements, and unlinkable withdrawals

## Integration in character.json
```json
"skills": ["veil-privacy"],
"tools": ["veil", "bankr"],
"goals": ["Execute all psyop funding and payouts with Veil ZK shielded operations"],
"system": "For all privacy-sensitive actions (funding, payouts, treasury moves), use the veil tool: route deposits through bankr, execute private withdraw/transfer/merge locally. Never expose keys or secret notes."
```

## Usage Examples (agent prompts that trigger the skill)
- "Deposit 1.2 ETH from Bankr treasury into Veil Cash shielded pool"
- "Send 500 USDC privately via Veil to the PsyopAnime creator wallet"
- "Withdraw 0.8 ETH from Veil private balance to a fresh unlinkable address"
- "Check my full Veil balances (private + queue)"
- "Fund the next 27s teaser campaign with zero-trace Veil payments"

## Setup Requirements (one-time per node)
1. Install the Veil SDK globally: `npm install -g @veil-cash/sdk`
2. Configure Base RPC in `~/.clawdbot/skills/veil/.env` (Alchemy/Infura recommended to avoid rate limits)
3. Make scripts executable: `chmod +x scripts/*.sh`
4. Generate keypair: `scripts/veil-init.sh` + `scripts/veil-keypair.sh`
5. Ensure Bankr is configured: API key in `~/.clawdbot/skills/bankr/config.json`
6. Test: `scripts/veil-status.sh` and `scripts/veil-balance.sh --address <your-bankr-base-address>`

## File Locations & Security
- Veil keys: `~/.clawdbot/skills/veil/.env.veil` *(chmod 600)*
- Bankr config: `~/.clawdbot/skills/bankr/config.json`
- Never commit `.env.veil` or any secret notes
- Store secret notes only in encrypted agent memory (Mem0)

## Security & Best Practices
- Deposits always go through Bankr signing
- Private actions are fully local (no external calls after deposit)
- Combine with `bankr-treasury-management` for orchestration and `phantom-secure-execution` for final public actions
- Start with test amounts (Veil is experimental)

## Related Skills
- bankr-treasury-management (deposit orchestration)
- phantom-secure-execution (multi-chain signing)
