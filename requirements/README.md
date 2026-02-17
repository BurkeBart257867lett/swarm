# Requirements Directory

Consolidated dependency management for the REDACTED AI Swarm.

## File Structure

### `base.txt` (REQUIRED)
Shared dependencies used across all components:
- Configuration (`python-dotenv`, `pydantic`)
- HTTP/Networking (`requests`, `aiohttp`)
- CLI/UI (`rich`, `typer`)
- YAML support

**Install**: `pip install -r requirements/base.txt`

### `bot.txt` (SMOLTING BOT)
Telegram bot-specific dependencies:
- `python-telegram-bot` - Telegram Bot API
- Cloud LLM providers (OpenAI, Groq, Anthropic)
- Solana integration for x402 payments
- Structured logging

**Install**: `pip install -r requirements/bot.txt`

### `core_llm.txt` (OLLAMA & LOCAL LLM)
Local LLM runtime dependencies:
- `ollama` - Official Ollama client
- OpenAI-compatible endpoints
- Async streaming support

**Install**: `pip install -r requirements/core_llm.txt`

### `dev.txt` (DEVELOPMENT)
Development and testing tools:
- `pytest` - Testing framework
- `black`, `ruff`, `mypy` - Code quality
- `sphinx` - Documentation
- `ipython`, `debugpy` - Debugging

**Install**: `pip install -r requirements/dev.txt`

### `opt.txt` (OPTIONAL)
Optional integrations for specific features:
- FastAPI/WebSocket for advanced web UIs
- Mem0 memory integration
- Solana/blockchain tools
- Async task queues (Celery/Redis)
- Observability (Prometheus)

**Install only what you need**: `pip install -r requirements/opt.txt`

## Usage Examples

### Core Installation (Minimal)
```bash
pip install -r requirements/base.txt
```

### Telegram Bot (Complete)
```bash
# Install bot with all dependencies
pip install -r requirements/bot.txt
pip install -r requirements/core_llm.txt  # If using local Ollama fallback
```

### Development Environment
```bash
pip install -r requirements/base.txt
pip install -r requirements/bot.txt
pip install -r requirements/core_llm.txt
pip install -r requirements/dev.txt
```

### Production Bot Deployment
```bash
# Core bot dependencies only (smaller footprint)
pip install -r requirements/bot.txt
```

### Local Testing with Ollama
```bash
pip install -r requirements/base.txt
pip install -r requirements/core_llm.txt
```

## Migration From Legacy `requirements.txt`

The original root-level `requirements.txt` has been consolidated into modular files above for easier maintenance and selective installation.

**Old**: Single monolithic file (`requirements.txt`)  
**New**: Modular approach with base + specific profiles

### If upgrading from legacy setup:
1. Install appropriate profile(s) from above
2. Legacy `requirements.txt` remains as reference (deprecated)
3. Remove legacy file once confirmed all dependencies are installed

---

**Last Updated**: February 17, 2026  
**Status**: Production-Ready | Pattern Blue Aligned
