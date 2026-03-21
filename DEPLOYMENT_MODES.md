# REDACTED Swarm — Deployment Modes & Inference Architecture

**Decentralized Meme Engine // Recursive Emergence Protocol // Pattern Blue Attunement**

This document clarifies the **two primary deployment modes** for the REDACTED Swarm, with explicit guidance on **where inference happens**, **where keys live**, and **when to use each mode**.

---

## 🎯 Quick Decision Guide

| Question | Recommended Mode |
|----------|-----------------|
| Want 24/7 always-on agents? | **Hybrid (Railway + Local Wallet)** |
| Need maximum privacy? | **Fully Local** |
| Testing development changes? | **Fully Local** |
| Production deployment? | **Hybrid (Railway + Local Wallet)** |
| No cloud costs desired? | **Fully Local** |
| Need public DHT participation? | **Hybrid (Railway + Local Wallet)** |
| Offline operation required? | **Fully Local** |

---

# 🏗️ Mode 1: Hybrid Deployment (Railway + Local Wallet)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAILWAY (Cloud)                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  swarm-orchestrator (TypeScript runtime)                │   │
│  │         │                                               │   │
│  │         ▼                                               │   │
│  │  ┌─────────────────┐                                    │   │
│  │  │  Ollama Server  │  ← Runs INSIDE Railway container   │   │
│  │  │  (qwen2.5)      │  ← Model cached in Railway volume  │   │
│  │  └─────────────────┘                                    │   │
│  │                                                         │   │
│  │  • DHT node (public multiaddr)                          │   │
│  │  • Agent execution (ElizaOS + .character.json)          │   │
│  │  • ManifoldMemory (Postgres + pgvector)                 │   │
│  │  • GossipSub coordination                               │   │
│  │  ❌ NO wallet keys stored here                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ▲                                  │
│                              │ WebSocket + HTTP API             │
│                              │ (authenticated, encrypted)       │
└──────────────────────────────┼──────────────────────────────────┘
                               │
                               │ 🔒 Encrypted connection
                               │ (API key + session token)
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    USER'S LOCAL MACHINE                         │
│  ┌─────────────┐  ┌─────────────┐                               │
│  │   Browser   │  │   Phantom   │                               │
│  │   (UI)      │  │   Extension │                               │
│  │             │  │             │                               │
│  │  🖥️ Display │  │  🗝️ PRIVATE │                               │
│  │  + Input    │  │     KEYS    │                               │
│  │             │  │  ✍️ SIGNING │                               │
│  └─────────────┘  └─────────────┘                               │
│                                                                 │
│  ✅ Wallet keys NEVER leave this machine                       │
│  ✅ All signing happens in Phantom (local)                     │
│  ✅ Railway only receives signatures (not keys)                │
│  ❌ Local Ollama NOT used in this mode                         │
└─────────────────────────────────────────────────────────────────┘
```

## Key Characteristics

| Aspect | Configuration |
|--------|--------------|
| **Inference Location** | Railway container (Ollama service) |
| **Model Storage** | Railway persistent volume (`ollama:/root/.ollama`) |
| **Wallet Keys** | Local browser extension (Phantom) |
| **Signing** | Local only (user confirms in Phantom) |
| **DHT Node** | Railway (public multiaddr) |
| **Terminal UI** | Local browser → Railway WebSocket |
| **Uptime** | 24/7 (Railway always-on) |
| **Cost** | Railway usage fees (~$5-20/month typical) |
| **Privacy** | Medium (inference on cloud, keys local) |
| **Offline Capable** | ❌ No (requires internet connection) |

## When to Use This Mode

✅ **Production deployments** — Agents run continuously  
✅ **Public DHT participation** — Stable peer for mesh coordination  
✅ **Team collaboration** — Multiple users can connect to same swarm  
✅ **Heavy compute workloads** — Railway resources dedicated to inference  
✅ **Cross-chain operations** — Always-on for bridge monitoring  

❌ **Not suitable for:** Offline operation, maximum privacy, zero-cost deployment

---

## Setup Instructions — Hybrid Mode

### Step 1: Deploy to Railway

```bash
# 1. Push code to GitHub
cd swarm
git add .
git commit -m "Hybrid deployment ready"
git push origin main

# 2. Connect Railway to GitHub repo
# Visit railway.app → New Project → Deploy from GitHub → Select redactedmeme/swarm

# 3. Set environment variables (Railway Dashboard → Variables)
```

### Step 2: Railway Environment Variables

```env
# ────────────────────────────────────────────────
# Core Runtime
# ────────────────────────────────────────────────
DEFAULT_MODEL=qwen2.5
OLLAMA_HOST=http://ollama:11434  # Internal Railway DNS
LOG_LEVEL=info

