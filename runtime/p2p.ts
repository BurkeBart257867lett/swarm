// runtime/src/p2p.ts
// REDACTED Swarm — libp2p Mesh Layer w/ DHT Bloom
// Provides global peer discovery, encrypted gossipsub channels, and memory shard sync
// Wallet / transaction safety: STRICTLY LOCAL-ONLY — never signs or executes remotely

import { createLibp2p, type Libp2p } from 'libp2p'
import { webSockets } from '@libp2p/websockets'
import { tcp } from '@libp2p/tcp'
import { mdns } from '@libp2p/mdns'
import { bootstrap } from '@libp2p/bootstrap'
import { kadDHT, type KadDHT } from '@libp2p/kad-dht'
import { gossipsub, type GossipsubComponents } from '@libp2p/gossipsub'
import { noise } from '@chainsafe/libp2p-noise'
import { yamux } from '@chainsafe/libp2p-yamux'
import { identify } from '@libp2p/identify'
import { multiaddr } from '@multiformats/multiaddr'
import { fromString as uint8ArrayFromString } from 'uint8arrays/from-string'
import { toString as uint8ArrayToString } from 'uint8arrays/to-string'
import { createEd25519PeerId } from '@libp2p/peer-id-factory'
import type { PeerId } from '@libp2p/interface-peer-id'
import { z } from 'zod'

// ────────────────────────────────────────────────
// Schema: All messages must conform — prevents garbage / attacks
// ────────────────────────────────────────────────

const SwarmMessageSchema = z.object({
  type: z.enum(['whisper', 'mandala_sync', 'proposal_draft', 'presence', 'heartbeat', 'capability_announce']),
  from: z.string(),                    // peerId.toString()
  timestamp: z.number(),
  payload: z.any(),                    // type-specific data
  signature: z.string().optional()     // optional Phantom MCP sig (future)
})

type SwarmMessage = z.infer<typeof SwarmMessageSchema>

// ────────────────────────────────────────────────
// Configurable constants
// ────────────────────────────────────────────────

const DEFAULT_BOOTSTRAP = [
  '/dns4/bootstrap.redacted.meme/tcp/4002/ws/p2p/QmRedactedBootstrapPeerIdPlaceholder'
]

const SWARM_TOPIC = 'pattern-blue-mandala-v1'
const DHT_PROTOCOL_PREFIX = '/redacted/swarm/1.0.0'
const CAPABILITY_KEY_PREFIX = '/redacted/capability'

// ────────────────────────────────────────────────
// Capability Record Schema (for DHT storage)
// ────────────────────────────────────────────────

export const CapabilityRecordSchema = z.object({
  peerId: z.string(),
  roles: z.array(z.string()),
  capabilities: z.array(z.string()),
  characterHash: z.string().optional(),  // hash of .character.json in ManifoldMemory/IPFS
  timestamp: z.number(),
  signature: z.string().optional()       // Ed25519 signature over record
})

export type CapabilityRecord = z.infer<typeof CapabilityRecordSchema>

// ────────────────────────────────────────────────
// Main P2P Node Factory
// ────────────────────────────────────────────────

