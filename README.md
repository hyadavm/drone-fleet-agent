# Autonomous Drone Fleet Inspection — Multi-Agent System

An autonomous aerial drone inspection system featuring a **simple, light-themed user interface**, multi-agent graph orchestration (VLM perception, local RAG knowledge base retrieval, reasoning planner agent), mock drone tool execution, real-time WebSocket telemetry streaming, and a **Human-in-the-Loop (HITL)** safety approval gate.

---

## 🌟 Highlights & Architecture

```
[ Sample Photo ] ──> [ VLM Perception ] ──> [ RAG Knowledge Base ]
                                                    │
                                                    ▼
[ Drone Tool Execution ] <── [ HITL Safety Gate ] <── [ Planner Agent ]
   (flag_for_repair,             (Human Operator
    reschedule_flight)           Approve / Reject)
```

- **Clean Light-Themed UI**: Designed with a simple off-white slate background (`#f8fafc`), clean cards, responsive gallery preview, and clear status indicators (no dark theme).
- **VLM Perception Agent**: Analyzes aerial drone inspection shots for solar panel defects (micro-cracks, heavy soiling/dust, thermal hotspots, bird debris, clean panels).
- **RAG Knowledge Base**: Performs local vector/keyword retrieval over maintenance SOPs (`data/knowledge_base/maintenance_manual.md` & `safety_protocols.md`).
- **Planner Agent**: Combines perception findings with SOP rules to decide action severity (`LOG_ONLY`, `SCHEDULE_REPAIR`, `RE_FLY`).
- **Human-In-The-Loop (HITL) Gate**: Mandates explicit operator approval before dispatching repair dispatches or re-fly sweeps over WebSocket signals.
- **Mock Drone Tools**: Executes mock control commands (`flag_for_repair`, `reschedule_flight`, `log_report`).

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Sample Images (Optional - Pre-generated)
```bash
python data/generate_images.py
```

### 3. Run Application Server
```bash
python -m uvicorn backend.main:app --port 8000 --reload
```
Open your browser at **`http://localhost:8000`** to view the application.

---

## 🧪 Running Automated Tests

Run the pytest suite to verify all execution paths (clean path, HITL approval, HITL rejection):
```bash
pytest tests/test_workflow.py
```

---

## 📁 File Structure

```
.
├── README.md
├── requirements.txt
├── .env.example
├── data/
│   ├── generate_images.py
│   ├── sample_images/            # Aerial solar panel sample shots
│   └── knowledge_base/           # RAG SOP documents
│       ├── maintenance_manual.md
│       └── safety_protocols.md
├── backend/
│   ├── main.py                   # FastAPI server & REST/WebSocket routes
│   ├── config.py                 # Configuration settings
│   ├── memory/
│   │   └── vector_store.py       # Knowledge Base search retriever
│   ├── perception/
│   │   └── vlm_agent.py          # VLM defect analyzer
│   ├── agents/
│   │   ├── planner_agent.py      # Reasoning planner agent
│   │   └── hitl_gate.py          # Human-in-the-loop safety gate
│   ├── tools/
│   │   └── drone_tools.py        # Mock drone execution tools
│   ├── graph/
│   │   └── workflow.py           # Multi-agent state machine workflow
│   └── observability/
│       └── tracing.py            # Telemetry tracing & LangSmith integration
├── frontend/
│   ├── index.html                # Light-themed single-page app layout
│   ├── css/
│   │   └── style.css             # Light theme styling
│   └── js/
│       ├── api.js                # REST API client
│       ├── socket.js             # WebSocket streaming manager
│       └── app.js                # UI application logic
└── tests/
    └── test_workflow.py          # Pytest suite
```