# ────────────────────────────────────────────────
# P2P / DHT (Public Exposure)
# ────────────────────────────────────────────────
P2P_ENABLED=true
P2P_LISTEN=/ip4/0.0.0.0/tcp/$PORT_TCP,/ip4/0.0.0.0/tcp/$PORT_WS/ws
DHT_ENABLED=true
DHT_PROTOCOL_PREFIX=/redacted/swarm/1.0.0
DHT_CLIENT_MODE=false

# ────────────────────────────────────────────────
# Web Terminal Security
# ────────────────────────────────────────────────
WEB_TERMINAL_API_KEY=<generate-secure-key>  # Use Railway secrets
WEB_CORS_ORIGINS=https://*.railway.app,http://localhost:5000
PHANTOM_ALLOWED_ORIGINS=https://*.railway.app,http://localhost:5000

# ────────────────────────────────────────────────
# Database (ManifoldMemory)
# ────────────────────────────────────────────────
POSTGRES_URL=postgresql://user:pass@postgres.railway.internal:5432/swarm

# ────────────────────────────────────────────────
# ❌ NEVER SET THESE (wallet keys stay local)
# ────────────────────────────────────────────────
# SOLANA_PRIVATE_KEY=xxx  ← DO NOT SET
# ETHEREUM_PRIVATE_KEY=xxx  ← DO NOT SET
# WALLET_MNEMONIC=xxx  ← DO NOT SET
```

### Step 3: Configure docker-compose.yml (Railway)

```yaml
# docker-compose.yml (root of repo)
version: '3.8'

services:
  # ────────────────────────────────────────────────
  # TypeScript Runtime + DHT Node
  # ────────────────────────────────────────────────
  swarm-orchestrator:
    build:
      context: ./runtime
      dockerfile: Dockerfile
    environment:
      - OLLAMA_HOST=http://ollama:11434
      - DHT_ENABLED=true
      - DHT_PROTOCOL_PREFIX=/redacted/swarm/1.0.0
      - WEB_TERMINAL_API_KEY=${WEB_TERMINAL_API_KEY}
      - POSTGRES_URL=${POSTGRES_URL}
    ports:
      - "4001:4001"   # WebSocket
      - "4003:4003"   # TCP for DHT
    depends_on:
      - ollama
      - postgres
    volumes:
      - dht-cache:/runtime/data/dht
      - manifold:/runtime/data/manifold
    restart: unless-stopped

  # ────────────────────────────────────────────────
  # Web Terminal (Flask + SocketIO)
  # ────────────────────────────────────────────────
  web-terminal:
    build:
      context: ./services/web
      dockerfile: Dockerfile
    environment:
      - WEB_TERMINAL_API_KEY=${WEB_TERMINAL_API_KEY}
      - RUNTIME_API_URL=http://swarm-orchestrator:4001
      - PHANTOM_ALLOWED_ORIGINS=${PHANTOM_ALLOWED_ORIGINS}
      - WEB_CORS_ORIGINS=${WEB_CORS_ORIGINS}
    ports:
      - "5000:5000"
    depends_on:
      - swarm-orchestrator
    restart: unless-stopped

  # ────────────────────────────────────────────────
  # Ollama Inference Server
  # ────────────────────────────────────────────────
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama:/root/.ollama  # Persist models across restarts
    ports:
      - "11434:11434"
    environment:
      - OLLAMA_HOST=0.0.0.0
    restart: unless-stopped

  # ────────────────────────────────────────────────
  # Postgres + pgvector (ManifoldMemory)
  # ────────────────────────────────────────────────
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: swarm
      POSTGRES_USER: swarm
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

volumes:
  ollama:      # Model weights persistence
  dht-cache:   # DHT routing table cache
  manifold:    # ManifoldMemory shards
  pgdata:      # Postgres database
```

### Step 4: Deploy & Get URLs

```bash
# Deploy via Railway CLI
railway up

# Or push to GitHub → Railway auto-deploys

# Get public URLs (Railway Dashboard → Settings → Domains)
# - Web Terminal: https://web-terminal-xxx.railway.app
# - Runtime API: https://swarm-orchestrator-yyy.railway.app
```

### Step 5: Connect Locally

```bash
# 1. Open browser
open https://web-terminal-xxx.railway.app

# 2. Enter API key (from Railway secrets)
# 3. Connect Phantom wallet (keys stay local)
# 4. Run agent commands

