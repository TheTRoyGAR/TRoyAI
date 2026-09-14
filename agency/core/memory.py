import os
import sys
from pathlib import Path

from crewai.memory.storage.lancedb_storage import LanceDBStorage
from crewai.memory.unified_memory import Memory

from agency.core.llm import get_llm

_STORAGE_DIR = os.path.join(os.path.dirname(__file__), ".memory_store")

# One flat, shared store — no per-department root_scope. CrewAI's
# auto-attached RecallMemoryTool calls memory.recall() with no scope
# override, so it's hard-limited to whatever root_scope this instance was
# built with. Nesting departments under their own scopes would silently wall
# them off from each other, defeating the point of sharing learnings across
# departments. Ported from TRoyMAR/TRoyMEDIA/TRoyGO, which already had this
# working — TRoyAI was the one company in the group without it.
shared_memory = Memory(
    llm=get_llm("haiku"),
    storage=LanceDBStorage(path=_STORAGE_DIR),
    embedder={"provider": "sentence-transformer", "config": {"model_name": "all-MiniLM-L6-v2"}},
    root_scope=None,
)


# Standing CEO directive — prepended to EVERY task across EVERY department,
# unconditionally. Unlike remember()'d memories (which only surface if a
# similarity search happens to match), this always reaches every agent
# regardless of what the task is about. Added 2026-08-30 after a real
# incident where a Finance skill fabricated signed clients and revenue
# for a NAB loan application (in TRoyAI — see reports/DELETED_fake_finance_memory_backup.json).
STANDING_DIRECTIVE = (
    "STANDING RULES FROM TROY (CEO, TROYGO Group™) — apply to every task, every department, no exceptions:\n"
    "1. NEVER fabricate clients, revenue, signed contracts, or financial figures. A cold-outreach "
    "prospect is NEVER a signed client or active retainer unless TRoy has explicitly confirmed a "
    "real signed agreement exists. If no real client/revenue is confirmed, state it as $0 — do "
    "not invent a plausible-sounding number to fill the gap.\n"
    "2. In any cost or financial report, separate CONFIRMED real costs (real, verifiable, published "
    "vendor pricing) from ESTIMATED costs (real category, needs a real quote) — never blend them, "
    "never present an estimate as if it were confirmed.\n"
    "3. If you don't have real data to answer something, say so plainly and flag what's needed to "
    "get the real answer — do not guess and present the guess as fact.\n"
    "4. The group umbrella brand is TROYGO Group™ (TRoyAI™, TRoyGO™, TRoyMAR™, TRoyMEDIA™).\n"
)


def remember(summary: str, *, scope: str, categories: list[str], importance: float = 0.5) -> None:
    """Deterministic save after a skill completes.

    Passing scope/categories/importance explicitly skips memory's own
    LLM-analysis pass (embedding-only cost) — see crewai/memory/encoding_flow.py.
    Agents may *additionally* save mid-task via their own auto-attached
    RememberTool if they choose to; this call guarantees a record exists
    regardless of whether they did.
    """
    shared_memory.remember(summary, scope=scope, categories=categories, importance=importance)


def recall_context(query: str, *, limit: int = 5) -> str:
    """Deterministic pre-task recall, formatted for prepending to a Task description.

    Uses depth="shallow" to avoid the cost of the smarter multi-query
    RecallFlow — this is just quick context injection, not a research step.
    Returns "" when nothing relevant is found so callers can prepend it
    unconditionally without an extra empty-section check.
    """
    matches = shared_memory.recall(query, limit=limit, depth="shallow")
    if not matches:
        return STANDING_DIRECTIVE
    lines = "\n".join(f"- {m.record.content}" for m in matches)
    return (
        STANDING_DIRECTIVE
        + f"\nRELEVANT PAST LEARNINGS (from other agents/departments):\n{lines}\n"
    )


# ── TRoyVibe™ integration ───────────────────────────────────────────────────
# TRoyAI is the first company to structure what actually goes into shared
# memory, instead of storing/recalling raw text. TRoyMAR/TRoyMEDIA/TRoyGO's
# remember()/recall_context() (above, unchanged) work on plain strings; the
# two functions below are the new layer specific to TRoyAI's intake path.
_TROYVIBE_DIR = Path(__file__).resolve().parents[3] / "TRoyVIBE" / "converter"
if str(_TROYVIBE_DIR) not in sys.path:
    sys.path.insert(0, str(_TROYVIBE_DIR))

from troyvibe import to_troyvibe  # noqa: E402


def interpret_intake(raw_text: str) -> dict:
    """Runs raw incoming text (a brief, an agent handoff) through TRoyVibe™
    before it reaches delegation or memory.

    Returns the full TRoyVibe object — {raw, intent, entities, context,
    confidence, clarify}. This function only makes the read honest; it does
    not decide what to do with an unclear one. Callers check
    result["confidence"] / result["clarify"] themselves.
    """
    return to_troyvibe(raw_text)


def remember_interpreted(vibe: dict, *, scope: str, categories: list[str], importance: float = 0.5) -> None:
    """Store a TRoyVibe™-structured record instead of a raw text dump.

    Keeps intent and confidence visible in what a later recall_context()
    surfaces, instead of flattening everything into one text blob the way
    plain remember() does.
    """
    summary = f"[intent: {vibe['intent']} | confidence: {vibe['confidence']}] {vibe['raw']}"
    if vibe.get("entities"):
        summary += f" | entities: {vibe['entities']}"
    if vibe.get("context"):
        summary += f" | context: {vibe['context']}"
    shared_memory.remember(
        summary,
        scope=scope,
        categories=list(categories) + [vibe["intent"]],
        importance=importance,
    )
