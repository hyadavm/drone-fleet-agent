import logging
import time
from typing import Dict, Any, List
from backend.config import settings

logger = logging.getLogger("tracing")

class ExecutionTracer:
    """Archiver for step-by-step multi-agent execution traces with LangSmith export support."""

    def __init__(self):
        self.runs: Dict[str, List[Dict[str, Any]]] = {}

    def log_step(self, run_id: str, step_name: str, agent_name: str, payload: Dict[str, Any]):
        step_event = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "step_name": step_name,
            "agent_name": agent_name,
            "payload": payload
        }
        if run_id not in self.runs:
            self.runs[run_id] = []
        self.runs[run_id].append(step_event)
        
        logger.info(f"[TRACE:{run_id}] [{agent_name}] -> {step_name}")

        if settings.LANGSMITH_TRACING and settings.LANGSMITH_API_KEY:
            # LangSmith tracing hook
            self._send_to_langsmith(run_id, step_event)

    def get_run_trace(self, run_id: str) -> List[Dict[str, Any]]:
        return self.runs.get(run_id, [])

    def _send_to_langsmith(self, run_id: str, step_event: Dict[str, Any]):
        # Mock/Extensible LangSmith telemetry submission
        pass

tracer = ExecutionTracer()
