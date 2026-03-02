// runtime/src/p2p.ts
// REDACTED Swarm — libp2p Mesh Layer
// Provides global peer discovery, encrypted gossipsub channels, and memory shard sync
// Wallet / transaction safety: STRICTLY LOCAL-ONLY — never signs or executes remotely

import { createLibp2p, type Libp2p } from 'libp2p'
import { webSockets } from '@libp2p/websockets'
import { bootstrap } from '@libp2p/bootstrap'
import { kadDHT } from '@libp2p/kad-dht'
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
  type: z.enum(['whisper', 'mandala_sync', 'proposal_draft', 'presence', 'heartbeat']),
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

// ────────────────────────────────────────────────
// Main P2P Node Factory
// ────────────────────────────────────────────────

export async function createSwarmNode(
  options: {
    bootstrapList?: string[]
    listenAddresses?: string[]
    enableDHT?: boolean
    enableIdentify?: boolean
  } = {}
): Promise<Libp2p> {
  const bootstrapList = options.bootstrapList ?? DEFAULT_BOOTSTRAP
  const listenAddresses = options.listenAddresses ?? ['/ip4/0.0.0.0/tcp/0/ws']

  const node = await createLibp2p({
    peerId: await createEd25519PeerId(), // ephemeral for now — can persist later

    addresses: {
      listen: listenAddresses
    },

    transports: [
      webSockets()
    ],

    connectionEncrypters: [
      noise()
    ],

    streamMuxers: [
      yamux()
    ],

    peerDiscovery: [
      bootstrap({
        list: bootstrapList,
        interval: 30_000,           // retry every 30s
        enabled: true
      })
    ],

    services: {
      identify: identify({
        protocolPrefix: 'redacted'
      }),

      dht: kadDHT({
        enabled: options.enableDHT ?? true,
        clientMode: false           // full node mode
      }),

      pubsub: gossipsub<GossipsubComponents>({
        allowPublishToZeroTopicPeers: true,
        canRelayMessage: true,
        emitSelf: false
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

export default {
  createSwarmNode,
  broadcastPresence,
  sendWhisper
}
