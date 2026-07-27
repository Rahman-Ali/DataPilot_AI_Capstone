"""Durable LangGraph orchestration for the AutoML agents.

Checkpoints are stored on the Run row, so they survive process restarts.  The
graph state only carries JSON-safe values; fitted sklearn objects are persisted
as a joblib checkpoint between ModelForge and InsightBoard.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, TypedDict

import joblib
from django.conf import settings
from langgraph.graph import END, START, StateGraph

from .models import Run


class WorkflowState(TypedDict, total=False):
    run_id: str
    profile: dict[str, Any]
    route: dict[str, Any]
    prepared: bool
    training_checkpoint: str
    results: dict[str, Any]


def _workflow(state: WorkflowState):
    from .pipeline import AgentWorkflow

    run = Run.objects.select_related("dataset").get(pk=state["run_id"])
    return AgentWorkflow(run)


def _checkpoint(workflow, stage: str, state: dict[str, Any]) -> None:
    workflow.run.checkpoint_stage = stage
    workflow.run.workflow_state = state
    workflow.run.save(
        update_fields=["checkpoint_stage", "workflow_state", "updated_at"]
    )


def data_lens_node(state: WorkflowState) -> WorkflowState:
    workflow = _workflow(state)
    profile = workflow.data_lens()
    saved = {"run_id": state["run_id"], "profile": profile}
    _checkpoint(workflow, "data_lens", saved)
    return saved


def pilot_flow_node(state: WorkflowState) -> WorkflowState:
    workflow = _workflow(state)
    route = workflow.pilot_flow(state["profile"])
    if route["blocking_issues"]:
        raise ValueError("; ".join(route["blocking_issues"]))
    saved = {**state, "route": route}
    _checkpoint(workflow, "pilot_flow", saved)
    return saved


def preparation_node(state: WorkflowState) -> WorkflowState:
    workflow = _workflow(state)
    if state["route"]["needs_corrective_cleaning"]:
        workflow.clean_craft(state["profile"], state["route"])
    else:
        workflow.prepare_model_ready_data(state["profile"])
    saved = {**state, "prepared": True}
    _checkpoint(workflow, "preparation", saved)
    return saved


def model_forge_node(state: WorkflowState) -> WorkflowState:
    workflow = _workflow(state)
    if state["route"]["needs_corrective_cleaning"]:
        prepared = workflow.clean_craft(state["profile"], state["route"])
    else:
        prepared = workflow.prepare_model_ready_data(state["profile"])
    training = workflow.model_forge(prepared)
    folder = Path(settings.MEDIA_ROOT) / "checkpoints" / str(workflow.run.id)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "model_forge.joblib"
    joblib.dump({"prepared": prepared, "training": training}, path)
    saved = {**state, "training_checkpoint": str(path)}
    _checkpoint(workflow, "model_forge", saved)
    return saved


def insight_board_node(state: WorkflowState) -> WorkflowState:
    workflow = _workflow(state)
    payload = joblib.load(state["training_checkpoint"])
    results = workflow.insight_board(
        state["profile"], payload["prepared"], payload["training"], state["route"]
    )
    saved = {**state, "results": results}
    _checkpoint(workflow, "completed", saved)
    return saved


def _entry(state: WorkflowState) -> str:
    run = Run.objects.get(pk=state["run_id"])
    return {
        "": "data_lens",
        "data_lens": "pilot_flow",
        "pilot_flow": "preparation",
        "preparation": "model_forge",
        "model_forge": "insight_board",
    }.get(run.checkpoint_stage, "data_lens")


builder = StateGraph(WorkflowState)
builder.add_node("data_lens", data_lens_node)
builder.add_node("pilot_flow", pilot_flow_node)
builder.add_node("preparation", preparation_node)
builder.add_node("model_forge", model_forge_node)
builder.add_node("insight_board", insight_board_node)
builder.add_conditional_edges(
    START,
    _entry,
    {
        "data_lens": "data_lens",
        "pilot_flow": "pilot_flow",
        "preparation": "preparation",
        "model_forge": "model_forge",
        "insight_board": "insight_board",
    },
)
builder.add_edge("data_lens", "pilot_flow")
builder.add_edge("pilot_flow", "preparation")
builder.add_edge("preparation", "model_forge")
builder.add_edge("model_forge", "insight_board")
builder.add_edge("insight_board", END)
workflow_graph = builder.compile()


def execute_graph(run: Run, resume: bool = True) -> dict[str, Any]:
    run.refresh_from_db()
    if not resume:
        run.checkpoint_stage = ""
        run.workflow_state = {}
        run.progress = 0
        run.logs = []
        run.results = {}
        run.error = ""
        run.save()
    initial: WorkflowState = {"run_id": str(run.id)}
    if resume and run.workflow_state:
        initial.update(run.workflow_state)
    final = workflow_graph.invoke(initial)
    return final["results"]
