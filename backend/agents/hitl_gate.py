import asyncio
from typing import Dict, Any, Optional

class HITLGateManager:
    """Manages Human-in-the-Loop decision queues and async waiting events."""

    def __init__(self):
        self._pending_decisions: Dict[str, Dict[str, Any]] = {}
        self._events: Dict[str, asyncio.Event] = {}
        self._responses: Dict[str, Dict[str, Any]] = {}

    def register_pending(self, run_id: str, plan_data: Dict[str, Any]):
        event = asyncio.Event()
        self._pending_decisions[run_id] = {
            "run_id": run_id,
            "status": "AWAITING_HUMAN_APPROVAL",
            "proposed_action": plan_data["action"],
            "reasoning": plan_data["reasoning"],
            "recommended_tool": plan_data["recommended_tool"],
            "priority": plan_data.get("priority", "HIGH"),
        }
        self._events[run_id] = event
        return event

    def get_pending(self, run_id: str) -> Optional[Dict[str, Any]]:
        return self._pending_decisions.get(run_id)

    def submit_decision(self, run_id: str, approved: bool, operator_notes: str = "") -> bool:
        if run_id not in self._pending_decisions:
            return False

        response = {
            "approved": approved,
            "operator_notes": operator_notes,
            "status": "APPROVED" if approved else "REJECTED"
        }
        self._responses[run_id] = response
        
        # Remove from pending
        del self._pending_decisions[run_id]
        
        # Signal waiting task
        if run_id in self._events:
            self._events[run_id].set()
        
        return True

    def get_response(self, run_id: str) -> Optional[Dict[str, Any]]:
        return self._responses.get(run_id)

hitl_gate = HITLGateManager()
