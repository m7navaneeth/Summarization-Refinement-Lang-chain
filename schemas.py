from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class NodeDef(BaseModel):
    name: str
    func: str  # name of registered function

class GraphCreateRequest(BaseModel):
    nodes: Dict[str, str]  # node_name -> func_name
    edges: Dict[str, Optional[str]]  # node_name -> next_node_name (or null)
    branches: Optional[Dict[str, Dict[str, Optional[str]]]] = None  # node -> {outcome: node}

class GraphResponse(BaseModel):
    graph_id: str

class GraphRunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]
    run_async: Optional[bool] = True

class RunStatus(BaseModel):
    run_id: str
    status: str
    state: Dict[str, Any]
    logs: List[str]
