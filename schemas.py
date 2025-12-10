from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class NodeDef(BaseModel):
    name: str
    func: str  

class GraphCreateRequest(BaseModel):
    nodes: Dict[str, str] 
    edges: Dict[str, Optional[str]]  
    branches: Optional[Dict[str, Dict[str, Optional[str]]]] = None  

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
