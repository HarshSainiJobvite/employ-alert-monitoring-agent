"""LangGraph workflow for New Relic Alert Agent."""
from typing import Literal
from langgraph.graph import StateGraph, END
from agent_state import AgentState
from agent_nodes import (
    send_notification_node,
    end_node
)
from nrql_nodes import (
    fetch_frequent_conditions_node,
    fetch_condition_details_node,
    fetch_null_pointer_details_node,
    summarize_conditions_node
)


def route_after_fetch_conditions(state: AgentState) -> Literal["fetch_condition_details", "end"]:
    """Route after fetching frequent conditions."""
    if state.get("frequent_conditions"):
        return "fetch_condition_details"
    return "end"


def route_after_condition_details(state: AgentState) -> Literal["fetch_null_pointer_details", "summarize_conditions"]:
    """Route after fetching condition details - check if we need null pointer details."""
    # Check if any condition is related to NullPointerException
    conditions = state.get("frequent_conditions", [])
    for cond in conditions:
        name = cond.get("conditionName", "").lower()
        if "nullpointer" in name or "null" in name:
            return "fetch_null_pointer_details"
    return "summarize_conditions"


def route_after_null_pointer(state: AgentState) -> Literal["summarize_conditions"]:
    """Route after null pointer details."""
    return "summarize_conditions"


def route_after_summarize(state: AgentState) -> Literal["send_notification", "end"]:
    """Route after summarizing conditions."""
    if state.get("incidents_summary"):
        return "send_notification"
    return "end"


def route_after_notification(state: AgentState) -> Literal["end"]:
    """Route after sending notification."""
    return "end"


def create_agent_graph() -> StateGraph:
    """
    Create and configure the LangGraph workflow for frequent condition analysis.

    Returns:
        Compiled StateGraph
    """
    # Initialize the workflow with state schema
    workflow = StateGraph(AgentState)

    # Add nodes for NRQL-based analysis
    workflow.add_node("fetch_frequent_conditions", fetch_frequent_conditions_node)
    workflow.add_node("fetch_condition_details", fetch_condition_details_node)
    workflow.add_node("fetch_null_pointer_details", fetch_null_pointer_details_node)
    workflow.add_node("summarize_conditions", summarize_conditions_node)
    workflow.add_node("send_notification", send_notification_node)
    workflow.add_node("end", end_node)

    # Set entry point
    workflow.set_entry_point("fetch_frequent_conditions")

    # Add conditional edges
    workflow.add_conditional_edges(
        "fetch_frequent_conditions",
        route_after_fetch_conditions,
        {
            "fetch_condition_details": "fetch_condition_details",
            "end": "end"
        }
    )

    workflow.add_conditional_edges(
        "fetch_condition_details",
        route_after_condition_details,
        {
            "fetch_null_pointer_details": "fetch_null_pointer_details",
            "summarize_conditions": "summarize_conditions"
        }
    )

    workflow.add_edge("fetch_null_pointer_details", "summarize_conditions")

    workflow.add_conditional_edges(
        "summarize_conditions",
        route_after_summarize,
        {
            "send_notification": "send_notification",
            "end": "end"
        }
    )

    workflow.add_edge("send_notification", "end")
    workflow.add_edge("end", END)

    # Compile and return
    return workflow.compile()


def visualize_graph():
    """
    Generate a text representation of the workflow.
    """
    print("="*60)
    print("WORKFLOW GRAPH - NRQL Frequent Condition Analysis")
    print("="*60)
    print()
    print("fetch_frequent_conditions")
    print("    ↓")
    print("fetch_condition_details")
    print("    ↓")
    print("fetch_null_pointer_details (conditional)")
    print("    ↓")
    print("summarize_conditions")
    print("    ↓")
    print("send_notification")
    print("    ↓")
    print("end")
    print()
    print("="*60)
