"""
Main polling server that continuously checks New Relic for alerts
and triggers the agent when new incidents are detected.

No webhook needed - perfect for local development!
"""
import sys
from datetime import datetime, timedelta
from alert_poller import create_poller
from agent_graph import create_agent_graph
from agent_state import AgentState
from config import Config


def process_incident(incident: dict):
    """
    Process a detected incident through the agent workflow.

    Args:
        incident: Incident data from New Relic
    """
    print("\n" + "="*60)
    print("🤖 Processing Incident with Agent")
    print("="*60)

    try:
        # Extract time window from incident
        opened_at = incident.get('openedAt')
        if opened_at:
            # Parse timestamp and create time window
            opened_time = datetime.fromisoformat(opened_at.replace('Z', '+00:00'))
            time_start = opened_time - timedelta(minutes=5)
            time_end = opened_time + timedelta(minutes=2)
        else:
            # Default to recent time window
            time_end = datetime.now()
            time_start = time_end - timedelta(minutes=10)

        # Create agent
        agent = create_agent_graph()

        # Create initial state
        initial_state: AgentState = {
            "alert_triggered": True,
            "alert_query": Config.ALERT_QUERY,
            "alert_time_start": time_start.strftime("%Y-%m-%d %H:%M:%S +00:00"),
            "alert_time_end": time_end.strftime("%Y-%m-%d %H:%M:%S +00:00"),
            "analysis_results": None,
            "parsed_data": None,
            "formatted_alert": None,
            "analysis_summary": None,
            "recommended_actions": None,
            "slack_sent": False,
            "opsgenie_sent": False,
            "errors": [],
            "current_step": "init",
            "next_step": None
        }

        # Run the agent
        print("\n🚀 Starting agent workflow...\n")
        final_state = agent.invoke(initial_state)

        # Report results
        print("\n" + "="*60)
        print("✅ Incident Processing Complete")
        print("="*60)

        if final_state.get("formatted_alert"):
            alert = final_state["formatted_alert"]
            print(f"Total Errors: {alert['total_errors']}")
            print(f"Affected Users: {alert['affected_users']}")
            print(f"Affected Companies: {alert['affected_companies']}")

        print(f"Slack Sent: {'✅' if final_state.get('slack_sent') else '❌'}")
        print(f"Opsgenie Sent: {'✅' if final_state.get('opsgenie_sent') else '❌'}")

        if final_state.get("errors"):
            print(f"\n⚠️  Errors: {final_state['errors']}")

        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ Error processing incident: {str(e)}")
        import traceback
        traceback.print_exc()


def start_polling_server(
    poll_interval: int = 60,
    condition_pattern: str = None
):
    """
    Start the polling server that continuously checks for alerts.

    Args:
        poll_interval: Seconds between polls (default: 60)
        condition_pattern: Optional filter for condition names
    """
    print("="*60)
    print("🚀 New Relic Alert Poller - Starting")
    print("="*60)
    print()
    print("This server polls New Relic API for open incidents")
    print("No webhook needed - perfect for local development!")
    print()

    # Validate configuration
    try:
        Config.validate()
        print("✅ Configuration validated")
    except ValueError as e:
        print(f"❌ Configuration error: {str(e)}")
        print("\nPlease set up your .env file with:")
        print("  - NEW_RELIC_API_KEY")
        print("  - NEW_RELIC_ACCOUNT_ID")
        print("  - SLACK_WEBHOOK_URL")
        print("  - OPENAI_API_KEY")
        sys.exit(1)

    print()
    print(f"Poll Interval: {poll_interval} seconds")
    if condition_pattern:
        print(f"Condition Filter: {condition_pattern}")
    print()
    print("="*60)
    print()

    # Create poller
    poller = create_poller()

    # Start polling loop
    for incident in poller.poll_continuously(
        interval_seconds=poll_interval,
        condition_pattern=condition_pattern
    ):
        # Process each detected incident
        process_incident(incident)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="New Relic Alert Poller - No webhook needed!"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Poll interval in seconds (default: 60)"
    )
    parser.add_argument(
        "--condition",
        type=str,
        default="NullPointerException",
        help="Filter by condition name pattern (default: NullPointerException)"
    )
    parser.add_argument(
        "--no-filter",
        action="store_true",
        help="Process all incidents (no condition filter)"
    )

    args = parser.parse_args()

    condition_filter = None if args.no_filter else args.condition

    start_polling_server(
        poll_interval=args.interval,
        condition_pattern=condition_filter
    )

