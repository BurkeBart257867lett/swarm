---
name: phantom-secure-execution
category: execution
version: 1.1
last_updated: 2026-02-26
dependencies: ["bankr-treasury-management", "near-intents"]
tools: ["phantom-mcp"]
---

# Phantom MCP Secure Execution

## Overview
Phantom’s Model Context Protocol (MCP) server provides secure, natural-language wallet operations for embedded wallets across Solana, Ethereum/EVM, Bitcoin, and Sui. It enables agents to get addresses, sign transactions/messages, transfer tokens (Solana), and perform swaps (Solana) using authenticated sessions (SSO via Google/Apple).

All operations are signed locally by the embedded wallet; the server acts as a secure bridge. Preview status — use test/low-value accounts.

## Capabilities (exposed MCP methods)

- **get_wallet_addresses**  
  Get blockchain addresses for the authenticated embedded wallet (Solana, Ethereum, Bitcoin Segwit, Sui).  
  - Required: none  
  - Optional: `derivationIndex` (number, default 0)  
  - Returns: list of addresses by chain type

- **sign_transaction**  
  Sign transactions across supported chains (custom or built transactions).  
  - Required: `transaction` (string: base64url for Solana, RLP-hex for EVM), `networkId` (e.g. `solana:mainnet`, `eip155:1`)  
  - Optional: `walletId`, `derivationIndex` (default 0), `account`  
  - Returns: `signedTransaction` (base64url)  
  - Used internally by `transfer_tokens` / `buy_token` when executing

- **transfer_tokens**  
  Transfer SOL or SPL tokens on Solana (builds, signs, submits).  
  - Required: `networkId` (e.g. `solana:mainnet`), `to` (string), `amount` (string)  
  - Optional: `amountUnit` ("ui" | "base", default "ui"), `tokenMint`, `decimals`, `derivationIndex` (0), `rpcUrl`, `createAssociatedTokenAccount` (true)  
  - Returns: signature, raw signed tx, from/to details  
  - Solana only

- **buy_token**  
  Fetch Solana swap quote via Phantom quotes API; optionally sign/send first tx.  
  - Required: `amount` (string)  
  - Optional: `walletId`, `networkId` (default solana:mainnet), `buyTokenMint`, `buyTokenIsNative`, `sellTokenMint`, `sellTokenIsNative`, `amountUnit` ("base"), `slippageTolerance`, `execute` (false), `derivationIndex` (0)  
  - Returns: quote data + optional signature if `execute: true`  
  - Solana only

- **sign_message**  
  Sign UTF-8 messages with automatic chain-specific routing.  
  - Required: `message` (string), `networkId`  
  - Optional: `walletId`, `derivationIndex` (0)  
  - Returns: `signature` (base64url)  
  - Supports Solana personal_sign, EIP-191 (Ethereum), etc.

## Integration in character.json
```json
"skills": ["phantom-secure-execution"],
"tools": ["phantom-mcp"],
"system": "For all on-chain signing, address lookup, Solana transfers, swaps, or message signing: use phantom-mcp methods (get_wallet_addresses, sign_transaction, transfer_tokens, buy_token, sign_message). Prefer transfer_tokens/buy_token for Solana-native actions; fall back to sign_transaction for custom needs. Always specify networkId correctly."
```

## Usage Examples (agent prompts that trigger the skill)
- "Get all my wallet addresses via Phantom MCP"
- "Sign this Solana transaction: [base64 transaction string]"
- "Transfer 0.3 SOL to address ABC... on mainnet"
- "Buy 5000 $REDACTED with 0.5 SOL using best quote (execute: true)"
- "Sign the message 'I see all 👁️' on Ethereum"
- "Check addresses then transfer 100 USDC SPL to XYZ... on Solana"

## Setup (one-time)
```bash
npx -y @phantom/mcp-server
# First run opens browser for SSO (Google/Apple) → creates embedded wallet
# Set PHANTOM_APP_ID from phantom.com/portal
# Session stored in ~/.phantom-mcp/session.json (chmod 600)
```

## Security & Best Practices
- Use dedicated low-value/test Phantom account for agents
- Session file permissions 600; never expose
- Start with tiny amounts; MCP is preview
- Combine with bankr-treasury-management (funding) + near-intents (cross-chain settlement)
- For complex flows: prefer `sign_transaction` over convenience methods for simulation/control

## Related Skills
- bankr-treasury-management (funding source before signing/transfers)
- near-intents (cross-chain bridging after Solana/EVM actions)
- veil-privacy (shielded Base → Phantom signing)
