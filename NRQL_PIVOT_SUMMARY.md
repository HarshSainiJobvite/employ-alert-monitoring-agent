python main.py# NRQL-Based Frequent Condition Analysis - Implementation Summary

## Overview
Successfully pivoted the agent from fetching open incidents to analyzing the most frequent alert conditions from the past 7 days using New Relic NRQL queries.

## Changes Made

### 1. New File: `nrql_nodes.py`
Created three new workflow nodes for NRQL-based analysis:

#### `fetch_frequent_conditions_node`
- Executes NRQL query to find most frequent conditions matching `%jhire%` policy
- Uses GraphQL API with NRQL query:
  ```sql
  SELECT count(*) 
  FROM NrAiIncident 
  WHERE policyName LIKE '%jhire%' 
  FACET conditionName, conditionId, entity.name 
  SINCE 7 days ago 
  LIMIT 50
  ```
- Returns top 10 most frequent conditions sorted by occurrence count

#### `fetch_condition_details_node`
- Fetches latest 5 alerts for each frequent condition
- Retrieves detailed information: timestamp, priority, state, openedAt, closedAt, incidentId
- Stores all details in a structured format for analysis

#### `summarize_conditions_node`
- Creates structured summary with condition occurrence counts
- Generates AI-powered insights using IBM WatsonX Granite
- Provides actionable recommendations based on patterns
- Includes both raw data and intelligent analysis

### 2. Updated: `agent_state.py`
Added new state fields:
- `frequent_conditions`: List of most frequent conditions with metadata
- `condition_details`: Detailed information about alerts for each condition

### 3. Updated: `agent_graph.py`
Modified workflow to use NRQL-based nodes:
```
fetch_frequent_conditions → fetch_condition_details → summarize_conditions → send_notification → end
```

### 4. Updated: `main.py`
Initialized new state fields in the initial state configuration

## New Workflow Flow

```
Start
  ↓
fetch_frequent_conditions (NRQL query for top conditions)
  ↓
fetch_condition_details (Get latest 5 alerts per condition)
  ↓
summarize_conditions (AI-powered analysis)
  ↓
send_notification (Slack notification)
  ↓
End
```

## API Used

### GraphQL NerdGraph API
- **Endpoint**: `https://api.newrelic.com/graphql`
- **Authentication**: API-Key header
- **Query Type**: NRQL queries via GraphQL

### Example Request
```bash
curl -X POST https://api.newrelic.com/graphql \
  -H "API-Key: ${NR_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query($accountId: Int!, $nrqlQuery: Nrql!) { actor { account(id: $accountId) { nrql(query: $nrqlQuery) { results } } } }",
    "variables": { 
      "accountId": 1234567,
      "nrqlQuery": "SELECT count(*) FROM NrAiIncident WHERE policyName LIKE '%jhire%' FACET conditionName, conditionId, entity.name SINCE 7 days ago LIMIT 50"
    }
  }'
```

## Features

### 1. Frequency Analysis
- Identifies which alert conditions trigger most often
- Focuses on closed incidents from past 7 days
- Filters by policy name pattern (`%jhire%`)

### 2. Detailed Alert Information
- Fetches latest 5 occurrences per condition
- Includes priority, state, timestamps, and incident IDs
- Provides complete context for each alert

### 3. AI-Powered Insights
- Uses IBM WatsonX Granite for intelligent analysis
- Identifies patterns and trends
- Provides actionable remediation recommendations
- Generates concise executive summary

### 4. Structured Output
- Organized by condition with occurrence counts
- Entity information for each condition
- Timeline of recent alerts
- AI-generated insights and recommendations

## How to Run

```bash
# Ensure environment variables are set
export NEW_RELIC_API_KEY="your_api_key"
export NEW_RELIC_ACCOUNT_ID="your_account_id"
export WATSONX_APIKEY="your_watsonx_key"
export WATSONX_PROJECT_ID="your_project_id"
export SLACK_WEBHOOK_URL="your_slack_webhook"

# Run the agent
python main.py
```

## Expected Output

The agent will:
1. Query NRQL for most frequent conditions
2. Display top conditions with occurrence counts
3. Fetch details for each condition
4. Generate AI-powered summary with insights
5. Send comprehensive report to Slack

## Benefits

1. **Proactive Monitoring**: Identify recurring issues before they escalate
2. **Pattern Recognition**: AI identifies trends in alert frequency
3. **Prioritization**: Focus on most frequent problems first
4. **Actionable Insights**: AI provides specific recommendations
5. **Historical Context**: 7-day lookback provides meaningful patterns

## Testing

The import test confirms all modules load successfully:
```
✅ All NRQL nodes imported successfully
```

Note: IBM WatsonX shows a lifecycle warning about Granite 3-8b being deprecated, but it continues to work. Consider upgrading to `ibm/granite-4-h-small` in the future.

## Next Steps

1. Customize the NRQL query pattern (`%jhire%`) as needed
2. Adjust the time window (currently 7 days)
3. Modify the number of conditions analyzed (currently top 10)
4. Tune the number of recent alerts per condition (currently 5)
5. Customize AI analysis prompts for specific insights

## Configuration

Key parameters in `nrql_nodes.py`:
- **Policy Pattern**: `%jhire%` (line 31)
- **Time Window**: `7 days ago` (line 35)
- **Condition Limit**: `50` (line 36, top 10 tracked)
- **Alerts Per Condition**: `5` (line 127)

