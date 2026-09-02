from typing import Dict, Any

class PlannerAgent:
    """Agent that reasons over VLM perception output + RAG SOP snippets to decide next action."""

    def plan(self, vlm_output: Dict[str, Any], rag_context: str) -> Dict[str, Any]:
        severity = vlm_output.get("severity", "NONE")
        defect = vlm_output.get("defect_type", "Clean")
        confidence = vlm_output.get("confidence", 0.9)

        if severity == "CRITICAL" or severity == "HIGH":
            action = "SCHEDULE_REPAIR"
            requires_hitl = True
            reasoning = f"Severity is {severity} for '{defect}' (Confidence: {confidence*100:.1f}%). Maintenance manual SOP requires immediate dispatch ticket."
            tool = "flag_for_repair"
            priority = "URGENT" if severity == "CRITICAL" else "HIGH"

        elif severity == "MEDIUM":
            if "debris" in defect.lower() or "shadow" in defect.lower():
                action = "RE_FLY"
                requires_hitl = True
                reasoning = f"Medium severity anomaly '{defect}'. RAG safety protocol specifies close 5m re-fly sweep to verify obstruction boundary."
                tool = "reschedule_flight"
                priority = "MEDIUM"
            else:
                action = "SCHEDULE_REPAIR"
                requires_hitl = True
                reasoning = f"Medium severity soiling '{defect}'. RAG SOP mandates scheduling routine washing crew within 72 hrs."
                tool = "flag_for_repair"
                priority = "MEDIUM"

        else: # NONE or LOW
            action = "LOG_ONLY"
            requires_hitl = False
            reasoning = f"Panel status normal ('{defect}'). No immediate maintenance required. Archiving operational telemetry."
            tool = "log_report"
            priority = "LOW"

        return {
            "action": action,
            "requires_hitl": requires_hitl,
            "reasoning": reasoning,
            "recommended_tool": tool,
            "priority": priority,
            "target_panel": "SOLAR-PANEL-ROW-04-B",
            "drone_id": "DRONE-ALPHA-04"
        }

planner_agent = PlannerAgent()
