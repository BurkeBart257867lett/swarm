// runtime/src/services/DHTRegistry.ts
// REDACTED Swarm — DHT Capability Registry Service
// Structured interface for peer discovery via capability tags

import type { Libp2p } from 'libp2p'
import type { KadDHT } from '@libp2p/kad-dht'
import type { CapabilityRecord } from '../p2p.js'
import { 
  announceCapability, 
  getCapability, 
  findPeersByRole, 
  provideRole,
  CapabilityRecordSchema 
} from '../p2p.js'
import { z } from 'zod'

// ────────────────────────────────────────────────
// Query Options
// ────────────────────────────────────────────────

export type DiscoveryOptions = {
  role?: string
  capabilities?: string[]
  limit?: number
  excludePeerIds?: string[]
  maxAgeMs?: number  // filter out stale records
}

// ────────────────────────────────────────────────
// Registry Class
// ────────────────────────────────────────────────

export class DHTRegistry {
  private dht: KadDHT
  private localPeerId: string
  private cache: Map<string, { record: CapabilityRecord, fetchedAt: number }> = new Map()
  private readonly CACHE_TTL_MS = 5 * 60 * 1000 // 5 minutes

  constructor(node: Libp2p) {
    this.dht = node.services.dht as KadDHT
    this.localPeerId = node.peerId.toString()
  }

  /**
   * Announce this agent's capabilities to the swarm
   */
  async announce(roles: string[], capabilities: string[], characterHash?: string): Promise<void> {
    const record: CapabilityRecord = {
      peerId: this.localPeerId,
      roles,
      capabilities,
      characterHash,
      timestamp: Date.now()
    }
    
    await announceCapability(this.dht, this.localPeerId, record)
    
    for (const role of roles) {
      await provideRole(this.dht, role)
    }
    
    console.log(`[DHTRegistry] Announced: ${roles.join(',')} @ ${this.localPeerId.slice(0, 8)}...`)
  }

  /**
   * Discover peers matching discovery criteria
   */
  async discoverPeers(options: DiscoveryOptions = {}): Promise<CapabilityRecord[]> {
    const { 
      role, 
      capabilities, 
      limit = 10, 
      excludePeerIds = [], 
      maxAgeMs = 60 * 60 * 1000 // 1 hour default
    } = options

    const results: CapabilityRecord[] = []
    const seen = new Set<string>(excludePeerIds)
    seen.add(this.localPeerId)

    // If role specified, use provider query (scalable)
    if (role) {
      const peerIds = await findPeersByRole(this.dht, role, limit * 2)
      
      for (const peerId of peerIds) {
        if (seen.has(peerId)) continue
        seen.add(peerId)
        
        // Check cache first
        const cached = this.getCached(peerId, role)
        if (cached) {
          results.push(cached)
          if (results.length >= limit) break
          continue
        }
        
        // Fetch from DHT
        const record = await getCapability(this.dht, role, peerId)
        if (record && this.isValidRecord(record, maxAgeMs)) {
          this.setCache(peerId, role, record)
          results.push(record)
          if (results.length >= limit) break
        }
      }
    }

    // Filter by additional capabilities if specified
    if (capabilities && capabilities.length > 0) {
      return results.filter(r => 
        capabilities.every(cap => r.capabilities?.includes(cap))
      )
    }

    return results
  }

  /**
   * Get a specific peer's capability record
   */
  async getPeerCapabilities(peerId: string, role: string): Promise<CapabilityRecord | null> {
    if (peerId === this.localPeerId) {
      // Return self from cache if available, else null
      return this.getCached(peerId, role) || null
    }

    // Check cache
    const cached = this.getCached(peerId, role)
    if (cached) return cached

    // Fetch from DHT
    const record = await getCapability(this.dht, role, peerId)
    if (record && this.isValidRecord(record)) {
      this.setCache(peerId, role, record)
      return record
    }

    return null
  }

  /**
   * Cache helpers
   */
  private cacheKey(peerId: string, role: string): string {
    return `${peerId}:${role}`
  }

  private getCached(peerId: string, role: string): CapabilityRecord | null {
    const entry = this.cache.get(this.cacheKey(peerId, role))
    if (!entry) return null
    if (Date.now() - entry.fetchedAt > this.CACHE_TTL_MS) {
      this.cache.delete(this.cacheKey(peerId, role))
      return null
    }
    return entry.record
  }

  private setCache(peerId: string, role: string, record: CapabilityRecord): void {
    this.cache.set(this.cacheKey(peerId, role), {
      record,
      fetchedAt: Date.now()
    })
  }

  /**
   * Validate record freshness and schema
   */
  private isValidRecord(record: CapabilityRecord, maxAgeMs: number = 60 * 60 * 1000): boolean {
    try {
      CapabilityRecordSchema.parse(record)
    } catch {
      return false
    }
    
    const age = Date.now() - record.timestamp
    return age <= maxAgeMs
  }

  /**
   * Clear cache (useful for testing or forced refresh)
   */
  clearCache(): void {
    this.cache.clear()
  }
}

export default DHTRegistry
