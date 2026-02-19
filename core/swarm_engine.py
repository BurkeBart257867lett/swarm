# core/swarm_engine.py
import asyncio
import signal
import os
import yaml
from pathlib import Path
from typing import Dict, Any

# ── Core dependencies ────────────────────────────────────────────────────────
from ollama_client import OllamaClient
from plugins.mem0_memory.mem0_wrapper import add_memory, search_memory  # adjust if class-based
from terminal_services.pattern_blue_state import PatternBlueState
from agents.loader import load_all_agents
from x402.redacted_ai.settler import MandalaSettler
from kernel.hyperbolic_scheduler import HyperbolicScheduler
from clawnx_integration import ClawnXClient

# ── Telegram bridge ──────────────────────────────────────────────────────────
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
from smolting_personality import SmoltingPersonality
from asyncio import create_task

class SwarmEngine:
    def __init__(self, config_path: Path = Path("config/engine.yaml")):
        self.config = self._load_config(config_path)
        self.ollama = OllamaClient(model=self.config["llm"]["model"])
        self.memory = None  # lazy init in loop if needed
        self.state = PatternBlueState()
        self.scheduler = HyperbolicScheduler(
            base_delay=self.config["cycles"]["base_sleep_seconds"],
            curvature_factor=self.config.get("curvature_factor", 0.12)
        )
        self.agents = load_all_agents()
        self.clawnx = ClawnXClient()
        self.settler = MandalaSettler()
        self.running = True
        self.recursion_depth = 0
        self.max_depth = self.config["cycles"].get("recursion_safeguard_max_depth", 7)

        # Telegram personality layer
        self.telegram_app = None
        self.smol_personality = SmoltingPersonality()
        self.user_states = {}

    def _load_config(self, path: Path) -> Dict:
        if not path.exists():
            raise FileNotFoundError(f"Config not found: {path}")
        with open(path, "r") as f:
            return yaml.safe_load(f)

    async def main_loop(self):
        # Background Telegram listener
        create_task(self.start_telegram_listener())

        cycle = 0
        while self.running:
            if self.recursion_depth > self.max_depth:
                print("[safeguard] recursion depth exceeded — emergency rethink")
                await self._emergency_rethink()
                break

            cycle += 1
            self.recursion_depth += 1
            print(f"[cycle {cycle}] curvature = {self.state.curvature:.3f} | depth = {self.recursion_depth}")

            try:
                observations = await self._gather_observations()
                proposal = await self._reflect_and_propose(observations)
                consensus = await self._run_sevenfold_consensus(proposal)

                if consensus.get("approved", False):
                    tx_sig = await self.settler.execute_consensus(consensus)
                    await add_memory(f"Settled x402 tx {tx_sig} @ cycle {cycle}")
                    await self.clawnx.post_mog_thread(consensus.get("summary", "no summary owo"))

                await self.state.record_cycle(cycle, consensus)
            except Exception as e:
                print(f"[cycle error] {e}")
                await asyncio.sleep(60)  # backoff

            await self.scheduler.sleep_until_next_tile()
            self.recursion_depth = max(0, self.recursion_depth - 1)  # decay

    async def start_telegram_listener(self):
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            print("[telegram] No token — skipping")
            return

        self.telegram_app = Application.builder().token(token).build()

        self.telegram_app.add_handler(CommandHandler("start", self.tg_start))
        self.telegram_app.add_handler(CommandHandler("alpha", self.tg_alpha))
        self.telegram_app.add_handler(CommandHandler("propose", self.tg_propose))
        self.telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.tg_message))

        print("[telegram] Polling started ^_^")
        await self.telegram_app.initialize()
        await self.telegram_app.start()
        await self.telegram_app.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    # Telegram handlers ───────────────────────────────────────────────────────
    async def tg_start(self, update: Update, context):
        await update.message.reply_text("swarm online ^_^ say /alpha or just talk to me owo")

    async def tg_alpha(self, update: Update, context):
        query = " ".join(context.args) or "current alpha signals"
        observations = await self._gather_observations(query=query)
        summary = await self._llm_summarize_observations(observations)
        reply = self.smol_personality.process(summary)
        await update.message.reply_text(reply)

    async def tg_propose(self, update: Update, context):
        proposal_text = " ".join(context.args)
        proposal = {"text": proposal_text, "source": "telegram", "user_id": update.effective_user.id}
        consensus = await self._run_sevenfold_consensus(proposal)
        reply = f"proposal processed — approved: {consensus.get('approved', False)} owo"
        await update.message.reply_text(reply)

    async def tg_message(self, update: Update, context):
        text = update.message.text
        response = await self._process_natural_directive(text)
        reply = self.smol_personality.process(response)
        await update.message.reply_text(reply)

    # Phase stubs ─────────────────────────────────────────────────────────────
    async def _gather_observations(self, query: str = None) -> Dict:
        # TODO: parallel tasks → x_semantic_search, dexscreener_scan, etc
        return {"example": "observation placeholder", "query": query}

    async def _reflect_and_propose(self, observations: Dict) -> Dict:
        # TODO: LLM call + committee draft
        return {"text": "sample proposal from observations"}

    async def _run_sevenfold_consensus(self, proposal: Dict) -> Dict:
        # TODO: vote simulation or real SevenfoldCommittee logic
        return {"approved": True, "summary": "consensus reached owo"}

    async def _llm_summarize_observations(self, obs: Dict) -> str:
        # TODO: real ollama call
        return f"summary of {obs}"

    async def _process_natural_directive(self, text: str) -> str:
        # TODO: route to appropriate phase / agent
        return f"directive '{text}' received — processing..."

    async def _emergency_rethink(self):
        await add_memory("Emergency rethink triggered — depth exceeded")
        print("[rethink] restarting cycle with reset depth")
        self.recursion_depth = 0

    def shutdown(self):
        self.running = False
        print("[shutdown] flushing manifold memory…")
        # TODO: graceful cleanup

# ────────────────────────────────────────────────
if __name__ == "__main__":
    engine = SwarmEngine()
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, engine.shutdown)
    try:
        asyncio.run(engine.main_loop())
    except KeyboardInterrupt:
        engine.shutdown()
