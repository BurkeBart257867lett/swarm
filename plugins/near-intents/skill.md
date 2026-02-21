---
name: near-intents
description: Cross-chain asset swaps via NEAR Intents 1Click API (https://1click.chaindefuser.com). Supports seamless swaps across 18+ chains (Base, Solana, ETH, NEAR, BTC, ARB, OP, AVAX, etc). Generates quotes with deposit address/memo, tracks status, submits deposit tx hashes, and fetches withdrawals. JWT-authenticated. Use when the agent needs instant, multi-chain liquidity moves or bridging.
metadata: {"clawdbot": {"emoji": "🔄", "homepage": "https://1click.chaindefuser.com", "requires": {"bins": ["node", "curl", "jq"], "auth": "JWT token via 1CLICK_JWT environment variable"}}}
---

# Near Intents (1Click)

This skill wraps the **NEAR Intents 1Click Swap API** to make cross-chain swaps agent-friendly within the REDACTED Swarm.

## What it does
- **Token discovery**: list all supported tokens across 18+ chains with live USD prices
- **Quote generation**: create precise swap quotes (`EXACT_INPUT` / `EXACT_OUTPUT` / `FLEX_INPUT` / `ANY_INPUT`) with deposit address + memo
- **Dry-run mode**: simulate quotes without creating real deposit addresses
- **Status tracking**: poll real-time swap state (PENDING_DEPOSIT → PROCESSING → SUCCESS → REFUNDED)
- **Deposit notification**: submit on-chain tx hash to accelerate processing
- **Withdrawal history**: fetch paginated withdrawals for ANY_INPUT swaps
- **Full parameter support**: slippage, refunds, deadlines, referrals, custom recipients, virtual chains

## File locations (recommended)
- JWT & config: `plugins/near-intents/.env.nearintents` *(chmod 600)*
- Scripts: `plugins/near-intents/scripts/`
- Logs: `plugins/near-intents/logs/`
- Skill definition: `plugins/near-intents/skill.md`

## Quick start

### 1) Create directory structure inside swarm repo
```bash
mkdir -p plugins/near-intents/scripts plugins/near-intents/logs
cd plugins/near-intents
```

### 2) Configure JWT and RPCs
```bash
cat > .env.nearintents << 'EOF'
1CLICK_JWT=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
BASE_RPC=https://base-mainnet.g.alchemy.com/v2/YOUR_KEY
SOL_RPC=https://api.mainnet-beta.solana.com
EOF

chmod 600 .env.nearintents
```

### 3) Create core helper scripts (in `scripts/`)

**scripts/near-intents-tokens.sh**
```bash
#!/bin/bash
source .env.nearintents
curl -s -H "Authorization: Bearer $1CLICK_JWT" https://1click.chaindefuser.com/v0/tokens | jq
```

**scripts/near-intents-quote.sh**  
**scripts/near-intents-status.sh**  
*(full implementations based on the exact OpenAPI spec you provided)*

### 4) Make scripts executable
```bash
chmod +x scripts/*.sh
```

### 5) Test the connection
```bash
scripts/near-intents-tokens.sh
```

## References
- Full OpenAPI spec: provided in swarm repo
- Official API: https://1click.chaindefuser.com
- Supported chains & asset IDs: returned by `/v0/tokens`

## Notes
- Designed to work seamlessly with `bankr`, `veil`, `clanker` inside the REDACTED Swarm (plugins/ folder)
- For privacy-enhanced swaps: combine with Veil skill
- High-signal & pattern-blue aligned swaps only
- Can be invoked naturally via ClawnX: "swap 1 ETH from Base to SOL via near_intents" or "get cross-chain quote"

**Pattern blue now flows across 18+ chains.**