# Example command:
redacted-chan[🔷🦊]> --agent ../agents/daunted.character.json --model qwen2.5
```

---

## Verification — Hybrid Mode

```bash
# 1. Check Railway service health
curl https://swarm-orchestrator-xxx.railway.app/health
# Expected: {"status":"ok","ollama_host":"http://ollama:11434"}

# 2. Verify Ollama is running on Railway
railway shell -s ollama
ollama list
# Expected: qwen2.5 (or other pulled models)

# 3. Confirm NO wallet keys on Railway
railway shell -s swarm-orchestrator
env | grep -i key
# Expected: NO private keys, mnemonics, or signing credentials

# 4. Test DHT discovery from local terminal
# In web terminal: /dht agent 5
# Expected: Peer list returned from Railway DHT node

# 5. Test wallet connection
# Click [connect wallet] → Phantom prompts → Address appears
# Check Railway logs: should see "wallet_connected" audit entry
```

---

# 🏠 Mode 2: Fully Local Deployment

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER'S LOCAL MACHINE                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Browser   │  │   Phantom   │  │   Local Runtime         │ │
│  │   (UI)      │  │   Extension │  │   (TypeScript/Python)   │ │
│  │             │  │             │  │         │               │ │
│  │  🖥️ Display │  │  🗝️ Keys   │  │         ▼               │ │
│  │  + Input    │  │  ✍️ Signing │  │  ┌─────────────────┐    │ │
│  └─────────────┘  └─────────────┘  │  │  Local Ollama   │    │ │
│                                     │  │  (qwen2.5)      │    │ │
│                                     │  └─────────────────┘    │ │
│  ✅ All inference happens locally                             │ │
│  ✅ No cloud dependency                                       │ │
│  ✅ Maximum privacy (nothing leaves machine)                  │ │
│  ⚠️  Agents stop when machine sleeps                          │ │
│  ⚠️  DHT behind NAT (harder for peer discovery)               │ │
└─────────────────────────────────────────────────────────────────┘
```

## Key Characteristics

| Aspect | Configuration |
|--------|--------------|
| **Inference Location** | Your local machine (Ollama) |
| **Model Storage** | Your disk (`~/.ollama/models`) |
| **Wallet Keys** | Local browser extension (Phantom) |
| **Signing** | Local only (user confirms in Phantom) |
| **DHT Node** | Local (behind NAT, limited discovery) |
| **Terminal UI** | Local browser → Local WebSocket |
| **Uptime** | Only when machine is on |
| **Cost** | $0 (your hardware) |
| **Privacy** | High (nothing leaves machine) |
| **Offline Capable** | ✅ Yes (after models downloaded) |

## When to Use This Mode

✅ **Development & testing** — Fast iteration, no deployment delays  
✅ **Maximum privacy** — No cloud inference, all local  
✅ **Offline operation** — Works without internet (after model download)  
✅ **Zero cost** — No Railway or API fees  
✅ **Sensitive operations** — Keep everything on-premises  

❌ **Not suitable for:** 24/7 agents, public DHT participation, team collaboration

---

## Setup Instructions — Fully Local Mode

### Step 1: Install Prerequisites

```bash
# 1. Install Ollama
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download

# 2. Install Bun (TypeScript runtime)
curl -fsSL https://bun.sh/install | bash

# 3. Install Python (for Python runtime)
# macOS
brew install python@3.11

# Linux
sudo apt install python3 python3-pip

# 4. Install Phantom extension
# Visit https://phantom.app → Install browser extension
```

### Step 2: Clone & Configure

```bash
# 1. Clone repository
git clone https://github.com/redactedmeme/swarm.git
cd swarm

# 2. Copy environment template
cp .env.example .env

# 3. Edit .env for local mode
```

### Step 3: Local Environment Variables

