"""New Relic NerdGraph API client.

This client uses New Relic's NerdGraph (GraphQL) API to execute NRQL queries.
Documentation: https://docs.newrelic.com/docs/apis/nerdgraph/get-started/introduction-new-relic-nerdgraph/
"""
import requests
from typing import Dict, List, Any, Optional
from config import Config


class NewRelicClient:
    """Client for interacting with New Relic NerdGraph API."""

    def __init__(self):
        self.api_key = Config.NEW_RELIC_API_KEY
        self.account_id = Config.NEW_RELIC_ACCOUNT_ID
        self.graphql_endpoint = Config.GRAPHQL_ENDPOINT
        self.headers = {
            "API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def execute_nrql_query(self, query: str) -> Dict[str, Any]:
        """
        Execute a NRQL query using New Relic's NerdGraph (GraphQL) API.

        Args:
            query: The NRQL query to execute

        Returns:
            Query results as a dictionary
        """
        graphql_query = """
        query($accountId: Int!, $nrql: Nrql!) {
          actor {
            account(id: $accountId) {
              nrql(query: $nrql) {
                results
                metadata {
                  timeWindow {
                    begin
                    end
                  }
                  eventTypes
                }
              }
            }
          }
        }
        """

        variables = {
            "accountId": int(self.account_id),
            "nrql": query
        }

        payload = {
            "query": graphql_query,
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
                raise Exception(f"GraphQL errors: {data['errors']}")

            return data.get("data", {}).get("actor", {}).get("account", {}).get("nrql", {})

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to execute NRQL query: {str(e)}")

    def get_alert_analysis(self, start_time: Optional[str] = None, end_time: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute the analysis query to get affected users and companies.

        Args:
            start_time: Optional start time for the query
            end_time: Optional end time for the query

        Returns:
            Analysis results
        """
        query = Config.ANALYSIS_QUERY

        # Optionally modify query with specific time range
        if start_time and end_time:
            query = query.replace("SINCE 7 days ago", f"SINCE '{start_time}' UNTIL '{end_time}'")

        return self.execute_nrql_query(query)

    def parse_faceted_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse faceted NRQL results into a structured format.

        Args:
            results: Raw NRQL query results

        Returns:
            List of parsed results with company_id, email, and count
        """
        parsed_data = []

        raw_results = results.get("results", [])

        for item in raw_results:
            # Extract facet values
            facet = item.get("facet", [])
            count = item.get("count", 0)

            # Facet should contain [USER_COMPANY_ID, USER_EMAIL_ID]
            if len(facet) >= 2:
                company_id = facet[0]
                email = facet[1]

                parsed_data.append({
                    "company_id": company_id,
                    "email": email,
                    "error_count": count
                })

        # Sort by error count (descending)
        parsed_data.sort(key=lambda x: x["error_count"], reverse=True)

        return parsed_data

    def format_alert_data(self, analysis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Format analysis results into a structured alert data.

        Args:
            analysis_results: Parsed analysis results

        Returns:
            Formatted alert data
        """
        total_errors = sum(item["error_count"] for item in analysis_results)
        affected_users = len(analysis_results)
        affected_companies = len(set(item["company_id"] for item in analysis_results))

        return {
            "total_errors": total_errors,
            "affected_users": affected_users,
            "affected_companies": affected_companies,
            "top_affected": analysis_results[:10],  # Top 10 affected users
            "all_affected": analysis_results
        }
