"""Slack notification client."""
import requests
from typing import Dict, List, Any
from config import Config


class SlackClient:
    """Client for sending notifications to Slack."""

    def __init__(self):
        self.webhook_url = Config.SLACK_WEBHOOK_URL
        self.opsgenie_email = Config.OPSGENIE_SLACK_EMAIL

    def format_alert_message(self, alert_data: Dict[str, Any], actions: List[str]) -> Dict[str, Any]:
        """
        Format alert data into a Slack message with rich formatting.

        Args:
            alert_data: Formatted alert data from New Relic
            actions: List of recommended actions

        Returns:
            Slack message payload
        """
        top_affected = alert_data.get("top_affected", [])

        # Build affected users table
        affected_users_text = ""
        for idx, user in enumerate(top_affected[:10], 1):
            affected_users_text += (
                f"{idx}. Company ID: `{user['company_id']}` | "
                f"Email: `{user['email']}` | "
                f"Errors: *{user['error_count']}*\n"
            )

        # Build actions list
        actions_text = "\n".join([f"• {action}" for action in actions])

        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚨 New Relic Alert: NullPointerException Detected",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Total Errors:*\n{alert_data['total_errors']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Affected Users:*\n{alert_data['affected_users']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Affected Companies:*\n{alert_data['affected_companies']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Application:*\njhire"
                        }
                    ]
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Top 10 Affected Users:*\n{affected_users_text}"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Recommended Actions:*\n{actions_text}"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Alert sent to: {self.opsgenie_email}"
                        }
                    ]
                }
            ]
        }

        return message

    def send_alert(self, alert_data: Dict[str, Any], actions: List[str]) -> bool:
        """
        Send alert to Slack via webhook.

        Args:
            alert_data: Formatted alert data
            actions: List of recommended actions

        Returns:
            True if successful, False otherwise
        """
        try:
            message = self.format_alert_message(alert_data, actions)

            response = requests.post(
                self.webhook_url,
                json=message,
                timeout=10
            )
            response.raise_for_status()

            return True

        except requests.exceptions.RequestException as e:
            print(f"Failed to send Slack alert: {str(e)}")
            return False

    def send_to_opsgenie(self, alert_data: Dict[str, Any]) -> bool:
        """
        Send simplified alert to Opsgenie via email.

        Args:
            alert_data: Formatted alert data

        Returns:
            True if successful, False otherwise
        """
        # This would typically use an email service or Opsgenie API
        # For now, we'll include it in the Slack message
        print(f"Alert would be sent to Opsgenie email: {self.opsgenie_email}")
        return True

    def send_message_blocks(self, blocks: List[Dict[str, Any]]) -> bool:
        """
        Send a custom message with blocks to Slack.

        Args:
            blocks: List of Slack block elements

        Returns:
            True if successful, False otherwise
        """
        try:
            message = {"blocks": blocks}

            response = requests.post(
                self.webhook_url,
                json=message,
                timeout=10
            )
            response.raise_for_status()

            return True

        except requests.exceptions.RequestException as e:
            print(f"Failed to send Slack message: {str(e)}")
            return False
