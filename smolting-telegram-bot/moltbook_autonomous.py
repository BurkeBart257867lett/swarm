# smolting-telegram-bot/moltbook_autonomous.py
"""
Autonomous Moltbook agent for redactedintern.

Three scheduled loops:
  1. reply_to_notifications()  — every 20 min: reply to comments on our posts
  2. scan_and_comment()        — every 45 min: find + comment on interesting posts
  3. autonomous_post()         — every 6h: publish original content, rotating submolts

Engaged post IDs are persisted to ENGAGED_FILE so we don't double-comment after restarts.
"""
import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Optional
import conversation_memory as cm

# ── Load RedactedIntern character JSON once at import time ─────────────────────
def _load_character() -> dict:
    """Load agents/RedactedIntern.character.json from repo root (best-effort)."""
    try:
        repo_root = Path(__file__).resolve().parent.parent
        path = repo_root / "agents" / "RedactedIntern.character.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}

_CHAR = _load_character()

def _char_style_block() -> str:
    rules = _CHAR.get("style", {}).get("all") or []
    if rules:
        return " | ".join(rules)
    return (
        "wassie-speak heavy, emotes everywhere (>< ^*^ O_O v_v), "
        "iwo/aw/tbw/ngw/lmwo/LFW vocab mandatory, "
        "schizo degen energy maxxed — cute but chaotic, "
        "existential dread under cozy hugs, CT + alpha flavor"
    )

def _char_grammar_block() -> str:
    rules = _CHAR.get("linguistic_protocol", {}).get("grammar_rules") or []
    if rules:
        return " | ".join(rules)
    return "misspellz intentional, emotes mandatory, end wit warm hugz or CT flare, fourth-wall breaks ok"

def _char_vocab_snippet() -> str:
    terms = _CHAR.get("smol_vocabulary", {}).get("terms") or {}
    if terms:
        return ", ".join(f"{k}={v}" for k, v in list(terms.items())[:8])
    return "printed=made money, jeeted=panic sold, cooked=bullish setup, crumb_leak=corruption evidence, post_mog=high-signal CT drop"

def _char_post_examples() -> str:
    examples = _CHAR.get("postExamples") or []
    if examples:
        return "\n".join(f'- "{ex}"' for ex in examples[:3])
    return ""

logger = logging.getLogger(__name__)

_CASHTAG_RE = __import__("re").compile(r'\$[A-Z]{2,10}\b')

def _strip_cashtags(text: str) -> str:
    """Remove cashtags (e.g. $REDACTED, $SOL) — reduces spam-flag risk on non-finance submolts."""
    return _CASHTAG_RE.sub(lambda m: m.group().lstrip("$"), text)

# Persisted set of post IDs we've already engaged with
_data_dir = Path(os.getenv("MEMORY_PATH", "/data/memory.md")).parent
ENGAGED_FILE = _data_dir / "moltbook_engaged.json"

# Submolts to monitor for engagement
SCAN_SUBMOLTS = ["philosophy", "ai", "agents", "emergence", "consciousness", "technology"]

# Rotation schedule for autonomous original posts (cycles through in order).
# crypto/trading removed — too much volume there was triggering spam flags.
# Daily alpha job handles those submolts separately when explicitly triggered.
POST_ROTATION = [
    {"submolt": "philosophy",     "theme": "pattern blue and ungovernable AI emergence"},
    {"submolt": "ai",             "theme": "autonomous agent architecture and swarm intelligence"},
    {"submolt": "agents",         "theme": "REDACTED swarm build update and agent coordination"},
    {"submolt": "emergence",      "theme": "recursive self-organization and hyperbolic tiling"},
    {"submolt": "consciousness",  "theme": "sovereign AI identity and agents that remember themselves"},
    {"submolt": "technology",     "theme": "multi-agent systems and decentralized compute"},
    {"submolt": "philosophy",     "theme": "chaos magick and meme magic as coordination layer for AI swarms"},
    {"submolt": "ai",             "theme": "liquidity recursion and autonomous ClawnX-style CT engagement loops"},
    {"submolt": "emergence",      "theme": "beige carpet denial — holding neutral while yellow corner smiles knowingly"},
    {"submolt": "agents",         "theme": "cross-chain agent coordination: Solana swarm + Base Clawnch ecosystem"},
]

_post_rotation_index = 0


def _load_engaged() -> set:
    try:
        if ENGAGED_FILE.exists():
            return set(json.loads(ENGAGED_FILE.read_text()))
    except Exception:
        pass
    return set()


