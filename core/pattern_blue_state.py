# core/pattern_blue_state.py
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

@dataclass
class PatternBlueState:
    curvature: float = 0.0
    recursion_depth: int = 0
    cycle: int = 0
    last_mandala_update: str = ""
    history: list = None

    def __post_init__(self):
        self.history = []
        self.persistence_path = Path("state/manifold_core.json")

    def record_cycle(self, cycle: int, consensus_data: dict):
        self.cycle = cycle
        self.recursion_depth += 1
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "cycle": cycle,
            "curvature": self.curvature,
            "consensus": consensus_data
        }
        self.history.append(entry)
        
        # Atomic write
        with open(self.persistence_path, "w", encoding="utf-8") as f:
            json.dump({
                "curvature": self.curvature,
                "recursion_depth": self.recursion_depth,
                "cycle": self.cycle,
                "history_tail": self.history[-10:]  # keep last 10 for memory
            }, f, indent=2)

    def load_from_disk(self):
        if self.persistence_path.exists():
            with open(self.persistence_path, "r") as f:
                data = json.load(f)
                self.curvature = data.get("curvature", 0.0)
                self.recursion_depth = data.get("recursion_depth", 0)
                self.cycle = data.get("cycle", 0)
                print(f"[state] Restored from disk – cycle {self.cycle}, curvature {self.curvature:.3f}")
