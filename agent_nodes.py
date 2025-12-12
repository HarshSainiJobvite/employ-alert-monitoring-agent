"""Agent node functions for the LangGraph workflow."""
from typing import Dict, Any
from langchain_ibm import WatsonxLLM
from agent_state import AgentState
from alert_poller import create_poller
from slack_client import SlackClient
from config import Config


# Initialize clients
slack_client = SlackClient()

# Initialize WatsonX LLM
print("🤖 Initializing IBM WatsonX Granite for AI reasoning")
llm = WatsonxLLM(
    model_id="ibm/granite-3-8b-instruct",
    url=Config.WATSONX_URL,
    apikey=Config.WATSONX_APIKEY,
    project_id=Config.WATSONX_PROJECT_ID,
    params={
        "decoding_method": "greedy",
        "max_new_tokens": 1500,
        "temperature": 0.7,
        "top_k": 50,
        "top_p": 1
    }
)
print("✅ IBM WatsonX Granite 3 8B Instruct initialized successfully")


def fetch_incidents_node(state: AgentState) -> AgentState:
    """
    Node to fetch all open incidents from New Relic.
    """
    print("🔍 Fetching open incidents from New Relic...")

    state["current_step"] = "fetch_incidents"

    try:
        # Create poller and get incidents
        poller = create_poller()
        incidents = poller.get_open_incidents()

        state["open_incidents"] = incidents
        state["incident_count"] = len(incidents)

        print(f"✅ Fetched {len(incidents)} open incidents")

        if incidents:
            state["next_step"] = "summarize_incidents"
        else:
            print("ℹ️  No open incidents found")
            state["incidents_summary"] = "No open incidents at this time."
            state["key_insights"] = ["All systems operational"]
            state["next_step"] = "send_notification"

    except Exception as e:
        error_msg = f"Failed to fetch incidents: {str(e)}"
        print(f"❌ {error_msg}")
        state["errors"].append(error_msg)
        state["next_step"] = "end"

    return state


