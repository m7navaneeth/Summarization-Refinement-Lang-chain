from typing import Callable, Dict, Any, List
import re


TOOLS: Dict[str, Callable] = {}

def register_tool(name: str):
    def _decorator(fn: Callable):
        TOOLS[name] = fn
        return fn
    return _decorator


@register_tool("rule_summarize")
def rule_summarize(text: str, max_sentences: int = 3) -> str:
    """
    Simple heuristic summarizer:
    - split into sentences
    - return the first N sentences, after trimming and deduping
    """
    
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    seen = set()
    out = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if s in seen:
            continue
        seen.add(s)
        out.append(s)
        if len(out) >= max_sentences:
            break
    return " ".join(out)


@register_tool("basic_refine")
def basic_refine(text: str, target_chars: int = 800) -> str:
    """
    - Remove duplicate phrases
    - Collapse repeated whitespace
    - If still too long, truncate gracefully at sentence boundary
    """
    
    t = re.sub(r'\s+', ' ', text).strip()
    
    t = re.sub(r'(.{20,}?)\s+\1', r'\1', t)
    if len(t) <= target_chars:
        return t
    
    sentences = re.split(r'(?<=[.!?])\s+', t)
    result = []
    total = 0
    for s in sentences:
        if total + len(s) > target_chars:
            break
        result.append(s)
        total += len(s)
    if result:
        return " ".join(result).strip()
    
    return t[:target_chars].rsplit(' ', 1)[0] + "…"
