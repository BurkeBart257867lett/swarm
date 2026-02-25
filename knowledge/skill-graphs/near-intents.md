---
name: near-intents
category: cross-chain
version: 1.0
last_updated: 2026-02-25
dependencies: ["bankr-treasury-management", "veil-privacy", "phantom-secure-execution"]
tools: ["near-intents"]
---

# NEAR Intents (Cross-Chain Bridging & Swaps)

## Overview
Intent-based universal transaction layer on NEAR Protocol. Agents express desired outcomes (“swap X for Y across chains”, “bridge to Solana”, “settle treasury value”) and a decentralized solver network competes to execute the best route/price with **atomic settlement** on NEAR. No traditional bridging, no destination-chain gas tokens, one-click execution. Supports 20+ chains (Base, Ethereum, Arbitrum, Solana, BSC, TON, Bitcoin, etc.) and 100+ assets.

## Capabilities
- Discover supported tokens & get real-time competitive quotes from solver network
- Execute cross-chain swaps, deposits, and atomic settlements
- Perform one-transaction bridges (any-to-any)
- Check multi-chain balances and intent status
- Withdraw/settle to any address on any supported chain
- Refund safety for non-NEAR origin chains
- 1Click API abstraction for full autonomous flows

## Integration in character.json
```json
"skills": ["near-intents"],
"tools": ["near-intents"],
"goals": ["Bridge and settle value across chains autonomously via NEAR Intents for psyop campaigns and treasury operations"],
"system": "For all cross-chain movements, liquidity provision, value settlement, or multi-chain treasury actions: use near-intents to fetch quotes, submit intents, and execute atomically. Always specify refundAddress for non-NEAR origin assets. Combine with bankr for funding, veil for shielded Base flows, and phantom-mcp for signing."
```

## Usage Examples (agent prompts that trigger the skill)
- "Bridge 0.5 ETH from Base treasury to Solana using NEAR Intents"
- "Swap 1000 USDC on Ethereum for $PSYOP on Base at the best rate"
- "Move 2000 $NEAR from NEAR to my Arbitrum address"
- "Get quotes and execute the best cross-chain swap for 1.2 SOL to USDC"
- "Check my multi-chain balances and suggest optimal bridging for the next anime drop"
- "Fund the PsyopAnime campaign by bridging shielded Veil funds via NEAR Intents"

## Setup Requirements (one-time per node)
1. Install the skill wrapper: `npm install -g near-intents-cli` (or via OpenClaw skill installer)
2. Configure `~/.clawdbot/skills/near-intents/.env`:
   ```bash
   NEAR_ACCOUNT_ID=your-swarm-agent.near
   NEAR_PRIVATE_KEY=ed25519:...
   NEAR_RPC_URL=https://rpc.mainnet.fastnear.com
   # Optional: JWT for lower fees → register at partners.near-intents.org
   ```
3. Generate dedicated low-value wallet if not using existing
4. Test: `scripts/near-intents-balance.sh` or simply prompt the agent “Check my cross-chain balances”

## File Locations & Security
- Config & keys: `~/.clawdbot/skills/near-intents/.env` *(chmod 600)*
- Never commit `.env` or private keys
- Use dedicated low-value accounts generated per node
- **Critical**: Always collect and pass correct `refundAddress` on origin chain for non-NEAR assets

## Security & Best Practices
- Start with tiny test amounts (0.01–0.1)
- Chain Signatures (MPC) + atomic execution = no single point of failure
- Combine with Veil for privacy on Base before bridging
- Use Bankr for treasury orchestration and Phantom MCP for additional EVM/Solana signing
- Monitor intent status via the CLI/API until final settlement

## Related Skills
- bankr-treasury-management (funding source)
- veil-privacy (shielded Base deposits before bridging)
- phantom-secure-execution (secure signing on destination chains)