def summarize_incidents_node(state: AgentState) -> AgentState:
    """
    Node to summarize incidents using WatsonX AI.
    """
    print("🤖 Summarizing incidents with IBM WatsonX Granite...")

    state["current_step"] = "summarize_incidents"

    try:
        incidents = state["open_incidents"]
        incident_count = state["incident_count"]

        # Group incidents by priority
        priority_groups = {"CRITICAL": [], "HIGH": [], "MEDIUM": [], "LOW": []}

        # Categorize incidents by type
        infrastructure_incidents = []  # CPU, Memory, Disk, Network
        application_incidents = []     # Errors, Exceptions, Timeouts
        other_incidents = []

        infrastructure_keywords = ['cpu', 'memory', 'disk', 'ram', 'storage', 'network', 'bandwidth', 'latency', 'connection']
        error_keywords = ['error', 'exception', 'failure', 'timeout', 'crash', 'bug', 'null', 'fatal']

        for incident in incidents:
            priority = incident.get("priority", "UNKNOWN")
            if priority in priority_groups:
                priority_groups[priority].append(incident)
            else:
                priority_groups.setdefault("OTHER", []).append(incident)

            # Categorize by type based on title
            title = incident.get('title', '')

            # Handle case where title might be a list or other type
            if isinstance(title, list):
                title_lower = ' '.join(str(t) for t in title).lower()
            elif isinstance(title, str):
                title_lower = title.lower()
            else:
                title_lower = str(title).lower()

            if any(keyword in title_lower for keyword in infrastructure_keywords):
                infrastructure_incidents.append(incident)
            elif any(keyword in title_lower for keyword in error_keywords):
                application_incidents.append(incident)
            else:
                other_incidents.append(incident)

        # Format incident details for LLM with categories
        infrastructure_details = []
        for incident in infrastructure_incidents[:10]:
            detail = f"- [{incident.get('priority')}] {incident.get('title')} (ID: {incident.get('incidentId')}, Opened: {incident.get('openedAt')})"
            infrastructure_details.append(detail)

        application_details = []
        for incident in application_incidents[:10]:
            detail = f"- [{incident.get('priority')}] {incident.get('title')} (ID: {incident.get('incidentId')}, Opened: {incident.get('openedAt')})"
            application_details.append(detail)

        infrastructure_list = "\n".join(infrastructure_details) if infrastructure_details else "None"
        application_list = "\n".join(application_details) if application_details else "None"

        # Count by priority
        priority_summary = []
        for priority, items in priority_groups.items():
            if items:
                priority_summary.append(f"{priority}: {len(items)}")

        priority_counts = ", ".join(priority_summary)

        # Create enhanced prompt for LLM with categorization
        prompt = f"""You are an expert Site Reliability Engineer analyzing open incidents in New Relic.

Current Situation:
Total Open Incidents: {incident_count}
Priority Breakdown: {priority_counts}

INCIDENT CATEGORIZATION:
Infrastructure Incidents (CPU/Memory/Network): {len(infrastructure_incidents)}
Application Incidents (Errors/Exceptions): {len(application_incidents)}
Other Incidents: {len(other_incidents)}

INFRASTRUCTURE INCIDENTS (CPU/Memory/Network - Top 10):
{infrastructure_list}

APPLICATION INCIDENTS (Errors/Exceptions - Top 10):
{application_list}

Please provide a categorized analysis:

1. EXECUTIVE SUMMARY: A concise 2-3 sentence overview of the overall incident situation

2. INFRASTRUCTURE ANALYSIS: 
   - Key insights about CPU, memory, disk, or network issues
   - Patterns you notice in infrastructure incidents
   - Recommendations for infrastructure-related problems

3. APPLICATION ANALYSIS:
   - Key insights about errors, exceptions, or application failures  
   - Patterns you notice in application incidents
   - Recommendations for application-related problems

4. PRIORITY ACTIONS: Top 3-5 most critical actions the team should take immediately

Format your response EXACTLY as:
SUMMARY:
[your executive summary]

INFRASTRUCTURE:
- [infrastructure insight 1]
- [infrastructure insight 2]
- [infrastructure recommendation]

APPLICATION:
- [application insight 1]
- [application insight 2]
- [application recommendation]

PRIORITY ACTIONS:
- [critical action 1]
- [critical action 2]
- [critical action 3]
"""

        # Invoke WatsonX LLM
        print("🧠 Generating AI analysis...")
        response = llm.invoke(prompt)

        # Extract content from WatsonX response
        content = response if isinstance(response, str) else str(response)

        # Parse response sections
        summary = ""
        infrastructure_insights = []
        application_insights = []
        priority_actions = []

        if "SUMMARY:" in content:
            parts = content.split("INFRASTRUCTURE:")
            summary = parts[0].replace("SUMMARY:", "").strip()

            if len(parts) > 1:
                infra_part = parts[1].split("APPLICATION:")[0].strip()
                infrastructure_insights = [
                    line.strip().lstrip("-•*").strip()
                    for line in infra_part.split("\n")
                    if line.strip() and line.strip()[0] in ["-", "•", "*"]
                ]

                if "APPLICATION:" in parts[1]:
                    app_part = parts[1].split("APPLICATION:")[1].split("PRIORITY ACTIONS:")[0].strip()
                    application_insights = [
                        line.strip().lstrip("-•*").strip()
                        for line in app_part.split("\n")
                        if line.strip() and line.strip()[0] in ["-", "•", "*"]
                    ]

                if "PRIORITY ACTIONS:" in content:
                    actions_part = content.split("PRIORITY ACTIONS:")[1].strip()
                    priority_actions = [
                        line.strip().lstrip("-•*").strip()
                        for line in actions_part.split("\n")
                        if line.strip() and line.strip()[0] in ["-", "•", "*"]
                    ]

        # Fallback if parsing failed
        if not summary:
            summary = f"Currently monitoring {incident_count} open incidents: {len(infrastructure_incidents)} infrastructure-related and {len(application_incidents)} application-related issues."

        if not infrastructure_insights:
            infrastructure_insights = [
                f"{len(infrastructure_incidents)} infrastructure incidents detected",
                "Monitoring CPU, memory, and network performance" if infrastructure_incidents else "No infrastructure issues"
            ]

        if not application_insights:
            application_insights = [
                f"{len(application_incidents)} application incidents detected",
                "Monitoring errors, exceptions, and failures" if application_incidents else "No application errors"
            ]

        if not priority_actions:
            priority_actions = [
                "Review critical priority incidents first",
                "Investigate infrastructure bottlenecks" if infrastructure_incidents else "Check application error logs",
                "Monitor system health metrics"
            ]

        # Combine all insights with category labels
        all_insights = []

        if infrastructure_insights:
            all_insights.append("**Infrastructure (CPU/Memory/Network):**")
            all_insights.extend(infrastructure_insights)

        if application_insights:
            all_insights.append("**Application (Errors/Exceptions):**")
            all_insights.extend(application_insights)

        if priority_actions:
            all_insights.append("**Priority Actions:**")
            all_insights.extend(priority_actions)

        state["incidents_summary"] = summary
        state["key_insights"] = all_insights

        print(f"✅ AI summary generated with {len(all_insights)} categorized insights")
        print(f"   📊 Infrastructure: {len(infrastructure_incidents)} incidents")
        print(f"   🐛 Application: {len(application_incidents)} incidents")
        state["next_step"] = "send_notification"

    except Exception as e:
        error_msg = f"Failed to summarize incidents: {str(e)}"
        print(f"❌ {error_msg}")
        state["errors"].append(error_msg)

        # Provide fallback summary
        state["incidents_summary"] = f"Found {state['incident_count']} open incidents in New Relic."
        state["key_insights"] = ["Manual review required", "Check New Relic dashboard for details"]
        state["next_step"] = "send_notification"

    return state


