import os
import uuid
import asyncio
from typing import Dict, List, Set, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from backend.config import settings
from backend.graph.workflow import workflow_graph
from backend.agents.hitl_gate import hitl_gate
from backend.observability.tracing import tracer

app = FastAPI(title=settings.PROJECT_NAME)

# Connection manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, run_id: str, websocket: WebSocket):
        await websocket.accept()
        if run_id not in self.active_connections:
            self.active_connections[run_id] = set()
        self.active_connections[run_id].add(websocket)

    def disconnect(self, run_id: str, websocket: WebSocket):
        if run_id in self.active_connections:
            self.active_connections[run_id].discard(websocket)
            if not self.active_connections[run_id]:
                del self.active_connections[run_id]

    async def broadcast(self, run_id: str, message: Dict[str, Any]):
        if run_id in self.active_connections:
            for ws in list(self.active_connections[run_id]):
                try:
                    await ws.send_json(message)
                except Exception:
                    self.disconnect(run_id, ws)

manager = ConnectionManager()

# Data models
class RunRequest(BaseModel):
    image_filename: str

class ApprovalRequest(BaseModel):
    approved: bool
    operator_notes: str = ""

# API Endpoints
@app.get("/api/images")
def get_sample_images():
    """List available aerial sample images in data/sample_images."""
    images = []
    if os.path.exists(settings.SAMPLE_IMAGES_DIR):
        for f in sorted(os.listdir(settings.SAMPLE_IMAGES_DIR)):
            if f.endswith(('.jpg', '.jpeg', '.png')):
                title = f.replace("solar_panel_", "").replace(".jpg", "").replace("_", " ").title()
                images.append({
                    "filename": f,
                    "title": title,
                    "url": f"/sample_images/{f}"
                })
    return {"images": images}

@app.post("/api/run")
async def start_run(req: RunRequest):
    """Starts a multi-agent inspection workflow run."""
    image_path = os.path.join(settings.SAMPLE_IMAGES_DIR, req.image_filename)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail=f"Image {req.image_filename} not found.")

    run_id = f"RUN-{uuid.uuid4().hex[:8].upper()}"

    async def run_task():
        # Give WebSocket client time to connect
        await asyncio.sleep(0.5)
        async def ws_broadcast(msg: Dict[str, Any]):
            await manager.broadcast(run_id, msg)

        await workflow_graph.execute_run(run_id, image_path, ws_broadcast)

    asyncio.create_task(run_task())
    return {"run_id": run_id, "status": "STARTED"}

@app.post("/api/approve/{run_id}")
def approve_run(run_id: str, req: ApprovalRequest):
    """Submits human approval/rejection for a paused workflow."""
    success = hitl_gate.submit_decision(run_id, approved=req.approved, operator_notes=req.operator_notes)
    if not success:
        raise HTTPException(status_code=404, detail="Run not found or not currently awaiting approval.")
    return {"run_id": run_id, "status": "SUBMITTED", "approved": req.approved}

@app.get("/api/logs/{run_id}")
def get_logs(run_id: str):
    """Returns execution trace logs for a specific run."""
    traces = tracer.get_run_trace(run_id)
    return {"run_id": run_id, "traces": traces}

# WebSocket Endpoint
@app.websocket("/ws/{run_id}")
async def websocket_endpoint(websocket: WebSocket, run_id: str):
    await manager.connect(run_id, websocket)
    try:
        # Check if there is an active pending approval
        pending = hitl_gate.get_pending(run_id)
        if pending:
            await websocket.send_json({
                "step": "AWAITING_HUMAN_APPROVAL",
                "message": "Awaiting human decision...",
                "data": pending
            })

        while True:
            # Listen for client WS messages (e.g. approve/reject over WS)
            data = await websocket.receive_json()
            if data.get("action") == "APPROVE_DECISION":
                hitl_gate.submit_decision(run_id, approved=data.get("approved", True), operator_notes=data.get("notes", ""))
    except WebSocketDisconnect:
        manager.disconnect(run_id, websocket)

# Mount Static Files & Frontend
frontend_dir = os.path.join(settings.BASE_DIR, "frontend")
app.mount("/sample_images", StaticFiles(directory=settings.SAMPLE_IMAGES_DIR), name="sample_images")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(frontend_dir, "index.html"))
