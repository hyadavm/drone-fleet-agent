import asyncio
import logging
from typing import Dict, Any, Callable, Awaitable
from backend.perception.vlm_agent import vlm_agent
from backend.memory.vector_store import search_knowledge_base
from backend.agents.planner_agent import planner_agent
from backend.agents.hitl_gate import hitl_gate
from backend.tools.drone_tools import reschedule_flight, flag_for_repair, log_report
from backend.observability.tracing import tracer

logger = logging.getLogger("workflow")

class WorkflowGraph:
    """Orchestrates the multi-agent workflow: VLM Perception -> RAG SOP Retrieval -> Planner Agent -> HITL Gate -> Executor Agent."""

    async def execute_run(self, run_id: str, image_path: str, ws_broadcast: Callable[[Dict[str, Any]], Awaitable[None]]):
        try:
            # 1. Perception Node
            await ws_broadcast({"step": "PERCEPTION_START", "message": "VLM Agent analyzing aerial photo visual features..."})
            vlm_res = vlm_agent.analyze_image(image_path)
            tracer.log_step(run_id, "VLM_INSPECTION_COMPLETE", "VLM_Agent", vlm_res)
            
            await ws_broadcast({
                "step": "PERCEPTION_COMPLETE",
                "message": f"Defect Detected: {vlm_res['defect_type']} (Severity: {vlm_res['severity']}, Confidence: {int(vlm_res['confidence']*100)}%)",
                "data": vlm_res
            })
            await asyncio.sleep(0.8)

            # 2. RAG Retrieval Node
            await ws_broadcast({"step": "RAG_START", "message": "Querying solar maintenance knowledge base for SOP rules..."})
            rag_query = f"{vlm_res['defect_type']} severity {vlm_res['severity']}"
            rag_snippet = search_knowledge_base(rag_query, top_k=2)
            tracer.log_step(run_id, "RAG_RETRIEVAL_COMPLETE", "RAG_Retriever", {"query": rag_query, "snippet": rag_snippet})
            
            await ws_broadcast({
                "step": "RAG_COMPLETE",
                "message": "Retrieved relevant standard operating procedure from Knowledge Base.",
                "data": {"query": rag_query, "snippet": rag_snippet}
            })
            await asyncio.sleep(0.8)

            # 3. Planner Agent Node
            await ws_broadcast({"step": "PLANNING_START", "message": "Planner Agent synthesizing visual findings + SOP guidelines..."})
            plan = planner_agent.plan(vlm_res, rag_snippet)
            tracer.log_step(run_id, "PLAN_GENERATED", "Planner_Agent", plan)

            await ws_broadcast({
                "step": "PLANNING_COMPLETE",
                "message": f"Proposed Decision: {plan['action']} — {plan['reasoning']}",
                "data": plan
            })
            await asyncio.sleep(0.8)

            # 4. Human-In-The-Loop Gate Node
            if plan["requires_hitl"]:
                event = hitl_gate.register_pending(run_id, plan)
                await ws_broadcast({
                    "step": "AWAITING_HUMAN_APPROVAL",
                    "message": f"CRITICAL ACTION ({plan['action']}): Requiring human operator approval before execution.",
                    "data": hitl_gate.get_pending(run_id)
                })
                tracer.log_step(run_id, "HITL_GATE_PAUSE", "HITL_Gate", hitl_gate.get_pending(run_id))
                
                # Wait for human decision
                await event.wait()
                
                response = hitl_gate.get_response(run_id)
                tracer.log_step(run_id, "HITL_GATE_RESUME", "HITL_Gate", response)

                if not response["approved"]:
                    # User rejected
                    await ws_broadcast({
                        "step": "HITL_RESPONSE",
                        "message": "Human operator REJECTED the proposed decision.",
                        "data": response
                    })
                    # Override plan action to LOG_ONLY
                    plan["action"] = "ACTION_REJECTED"
                    plan["recommended_tool"] = "log_report"
                    plan["reasoning"] += f" (Overridden by human reject: '{response.get('operator_notes', '')}')"

                else:
                    await ws_broadcast({
                        "step": "HITL_RESPONSE",
                        "message": "Human operator APPROVED the decision. Proceeding with execution.",
                        "data": response
                    })

            # 5. Tool Executor Node
            await ws_broadcast({"step": "EXECUTION_START", "message": f"Executing tool: {plan['recommended_tool']}..."})
            tool_name = plan["recommended_tool"]
            
            if tool_name == "flag_for_repair":
                tool_out = flag_for_repair(panel_id="SOLAR-ROW-04", defect_type=vlm_res["defect_type"], priority=plan.get("priority", "HIGH"))
            elif tool_name == "reschedule_flight":
                tool_out = reschedule_flight(drone_id="DRONE-ALPHA-04", altitude_m=5.0, pattern="Close-range thermal sweep")
            else:
                tool_out = log_report(run_id=run_id, status=plan["action"], details={"vlm": vlm_res, "plan": plan})

            tracer.log_step(run_id, "TOOL_EXECUTED", "Executor_Agent", tool_out)
            await asyncio.sleep(0.5)

            final_summary = {
                "run_id": run_id,
                "status": "COMPLETED",
                "final_action": plan["action"],
                "vlm_summary": vlm_res,
                "plan_summary": plan,
                "tool_result": tool_out,
                "traces": tracer.get_run_trace(run_id)
            }

            await ws_broadcast({
                "step": "WORKFLOW_COMPLETE",
                "message": f"Workflow run {run_id} finished successfully.",
                "data": final_summary
            })
            return final_summary

        except Exception as e:
            logger.error(f"Error in workflow run {run_id}: {str(e)}", exc_info=True)
            await ws_broadcast({
                "step": "ERROR",
                "message": f"Execution error: {str(e)}"
            })
            raise e

workflow_graph = WorkflowGraph()