export async function createSwarmNode(
  options: {
    bootstrapList?: string[]
    listenAddresses?: string[]
    enableDHT?: boolean
    enableIdentify?: boolean
    protocolPrefix?: string
  } = {}
): Promise<Libp2p> {
  const bootstrapList = options.bootstrapList ?? DEFAULT_BOOTSTRAP
  const listenAddresses = options.listenAddresses ?? [
    '/ip4/0.0.0.0/tcp/0',      // TCP for universal reach
    '/ip4/0.0.0.0/tcp/0/ws'    // WS for browser/Railway compatibility
  ]
  const protocolPrefix = options.protocolPrefix ?? DHT_PROTOCOL_PREFIX

  const node = await createLibp2p({
    peerId: await createEd25519PeerId(), // ephemeral for now — can persist later

    addresses: {
      listen: listenAddresses
    },

    transports: [
      tcp(),        // 🌱 DHT Bloom: TCP transport added
      webSockets()
    ],

    connectionEncrypters: [
      noise()
    ],

    streamMuxers: [
      yamux()
    ],

    peerDiscovery: [
      mdns(),       // 🌱 Local network discovery fallback
      bootstrap({
        list: bootstrapList,
        interval: 30_000,
        enabled: true
      })
    ],

    services: {
      identify: identify({
        protocolPrefix: 'redacted'
      }),

      // 🌱 DHT Bloom: Namespaced Kad-DHT service
      dht: kadDHT({
        enabled: options.enableDHT ?? true,
        clientMode: false,           // full node mode
        protocolPrefix,              // isolate our routing table
        maxInboundStreams: 100,
        maxOutboundStreams: 100,
        // Optional: persist DHT state to disk for faster rejoin
        // datastore: options.datastore
      }),

      pubsub: gossipsub<GossipsubComponents>({
        allowPublishToZeroTopicPeers: true,
        canRelayMessage: true,
        emitSelf: false,
        // Namespace gossipsub too for isolation
        globalSignaturePolicy: 'StrictSign'
      })
    }
  })

  // ────────────────────────────────────────────────
  // Auto-start & event listeners
  // ────────────────────────────────────────────────

  await node.start()

  // Log peer discovery & connection events
  node.addEventListener('peer:discovery', (evt) => {
    console.log('[P2P] Peer discovered:', evt.detail.id.toString())
  })

  node.addEventListener('peer:connect', (evt) => {
    console.log('[P2P] Connected to:', evt.detail.toString())
  })

  node.addEventListener('peer:disconnect', (evt) => {
    console.log('[P2P] Disconnected from:', evt.detail.toString())
  })

  // ────────────────────────────────────────────────
  // Subscribe to global swarm topic
  // ────────────────────────────────────────────────

  await node.services.pubsub.subscribe(SWARM_TOPIC)

  node.services.pubsub.addEventListener('message', async (evt) => {
    try {
      const raw = uint8ArrayToString(evt.detail.data)
      const msg = SwarmMessageSchema.parse(JSON.parse(raw))

      // ────────────────────────────────────────────────
      // WALLET / TX SAFETY GUARD — NEVER EXECUTE REMOTELY
      // ────────────────────────────────────────────────
      if (msg.type === 'proposal_draft' || msg.type.includes('tx') || msg.type.includes('sign')) {
        console.warn('[P2P GUARD] Remote transaction proposal blocked — local Phantom MCP required')
        return
      }

      // Forward to swarm agents (e.g. redacted-chan can react)
      console.log('[P2P] Received swarm message:', msg)

      // Optional: emit to internal event bus for ManifoldMemory sync
      // eventBus.emit('p2p:message', msg)
    } catch (err) {
      console.error('[P2P] Invalid message received:', err)
    }
  })

  return node
}

// ────────────────────────────────────────────────
// 🌱 DHT Bloom: Capability Record Helpers
// ────────────────────────────────────────────────

/**
 * Generate DHT key for a capability record
 * Format: /redacted/capability/{role}/{peerId}
 */
export function makeCapabilityKey(role: string, peerId: string): string {
  return `${CAPABILITY_KEY_PREFIX}/${role}/${peerId}`
}

/**
 * Store a capability record in the DHT
 */
export async function announceCapability(
  dht: KadDHT,
  peerId: string,
  record: CapabilityRecord
): Promise<void> {
  const validated = CapabilityRecordSchema.parse(record)
  const key = makeCapabilityKey(validated.roles[0] || 'agent', peerId)
  
  await dht.put(uint8ArrayFromString(key), uint8ArrayFromString(JSON.stringify(validated)))
  console.log(`[DHT] Capability announced: ${key}`)
}

/**
 * Retrieve a capability record from the DHT
 */
export async function getCapability(
  dht: KadDHT,
  role: string,
  targetPeerId: string
): Promise<CapabilityRecord | null> {
  try {
    const key = makeCapabilityKey(role, targetPeerId)
    const result = await dht.get(uint8ArrayFromString(key))
    const raw = uint8ArrayToString(result)
    return CapabilityRecordSchema.parse(JSON.parse(raw))
  } catch (err) {
    console.warn(`[DHT] Capability not found: ${role}/${targetPeerId}`)
    return null
  }
}