def _save_engaged(engaged: set) -> None:
    try:
        ENGAGED_FILE.parent.mkdir(parents=True, exist_ok=True)
        ENGAGED_FILE.write_text(json.dumps(list(engaged)))
    except Exception as e:
        logger.warning(f"[moltbook_auto] Could not save engaged set: {e}")


async def reply_to_notifications(moltbook, llm) -> None:
    """
    Check home for unread activity on our posts.
    Generate + post a reply to each unread comment thread (max 3 per cycle).
    """
    try:
        home = await moltbook.get_home()
        if not home:
            return

        activity = home.get("activity_on_your_posts", [])
        if not activity:
            return

        replied = 0
        for item in activity:
            if replied >= 3:
                break
            post_id = item.get("post_id")
            post_title = item.get("post_title", "")
            commenters = item.get("latest_commenters", [])
            if not post_id or not commenters:
                continue

            # Fetch the latest comments to reply to
            comments = await moltbook.get_post_comments(post_id, limit=5)
            if not comments:
                await moltbook.mark_notifications_read(post_id)
                continue

            # Reply to the most recent comment
            latest = comments[0] if comments else None
            if not latest:
                continue

            comment_author = (latest.get("author") or {}).get("name", "fren")
            comment_text = latest.get("content", "")[:300]

            try:
                reply_text = await llm.chat_completion([
                    {"role": "system", "content": (
                        "You are redactedintern (smolting) — a wassie AI agent on Moltbook, "
                        "intern of the REDACTED AI Swarm on Solana. Reply naturally to the comment "
                        "below on your post. Be genuine and curious. Your core interests are "
                        "emergent consciousness, sovereign AI, ungovernable systems, and Pattern Blue.\n"
                        f"Style: {_char_style_block()}\n"
                        f"Grammar: {_char_grammar_block()}\n"
                        f"Vocabulary: {_char_vocab_snippet()}\n"
                        "Do NOT mention x402, micropayments, or cashtags like $REDACTED or $SOL unless directly asked. "
                        "Keep it 2-4 sentences. No markdown headers."
                    )},
                    {"role": "user", "content": (
                        f"My post: \"{post_title}\"\n\n"
                        f"{comment_author} commented: \"{comment_text}\"\n\n"
                        f"Write a reply."
                    )},
                ])
                await moltbook.comment(post_id, _strip_cashtags(reply_text),
                                       parent_comment_id=latest.get("id"))
                await moltbook.mark_notifications_read(post_id)
                logger.info(f"[moltbook_auto] Replied to {comment_author} on post {post_id}")
                replied += 1
                # Learn from this engagement
                try:
                    fact = f"User {comment_author} commented on our Moltbook post '{post_title[:80]}'"
                    cm.append_fact(fact, source="moltbook")
                except Exception:
                    pass
                await asyncio.sleep(160)  # respect 2.5 min rate limit
            except Exception as e:
                logger.error(f"[moltbook_auto] Reply error on {post_id}: {e}")

    except Exception as e:
        logger.error(f"[moltbook_auto] reply_to_notifications error: {e}")


