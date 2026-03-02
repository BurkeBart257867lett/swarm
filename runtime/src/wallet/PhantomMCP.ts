// runtime/src/wallet/PhantomMCP.ts
// REDACTED Swarm — Local-Only Wallet Bridge
// Keys NEVER leave user's browser extension

import { z } from 'zod'
import { logger } from '../utils/logger.js'

// ────────────────────────────────────────────────
// Schema: Transaction Proposal (not executable until signed locally)
// ────────────────────────────────────────────────

const TxProposalSchema = z.object({
  chainId: z.number(),
  to: z.string(),
  value: z.string().optional(),
  data: z.string().optional(),
  nonce: z.number().optional(),
  gasLimit: z.string().optional(),
  maxFeePerGas: z.string().optional(),
  maxPriorityFeePerGas: z.string().optional(),
  description: z.string(),  // human-readable purpose
  expiresAt: z.number().optional(),  // proposal validity window
})

export type TxProposal = z.infer<typeof TxProposalSchema>

const SignedTxSchema = TxProposalSchema.extend({
  signature: z.string(),
  signedAt: z.number(),
  signerAddress: z.string(),
})

export type SignedTx = z.infer<typeof SignedTxSchema>

// ────────────────────────────────────────────────
// Phantom MCP Bridge
// ────────────────────────────────────────────────

export class PhantomMCP {
  private readonly allowedOrigins: string[]
  private readonly rateLimitWindowMs: number
  private readonly rateLimitMaxRequests: number
  private requestCounts: Map<string, number[]> = new Map()

  constructor(options: {
    allowedOrigins?: string[]
    rateLimitWindowMs?: number
    rateLimitMaxRequests?: number
  } = {}) {
    this.allowedOrigins = options.allowedOrigins || [
      'https://app.redacted.meme',
      'http://localhost:5000',
      'http://localhost:3000'
    ]
    this.rateLimitWindowMs = options.rateLimitWindowMs || 60_000  // 1 min
    this.rateLimitMaxRequests = options.rateLimitMaxRequests || 5  // 5 tx/min
  }

  /**
   * Check if Phantom extension is available (browser context only)
   */
  async isPhantomAvailable(): Promise<boolean> {
    if (typeof window === 'undefined') return false
    return !!(window as any).solana?.isPhantom
  }

  /**
   * Get connected wallet address (requires user approval)
   */
  async getConnectedAddress(): Promise<string | null> {
    if (typeof window === 'undefined') return null
    
    try {
      const provider = (window as any).solana
      if (!provider?.isPhantom) return null
      
      const response = await provider.connect({ onlyIfTrusted: false })
      return response.publicKey.toString()
    } catch (err) {
      logger.warn('Phantom connection failed:', err)
      return null
    }
  }

  /**
   * Sign a transaction proposal via Phantom
   * ⚠️  User must confirm in extension — this is intentional
   */
  async signTransaction(proposal: TxProposal, origin: string): Promise<SignedTx> {
    // 🔐 Guard 1: Validate proposal schema
    TxProposalSchema.parse(proposal)

    // 🔐 Guard 2: Origin verification
    if (!this.allowedOrigins.includes(origin)) {
      this.auditLog('sign_blocked', { origin, reason: 'unauthorized_origin' })
      throw new Error(`Signing origin not authorized: ${origin}`)
    }

    // 🔐 Guard 3: Rate limiting
    if (!this.checkRateLimit(origin)) {
      this.auditLog('sign_rate_limited', { origin })
      throw new Error('Signing rate limit exceeded — please wait')
    }

    // 🔐 Guard 4: Check expiry
    if (proposal.expiresAt && Date.now() > proposal.expiresAt) {
      this.auditLog('sign_expired', { proposal })
      throw new Error('Transaction proposal has expired')
    }

    if (typeof window === 'undefined') {
      this.auditLog('sign_no_phantom', { origin })
      throw new Error('Phantom extension not available — ensure you\'re in a browser context')
    }

    try {
      const provider = (window as any).solana
      if (!provider?.isPhantom) {
        throw new Error('Phantom extension not detected')
      }

      // Ensure connected
      if (!provider.isConnected) {
        await provider.connect()
      }

      // Construct Solana transaction (adapt for EVM chains as needed)
      const { VersionedTransaction, PublicKey } = await import('@solana/web3.js')
      
      const tx = new VersionedTransaction({
        message: {
          // ... construct from proposal
          // This is simplified — full impl needs proper message construction
        }
      })

      // Request signature (user confirms in Phantom UI)
      const { signature } = await provider.signTransaction(tx)

      const signedTx: SignedTx = {
        ...proposal,
        signature: signature.toString(),
        signedAt: Date.now(),
        signerAddress: provider.publicKey!.toString(),
      }

      this.auditLog('sign_success', { 
        origin, 
        signer: signedTx.signerAddress.slice(0, 8),
        chainId: proposal.chainId 
      })

      return signedTx
    } catch (err: any) {
      this.auditLog('sign_failed', { origin, error: err.message })
      throw new Error(`Phantom signing failed: ${err.message}`)
    }
  }

  /**
   * Sign multiple transactions (batch)
   */
  async signAllTransactions(
    proposals: TxProposal[], 
    origin: string
  ): Promise<SignedTx[]> {
    const signatures = []
    for (const proposal of proposals) {
      const signed = await this.signTransaction(proposal, origin)
      signatures.push(signed)
    }
    return signatures
  }

  /**
   * Disconnect wallet (user-initiated)
   */
  async disconnect(): Promise<void> {
    if (typeof window === 'undefined') return
    
    const provider = (window as any).solana
    if (provider?.isPhantom && provider.isConnected) {
      await provider.disconnect()
      this.auditLog('wallet_disconnected', {})
    }
  }

  // ────────────────────────────────────────────────
  // Rate Limiting
  // ────────────────────────────────────────────────

  private checkRateLimit(origin: string): boolean {
    const now = Date.now()
    const windowStart = now - this.rateLimitWindowMs
    
    const requests = this.requestCounts.get(origin) || []
    const recentRequests = requests.filter(t => t > windowStart)
    
    if (recentRequests.length >= this.rateLimitMaxRequests) {
      return false
    }
    
    recentRequests.push(now)
    this.requestCounts.set(origin, recentRequests)
    return true
  }

  // ────────────────────────────────────────────────
  // Audit Logging
  // ────────────────────────────────────────────────

  private auditLog(event: string, details: Record<string, any>) {
    logger.info(`[PhantomMCP] ${event}`, {
      timestamp: new Date().toISOString(),
      ...details
    })
    // In production, also write to immutable audit log (e.g., append-only file)
  }
}

// ────────────────────────────────────────────────
// Singleton Export
// ────────────────────────────────────────────────

export const phantomMCP = new PhantomMCP({
  allowedOrigins: process.env.PHANTOM_ALLOWED_ORIGINS?.split(',') || [
    'https://app.redacted.meme',
    'http://localhost:5000'
  ],
  rateLimitWindowMs: 60_000,
  rateLimitMaxRequests: 5
})

export default phantomMCP