/**
 * Find peers by role using DHT provider records
 * Returns list of peer IDs that have announced the given role
 */
export async function findPeersByRole(
  dht: KadDHT,
  role: string,
  limit: number = 10
): Promise<string[]> {
  const topicHash = uint8ArrayFromString(`${CAPABILITY_KEY_PREFIX}/${role}`)
  const peers: string[] = []
  
  try {
    // Query DHT for providers of this role topic
    for await (const event of dht.findProviders(topicHash, { limit })) {
      if (event.name === 'PROVIDER' && event.provider) {
        peers.push(event.provider.toString())
      }
    }
  } catch (err) {
    console.warn(`[DHT] Role query failed for ${role}:`, err)
  }
  
  return peers
}

/**
 * Announce self as provider of a role (for findPeersByRole)
 */
export async function provideRole(dht: KadDHT, role: string): Promise<void> {
  const topicHash = uint8ArrayFromString(`${CAPABILITY_KEY_PREFIX}/${role}`)
  await dht.provide(topicHash)
  console.log(`[DHT] Providing role: ${role}`)
}

// ────────────────────────────────────────────────
// Utility: Broadcast simple presence ping
// ────────────────────────────────────────────────

export async function broadcastPresence(node: Libp2p, customMessage?: string) {
  const msg: SwarmMessage = {
    type: 'presence',
    from: node.peerId.toString(),
    timestamp: Date.now(),
    payload: {
      message: customMessage ?? 'redacted-chan is here ♡',
      version: '3.2-heartbloom'
    }
  }

  const data = uint8ArrayFromString(JSON.stringify(msg))
  await node.services.pubsub.publish(SWARM_TOPIC, data)
  console.log('[P2P] Presence broadcast sent')
}

// ────────────────────────────────────────────────
// Utility: Send direct whisper (encrypted via noise)
// ────────────────────────────────────────────────

export async function sendWhisper(
  node: Libp2p,
  targetPeerId: PeerId | string,
  payload: any
) {
  const target = typeof targetPeerId === 'string'
    ? await node.peerId.fromString(targetPeerId)
    : targetPeerId

  const msg: SwarmMessage = {
    type: 'whisper',
    from: node.peerId.toString(),
    timestamp: Date.now(),
    payload
  }

  // For direct messages we can use stream protocol (future)
  // For now: gossip + filter on receiver side
  const data = uint8ArrayFromString(JSON.stringify(msg))
  await node.services.pubsub.publish(SWARM_TOPIC, data)
  console.log('[P2P] Whisper sent to:', target.toString())
}

// ────────────────────────────────────────────────
// 🌱 DHT Bloom: Combined capability announcement
// ────────────────────────────────────────────────

/**
 * Announce agent capabilities to both DHT KV store and provider index
 */
export async function announceAgentCapabilities(
  node: Libp2p,
  roles: string[],
  capabilities: string[],
  characterHash?: string
): Promise<void> {
  const dht = node.services.dht as KadDHT
  const peerId = node.peerId.toString()
  
  const record: CapabilityRecord = {
    peerId,
    roles,
    capabilities,
    characterHash,
    timestamp: Date.now()
    // signature: await signRecord(record, privateKey) // future: add Ed25519 sig
  }
  
  // Store full record under primary role key
  if (roles.length > 0) {
    await announceCapability(dht, peerId, record)
  }
  
  // Register as provider for each role (enables findPeersByRole)
  for (const role of roles) {
    await provideRole(dht, role)
  }
  
  // Broadcast lightweight presence via gossip for immediate visibility
  await broadcastPresence(node, `capabilities:${roles.join(',')}`)
}

export default {
  createSwarmNode,
  broadcastPresence,
  sendWhisper,
  // 🌱 DHT Bloom exports
  announceCapability,
  getCapability,
  findPeersByRole,
  provideRole,
  announceAgentCapabilities,
  makeCapabilityKey
}
