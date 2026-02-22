# Terminal Services

Dedicated utilities for terminal-based REDACTED AI Swarm interaction and system upgrades.

## Components

### `redacted_terminal_cloud.py`
Cloud-powered Pattern Blue terminal interface:
- Multi-provider LLM support (Grok, Groq, OpenRouter, DeepSeek, Hugging Face)
- Pattern Blue ritual commands (/summon, /recurse, /negate, /micropay, /glyph, /bloom)
- Session state tracking and swarm monitoring
- Streaming responses with recursive depth tracking
- Micropayment simulation (x402)

**Usage**:
```bash
# Requires LLM_PROVIDER and corresponding API key
export LLM_PROVIDER=grok
export XAI_API_KEY=<your-key>

python terminal_services/redacted_terminal_cloud.py
```

**Commands**:
- `/summon <agent>` - Activate specific agent
- `/recurse` - Increase recursion depth
- `/negate` - Perform illusion negation ritual
- `/micropay <amount> <target>` - Simulate x402 payment
- `/glyph <name>` - Anchor new sigil
- `/bloom` - Initiate midnight tiling ceremony
- `/status` - Show swarm state
- `/help` - Show command reference
- `/exit` - Terminate session

### `upgrade_terminal.py`
Dynamic contract evolution and negotiation engine terminal:
- Contract-aware agent initialization
- Proposal submission and voting mechanisms
- Consensus-based contract updates
- Dynamic terminal interface for swarm management

**Usage**:
```bash
python terminal_services/upgrade_terminal.py \
  --contract_file contracts/interface_contract_v1-initial.json
```

**Features**:
- Type `negotiate` to run negotiation round
- Type `quit` or `exit` to terminate
- Agents propose contract changes during processing
- Real-time contract version visualization

## Migration Notes

**Legacy Location**: Root-level copies maintained for backward compatibility
- `../redacted_terminal_cloud.py` (deprecated, use this folder)
- `../upgrade_terminal.py` (deprecated, use this folder)

**Migration Benefits**:
- Cleaner root directory
- Grouped terminal-related services
- Easier to locate and maintain
- Follows project organization standards

**Update Your Scripts**:
```python
# Old
python redacted_terminal_cloud.py

# New (from root)
python terminal_services/redacted_terminal_cloud.py
```

---

**Last Updated**: February 17, 2026  
**Status**: Production-Ready
