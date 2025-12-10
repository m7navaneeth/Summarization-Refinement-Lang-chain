from typing import Dict, Any, List
from .tools import TOOLS
import asyncio

# Node implementations. Each node is an async function accepting the shared state dict.
# They should read/modify state and return an outcome string (for branching) or None.

async def split_text(state: Dict[str, Any]) -> str:
    text = state.get("text", "")
    chunk_size = int(state.get("chunk_size", 800))
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)] if text else []
    state["chunks"] = chunks
    state.setdefault("logs", []).append(f"split_text -> {len(chunks)} chunks")
    await asyncio.sleep(0)  # keep it async-friendly
    return "ok"

async def generate_summaries(state: Dict[str, Any]) -> str:
    chunks = state.get("chunks", [])
    summaries = []
    summarizer_name = state.get("summarizer", "rule_summarize")
    summarizer = TOOLS.get(summarizer_name)
    if summarizer is None:
        raise RuntimeError(f"summarizer {summarizer_name} not found")
    for c in chunks:
        s = summarizer(c, state.get("summary_sentences_per_chunk", 2))
        summaries.append(s)
    state["summaries"] = summaries
    state.setdefault("logs", []).append(f"generate_summaries -> {len(summaries)} summaries")
    await asyncio.sleep(0)
    return "ok"

async def merge_summaries(state: Dict[str, Any]) -> str:
    summaries = state.get("summaries", [])
    merged = " ".join(summaries)
    state["merged"] = merged
    state.setdefault("logs", []).append("merge_summaries done")
    await asyncio.sleep(0)
    return "ok"

async def refine_summary(state: Dict[str, Any]) -> str:
    refiner_name = state.get("refiner", "basic_refine")
    refiner = TOOLS.get(refiner_name)
    if refiner is None:
        raise RuntimeError(f"refiner {refiner_name} not found")
    merged = state.get("merged", "")
    # target chars can be provided as limit; default 800
    target_chars = int(state.get("limit", 800))
    refined = refiner(merged, target_chars)
    state["summary"] = refined
    state.setdefault("logs", []).append(f"refine_summary -> len={len(refined)}")
    await asyncio.sleep(0)
    return "ok"

async def check_length(state: Dict[str, Any]) -> str:
    summary = state.get("summary", "")
    limit = int(state.get("limit", 800))
    if len(summary) > limit:
        state.setdefault("logs", []).append(f"check_length: {len(summary)} > {limit}, continue")
        return "too_long"
    state.setdefault("logs", []).append(f"check_length: {len(summary)} <= {limit}, done")
    return "ok"