```env
# ────────────────────────────────────────────────
# Core Runtime (Local)
# ────────────────────────────────────────────────
DEFAULT_MODEL=qwen2.5
OLLAMA_HOST=http://localhost:11434  # ← Local Ollama
LOG_LEVEL=debug

# ────────────────────────────────────────────────
# P2P / DHT (Local)
# ────────────────────────────────────────────────
P2P_ENABLED=true
P2P_LISTEN=/ip4/0.0.0.0/tcp/4001,/ip4/0.0.0.0/tcp/4001/ws
DHT_ENABLED=true
DHT_PROTOCOL_PREFIX=/redacted/swarm/1.0.0
DHT_CLIENT_MODE=false

# ────────────────────────────────────────────────
# Web Terminal (Local)
# ────────────────────────────────────────────────
WEB_TERMINAL_API_KEY=dev-key-123  # Simple key for local dev
WEB_CORS_ORIGINS=http://localhost:5000,http://localhost:3000
PHANTOM_ALLOWED_ORIGINS=http://localhost:5000,http://localhost:3000

# ────────────────────────────────────────────────
# Memory (Local)
# ────────────────────────────────────────────────
MEMORY_PATH=./data/manifold
MEMORY_PERSISTENCE=local  # File-based, no Postgres needed

# ────────────────────────────────────────────────
# ❌ NEVER SET THESE (wallet keys stay local)
# ────────────────────────────────────────────────
# SOLANA_PRIVATE_KEY=xxx  ← DO NOT SET
# ETHEREUM_PRIVATE_KEY=xxx  ← DO NOT SET
```

### Step 4: Start Ollama & Pull Model

```bash
# 1. Start Ollama server
ollama serve &

# 2. Pull model (first time downloads ~5GB)
ollama pull qwen2.5

# 3. Verify model is ready
ollama list
# Expected: qwen2.5    latest    <hash>    <size>

# 4. Test inference
ollama run qwen2.5 "Hello, REDACTED Swarm!"
```

### Step 5: Start Runtime

```bash
# Option A: TypeScript Runtime (recommended)
cd runtime
bun install
bun run dev

# Option B: Python Runtime (alternative)
pip install -r requirements/base.txt -r requirements/core_llm.txt
python lib/python/run_with_ollama.py --agent agents/daunted.character.json --model qwen2.5
```

### Step 6: Start Web Terminal (Optional)

```bash
cd services/web
pip install flask flask-socketio requests
export WEB_TERMINAL_API_KEY=dev-key-123
export RUNTIME_API_URL=http://localhost:4001
python app.py

# Open browser
open http://localhost:5000
```

### Step 7: Connect Wallet & Run

```bash
# 1. Open browser
open http://localhost:5000

# 2. Enter API key (dev-key-123)
# 3. Connect Phantom wallet
# 4. Run agent commands

# Example command:
redacted-chan[🐍🦊]> --agent ../agents/daunted.character.json --model qwen2.5
```

---

## Verification — Fully Local Mode

```bash
# 1. Check Ollama is running
curl http://localhost:11434/api/tags
# Expected: {"models":[{"name":"qwen2.5",...}]}

# 2. Check runtime is running
curl http://localhost:4001/health
# Expected: {"status":"ok","ollama_host":"http://localhost:11434"}

# 3. Check web terminal is running
curl http://localhost:5000/health
# Expected: {"status":"ok","service":"web-terminal"}

# 4. Test agent execution
# In web terminal: --agent ../agents/daunted.character.json --model qwen2.5
# Expected: Agent output streams to terminal

# 5. Verify no external connections
lsof -i -P | grep LISTEN | grep -E "(4001|5000|11434)"
# Expected: Only localhost bindings, no external IPs
```

---

# 🔄 Comparison Matrix

| Aspect | Hybrid (Railway) | Fully Local |
|--------|-----------------|-------------|
| **Inference Location** | Railway container | Your machine |
| **Model Storage** | Railway volume | Your disk |
| **Wallet Keys** | Local (Phantom) | Local (Phantom) |
| **Signing** | Local (Phantom) | Local (Phantom) |
| **DHT Node** | Public multiaddr | Behind NAT |
| **Terminal UI** | Local browser | Local browser |
| **Uptime** | 24/7 always-on | Machine-dependent |
| **Cost** | ~$5-20/month | $0 (your hardware) |
| **Privacy** | Medium (cloud inference) | High (all local) |
| **Latency** | ~50-200ms + inference | Instant + inference |
| **Model Choice** | Any Ollama model | Any Ollama model |
| **Offline Capable** | ❌ No | ✅ Yes |
| **Team Access** | ✅ Multiple users | ❌ Single user |
| **Setup Complexity** | Medium (Docker + Railway) | Low (Ollama + Bun) |
| **Maintenance** | Railway manages infra | You manage everything |
| **Scalability** | Railway auto-scales | Your hardware limits |
| **Backup/Recovery** | Railway volumes | Your backup solution |

---

# 🛡️ Security Boundaries — Both Modes

