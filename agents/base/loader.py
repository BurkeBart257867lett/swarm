# agents/base/loader.py
from pathlib import Path
import json
from typing import Dict, List, Any

def load_all_agents(base_dir: Path = Path("agents")) -> List[Dict[str, Any]]:
    """
    Dynamically load all .character.json files from characters/ and nodes/ subdirectories.
    Returns list of agent configs with normalized paths/tools.
    """
    agents = []
    # Search in characters/ and nodes/ subdirectories recursively
    search_dirs = [
        base_dir / "characters",
        base_dir / "nodes"
    ]
    
    for search_dir in search_dirs:
        if search_dir.exists():
            for file_path in search_dir.rglob("*.character.json"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        config = json.load(f)
                    
                    # Normalize & enrich
                    config["file_path"] = str(file_path)
                    config["name"] = config.get("name", file_path.stem)
                    
                    # Tool registry stub – can later extract from .character.json "tools"
                    config["tools"] = config.get("tools", [])
                    
                    agents.append(config)
                    print(f"[loader] Loaded agent: {config['name']}")
                except Exception as e:
                    print(f"[loader] Failed to load {file_path}: {e}")
    
    return agents


def get_agent_by_name(agents: List[Dict], name: str) -> Dict | None:
    for agent in agents:
        if agent["name"].lower() == name.lower():
            return agent
    return None
