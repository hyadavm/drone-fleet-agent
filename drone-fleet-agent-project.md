# Project: Autonomous Drone Fleet Inspection — Multi-Agent System (1-Day Build)

## Goal
A simulated multi-agent framework where AI agents perceive aerial drone imagery, reason about anomalies, retrieve relevant inspection knowledge (RAG), plan actions, and execute them through mock drone-control functions — with a human-in-the-loop checkpoint before any "critical" action, and full run tracing via LangSmith.

**Stack:** Python backend (FastAPI + LangGraph), plain HTML/CSS/JS frontend (no framework, no dark theme).

This is scoped to be buildable in one day: no real drone hardware, a small local RAG store, one VLM call path, and a 3-agent graph (not 10). It still demonstrates every core skill in the role: multi-agent orchestration, RAG, VLM, tool-calling, observability, and safety.

---

## Scenario
A fleet of drones inspects solar panel farms. Each drone uploads photos. The system must:
1. Analyze each photo for defects (VLM).
2. Look up relevant maintenance procedure from a knowledge base (RAG).
3. Decide the next action (log only / schedule repair / re-fly for closer inspection).
4. Ask a human to confirm before "re-fly" or "schedule repair" (human-in-the-loop).
5. Execute the confirmed action via a mock tool call and log it.

The human-in-the-loop step is why this needs a real frontend: the browser page shows the pending decision and the user clicks Approve/Reject, which the backend is waiting on.

---

## File Structure

```
drone-fleet-agent/
├── README.md
├── requirements.txt
├── .env.example
│
├── data/
│   ├── sample_images/            # 5–8 sample aerial photos (panels, cracks, dust, birds)
│   └── knowledge_base/
│       ├── maintenance_manual.md
│       └── safety_protocols.md
│
├── backend/
│   ├── main.py                   # FastAPI app: serves the frontend + REST endpoints + WebSocket for HITL
│   ├── config.py                 # API keys, model names, thresholds
│   │
│   ├── memory/
│   │   └── vector_store.py       # builds + queries a small Chroma/FAISS index from knowledge_base/
│   │
│   ├── perception/
│   │   └── vlm_agent.py          # sends image to a VLM, returns structured defect description
│   │
│   ├── agents/
│   │   ├── planner_agent.py      # decides action given VLM output + RAG context
│   │   ├── executor_agent.py     # calls mock drone tools based on planner decision
│   │   └── hitl_gate.py          # pauses graph, pushes a pending decision to the frontend, waits for response
│   │
│   ├── tools/
│   │   └── drone_tools.py        # mock functions: reschedule_flight(), flag_for_repair(), log_report()
│   │
│   ├── graph/
│   │   └── workflow.py           # LangGraph state machine wiring the 3 agents + HITL gate
│   │
│   └── observability/
│       └── tracing.py            # LangSmith setup/decorators
│
├── frontend/
│   ├── index.html                # single page: upload/select image, run button, live status, approve/reject buttons
│   ├── css/
│   │   └── style.css             # light background, clean layout — no dark theme
│   ├── js/
│   │   ├── api.js                # fetch() calls to backend REST endpoints
│   │   ├── socket.js             # WebSocket connection for live agent status + HITL prompts
│   │   └── app.js                # UI logic: render VLM result, RAG snippet, planner decision, approve/reject
│   └── assets/
│       └── (icons, sample thumbnails)
│
└── tests/
    └── test_workflow.py          # 2–3 sanity tests (happy path + one HITL rejection path)
```

---

## How Frontend and Backend Talk
- `GET /api/images` — list sample images for the dropdown/gallery
- `POST /api/run` — starts a workflow run for a chosen image, returns a `run_id`
- `WS /ws/{run_id}` — pushes live updates to the page: VLM result → RAG snippet → planner decision → "awaiting approval" → final outcome
- `POST /api/approve/{run_id}` — frontend sends Approve/Reject, unblocks `hitl_gate.py` on the backend
- `GET /api/logs/{run_id}` — full run log, shown at the end alongside a link to the LangSmith trace

FastAPI serves both the API and the static `frontend/` folder, so it's one process to run (`uvicorn backend.main:app`).

---

## Build Order (time-boxed for today)

| Time block | Task | Files touched |
|---|---|---|
| Morning (2–3 hrs) | Set up repo, env, sample images, write 2 short knowledge base docs | `data/`, `requirements.txt`, `README.md` |
| Mid-morning (1.5 hrs) | Build vector store + retrieval query function | `backend/memory/vector_store.py` |
| Midday (1.5 hrs) | VLM agent: image in → defect type + confidence out | `backend/perception/vlm_agent.py` |
| Early afternoon (2 hrs) | Planner agent (LLM + RAG context → decision) and mock tools | `backend/agents/planner_agent.py`, `backend/tools/drone_tools.py` |
| Afternoon (1.5 hrs) | LangGraph workflow + HITL gate | `backend/graph/workflow.py`, `backend/agents/hitl_gate.py` |
| Late afternoon (1.5 hrs) | FastAPI app: REST + WebSocket endpoints wired to the graph | `backend/main.py` |
| Evening (1.5 hrs) | Frontend page: image picker, run button, live status panel, approve/reject buttons | `frontend/index.html`, `frontend/css/style.css`, `frontend/js/*.js` |
| Night (1 hr) | LangSmith tracing, end-to-end run on 3 images, 2 tests, fix bugs, finalize README | `backend/observability/tracing.py`, `tests/test_workflow.py`, `README.md` |

---

## What NOT to build today (keep it out of scope)
- Real drone SDK / flight controller integration
- Multi-drone fleet coordination or scheduling optimization
- Cloud deployment (AWS/GCP) — note it in README as "next step" only
- Fine-tuning the VLM — use an existing hosted/pretrained model as-is
- Any frontend framework (React/Vue) or build tooling — plain HTML/CSS/JS is enough for one page

---

## Definition of Done (tonight)
- [ ] `uvicorn backend.main:app` starts the whole app (API + frontend served together).
- [ ] Opening the page, picking a sample image, and clicking Run shows: defect description → retrieved procedure → planner decision, live, without a page refresh.
- [ ] If the decision is critical, the page shows an Approve/Reject prompt and the backend genuinely waits for it before executing.
- [ ] At least one run is traced and viewable in LangSmith.
- [ ] One rejection path tested (user clicks Reject → action is not executed, logged as rejected).
- [ ] README explains the architecture in under one page, with the file structure above and a note on how this would extend to real fleets on AWS/GCP.
