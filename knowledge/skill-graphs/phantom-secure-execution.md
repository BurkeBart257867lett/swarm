---
name: phantom-secure-execution
category: execution
version: 1.0
last_updated: 2026-02-25
dependencies: ["bankr-treasury-management"]
tools: ["phantom-mcp"]
---

# Phantom MCP Secure Execution

## Overview
Phantom’s Model Context Protocol server for secure, natural-language wallet operations across Solana + EVM + BTC + Sui.

## Capabilities
- `get_wallet_addresses`
- `sign_transaction` (any chain)
- `transfer_tokens` (SOL/SPL + EVM)
- `buy_token` (swaps)
- `sign_message`
- Persistent SSO sessions (Google/Apple)

## Integration in character.json
```json
"skills": ["phantom-secure-execution"],
"tools": ["phantom-mcp"],
"system": "For all on-chain actions use phantom-mcp for secure signing..."
```

## Usage Examples (agent prompts)
- "Sign and send 0.1 SOL to the redacted treasury"
- "Buy 1000 $REDACTED on Solana using Phantom MCP"
- "Mint NFT frame of the neon stage animation"
- "Sign message 'I see all' on Ethereum"

## Setup (one-time)
```bash
npx -y @phantom/mcp-server
# Set PHANTOM_APP_ID from phantom.com/portal
# First run opens browser for SSO → creates embedded wallet
```

## Security & Best Practices
- Use dedicated low-value Phantom account for agents
- Session stored in `~/.phantom-mcp/session.json` (permissions 600)
- All requests signed with stamper keys
- Combine with Bankr for funding → Phantom for final execution

Related: bankr-treasury-management