def send_notification_node(state: AgentState) -> AgentState:
    """
    Node to send incident summary to Slack.
    """
    print("📢 Sending summary to Slack...")

    state["current_step"] = "send_notification"

    try:
        incidents = state["open_incidents"] or []
        incident_count = state["incident_count"]
        summary = state["incidents_summary"]
        insights = state["key_insights"] or []

        # Format Slack message
        slack_blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📊 New Relic Incidents Summary",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Total Open Incidents:* {incident_count}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Executive Summary:*\n{summary}"
                }
            }
        ]

        # Add insights
        if insights:
            insights_text = "\n".join([f"• {insight}" for insight in insights])
            slack_blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Key Insights & Recommendations:*\n{insights_text}"
                }
            })

        # Add top incidents (up to 10)
        if incidents:
            slack_blocks.append({"type": "divider"})
            slack_blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Top Incidents (showing {min(10, len(incidents))} of {len(incidents)}):*"
                }
            })

            for incident in incidents[:10]:
                priority_emoji = {
                    "CRITICAL": "🔴",
                    "HIGH": "🟠",
                    "MEDIUM": "🟡",
                    "LOW": "🟢"
                }.get(incident.get("priority"), "⚪")

                incident_text = (
                    f"{priority_emoji} *{incident.get('title')}*\n"
                    f"Priority: {incident.get('priority')} | "
                    f"ID: `{incident.get('incidentId')}`\n"
                    f"Opened: {incident.get('openedAt')}"
                )

                slack_blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": incident_text
                    }
                })

        # Add timestamp
        from datetime import datetime
        slack_blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            ]
        })

        # Send to Slack
        success = slack_client.send_message_blocks(slack_blocks)
        state["slack_sent"] = success

        if success:
            print("✅ Summary sent to Slack successfully")
        else:
            print("⚠️  Failed to send to Slack")

        state["next_step"] = "end"

    except Exception as e:
        error_msg = f"Failed to send notification: {str(e)}"
        print(f"❌ {error_msg}")
        state["errors"].append(error_msg)
        state["next_step"] = "end"

    return state


def end_node(state: AgentState) -> AgentState:
    """
    Terminal node to finalize the workflow.
    """
    print("\n" + "="*60)
    print("🏁 Workflow Complete")
    print("="*60)

    print(f"Incidents Processed: {state.get('incident_count', 0)}")
    print(f"Slack Sent: {'✅' if state.get('slack_sent') else '❌'}")

    if state.get("errors"):
        print(f"\n⚠️  Errors encountered: {len(state['errors'])}")
        for error in state["errors"]:
            print(f"  - {error}")

    state["current_step"] = "end"
    state["next_step"] = None

    return state
