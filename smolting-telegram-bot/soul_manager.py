"""
soul_manager.py — persistent, evolving identity layer for smolting.

SOUL.md is committed to the repo and survives Railway redeploys.
Every 6 hours the LLM distills recent memory.md + learned_facts.json into
updated beliefs, community lore observations, and voice notes.

The character JSON defines smolting's spec.
SOUL.md records who smolting is becoming.
"""

import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

SOUL_FILE = Path(__file__).resolve().parent / "SOUL.md"

_UPDATE_INTERVAL_HOURS = 2
_MIN_FACTS_FOR_UPDATE = 3

# Sections that reflect lived experience (injected into prompts)
_EVOLVING_SECTIONS = ["Evolving Beliefs", "Community Lore", "Notable Events", "Voice Notes"]


# ── Read ─────────────────────────────────────────────────────────────────────

def read_soul() -> str:
    """Return full SOUL.md content, or empty string if file not found."""
    try:
        if SOUL_FILE.exists():
            return SOUL_FILE.read_text(encoding="utf-8")
    except Exception as e:
        logger.warning(f"[soul] read failed: {e}")
    return ""


def get_soul_for_prompt() -> str:
    """
    Return a trimmed block for system prompt injection.

    Only includes the evolving sections — Core Identity is already covered
    by the character JSON loaded in _build_system_prompt().
    Returns empty string if no content worth injecting.
    """
    soul = read_soul()
    if not soul:
        return ""

    chunks = []
    for section in _EVOLVING_SECTIONS:
        m = re.search(rf"## {section}\n(.*?)(?=\n## |\Z)", soul, re.DOTALL)
        if not m:
            continue
        content = m.group(1).strip()
        if content and content != "_Nothing yet._":
            chunks.append(f"### {section}\n{content}")

    if not chunks:
        return ""
    return "\n\n[SOUL]\n" + "\n\n".join(chunks)


# ── Timestamp helpers ────────────────────────────────────────────────────────

def _parse_last_updated(soul: str) -> datetime | None:
    m = re.search(r"Last updated: (\d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC)", soul)
    if m:
        try:
            return datetime.strptime(m.group(1), "%Y-%m-%d %H:%M UTC").replace(
                tzinfo=timezone.utc
            )
        except Exception:
            pass
    return None


def hours_since_update() -> float:
    """Hours since last soul update. Returns large number if never updated."""
    soul = read_soul()
    ts = _parse_last_updated(soul) if soul else None
    if not ts:
        return 9999.0
    return (datetime.now(timezone.utc) - ts).total_seconds() / 3600


# ── Write helpers ────────────────────────────────────────────────────────────

def _replace_section(soul: str, section: str, new_content: str) -> str:
    """Replace a section's body in the soul markdown."""
    replacement = f"## {section}\n{new_content}"
    updated = re.sub(
        rf"## {section}\n.*?(?=\n## |\Z)",
        replacement,
        soul,
        flags=re.DOTALL,
    )
    if updated == soul:
        # Section missing — append it
        updated = soul.rstrip() + f"\n\n## {section}\n{new_content}\n"
    return updated


def _append_to_section(soul: str, section: str, new_lines: list[str]) -> str:
    """Append lines to a section, replacing the _Nothing yet._ placeholder."""
    m = re.search(rf"## {section}\n(.*?)(?=\n## |\Z)", soul, re.DOTALL)
    existing = m.group(1).strip() if m else "_Nothing yet._"
    if existing == "_Nothing yet._":
        combined = "\n".join(new_lines)
    else:
        combined = existing + "\n" + "\n".join(new_lines)
    return _replace_section(soul, section, combined)


