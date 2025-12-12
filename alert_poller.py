"""
Polling-based alert monitor that queries New Relic API for open incidents.
This approach doesn't require webhooks - perfect for local development!
"""
import time
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
from config import Config


class NewRelicAlertPoller:
    """
    Polls New Relic API to check for open incidents/violations.
    No webhook needed - queries the API directly.
    """

    def __init__(self):
        self.api_key = Config.NEW_RELIC_API_KEY
        self.account_id = Config.NEW_RELIC_ACCOUNT_ID
        self.graphql_endpoint = Config.GRAPHQL_ENDPOINT
        self.headers = {
            "API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        self.processed_incidents = set()  # Track already processed incidents

    def get_open_incidents(self) -> List[Dict[str, Any]]:
        """
        Query New Relic NerdGraph API for currently open incidents.
        Uses the aiIssues query with correct structure.

        Returns:
            List of open incidents
        """
        query = """
        query($accountId: Int!) {
          actor {
            account(id: $accountId) {
              aiIssues {
                issues(filter: {states: [CREATED, ACTIVATED]}) {
                  issues {
                    issueId
                    title
                    priority
                    state
                    createdAt
                    updatedAt
                    closedAt
                    sources
                  }
                }
              }
            }
          }
        }
        """

        variables = {
            "accountId": int(self.account_id)
        }

        payload = {
            "query": query,
            "variables": variables
        }

        try:
            response = requests.post(
                self.graphql_endpoint,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            if "errors" in data:
                print(f"⚠️  GraphQL errors: {data['errors']}")
                return []

            # Extract issues from the correct structure
            issues_wrapper = data.get("data", {}).get("actor", {}).get("account", {}).get("aiIssues", {}).get("issues", {})
            issues_list = issues_wrapper.get("issues", [])

            print(f"📊 Found {len(issues_list)} open issues in New Relic")

            incidents = []
            for issue in issues_list:
                try:
                    # Extract sources to get condition and policy names
                    sources = issue.get("sources", [])
                    condition_name = ""
                    policy_name = ""

                    if sources and len(sources) > 0:
                        first_source = sources[0]
                        # Check if source is a dict (object) or string
                        if isinstance(first_source, dict):
                            condition_name = first_source.get("title", "")
                        elif isinstance(first_source, str):
                            # If it's a string, use it directly
                            condition_name = first_source

                    incidents.append({
                        "incidentId": issue.get("issueId"),
                        "title": issue.get("title"),
                        "priority": issue.get("priority"),
                        "state": "OPEN",
                        "openedAt": issue.get("createdAt"),
                        "closedAt": issue.get("closedAt"),
                        "conditionName": condition_name or issue.get("title", ""),
                        "policyName": policy_name
                    })
                except Exception as e:
                    print(f"⚠️  Error parsing issue: {str(e)}")
                    continue

            return incidents

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to query incidents: {str(e)}")
            return []

    def check_for_matching_incidents(self, condition_name_pattern: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Check for open incidents that match criteria.

        Args:
            condition_name_pattern: Optional pattern to match in condition name

        Returns:
            List of matching incidents that haven't been processed yet
        """
        all_incidents = self.get_open_incidents()

        new_incidents = []
        for incident in all_incidents:
            incident_id = incident.get("incidentId")

            # Skip if already processed
            if incident_id in self.processed_incidents:
                continue

            # Filter by condition name if specified
            if condition_name_pattern:
                condition_name = incident.get("conditionName", "")
                title = incident.get("title", "")

                # Ensure both are strings (handle lists or other types)
                if not isinstance(condition_name, str):
                    condition_name = str(condition_name) if condition_name else ""
                if not isinstance(title, str):
                    title = str(title) if title else ""

                # Search in both condition name and title
                if condition_name_pattern.lower() not in condition_name.lower() and \
                   condition_name_pattern.lower() not in title.lower():
                    continue

            new_incidents.append(incident)
            self.processed_incidents.add(incident_id)

        return new_incidents

    def display_all_open_incidents(self, condition_pattern: Optional[str] = None):
        """
        Display all currently open incidents without marking them as processed.

        Args:
            condition_pattern: Optional pattern to match in condition name
        """
        all_incidents = self.get_open_incidents()

        if not all_incidents:
            print("No open incidents found.")
            return

        # Filter by pattern if specified
        filtered_incidents = []
        for incident in all_incidents:
            if condition_pattern:
                condition_name = incident.get("conditionName", "")
                title = incident.get("title", "")

                # Ensure both are strings
                if not isinstance(condition_name, str):
                    condition_name = str(condition_name) if condition_name else ""
                if not isinstance(title, str):
                    title = str(title) if title else ""

                # Search in both condition name and title
                if condition_pattern.lower() not in condition_name.lower() and \
                   condition_pattern.lower() not in title.lower():
                    continue

            filtered_incidents.append(incident)

        print(f"\n{'='*60}")
        print(f"📋 Currently Open Incidents: {len(filtered_incidents)}")
        print(f"{'='*60}\n")

        for i, incident in enumerate(filtered_incidents, 1):
            print(f"{i}. Incident ID: {incident.get('incidentId')}")
            print(f"   Title: {incident.get('title')}")
            print(f"   Condition: {incident.get('conditionName')}")
            print(f"   Priority: {incident.get('priority')}")
            print(f"   Opened At: {incident.get('openedAt')}")
            print(f"   State: {incident.get('state')}")
            print()

    def poll_continuously(self, interval_seconds: int = 60, condition_pattern: Optional[str] = None, show_initial: bool = True):
        """
        Continuously poll for new incidents.

        Args:
            interval_seconds: How often to poll (default: 60 seconds)
            condition_pattern: Optional pattern to match in condition name
            show_initial: Whether to show initial open incidents on startup (default: True)
        """
        print("="*60)
        print("🔄 Starting New Relic Alert Poller")
        print("="*60)
        print(f"Account ID: {self.account_id}")
        print(f"Poll Interval: {interval_seconds} seconds")
        if condition_pattern:
            print(f"Filter Pattern: {condition_pattern}")
        print()
        print("Polling for incidents... Press Ctrl+C to stop")
        print("="*60)
        print()

        try:
            # Show initial open incidents if requested
            if show_initial:
                print("🔍 Checking for currently open incidents...\n")
                self.display_all_open_incidents(condition_pattern)
                print(f"{'='*60}")
                print("👀 Now monitoring for NEW incidents...")
                print(f"{'='*60}\n")

            while True:
                try:
                    # Check for new incidents
                    new_incidents = self.check_for_matching_incidents(condition_pattern)

                    if new_incidents:
                        print(f"\n🔔 Found {len(new_incidents)} new incident(s)!")

                        for incident in new_incidents:
                            print(f"\n{'='*60}")
                            print(f"📨 New Incident Detected")
                            print(f"{'='*60}")
                            print(f"Incident ID: {incident.get('incidentId')}")
                            print(f"Title: {incident.get('title')}")
                            print(f"Condition: {incident.get('conditionName')}")
                            print(f"Policy: {incident.get('policyName')}")
                            print(f"Priority: {incident.get('priority')}")
                            print(f"Opened At: {incident.get('openedAt')}")
                            print(f"{'='*60}\n")

                            # Yield this incident for processing
                            yield incident
                    else:
                        # No new incidents
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"[{timestamp}] ✓ No new incidents", end="\r")

                except Exception as e:
                    print(f"\n⚠️  Error during poll: {str(e)}")

                # Wait before next poll
                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            print("\n\n🛑 Polling stopped by user")
            print("Goodbye!")


# Convenience function to get the poller instance
def create_poller() -> NewRelicAlertPoller:
    """Create a new alert poller instance."""
    return NewRelicAlertPoller()