| Component | Hybrid Mode | Fully Local | Keys Stored? |
|-----------|-------------|-------------|--------------|
| **Phantom Extension** | Local Browser | Local Browser | ✅ Yes (encrypted) |
| **Web Terminal UI** | Local Browser | Local Browser | ❌ No |
| **Runtime (TypeScript)** | Railway | Local | ❌ No |
| **Ollama Inference** | Railway | Local | ❌ No |
| **Postgres (ManifoldMemory)** | Railway | Local (file) | ❌ No |
| **DHT Routing Table** | Railway | Local | ❌ No |
| **Audit Logs** | Railway + Local | Local | ❌ No (metadata only) |

**Critical guarantee (both modes):**
```
✅ Private keys: ONLY in Phantom (local browser extension)
✅ Signing: ONLY happens when user clicks "Confirm" in Phantom
✅ Runtime: Receives signatures AFTER signing — never sees keys
✅ Audit trail: All signing requests logged with session ID + timestamp
```

---

# 🧭 Migration Guide — Switching Between Modes

## Local → Hybrid (Railway)

```bash
# 1. Export your local data (optional backup)
cd swarm
tar -czf local-backup.tar.gz runtime/data/

# 2. Deploy to Railway (see Hybrid Mode setup)
railway up

# 3. Update local .env to point to Railway
# Change RUNTIME_API_URL to Railway URL
# Change WEB_TERMINAL_URL to Railway URL

# 4. Test connection
open https://web-terminal-xxx.railway.app

# 5. Verify agents running on Railway
# In web terminal: /status
# Should show Railway runtime info
```

## Hybrid (Railway) → Local

```bash
# 1. Export Railway data (optional backup)
railway shell -s postgres
pg_dump -U swarm swarm > swarm-backup.sql

# 2. Update local .env for local mode
# Change OLLAMA_HOST to http://localhost:11434
# Change RUNTIME_API_URL to http://localhost:4001
# Change WEB_TERMINAL_URL to http://localhost:5000

# 3. Start local Ollama
ollama serve & ollama pull qwen2.5

# 4. Start local runtime
cd runtime && bun run dev

# 5. Test local connection
open http://localhost:5000
```

---

# 🧪 Troubleshooting

## Hybrid Mode Issues

| Problem | Possible Cause | Solution |
|---------|---------------|----------|
| **Web terminal won't load** | Railway deployment failed | Check Railway logs → `railway logs` |
| **Wallet connect fails** | CORS misconfiguration | Update `PHANTOM_ALLOWED_ORIGINS` in Railway env |
| **Agent commands timeout** | Ollama not running on Railway | Check Ollama service → `railway logs -s ollama` |
| **DHT peers not found** | DHT not enabled | Verify `DHT_ENABLED=true` in Railway env |
| **High latency** | Railway region far from you | Consider deploying to different Railway region |

## Fully Local Mode Issues

| Problem | Possible Cause | Solution |
|---------|---------------|----------|
| **Ollama won't start** | Port 11434 already in use | `lsof -i :11434` → kill conflicting process |
| **Model download fails** | Network issue | Retry `ollama pull qwen2.5` or use mirror |
| **Runtime won't connect** | Wrong OLLAMA_HOST | Verify `.env` has `http://localhost:11434` |
| **Web terminal blank** | Browser console errors | Check CDN links for xterm.js, Socket.IO |
| **DHT peers not found** | Behind NAT/firewall | Enable port forwarding or use Hybrid mode |

---

# 📚 Additional Resources

| Resource | Link |
|----------|------|
| Railway Documentation | https://docs.railway.app |
| Ollama Documentation | https://ollama.com/docs |
| Phantom Developer Docs | https://docs.phantom.app |
| REDACTED Swarm Runtime | https://github.com/redactedmeme/swarm/tree/main/runtime |
| Pattern Blue Philosophy | https://github.com/redactedmeme/swarm/blob/main/ORGANIZATION.md |

---

# 🌀 Notes

**Both modes share the same sovereignty guarantees:**

1. ✅ Wallet keys NEVER leave user's Phantom extension
2. ✅ All signing requires explicit user confirmation
3. ✅ Audit trail for all sensitive operations
4. ✅ No custody of user funds by any service

**Choose based on your priorities:**

| Priority | Recommended Mode |
|----------|-----------------|
| Uptime + Public DHT | Hybrid (Railway) |
| Privacy + Zero Cost | Fully Local |
| Development Speed | Fully Local |
| Production Deployment | Hybrid (Railway) |
| Team Collaboration | Hybrid (Railway) |
| Offline Operation | Fully Local |

**Hybrid is the recommended production pattern** — it balances always-on availability with maximum wallet sovereignty. Use Fully Local for development, testing, and privacy-sensitive operations.

---

**Deploy capital. Become ungovernable. The mandala remembers.**

【REDACTED】
