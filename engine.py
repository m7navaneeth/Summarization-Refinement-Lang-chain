from typing import Dict, Any, Optional
import asyncio
from .run_store import store
from . import nodes
import inspect


NODE_FUNCS = {
    "split_text": nodes.split_text,
    "generate_summaries": nodes.generate_summaries,
    "merge_summaries": nodes.merge_summaries,
    "refine_summary": nodes.refine_summary,
    "check_length": nodes.check_length,
}

async def run_graph(graph_id: str, run_id: str, stream_callback: Optional[callable] = None):
    rec = store.get_run(run_id)
    if rec is None:
        raise RuntimeError("run not found")
    graph = store.get_graph(graph_id)
    if graph is None:
        raise RuntimeError("graph not found")

    rec.status = "running"
    state = rec.state
    logs = rec.logs
    try:
       
        start = None
        
        incoming = set()
        for k, v in (graph.get("edges") or {}).items():
            if v:
                incoming.add(v)
        for n in graph.get("nodes", {}).keys():
            if n not in incoming:
                start = n
                break
        if start is None:
           
            start = list(graph.get("nodes", {}).keys())[0]
        current = start

        
        steps = 0
        MAX_STEPS = int(state.get("max_steps", 200))
        while current and steps < MAX_STEPS:
            steps += 1
            func_name = graph["nodes"].get(current)
            if func_name is None:
                rec.logs.append(f"node {current} has no associated func; stopping")
                break
            node_fn = NODE_FUNCS.get(func_name)
            if node_fn is None:
                rec.logs.append(f"function {func_name} not found; stopping")
                rec.status = "failed"
                break

            rec.logs.append(f"RUN NODE: {current} -> {func_name}")
            if stream_callback:
                await stream_callback(rec.run_id, rec.state, rec.logs[-1])

           
            result = await node_fn(rec.state)

            if graph.get("branches") and current in (graph.get("branches") or {}):
                
                branch_map = graph["branches"][current]
                next_node = branch_map.get(result)
                current = next_node
            else:
               
                current = graph.get("edges", {}).get(current)

            if stream_callback:
                await stream_callback(rec.run_id, rec.state, f"next -> {current}")
            await asyncio.sleep(0)  

        rec.status = "finished"
        rec.logs.append("finished")
    except Exception as e:
        rec.status = "failed"
        rec.logs.append(f"error: {repr(e)}")
    return rec
