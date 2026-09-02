import os
import asyncio
from backend.perception.vlm_agent import vlm_agent
from backend.memory.vector_store import search_knowledge_base
from backend.agents.planner_agent import planner_agent
from backend.agents.hitl_gate import hitl_gate
from backend.graph.workflow import workflow_graph
from backend.config import settings

def test_vlm_and_rag_retrieval():
    image_path = os.path.join(settings.SAMPLE_IMAGES_DIR, "solar_panel_cracked.jpg")
    vlm_res = vlm_agent.analyze_image(image_path)
    assert vlm_res["severity"] == "HIGH"
    assert "crack" in vlm_res["defect_type"].lower()

    snippet = search_knowledge_base("Micro-cracks high severity", top_k=1)
    assert len(snippet) > 0
    assert "SOP" in snippet or "Micro-cracks" in snippet

def test_workflow_clean_log_only():
    async def run():
        image_path = os.path.join(settings.SAMPLE_IMAGES_DIR, "solar_panel_clean.jpg")
        events = []
        async def mock_broadcast(msg):
            events.append(msg)

        run_id = "TEST-RUN-CLEAN-01"
        summary = await workflow_graph.execute_run(run_id, image_path, mock_broadcast)
        
        assert summary["final_action"] == "LOG_ONLY"
        assert summary["tool_result"]["tool"] == "log_report"

    asyncio.run(run())

def test_workflow_hitl_approval():
    async def run():
        image_path = os.path.join(settings.SAMPLE_IMAGES_DIR, "solar_panel_cracked.jpg")
        events = []
        async def mock_broadcast(msg):
            events.append(msg)

        run_id = "TEST-RUN-HITL-APPROVE-02"

        async def auto_approve():
            await asyncio.sleep(0.3)
            pending = hitl_gate.get_pending(run_id)
            if pending:
                hitl_gate.submit_decision(run_id, approved=True, operator_notes="Auto approved test")

        task = asyncio.create_task(auto_approve())
        summary = await workflow_graph.execute_run(run_id, image_path, mock_broadcast)
        await task

        assert summary["final_action"] == "SCHEDULE_REPAIR"
        assert summary["tool_result"]["tool"] == "flag_for_repair"

    asyncio.run(run())

def test_workflow_hitl_rejection():
    async def run():
        image_path = os.path.join(settings.SAMPLE_IMAGES_DIR, "solar_panel_hotspot.jpg")
        events = []
        async def mock_broadcast(msg):
            events.append(msg)

        run_id = "TEST-RUN-HITL-REJECT-03"

        async def auto_reject():
            await asyncio.sleep(0.3)
            pending = hitl_gate.get_pending(run_id)
            if pending:
                hitl_gate.submit_decision(run_id, approved=False, operator_notes="Inspection deferred")

        task = asyncio.create_task(auto_reject())
        summary = await workflow_graph.execute_run(run_id, image_path, mock_broadcast)
        await task

        assert summary["final_action"] == "ACTION_REJECTED"
        assert summary["tool_result"]["tool"] == "log_report"

    asyncio.run(run())
