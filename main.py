from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from uuid import uuid4
from .schemas import GraphCreateRequest, GraphResponse, GraphRunRequest, RunStatus
from .run_store import store
from . import engine
from typing import Dict, Any
import asyncio

app = FastAPI(title="Minimal Workflow Engine")

@app.post("/graph/create", response_model=GraphResponse)
async def create_graph(payload: GraphCreateRequest):
    graph_id = str(uuid4())
    graph = {
        "nodes": payload.nodes,
        "edges": payload.edges,
        "branches": payload.branches or {}
    }
    store.save_graph(graph_id, graph)
    return {"graph_id": graph_id}

@app.post("/graph/run", response_model=RunStatus)
async def run_graph_endpoint(payload: GraphRunRequest, background_tasks: BackgroundTasks):
    graph = store.get_graph(payload.graph_id)
    if not graph:
        raise HTTPException(404, "graph not found")
    run_rec = store.new_run(payload.graph_id, payload.initial_state)
    run_rec.logs.append("created run")
    
    if payload.run_async:
        
        background_tasks.add_task(engine.run_graph, payload.graph_id, run_rec.run_id)
        run_rec.status = "running"
    else:
      
        await engine.run_graph(payload.graph_id, run_rec.run_id)
    return {"run_id": run_rec.run_id, "status": run_rec.status, "state": run_rec.state, "logs": run_rec.logs}

@app.get("/graph/state/{run_id}", response_model=RunStatus)
async def get_run_state(run_id: str):
    rec = store.get_run(run_id)
    if not rec:
        raise HTTPException(404, "run not found")
    return {"run_id": rec.run_id, "status": rec.status, "state": rec.state, "logs": rec.logs}


@app.websocket("/ws/run/{run_id}")
async def websocket_run(ws: WebSocket, run_id: str):
    await ws.accept()
    rec = store.get_run(run_id)
    if not rec:
        await ws.send_text("run not found")
        await ws.close()
        return

    async def send_updates(rid: str, state: Dict[str, Any], message: str):
        try:
            await ws.send_json({"run_id": rid, "state": state, "message": message})
        except Exception:
            pass

    try:
        
        while rec.status not in ("finished", "failed"):
            await ws.send_json({"run_id": rec.run_id, "status": rec.status, "state": rec.state, "logs": rec.logs[-5:]})
            await asyncio.sleep(1)
            rec = store.get_run(run_id)
        
        await ws.send_json({"run_id": rec.run_id, "status": rec.status, "state": rec.state, "logs": rec.logs[-20:]})
        await ws.close()
    except WebSocketDisconnect:
        return
