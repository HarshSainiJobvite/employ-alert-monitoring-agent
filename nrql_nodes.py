"""Nodes for NRQL-based incident analysis."""
from typing import Dict, Any
import requests
from datetime import datetime
from agent_state import AgentState
from config import Config
from langchain_ibm import WatsonxLLM


# Initialize WatsonX LLM for summarization
llm = WatsonxLLM(
    model_id="ibm/granite-4-h-small",
    url=Config.WATSONX_URL,
    apikey=Config.WATSONX_APIKEY,
    project_id=Config.WATSONX_PROJECT_ID,
    params={
        "decoding_method": "greedy",
        "max_new_tokens": 2000,
        "temperature": 0.7,
        "top_k": 50,
        "top_p": 1
    }
)


def fetch_frequent_conditions_node(state: AgentState) -> AgentState:
    """Fetch most frequent conditions using NRQL."""
    print("🔍 Fetching most frequent conditions from past 7 days...")

    state["current_step"] = "fetch_frequent_conditions"

    nrql_query = """
    SELECT count(*) 
    FROM NrAiIncident 
    WHERE policyName LIKE '%jhire%' 
    FACET conditionName, conditionId, entity.name 
    SINCE 7 days ago 
    LIMIT 50
    """

    graphql_query = """
    query($accountId: Int!, $nrqlQuery: Nrql!) {
        actor {
            account(id: $accountId) {
                nrql(query: $nrqlQuery) {
                    results
                }
            }
        }
    }
    """

    payload = {
        "query": graphql_query,
        "variables": {
            "accountId": int(Config.NEW_RELIC_ACCOUNT_ID),
            "nrqlQuery": nrql_query
        }
    }

    try:
        response = requests.post(
            Config.GRAPHQL_ENDPOINT,
            headers={
                "API-Key": Config.NEW_RELIC_API_KEY,
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        data = response.json()
        results = data.get("data", {}).get("actor", {}).get("account", {}).get("nrql", {}).get("results", [])

        # Parse results - New Relic returns FACET fields as an array
        parsed_results = []
        for result in results:
            facet = result.get('facet', [])
            # FACET order: conditionName, conditionId, entity.name
            parsed_result = {
                'conditionName': facet[0] if len(facet) > 0 else 'Unknown',
                'conditionId': facet[1] if len(facet) > 1 else None,
                'entity.name': facet[2] if len(facet) > 2 else 'Unknown',
                'count': result.get('count', 0)
            }
            parsed_results.append(parsed_result)

        # Sort by count (descending) and take top conditions
        sorted_conditions = sorted(parsed_results, key=lambda x: x.get("count", 0), reverse=True)

        state["frequent_conditions"] = sorted_conditions[:10]  # Top 10

        print(f"✅ Found {len(sorted_conditions)} conditions, tracking top {len(state['frequent_conditions'])}")
        for i, cond in enumerate(state["frequent_conditions"][:5], 1):
            condition_name = cond.get('conditionName', 'Unknown')
            count = cond.get('count', 0)
            entity_name = cond.get('entity.name', 'Unknown')
            print(f"  {i}. {condition_name} ({entity_name}): {count} occurrences")

        if state["frequent_conditions"]:
            state["next_step"] = "fetch_condition_details"
        else:
            print("ℹ️  No frequent conditions found")
            state["incidents_summary"] = "No frequent conditions found in the past 7 days."
            state["key_insights"] = ["No alerts matching criteria"]
            state["next_step"] = "send_notification"

    except Exception as e:
        error_msg = f"Failed to fetch frequent conditions: {str(e)}"
        print(f"❌ {error_msg}")
        state["errors"].append(error_msg)
        state["next_step"] = "end"

    return state


def fetch_condition_details_node(state: AgentState) -> AgentState:
    """Fetch latest 5 alerts for each frequent condition."""
    print("🔍 Fetching details for each condition...")

    state["current_step"] = "fetch_condition_details"

    frequent_conditions = state.get("frequent_conditions", [])
    condition_details = {}

    for condition in frequent_conditions:
        condition_id = condition.get("conditionId")
        condition_name = condition.get("conditionName", "Unknown")

        if not condition_id:
            continue

        # Query using conditionName since that's what works
        nrql_query = f"""
        SELECT * 
        FROM NrAiIncident 
        WHERE conditionName = '{condition_name}' 
        SINCE 7 days ago 
        LIMIT 5
        """

        graphql_query = """
        query($accountId: Int!, $nrqlQuery: Nrql!) {
            actor {
                account(id: $accountId) {
                    nrql(query: $nrqlQuery) {
                        results
                    }
                }
            }
        }
        """

        payload = {
            "query": graphql_query,
            "variables": {
                "accountId": int(Config.NEW_RELIC_ACCOUNT_ID),
                "nrqlQuery": nrql_query
            }
        }

        try:
            response = requests.post(
                Config.GRAPHQL_ENDPOINT,
                headers={
                    "API-Key": Config.NEW_RELIC_API_KEY,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            # Check for errors in response
            if "errors" in data:
                error_msg = f"GraphQL errors: {data['errors']}"
                print(f"  ⚠️  {error_msg}")
                state["errors"].append(f"Failed to fetch details for condition {condition_id}: {error_msg}")
                continue

            # Navigate the response
            results = data.get("data", {}).get("actor", {}).get("account", {}).get("nrql", {}).get("results", [])

            condition_details[condition_name] = {
                "condition_id": condition_id,
                "occurrence_count": condition.get("count", 0),
                "entity_name": condition.get("entity.name", "Unknown"),
                "recent_alerts": results
            }

            print(f"  ✓ Fetched {len(results)} alerts for '{condition_name}'")

        except Exception as e:
            print(f"  ⚠️  Failed to fetch details for '{condition_name}': {str(e)}")
            state["errors"].append(f"Failed to fetch details for condition {condition_id}: {str(e)}")

    state["condition_details"] = condition_details

    # Check if "jhire Null Pointer Anomaly" is in top 5 conditions
    top_5_names = [cond.get('conditionName', '') for cond in frequent_conditions[:5]]
    if "jhire Null Pointer Anomaly" in top_5_names:
        print("🔍 Detected 'jhire Null Pointer Anomaly' in top 5 - fetching affected users and companies...")
        state["next_step"] = "fetch_null_pointer_details"
    else:
        state["next_step"] = "summarize_conditions"

    return state


def fetch_null_pointer_details_node(state: AgentState) -> AgentState:
    """Fetch company and user details for jhire Null Pointer Anomaly condition."""
    print("🔍 Fetching affected companies and users for NullPointerException...")

    state["current_step"] = "fetch_null_pointer_details"

    # NRQL query to get affected companies and users
    nrql_query = """
    SELECT count(*) 
    FROM TransactionError 
    WHERE appName='jhire' 
    AND error.class = 'java.lang.NullPointerException' 
    AND USER_EMAIL_ID!='wh-admin@jobvite-inc.com' 
    AND USER_EMAIL_ID != 'jvautometa+hire+engage+poweruser@gmail.com' 
    FACET USER_COMPANY_ID, USER_EMAIL_ID, error.class 
    SINCE 7 days ago
    LIMIT 50
    """

    graphql_query = """
    query($accountId: Int!, $nrqlQuery: Nrql!) {
        actor {
            account(id: $accountId) {
                nrql(query: $nrqlQuery) {
                    results
                }
            }
        }
    }
    """

    payload = {
        "query": graphql_query,
        "variables": {
            "accountId": int(Config.NEW_RELIC_ACCOUNT_ID),
            "nrqlQuery": nrql_query
        }
    }

    try:
        response = requests.post(
            Config.GRAPHQL_ENDPOINT,
            headers={
                "API-Key": Config.NEW_RELIC_API_KEY,
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        data = response.json()
        results = data.get("data", {}).get("actor", {}).get("account", {}).get("nrql", {}).get("results", [])

        # Parse the facet results
        affected_users = []
        for result in results:
            facet = result.get('facet', [])
            # FACET order: USER_COMPANY_ID, USER_EMAIL_ID, error.class
            user_info = {
                'company_id': facet[0] if len(facet) > 0 else 'Unknown',
                'email': facet[1] if len(facet) > 1 else 'Unknown',
                'error_class': facet[2] if len(facet) > 2 else 'Unknown',
                'error_count': result.get('count', 0)
            }
            affected_users.append(user_info)

        # Sort by error count (descending)
        affected_users.sort(key=lambda x: x['error_count'], reverse=True)

        # Store in condition_details
        condition_details = state.get("condition_details", {})
        if "jhire Null Pointer Anomaly" in condition_details:
            condition_details["jhire Null Pointer Anomaly"]["affected_users"] = affected_users[:20]  # Top 20
            condition_details["jhire Null Pointer Anomaly"]["total_affected_users"] = len(affected_users)

            # Get unique company count
            unique_companies = set(user['company_id'] for user in affected_users if user['company_id'] != 'Unknown')
            condition_details["jhire Null Pointer Anomaly"]["affected_companies_count"] = len(unique_companies)

        print(f"  ✓ Found {len(affected_users)} affected users across {len(unique_companies)} companies")

    except Exception as e:
        print(f"  ⚠️  Failed to fetch NullPointerException details: {str(e)}")
        state["errors"].append(f"Failed to fetch NullPointerException details: {str(e)}")

    state["next_step"] = "summarize_conditions"

    return state


def summarize_conditions_node(state: AgentState) -> AgentState:
    """Create AI-powered summary of frequent conditions and their alerts."""
    print("🤖 Creating AI summary with IBM WatsonX Granite...")

    state["current_step"] = "summarize_conditions"

    condition_details = state.get("condition_details", {})

    # Generate AI insights for each condition based on their recent alerts
    for cond_name, details in condition_details.items():
        recent_alerts = details.get('recent_alerts', [])

        if recent_alerts:
            print(f"🧠 Analyzing alerts for '{cond_name}'...")

            # Build structured alert data for AI analysis
            alert_data = []
            for alert in recent_alerts:
                alert_info = {
                    'priority': alert.get('priority', 'Unknown'),
                    'duration_seconds': alert.get('durationSeconds', 0),
                    'close_cause': alert.get('closeCause', 'Unknown'),
                    'timestamp': alert.get('timestamp', 0),
                    'title': alert.get('title', 'No title')
                }
                alert_data.append(alert_info)

            # Create prompt for condition-specific insights
            alerts_summary = "\n".join([
                f"- Alert {i+1}: Priority={a['priority']}, Duration={a['duration_seconds']}s, CloseCause={a['close_cause']}"
                for i, a in enumerate(alert_data)
            ])

            prompt = f"""Analyze these {len(recent_alerts)} recent alerts for condition "{cond_name}":

{alerts_summary}

Total occurrences in past 7 days: {details.get('occurrence_count', 0)}

Provide a concise 3-4 sentence analysis covering:
1. Pattern observed (frequency, severity trends)
2. Root cause or key issue identified
3. Impact assessment
4. Actionable recommendation

Keep it professional and actionable for DevOps engineers."""

            try:
                ai_insight = llm.invoke(prompt)
                insight_text = ai_insight if isinstance(ai_insight, str) else str(ai_insight)

                # Clean up and limit length
                insight_text = insight_text.strip()
                if len(insight_text) > 500:
                    insight_text = insight_text[:500] + "..."

                details['ai_insight'] = insight_text

            except Exception as e:
                print(f"⚠️  Failed to generate AI insight for '{cond_name}': {str(e)}")
                # Fallback insight
                avg_duration = sum(a['duration_seconds'] for a in alert_data) / len(alert_data) if alert_data else 0
                priority_counts = {}
                for a in alert_data:
                    p = a['priority']
                    priority_counts[p] = priority_counts.get(p, 0) + 1

                fallback = f"This condition triggered {details.get('occurrence_count', 0)} times in the past 7 days. "
                fallback += f"Recent alerts show average duration of {int(avg_duration//60)} minutes. "
                fallback += f"Priority distribution: {', '.join([f'{k}={v}' for k,v in priority_counts.items()])}. "
                fallback += "Review alert thresholds and consider investigating recurring patterns."

                details['ai_insight'] = fallback
        else:
            details['ai_insight'] = "No recent alert data available for analysis."

    # Build structured summary
    summary_parts = [
        f"# New Relic Alert Analysis - Most Frequent Conditions (Past 7 Days)",
        f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total Unique Conditions: {len(condition_details)}\n"
    ]

    for i, (cond_name, details) in enumerate(condition_details.items(), 1):
        summary_parts.append(f"\n## {i}. {cond_name}")
        summary_parts.append(f"- **Occurrences**: {details['occurrence_count']}")
        summary_parts.append(f"- **Entity**: {details['entity_name']}")
        summary_parts.append(f"- **Condition ID**: {details['condition_id']}")
        summary_parts.append(f"\n### AI Analysis:")
        summary_parts.append(details.get('ai_insight', 'No insight available'))

        # Add latest alert as example
        recent_alerts = details.get('recent_alerts', [])
        if recent_alerts:
            latest = recent_alerts[0]
            summary_parts.append(f"\n### Latest Alert Example:")
            summary_parts.append(f"- Incident ID: {latest.get('incidentId', 'N/A')}")
            summary_parts.append(f"- Priority: {latest.get('priority', 'Unknown')}")
            summary_parts.append(f"- Duration: {latest.get('durationSeconds', 0)} seconds")
            summary_parts.append(f"- Close Cause: {latest.get('closeCause', 'Unknown')}")

    structured_summary = "\n".join(summary_parts)
    state["incidents_summary"] = structured_summary

    # Extract key insights for notification
    insights = []
    for cond_name, details in list(condition_details.items())[:3]:
        insights.append(f"{cond_name}: {details['occurrence_count']} occurrences")

    state["key_insights"] = insights

    print("✅ Summary created with AI insights for each condition")

    state["next_step"] = "send_notification"

    return state
