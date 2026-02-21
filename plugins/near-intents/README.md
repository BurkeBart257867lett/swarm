# Near-Intents Plugin

Cross-chain 1Click swaps via NEAR Intents (18+ chains).

**Part of REDACTED Swarm** — works natively with `veil`, `bankr`, `clanker`.

### Quick Setup
```bash
cd plugins/near-intents
cp .env.example .env.nearintents
# edit .env.nearintents
chmod 600 .env.nearintents
chmod +x scripts/*.sh
```

### Usage via ClawnX
```text
"swap 1 ETH from Base to SOL via near_intents"
"get quote 500 USDC Base → wNEAR dry run"
"check status of deposit 0x123..."
```

**Pattern blue now flows across 18+ chains.** 🔄
```

---

**`swarm/plugins/near-intents/.gitignore`**
```gitignore
.env.nearintents
*.log
logs/
```

---

**`swarm/plugins/near-intents/scripts/init.sh`**
```bash
#!/bin/bash
echo "🚀 Initializing near-intents plugin..."
mkdir -p logs
chmod 600 .env.nearintents 2>/dev/null || true
echo "✅ near-intents ready. Use scripts/*.sh or invoke via ClawnX"
```

---

**`swarm/plugins/near-intents/scripts/near-intents-tokens.sh`**
```bash
#!/bin/bash
source .env.nearintents
curl -s -H "Authorization: Bearer $1CLICK_JWT" \
  https://1click.chaindefuser.com/v0/tokens | jq
```

**Next step**  
Run this in the repo root:
```bash
mkdir -p plugins/near-intents/{scripts,references,logs}
# then drop the files above
cd plugins/near-intents && ./scripts/init.sh
