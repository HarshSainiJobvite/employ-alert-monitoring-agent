"""Simple state machine workflow for New Relic Alert Agent (Python 3.8 compatible)."""
from typing import Callable, Dict, Any, Optional
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


class SimpleWorkflow:
    """
    A simple state machine workflow implementation that replaces LangGraph.
    Compatible with Python 3.8+.
    """

    def __init__(self):
        self.nodes: Dict[str, Callable] = {}
        self.entry_point: Optional[str] = None

    def add_node(self, name: str, func: Callable):
        """Add a node to the workflow."""
        self.nodes[name] = func

    def set_entry_point(self, name: str):
        """Set the entry point for the workflow."""
        self.entry_point = name

    def invoke(self, initial_state: AgentState) -> AgentState:
        """
        Execute the workflow starting from the entry point.

        Args:
            initial_state: Initial state

        Returns:
            Final state after execution
        """
        if not self.entry_point:
            raise ValueError("Entry point not set")

        state = initial_state
        current_node = self.entry_point

        # Execute nodes in sequence based on next_step
        max_iterations = 20  # Safety limit
        iteration = 0

        while current_node and iteration < max_iterations:
            if current_node not in self.nodes:
                print(f"⚠️  Node '{current_node}' not found, ending workflow")
                break

            # Execute current node
            node_func = self.nodes[current_node]
            state = node_func(state)

            # Determine next node
            next_step = state.get("next_step")

            if next_step == "end" or next_step is None:
                # Execute end node
                if "end" in self.nodes:
                    state = self.nodes["end"](state)
                break

            current_node = next_step
            iteration += 1

        if iteration >= max_iterations:
            print("⚠️  Max iterations reached, ending workflow")
            state["errors"].append("Max iterations reached")

        return state


def create_agent_graph():
    """
    Create and configure the workflow for frequent condition analysis.

    Returns:
        Configured SimpleWorkflow
    """
    # Initialize the workflow
    workflow = SimpleWorkflow()

    # Add nodes for NRQL-based analysis
    workflow.add_node("fetch_frequent_conditions", fetch_frequent_conditions_node)
    workflow.add_node("fetch_condition_details", fetch_condition_details_node)
    workflow.add_node("fetch_null_pointer_details", fetch_null_pointer_details_node)
    workflow.add_node("summarize_conditions", summarize_conditions_node)
    workflow.add_node("send_notification", send_notification_node)
    workflow.add_node("end", end_node)

    # Set entry point
    workflow.set_entry_point("fetch_frequent_conditions")

    return workflow


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
