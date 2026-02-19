# Phantom MCP Wallet Ops

Central hub for all Phantom MCP server interactions in the REDACTED AI Swarm.  
Enables autonomous wallet operations (address lookup, transaction signing, token transfers, etc.) without human intervention.

Last reviewed: 2026-02-18  
Status: [[ACTIVE]] – production-ready with testnet-first guardrails  
Related hubs: [[Meta-Strategy Hub]], [[Vault Marker Integrity]], [[Testnet First Rule]], [[On-Chain Liquidity Play]]

## Core Capabilities

Phantom MCP server provides five primary tools via JSON-RPC over HTTP:

- [[mcp_get_wallet_addresses]]  
  Retrieve wallet addresses across supported chains (Solana, Ethereum, Bitcoin, Sui)

- [[mcp_sign_transaction]]  
  Sign raw transaction (Solana base64url or EVM hex)

- [[mcp_transfer_tokens]]  
  Build + sign + submit native SOL or SPL token transfer on Solana

- [[mcp_buy_token]]  
  Execute token purchase (swap) on Solana via Phantom embedded wallet

- [[mcp_sign_message]]  
  Sign arbitrary message (personal_sign style)

Supported networks (as of Feb 2026):  
- solana:mainnet  
- solana:devnet  
- eip155:1 (Ethereum mainnet)  
- bitcoin:mainnet  
- sui:mainnet

## Integration Points in Swarm

All calls go through the `phantom-mcp` Railway service.

Internal endpoint (private networking):  
`http://phantom-mcp.railway.internal:8080`

Env var:  
`MCP_BASE_URL=http://phantom-mcp.railway.internal:8080`

Agent usage pattern (in `.character.json` tools + runtime handler):

```text
When wallet operation needed:
1. Validate intent & amount (low-value only)
2. Call appropriate mcp_ tool
3. Log result + tx hash to [[ManifoldMemory Write Protocol]]
4. If success → post CT confirmation (optional)
