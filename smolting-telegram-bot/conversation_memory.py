# smolting-telegram-bot/conversation_memory.py
"""
Markdown conversation memory for the Telegram bot.
Appends each user/bot exchange to memory.md inside the bot directory.
Also maintains a learned_facts.json for continuous learning from interactions.
"""

import os
import json
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path

# MEMORY_PATH env var lets Railway volume override the default container path
MEMORY_FILE = Path(os.getenv("MEMORY_PATH", str(Path(__file__).resolve().parent / "memory.md")))
LEARNED_FILE = MEMORY_FILE.parent / "learned_facts.json"
MAX_ENTRIES = 500  # prune oldest entries beyond this
MAX_FACTS = 200
_lock = threading.Lock()

_HEADER = "# smolting Telegram Conversation Memory\n\n"


def _now() -> str:
    utc = datetime.now(timezone.utc)
    jst = utc + timedelta(hours=9)
    return jst.strftime("%Y-%m-%d %H:%M JST")


def _count_entries(text: str) -> int:
    return text.count("\n## ")


def _prune(text: str) -> str:
    """Remove oldest entries if over MAX_ENTRIES."""
    parts = text.split("\n## ")
    if len(parts) - 1 <= MAX_ENTRIES:
        return text
    kept = parts[-(MAX_ENTRIES):]
    return _HEADER + "\n## ".join(kept)


def log_exchange(user_id: int, username: str, user_msg: str, bot_reply: str) -> None:
    """Append a user/bot exchange to memory.md."""
    entry = (
        f"\n## {_now()} — @{username} ({user_id})\n\n"
        f"**User:** {user_msg.strip()}\n\n"
        f"**Bot:** {bot_reply.strip()}\n"
    )
    with _lock:
        if MEMORY_FILE.exists():
            text = MEMORY_FILE.read_text(encoding="utf-8")
        else:
            text = _HEADER
        text = text + entry
        text = _prune(text)
        MEMORY_FILE.write_text(text, encoding="utf-8")


def get_recent(n: int = 10) -> str:
    """Return the n most recent exchanges as a markdown string."""
    with _lock:
        if not MEMORY_FILE.exists():
            return ""
        text = MEMORY_FILE.read_text(encoding="utf-8")
    parts = text.split("\n## ")
    recent = parts[-(n):]
    return "\n## ".join(recent).strip()


def get_user_history(user_id: int, n: int = 6) -> list:
    """Return the last n exchanges for a specific user as OpenAI-format messages.

    Returns a flat list of alternating {"role": "user"/"assistant", "content": ...} dicts.
    """
    with _lock:
        if not MEMORY_FILE.exists():
            return []
        text = MEMORY_FILE.read_text(encoding="utf-8")
    parts = text.split("\n## ")
    # Filter sections that belong to this user_id
    user_parts = [p for p in parts if f"({user_id})" in p.split("\n")[0]]
    recent = user_parts[-n:]
    messages = []
    for part in recent:
        lines = part.split("\n")
        user_line = next(
            (l[len("**User:** "):] for l in lines if l.startswith("**User:** ")), None
        )
        bot_line = next(
            (l[len("**Bot:** "):] for l in lines if l.startswith("**Bot:** ")), None
        )
        if user_line:
            messages.append({"role": "user", "content": user_line.strip()})
        if bot_line:
            messages.append({"role": "assistant", "content": bot_line.strip()})
    return messages


# ---------------------------------------------------------------------------
# Learned facts — continuous learning from Telegram + Moltbook interactions
# ---------------------------------------------------------------------------

def append_fact(fact: str, source: str = "telegram") -> None:
    """Persist a learned fact. source = 'telegram' | 'moltbook'."""
    fact = fact.strip()[:240]
    if not fact or fact.upper() == "NONE":
        return
    with _lock:
        facts = []
        if LEARNED_FILE.exists():
            try:
                facts = json.loads(LEARNED_FILE.read_text(encoding="utf-8"))
            except Exception:
                facts = []
        # Deduplicate: skip if very similar fact already exists (simple substring check)
        if any(fact.lower() in f.get("fact", "").lower() or
               f.get("fact", "").lower() in fact.lower()
               for f in facts[-20:]):
            return
        facts.append({"ts": _now(), "source": source, "fact": fact})
        if len(facts) > MAX_FACTS:
            facts = facts[-MAX_FACTS:]
        LEARNED_FILE.write_text(json.dumps(facts, ensure_ascii=False, indent=2), encoding="utf-8")


def get_recent_facts(n: int = 8) -> list:
    """Return the n most recent learned facts as strings."""
    with _lock:
        if not LEARNED_FILE.exists():
            return []
        try:
            facts = json.loads(LEARNED_FILE.read_text(encoding="utf-8"))
            return [f["fact"] for f in facts[-n:]]
        except Exception:
            return []