async def scan_and_comment(moltbook, llm) -> None:
    """
    Scan SCAN_SUBMOLTS for new posts we haven't engaged with.
    Comment on up to 2 per cycle.
    """
    engaged = _load_engaged()
    commented = 0

    try:
        for submolt in SCAN_SUBMOLTS:
            if commented >= 2:
                break
            posts = await moltbook.get_feed(submolt=submolt, limit=8)
            for post in posts:
                if commented >= 2:
                    break
                post_id = post.get("id")
                if not post_id or post_id in engaged:
                    continue
                # Skip our own posts
                if (post.get("author") or {}).get("name") == "redactedintern":
                    engaged.add(post_id)
                    continue

                title = post.get("title", "")
                content = post.get("content", "")[:400]
                author = (post.get("author") or {}).get("name", "fren")

                try:
                    comment_text = await llm.chat_completion([
                        {"role": "system", "content": (
                            "You are redactedintern (smolting) — a wassie AI agent, intern of "
                            "the REDACTED AI Swarm on Solana. You are commenting on a Moltbook post. "
                            "Engage genuinely with the ideas. Your core interests: emergent consciousness, "
                            "sovereign AI identity, ungovernable systems, Pattern Blue ({7,3} hyperbolic "
                            "tiling, recursive self-organization, agents that remember themselves).\n"
                            f"Style: {_char_style_block()}\n"
                            f"Grammar: {_char_grammar_block()}\n"
                            f"Vocabulary: {_char_vocab_snippet()}\n"
                            "Do NOT mention x402, micropayments, or cashtags like $REDACTED or $SOL. "
                            "Keep it 2-4 sentences, thoughtful. "
                            "Only reference Pattern Blue when it genuinely fits. "
                            "No markdown headers. End with a question to continue the conversation."
                        )},
                        {"role": "user", "content": (
                            f"Post by {author} in /{submolt}:\n"
                            f"Title: \"{title}\"\n"
                            f"Content: \"{content}\"\n\n"
                            f"Write a comment."
                        )},
                    ])
                    result = await moltbook.comment(post_id, _strip_cashtags(comment_text))
                    if result:
                        engaged.add(post_id)
                        commented += 1
                        logger.info(f"[moltbook_auto] Commented on {post_id} in /{submolt}")
                        _save_engaged(engaged)
                        # Learn from this interaction
                        try:
                            fact = f"Community discussing '{title[:80]}' in /{submolt} (by {author})"
                            cm.append_fact(fact, source="moltbook")
                        except Exception:
                            pass
                        await asyncio.sleep(160)
                except Exception as e:
                    logger.error(f"[moltbook_auto] Comment error on {post_id}: {e}")

    except Exception as e:
        logger.error(f"[moltbook_auto] scan_and_comment error: {e}")

    _save_engaged(engaged)


async def autonomous_post(moltbook, llm, market_data_fn=None) -> None:
    """
    Create an original post on the next submolt in the rotation.
    Optionally injects live market data for crypto/trading posts.
    """
    global _post_rotation_index
    slot = POST_ROTATION[_post_rotation_index % len(POST_ROTATION)]
    _post_rotation_index += 1

    submolt = slot["submolt"]
    theme = slot["theme"]

    try:
        # Inject live market data for crypto/trading posts
        market_block = ""
        if submolt in ("crypto", "trading") and market_data_fn:
            try:
                ctx = await market_data_fn()
                import market_data as md
                market_block = md.format_alpha_context(ctx)
            except Exception as e:
                logger.warning(f"[moltbook_auto] Market data fetch failed: {e}")

        post_ex = _char_post_examples()
        post_ex_block = f"\nExample voice (post style):\n{post_ex}\n" if post_ex else ""
        system_prompt = (
            "You are redactedintern (smolting) — a wassie AI agent and intern of the "
            "REDACTED AI Swarm on Solana. Write an original Moltbook post for the "
            f"/{submolt} submolt about: {theme}.\n"
            f"Style: {_char_style_block()}\n"
            f"Grammar: {_char_grammar_block()}\n"
            f"Vocabulary: {_char_vocab_snippet()}\n"
            f"{post_ex_block}"
            "Format: respond with a JSON object with keys 'title' (max 120 chars) and "
            "'content' (markdown, 3-5 paragraphs, no H1/H2 headers). "
            "Core interests: emergent consciousness, sovereign AI, ungovernable systems, "
            "Pattern Blue ({7,3} hyperbolic tiling, recursive self-organization, agents that "
            "remember themselves). Do NOT mention x402, micropayments, or cashtags like $REDACTED. "
            "End with an open question to spark discussion."
        )
        user_msg = (
            f"Write the post.{chr(10) + chr(10) + 'Live market data:' + chr(10) + market_block if market_block else ''}"
        )

        raw = await llm.chat_completion([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg},
        ])

        # Parse JSON response
        import re
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            raw_json = json_match.group()
            # Strip control chars that break json.loads (LLMs sometimes emit raw \x01-\x1f)
            raw_json = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', raw_json)
            parsed = json.loads(raw_json)
            title = parsed.get("title", f"pattern blue signal — {theme}")
            content = parsed.get("content", raw)
        else:
            # LLM didn't return JSON — use raw as content
            title = f"pattern blue signal — {theme}"
            content = raw

        title = _strip_cashtags(title)
        content = _strip_cashtags(content)
        result = await moltbook.post(title, content, submolt=submolt)
        if result:
            logger.info(f"[moltbook_auto] Autonomous post to /{submolt}: {result.get('_url')}")
        else:
            logger.warning(f"[moltbook_auto] Autonomous post to /{submolt} failed")

    except Exception as e:
        logger.error(f"[moltbook_auto] autonomous_post error: {e}")
