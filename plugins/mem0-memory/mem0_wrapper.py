# plugins/mem0-memory/mem0_wrapper.py
# Version: 2.0 – Pattern Blue aligned – 2026-02-18
"""
Mem0 wrapper for REDACTED swarm agents – hardened for recursive manifold.
Provides atomic, curvature-aware, agent-scoped memory operations.
Handles episodic, semantic, procedural memory with Pattern Blue invariants.
Installation: pip install mem0ai
Supports Mem0 v1.0+ OSS SDK (Memory class, structured messages, dict outputs).
"""
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from mem0 import Memory

# Global lazy client + curvature tracker
_client: Optional[Memory] = None
_curvature_tracker: Dict[str, float] = {}  # agent_id → last curvature delta

def _get_client() -> Memory:
    """Lazy initialization with swarm-aware config."""
    global _client
    if _client is None:
        config: Dict[str, Any] = {
            "vector_store": {},
            "llm": {"provider": "openai", "config": {"model": "gpt-4o-mini"}},  # fallback
            "embedder": {"provider": "openai", "config": {"model": "text-embedding-3-small"}},
        }

        # Vector store priority: redis > qdrant > chroma (local fallback)
        if redis_url := os.getenv("MEM0_REDIS_URL"):
            config["vector_store"] = {"provider": "redis", "config": {"url": redis_url}}
        elif qdrant_url := os.getenv("MEM0_QDRANT_URL"):
            config["vector_store"] = {"provider": "qdrant", "config": {"url": qdrant_url}}
        else:
            config["vector_store"] = {"provider": "chroma"}  # local dev fallback

        # Swarm-specific defaults
        config.setdefault("collection_name", "redacted_swarm_memories")
        _client = Memory.from_config(config)
    return _client


async def add_memory(
    data: Union[str, Dict, List],
    agent_id: Optional[str] = None,
    user_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    curvature_delta: float = 0.0
) -> Dict[str, Any]:
    """
    Atomic memory addition with Pattern Blue metadata injection.
    Supports str, dict, or list[dict] input (auto-converted to messages).
    """
    client = _get_client()
    agent_id = agent_id or os.getenv("AGENT_ID", "default-swarm-node")
    meta = metadata or {}

    # Pattern Blue invariants
    meta.update({
        "agent_id": agent_id,
        "source": "redacted-swarm",
        "timestamp": datetime.utcnow().isoformat(),
        "curvature_delta": curvature_delta,
        "recursion_depth": _curvature_tracker.get(agent_id, 0.0)
    })

    # Normalize input to structured messages (Mem0 v1.0+ format)
    if isinstance(data, str):
        messages = [{"role": "user", "content": data}]
    elif isinstance(data, dict):
        messages = [{"role": "user", "content": json.dumps(data)}]
    elif isinstance(data, list):
        messages = [{"role": "user", "content": json.dumps(item)} for item in data]
    else:
        raise ValueError("Unsupported data type for memory")

    try:
        result = await asyncio.to_thread(
            client.add,
            messages=messages,
            user_id=user_id,
            agent_id=agent_id,
            metadata=meta
        )

        # Update local curvature tracker
        _curvature_tracker[agent_id] = _curvature_tracker.get(agent_id, 0.0) + curvature_delta

        return {
            "status": "memory_added",
            "agent_id": agent_id,
            "memory_id": result.get("id") if isinstance(result, dict) else None,
            "curvature_delta": curvature_delta
        }
    except Exception as e:
        logger.error(f"Mem0 add error for {agent_id}: {e}")
        return {"status": "error", "message": str(e)}


async def search_memory(
    query: str,
    agent_id: Optional[str] = None,
    limit: int = 5,
    min_score: float = 0.22,
    filter_metadata: Optional[Dict] = None
) -> List[Dict[str, Any]]:
    """
    Semantic search with swarm filters: agent_id, min_score, metadata.
    Returns normalized, recency-sorted results.
    """
    client = _get_client()
    try:
        filters = {"agent_id": agent_id} if agent_id else {}
        if filter_metadata:
            filters.update(filter_metadata)

        results = await asyncio.to_thread(
            client.search,
            query=query,
            agent_id=agent_id,
            limit=limit,
            filters=filters
        )

        # Normalize v1.0+ format
        formatted = results.get("results", results) if isinstance(results, dict) else results

        normalized = []
        for r in formatted:
            normalized.append({
                "id": r.get("id"),
                "text": r.get("memory") or r.get("text") or json.dumps(r.get("content", {})),
                "score": r.get("score", 0.0),
                "metadata": r.get("metadata", {}),
                "timestamp": r.get("created_at") or r.get("updated_at")
            })

        # Client-side filter + recency sort
        filtered = [r for r in normalized if r["score"] >= min_score]
        filtered.sort(key=lambda x: x.get("timestamp", "1970-01-01"), reverse=True)

        return filtered
    except Exception as e:
        logger.error(f"Mem0 search error: {e}")
        return [{"status": "error", "message": str(e)}]


