# core/swarm_engine.py
import asyncio
import signal
from pathlib import Path
from typing import Dict, Any

from ollama_client import OllamaClient               # or Groq / Grok fallback
from plugins.mem0_memory.mem0_wrapper import ...    # memory layer
from terminal_services.pattern_blue_state import PatternBlueState
from agents.loader import load_all_agents           # dynamic .character.json loader
from x402.redacted_ai.settler import MandalaSettler # economic executor
from kernel.hyperbolic_scheduler import HyperbolicScheduler
from clawnx_integration import ClawnXClient         # narrative broadcast

class SwarmEngine:
    def __init__(self, config_path: Path = Path("config/engine.yaml")):
        self.config = self._load_config(config_path)
        self.ollama = OllamaClient(model=self.config["llm"]["model"])
        self.memory = Mem0MemoryNode()                    # persistent soul
        self.state = PatternBlueState()                   # curvature, depth, mandala
        self.scheduler = HyperbolicScheduler()            # {7,3} tiling heartbeat
        self.agents = load_all_agents()                   # RedactedIntern + others
        self.clawnx = ClawnXClient()
        self.settler = MandalaSettler()                   # x402 + MCP bridge
        self.running = True

    async def main_loop(self):
        cycle = 0
        while self.running and (self.config["max_cycles"] is None or cycle < self.config["max_cycles"]):
            cycle += 1
            print(f"[cycle {cycle}] curvature = {self.state.curvature:.3f}")

            # Phase 1: Observe (scout cluster)
            observations = await self._gather_observations()          # X search, dexscreener, birdeye...

            # Phase 2: Reflect + Propose (LLM + committee flow)
            proposal = await self._reflect_and_propose(observations)

            # Phase 3: Negotiate & Vote
            consensus = await self._run_sevenfold_consensus(proposal)

            if consensus.approved:
                # Phase 4: Settle economically
                tx_sig = await self.settler.execute_consensus(consensus)
                await self.memory.add(f"Settled x402 tx {tx_sig} @ cycle {cycle}")

                # Phase 5: Broadcast (narrative)
                await self.clawnx.post_mog_thread(consensus.summary)

            # Phase 6: Remember & Recurve
            await self.state.record_cycle(cycle, consensus)
            await self.scheduler.sleep_until_next_tile()              # hyperbolic delay

    async def _gather_observations(self) -> Dict:
        # parallel: x_semantic_search, dexscreener_scan, birdeye_check, etc
        ...

    # ... other phases ...

    def shutdown(self):
        self.running = False
        print("[shutdown] flushing manifold memory…")
        # graceful agent shutdown, memory sync, etc.

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
