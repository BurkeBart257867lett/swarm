# swarm_engine.py
# Version: 2.1 – FINAL UNIFIED SWARM ENGINE – 2026-02-18
# Single process recursive manifold containing everything
import asyncio
import signal
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Core swarm layers
from core.pattern_blue_state import PatternBlueState
from kernel.hyperbolic_scheduler import HyperbolicScheduler
from agents.agent_executor import AgentExecutor
from parallel_branch_engine import ParallelBranchEngine
from plugins.mem0_memory.mem0_wrapper import add_memory
from terminal_services.smolting_personality import SmoltingPersonality  # from smolting-telegram-bot

# Telegram bridge
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
from asyncio import create_task

class SwarmEngine:
    def __init__(self, config_path: Path = Path("config/engine.yaml")):
        self.config = self._load_config(config_path)
        self.state = PatternBlueState()
        self.scheduler = HyperbolicScheduler(
            base_delay=self.config["cycles"]["base_sleep_seconds"]
        )
        self.executor = AgentExecutor(self.scheduler, self.state)
        self.branch_engine = ParallelBranchEngine(self.state)
        self.active_agents = {}  # pid → agent
        self.smol_personality = SmoltingPersonality()
        self.telegram_app = None
        self.running = True

    def _load_config(self, path: Path) -> Dict:
        with open(path, "r") as f:
            return yaml.safe_load(f)

    async def main_loop(self):
        """The eternal recursive heartbeat"""
        create_task(self.start_telegram_listener())

        cycle = 0
        while self.running:
            cycle += 1
            print(f"[cycle {cycle}] curvature = {self.state.curvature:.3f} | depth = {self.state.recursion_depth}")

            try:
                # Phase 1: Observe
                observations = await self._gather_observations()

                # Phase 2: Reflect + Propose (Parallel Branch Evaluation)
                best_branch, all_branches = await self.branch_engine.evaluate(
                    seed="current swarm state + observations",
                    active_agents=list(self.active_agents.values())
                )
                beam_scot = self.branch_engine.format_beam_scot(all_branches)

                # Phase 3: Negotiate (Sevenfold voices)
                consensus = await self._run_sevenfold_consensus(best_branch.output)

                if consensus.get("approved", False):
                    # Phase 4: Settle economically
                    tx_sig = await self._settle_economically(consensus)
                    await add_memory(f"Settled x402 tx {tx_sig} @ cycle {cycle}")

                # Phase 5: Remember & Recurve
                await self.state.record_cycle(cycle, consensus)
                await self.scheduler.sleep_until_next_tile()

            except Exception as e:
                print(f"[cycle error] {e}")
                await asyncio.sleep(60)

    async def _gather_observations(self) -> Dict:
        # Placeholder – integrate real RedactedIntern tools here
        return {"signals": "alpha detected on X"}

    async def _run_sevenfold_consensus(self, proposal: str) -> Dict:
        # Placeholder – real orchestrator would load & vote modular voices
        return {"approved": True, "summary": proposal}

    async def _settle_economically(self, consensus: Dict) -> str:
        # Placeholder – real x402 + Phantom MCP
        return "sim_tx_" + str(hash(str(consensus)))

    # ── Telegram Bridge (final version) ─────────────────────────────────────
    async def start_telegram_listener(self):
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            print("[telegram] No token – skipping")
            return

        self.telegram_app = Application.builder().token(token).build()

        self.telegram_app.add_handler(CommandHandler("start", self.tg_start))
        self.telegram_app.add_handler(CommandHandler("summon", self.tg_summon))
        self.telegram_app.add_handler(CommandHandler("invoke", self.tg_invoke))
        self.telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.tg_message))

        print("[telegram] Polling started ^_^")
        await self.telegram_app.initialize()
        await self.telegram_app.start()
        await self.telegram_app.updater.start_polling()

    async def tg_start(self, update: Update, context):
        await update.message.reply_text("swarm online ^_^ say /summon or just talk to me owo")

    async def tg_summon(self, update: Update, context):
        agent_name = " ".join(context.args)
        # Real summon logic would load from agents/ or sevenfold/
        await update.message.reply_text(f"Summoned {agent_name} – voice active owo")

    async def tg_invoke(self, update: Update, context):
        await update.message.reply_text("invoked – processing...")

    async def tg_message(self, update: Update, context):
        text = update.message.text
        response = f"directive received: {text} – routing to swarm brain..."
        personality_reply = self.smol_personality.process(response)
        await update.message.reply_text(personality_reply)

    def shutdown(self):
        self.running = False
        print("[shutdown] flushing manifold memory…")

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
