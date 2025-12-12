"""Configuration management for New Relic Agent."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for the New Relic Agent."""

    # New Relic Configuration
    NEW_RELIC_API_KEY = os.getenv("NEW_RELIC_API_KEY")
    NEW_RELIC_ACCOUNT_ID = os.getenv("NEW_RELIC_ACCOUNT_ID")
    NEW_RELIC_REGION = os.getenv("NEW_RELIC_REGION", "US")

    # NerdGraph API Endpoints (GraphQL)
    # Documentation: https://docs.newrelic.com/docs/apis/nerdgraph/get-started/introduction-new-relic-nerdgraph/
    if NEW_RELIC_REGION == "EU":
        GRAPHQL_ENDPOINT = "https://api.eu.newrelic.com/graphql"
    else:
        GRAPHQL_ENDPOINT = "https://api.newrelic.com/graphql"

    # Slack Configuration
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
    OPSGENIE_SLACK_EMAIL = os.getenv(
        "OPSGENIE_SLACK_EMAIL",
        "opsgenie-jv-aaaapspxg6qkfwmd4rye7f46na@grid-employinc.org.slack.com"
    )

    # IBM WatsonX Configuration (REQUIRED)
    WATSONX_APIKEY = os.getenv("WATSONX_APIKEY") or os.getenv("WATSONX_API_KEY")
    WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID") or os.getenv("WATSONX_PROJECTID")
    WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

    # LLM Configuration - WatsonX ONLY
    USE_WATSONX = True  # Always use WatsonX

    # Alert Query Configuration
    ALERT_QUERY = """
    SELECT count(*) 
    FROM TransactionError 
    WHERE appName='jhire' 
    AND error.class = 'java.lang.NullPointerException' 
    AND USER_EMAIL_ID!='wh-admin@jobvite-inc.com' 
    AND USER_EMAIL_ID != 'jvautometa+hire+engage+poweruser@gmail.com' 
    TIMESERIES 1 SECOND 
    SINCE '2025-12-11 12:34:27 +05:30' 
    UNTIL '2025-12-11 12:36:30 +05:30'
    """

    # Analysis Query Configuration
    ANALYSIS_QUERY = """
    SELECT count(*) 
    FROM TransactionError 
    WHERE appName='jhire' 
    AND error.class = 'java.lang.NullPointerException' 
    AND USER_EMAIL_ID!='wh-admin@jobvite-inc.com' 
    AND USER_EMAIL_ID != 'jvautometa+hire+engage+poweruser@gmail.com' 
    FACET USER_COMPANY_ID,USER_EMAIL_ID 
    TIMESERIES 1 hour 
    SINCE 7 days ago
    """

    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        required = [
            ("NEW_RELIC_API_KEY", cls.NEW_RELIC_API_KEY),
            ("NEW_RELIC_ACCOUNT_ID", cls.NEW_RELIC_ACCOUNT_ID),
            ("SLACK_WEBHOOK_URL", cls.SLACK_WEBHOOK_URL),
            ("WATSONX_APIKEY", cls.WATSONX_APIKEY),
            ("WATSONX_PROJECT_ID", cls.WATSONX_PROJECT_ID),
        ]

        missing = [name for name, value in required if not value]
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
