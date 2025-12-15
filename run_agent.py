#!/usr/bin/env python
"""Run the New Relic Alert Agent analysis."""
from agent_graph import create_agent_graph
from agent_state import AgentState

def run_analysis():
    """Start the agent analysis workflow."""
    print("=" * 60)
    print("🚀 Starting New Relic Alert Analysis Agent")
    print("=" * 60)

    # Create the graph
    graph = create_agent_graph()

    # Initialize the state with default values
    initial_state: AgentState = {
        "open_incidents": None,
        "incident_count": 0,
        "frequent_conditions": None,
        "condition_details": None,
        "incidents_summary": None,
        "key_insights": None,
        "slack_sent": False,
        "errors": [],
        "current_step": "start",
        "next_step": None
    }

    print("\n📊 Running analysis workflow...\n")

    # Invoke the graph
    try:
        final_state = graph.invoke(initial_state)

        print("\n" + "=" * 60)
        print("✅ Analysis Complete!")
        print("=" * 60)

        # Print summary
        if final_state.get("incidents_summary"):
            print("\n📋 Summary:")
            print("-" * 40)
            print(final_state["incidents_summary"][:2000])  # Limit output
            if len(final_state.get("incidents_summary", "")) > 2000:
                print("... (truncated)")

        # Print key insights
        if final_state.get("key_insights"):
            print("\n🔑 Key Insights:")
            for insight in final_state["key_insights"]:
                print(f"  • {insight}")

        # Print errors if any
        if final_state.get("errors"):
            print("\n⚠️  Errors encountered:")
            for error in final_state["errors"]:
                print(f"  • {error}")

        # Print Slack notification status
        if final_state.get("slack_sent"):
            print("\n✅ Slack notification sent successfully!")
        else:
            print("\n⚠️  Slack notification was not sent")

        return final_state

    except Exception as e:
        print(f"\n❌ Error running analysis: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    run_analysis()

