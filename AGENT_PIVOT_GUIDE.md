# 🔄 Agent Pivot - Incident Summary Workflow

## Overview

The agent behavior has been **completely pivoted** from the original alert-based workflow to a new incident summary workflow.

### ✨ New Behavior

The agent now:
1. **Fetches** all open incidents from New Relic
2. **Summarizes** incidents using IBM WatsonX Granite AI
3. **Sends** the summary to Slack channel

### 🗑️ Original Behavior (Removed)

- ❌ Detecting specific alerts
- ❌ Running NRQL queries for analysis
- ❌ Analyzing NullPointerException errors
- ❌ Sending to Opsgenie

---

## 🏗️ New Architecture

### Workflow Steps

```
┌─────────────────────┐
│  Fetch Incidents    │  → Queries New Relic API for all open incidents
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Summarize Incidents │  → WatsonX AI analyzes and creates executive summary
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Send Notification   │  → Sends formatted summary to Slack
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│        End          │  → Workflow complete
└─────────────────────┘
```

### Modified Files

1. **agent_state.py** - Simplified state for incident summary workflow
2. **agent_nodes.py** - New nodes: fetch_incidents, summarize_incidents, send_notification
3. **agent_graph.py** - Updated workflow graph
4. **slack_client.py** - Added `send_message_blocks()` method
5. **run_summary.py** - NEW: Simple script to run the workflow once

---

## 🚀 How to Use

### Option 1: Run Once (Immediate Summary)

```bash
python run_summary.py
```

This will:
- Fetch all current open incidents
- Generate AI summary
- Send to Slack
- Exit

### Option 2: View Incidents Only (No AI)

```bash
python view_incidents.py
```

Shows raw incident list without AI analysis or Slack notification.

---

## 📊 What Gets Sent to Slack

### Message Format

**Header:** 📊 New Relic Incidents Summary

**Content:**
- Total open incidents count
- Executive summary (AI-generated)
- Key insights & recommendations (AI-generated)
- Top 10 incidents with details:
  - Priority (with emoji: 🔴 CRITICAL, 🟠 HIGH, 🟡 MEDIUM, 🟢 LOW)
  - Title
  - Incident ID
  - Opened timestamp

**Example Summary:**

```
📊 New Relic Incidents Summary

Total Open Incidents: 50

Executive Summary:
Currently monitoring 50 open incidents across the platform with varying 
severity levels. The majority are medium priority infrastructure alerts 
with several high-priority application errors requiring immediate attention.

Key Insights & Recommendations:
• Total of 50 incidents requiring attention
• Priority distribution: CRITICAL: 5, HIGH: 12, MEDIUM: 28, LOW: 5
• Multiple systems affected - database and API services showing strain
• Investigate recent deployment impacts on error rates
• Review log aggregation for pattern detection

Top Incidents (showing 10 of 50):
🔴 Database Connection Pool Exhausted
Priority: CRITICAL | ID: abc123 | Opened: 2025-12-12T10:30:00Z
...
```

---

## 🤖 AI Summary Features

The WatsonX Granite AI analyzes incidents and provides:

1. **Executive Summary** - High-level overview (2-3 sentences)
2. **Key Insights** - Patterns and observations from the data
3. **Recommendations** - Actionable next steps for the team

### AI Prompt Structure

The AI receives:
- Total incident count
- Priority breakdown
- Top 20 incidents with titles, IDs, and timestamps
- Context that it's a Site Reliability Engineer

---

## 🔧 Configuration

All configuration is in `.env`:

```bash
# New Relic
NEW_RELIC_API_KEY=your_api_key
NEW_RELIC_ACCOUNT_ID=your_account_id

# Slack
SLACK_WEBHOOK_URL=your_webhook_url

# WatsonX (for AI summaries)
WATSONX_URL=your_watsonx_url
WATSONX_APIKEY=your_api_key
WATSONX_PROJECT_ID=your_project_id
```

---

## 📁 Code Structure

### State (agent_state.py)

```python
class AgentState:
    open_incidents: List[Dict]  # Fetched incidents
    incident_count: int         # Total count
    incidents_summary: str      # AI-generated summary
    key_insights: List[str]     # AI insights
    slack_sent: bool           # Notification status
    errors: List[str]          # Error tracking
```

### Nodes (agent_nodes.py)

1. **fetch_incidents_node** - Queries New Relic API
2. **summarize_incidents_node** - Calls WatsonX for AI analysis
3. **send_notification_node** - Formats and sends to Slack
4. **end_node** - Cleanup and reporting

---

## 🔄 Future Enhancements

Potential additions:
- Schedule automatic summaries (e.g., every hour/day)
- Filter by specific priority levels
- Compare trends over time
- Add incident age analysis
- Export summaries to email/other channels
- Add incident correlation detection

---

## 🐛 Troubleshooting

### No incidents showing
- Check New Relic API key and account ID
- Verify incidents exist in New Relic UI

### Slack not receiving messages
- Verify webhook URL is correct
- Check Slack app permissions

### AI summary fails
- Falls back to simple summary automatically
- Check WatsonX credentials
- Verify network connectivity

---

## 📝 Notes

- The old alert-based workflow code has been **completely removed**
- No more NRQL queries for specific errors
- No more Opsgenie integration
- Focus is now on **incident overview** rather than **specific alert analysis**
- All 50 open incidents are fetched and analyzed together

---

## 🎯 Quick Start

```bash
# 1. Run immediate summary
python run_summary.py

# 2. Check output in terminal
# 3. Verify Slack message received
```

Done! 🎉