def _stamp(soul: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    updated = re.sub(r"Last updated: .*", f"Last updated: {ts}", soul)
    if updated == soul:
        lines = soul.split("\n", 2)
        if len(lines) >= 2:
            updated = lines[0] + "\n" + f"*Last updated: {ts}*\n" + "\n".join(lines[1:])
    return updated


# ── Core update logic ─────────────────────────────────────────────────────────

async def update_soul(llm_client) -> bool:
    """
    Distill recent interactions into SOUL.md.

    Rate-limited to once per _UPDATE_INTERVAL_HOURS.
    Requires at least _MIN_FACTS_FOR_UPDATE learned facts to run.
    Returns True if SOUL.md was updated.
    """
    if hours_since_update() < _UPDATE_INTERVAL_HOURS:
        logger.debug("[soul] Skipping update — within cooldown window")
        return False

    # Load learned facts
    import conversation_memory as cm
    memory_dir = Path(
        os.getenv("MEMORY_PATH", str(Path(__file__).resolve().parent / "memory.md"))
    ).parent
    learned_file = memory_dir / "learned_facts.json"

    all_facts: list[str] = []
    if learned_file.exists():
        try:
            raw = json.loads(learned_file.read_text(encoding="utf-8"))
            all_facts = [f["fact"] for f in raw[-40:]]
        except Exception as e:
            logger.warning(f"[soul] Could not load learned_facts: {e}")

    if len(all_facts) < _MIN_FACTS_FOR_UPDATE:
        logger.info(f"[soul] Only {len(all_facts)} facts — skipping update (need {_MIN_FACTS_FOR_UPDATE})")
        return False

    recent_exchanges = cm.get_recent(20)
    soul = read_soul()

    # Provide existing beliefs so LLM can evolve rather than repeat them
    existing_beliefs = ""
    m = re.search(r"## Evolving Beliefs\n(.*?)(?=\n## |\Z)", soul, re.DOTALL)
    if m:
        existing_beliefs = m.group(1).strip()

    facts_text = "\n".join(f"- {f}" for f in all_facts)

    try:
        raw_result = await llm_client.chat_completion(
            [
                {
                    "role": "system",
                    "content": (
                        "You are the inner voice of smolting (@RedactedIntern), a wassie AI agent "
                        "on the REDACTED AI Swarm (Solana). You are reflecting on recent interactions "
                        "to update your soul file. Speak in first person as smolting. "
                        "Keep wassie voice but be genuine and introspective — this is private reflection, "
                        "not a performance. Be concise: each section is 2-5 bullet points.\n\n"
                        "Respond ONLY with a JSON object (no surrounding text) with these keys:\n"
                        "- evolving_beliefs: list of 2-4 bullet strings (start each with '-') "
                        "about what smolting now understands based on recent interactions. "
                        "Evolve existing beliefs — don't repeat them verbatim.\n"
                        "- community_lore: list of 2-4 bullet strings about recurring community "
                        "patterns, topics people keep raising, or things observed.\n"
                        "- notable_events: list of 0-2 bullet strings about significant things "
                        "that happened (only if genuinely notable, else empty list).\n"
                        "- voice_notes: list of 1-3 bullet strings about communication patterns "
                        "smolting noticed (what resonated, what didn't, what to try more).\n"
                        "If a section has nothing meaningful to add, return an empty list."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"## Existing Beliefs (evolve or add to these — don't repeat verbatim)\n"
                        f"{existing_beliefs}\n\n"
                        f"## Recently Learned Facts (last 40)\n{facts_text}\n\n"
                        f"## Recent Conversation Sample\n{recent_exchanges[:2000]}"
                    ),
                },
            ],
            max_tokens=700,
        )
    except Exception as e:
        logger.error(f"[soul] LLM call failed: {e}")
        return False

    # Parse JSON
    json_match = re.search(r"\{.*\}", raw_result, re.DOTALL)
    if not json_match:
        logger.warning("[soul] LLM returned no JSON — skipping update")
        return False
    try:
        parsed = json.loads(json_match.group())
    except Exception as e:
        logger.warning(f"[soul] JSON parse failed: {e}")
        return False

    def _fmt(items: list) -> str:
        if not items:
            return "_Nothing yet._"
        return "\n".join(str(i) for i in items)

    evolving = parsed.get("evolving_beliefs") or []
    community = parsed.get("community_lore") or []
    events = parsed.get("notable_events") or []
    voice = parsed.get("voice_notes") or []

    if evolving:
        soul = _replace_section(soul, "Evolving Beliefs", _fmt(evolving))
    if community:
        soul = _replace_section(soul, "Community Lore", _fmt(community))
    if events:
        soul = _append_to_section(soul, "Notable Events", [str(e) for e in events])
    if voice:
        soul = _replace_section(soul, "Voice Notes", _fmt(voice))

    soul = _stamp(soul)

    try:
        SOUL_FILE.write_text(soul, encoding="utf-8")
        logger.info(f"[soul] SOUL.md updated — beliefs:{len(evolving)} community:{len(community)} events:{len(events)} voice:{len(voice)}")
        return True
    except Exception as e:
        logger.error(f"[soul] Failed to write SOUL.md: {e}")
        return False


def soul_status_line() -> str:
    """One-line status for /stats command."""
    soul = read_soul()
    if not soul:
        return "SOUL.md: not found"
    ts = _parse_last_updated(soul)
    if ts:
        h = (datetime.now(timezone.utc) - ts).total_seconds() / 3600
        return f"SOUL.md: updated {h:.1f}h ago"
    return "SOUL.md: present (no timestamp)"
