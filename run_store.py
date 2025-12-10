import uuid
import asyncio
from typing import Dict, Any
from dataclasses import dataclass, field

@dataclass
class RunRecord:
    run_id: str
    graph_id: str
    state: Dict[str, Any]
    logs: list = field(default_factory=list)
    status: str = "pending" 
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

class InMemoryStore:
    def __init__(self):
        self.graphs = {}  
        self.runs = {}    

    def save_graph(self, graph_id: str, graph: dict):
        self.graphs[graph_id] = graph

    def get_graph(self, graph_id: str):
        return self.graphs.get(graph_id)

    def new_run(self, graph_id: str, state: Dict[str, Any]) -> RunRecord:
        run_id = str(uuid.uuid4())
        rec = RunRecord(run_id=run_id, graph_id=graph_id, state=state.copy())
        self.runs[run_id] = rec
        return rec

    def get_run(self, run_id: str) -> RunRecord:
        return self.runs.get(run_id)

store = InMemoryStore()
