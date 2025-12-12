"""State definitions for the LangGraph agent."""
from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict):
    """State for the New Relic Incident Summary Agent."""

    # Incident information
    open_incidents: Optional[List[Dict[str, Any]]]
    incident_count: int

    # AI Summary
    incidents_summary: Optional[str]
    key_insights: Optional[List[str]]

    # Notification status
    slack_sent: bool

    # Error handling
    errors: List[str]

    # Agent control
    current_step: str
    next_step: Optional[str]
