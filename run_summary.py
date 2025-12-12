#!/usr/bin/env python3
"""
Run the incident summary agent immediately.
Fetches open incidents from New Relic, summarizes them with AI, and sends to Slack.
"""
from agent_graph import create_agent_graph
from agent_state import AgentState


def main():
    """Run the incident summary agent."""
    print("="*60)
    print("🤖 New Relic Incident Summary Agent")
    print("="*60)
    print()

    # Create agent
    agent = create_agent_graph()

    # Create initial state
    initial_state: AgentState = {
        "open_incidents": None,
        "incident_count": 0,
        "incidents_summary": None,
        "key_insights": None,
        "slack_sent": False,
        "errors": [],
        "current_step": "init",
        "next_step": None
    }

    # Run the agent
    print("🚀 Starting incident summary workflow...\n")
    final_state = agent.invoke(initial_state)

    # Report final results
    print("\n" + "="*60)
    print("✅ Agent Complete")
    print("="*60)
    print(f"Incidents Processed: {final_state.get('incident_count', 0)}")
    print(f"Slack Notification: {'✅ Sent' if final_state.get('slack_sent') else '❌ Failed'}")

    if final_state.get("errors"):
        print(f"\n⚠️  Errors: {len(final_state['errors'])}")
        for error in final_state["errors"]:
            print(f"  - {error}")

    print("="*60)


if __name__ == "__main__":
    main()