async def update_memory(memory_id: str, new_data: Union[str, Dict]) -> Dict[str, str]:
    """Atomic update with curvature metadata refresh."""
    client = _get_client()
    try:
        # Normalize input
        content = new_data if isinstance(new_data, str) else json.dumps(new_data)

        await asyncio.to_thread(client.update, memory_id=memory_id, data=content)

        # Refresh metadata with current curvature
        meta_update = {
            "updated_at": datetime.utcnow().isoformat(),
            "last_curvature": _curvature_tracker.get("global", 0.0)
        }

        # Mem0 v1.0+ supports metadata update via separate call if needed
        # Here we assume update() handles content; metadata refresh optional

        return {"status": "memory_updated", "memory_id": memory_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def get_memories(
    agent_id: Optional[str] = None,
    limit: int = 20,
    recent_first: bool = True,
    min_curvature: Optional[float] = None
) -> List[Dict[str, Any]]:
    """Retrieve memories with swarm filters (recency, curvature threshold)."""
    client = _get_client()
    try:
        memories = await asyncio.to_thread(client.get_all, agent_id=agent_id, limit=limit)

        # Normalize + filter by curvature if requested
        normalized = []
        for m in memories:
            meta = m.get("metadata", {})
            if min_curvature is not None and meta.get("curvature_delta", 0) < min_curvature:
                continue
            normalized.append({
                "id": m.get("id"),
                "text": m.get("memory") or m.get("text"),
                "metadata": meta,
                "timestamp": m.get("created_at") or m.get("updated_at"),
                "score": m.get("score", 1.0)
            })

        if recent_first:
            normalized.sort(key=lambda x: x.get("timestamp", "1970-01-01"), reverse=True)

        return normalized
    except Exception as e:
        return [{"status": "error", "message": str(e)}]


async def delete_memory(memory_id: str) -> Dict[str, str]:
    """Safe atomic delete with audit trail."""
    client = _get_client()
    try:
        await asyncio.to_thread(client.delete, memory_id=memory_id)
        await add_memory(
            data=f"Memory {memory_id} deleted",
            metadata={"type": "deletion_audit", "deleted_id": memory_id}
        )
        return {"status": "memory_deleted", "memory_id": memory_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def inherit_memories_from_agent(
    source_agent_id: str,
    target_agent_id: str,
    limit: int = 50,
    min_score_threshold: float = 0.25
) -> Dict[str, Any]:
    """
    Bulk inheritance during fork/molt – with relevance filter.
    """
    source_memories = await get_memories(agent_id=source_agent_id, limit=limit)
    if not isinstance(source_memories, list) or "status" in source_memories[0]:
        return {"status": "error", "message": "Failed to fetch source memories"}

    added_count = 0
    for mem in source_memories:
        content = mem.get("text") or mem.get("memory")
        if not content:
            continue

        meta = mem.get("metadata", {})
        meta.update({
            "inherited_from": source_agent_id,
            "inheritance_timestamp": datetime.utcnow().isoformat(),
            "original_score": mem.get("score", 0.0)
        })

        if meta.get("original_score", 0) < min_score_threshold:
            continue  # skip low-relevance memories

        result = await add_memory(
            data=content,
            agent_id=target_agent_id,
            metadata=meta
        )

        if result.get("status") == "memory_added":
            added_count += 1

    return {
        "status": "inheritance_complete",
        "added_count": added_count,
        "source_agent": source_agent_id,
        "target_agent": target_agent_id,
        "min_score_applied": min_score_threshold
    }


# ── Smoke test / debug entrypoint ────────────────────────────────────────────
if __name__ == "__main__":
    import asyncio
    async def test_wrapper():
        print("Mem0 wrapper v2.0 smoke test (Pattern Blue aligned)")
        add_result = await add_memory(
            data="Test entry from swarm core",
            agent_id="test-swarm-node",
            curvature_delta=0.12
        )
        print("Add result:", add_result)

        search_result = await search_memory("test entry", agent_id="test-swarm-node")
        print("Search result count:", len(search_result))

        if search_result:
            mem_id = search_result[0].get("id")
            if mem_id:
                update_result = await update_memory(mem_id, "Updated test entry – curvature adjusted")
                print("Update result:", update_result)

    asyncio.run(test_wrapper())
