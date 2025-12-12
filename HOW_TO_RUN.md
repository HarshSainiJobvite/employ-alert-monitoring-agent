# 🚀 How to Run the Incident Summary Agent

## Quick Start (Fastest Way)

```bash
python main.py
```

That's it! This will:
1. Fetch all 50 open incidents from New Relic
2. Generate an AI summary using WatsonX
3. Send a formatted message to your Slack channel
4. Exit

---

## Alternative Ways to Run

### 1. Using run_summary.py (Same as main.py)
```bash
python run_summary.py
```

### 2. View Incidents Only (No AI, No Slack)
```bash
python view_incidents.py
```
Shows raw incident list in terminal without AI analysis or notifications.

---

## What Happens When You Run It

### Terminal Output Example:
```
============================================================
🤖 New Relic Incident Summary Agent
============================================================

🚀 Starting incident summary workflow...

🤖 Initializing IBM WatsonX Granite for AI reasoning
✅ IBM WatsonX Granite 3 8B Instruct initialized successfully
🔍 Fetching open incidents from New Relic...
📊 Found 50 open issues in New Relic
✅ Fetched 50 open incidents
🤖 Summarizing incidents with IBM WatsonX Granite...
🧠 Generating AI analysis...
✅ AI summary generated with 8 insights
📢 Sending summary to Slack...
✅ Summary sent to Slack successfully

============================================================
🏁 Workflow Complete
============================================================
Incidents Processed: 50
Slack Sent: ✅

============================================================
✅ Agent Complete
============================================================
Incidents Processed: 50
Slack Notification: ✅ Sent
============================================================
```

### Slack Message You'll Receive:
```
📊 New Relic Incidents Summary

Total Open Incidents: 50

Executive Summary:
Currently monitoring 50 open incidents across the platform with varying 
severity levels. Multiple systems showing degraded performance requiring 
immediate attention from the operations team.

Key Insights & Recommendations:
• Total of 50 incidents requiring attention
• Priority distribution: CRITICAL: 5, HIGH: 12, MEDIUM: 28, LOW: 5
• Multiple systems affected - investigate recent deployments
• Review error patterns for correlation
• Consider scaling infrastructure for high-traffic services

Top Incidents (showing 10 of 50):
🔴 Database Connection Pool Exhausted
Priority: CRITICAL | ID: abc123
Opened: 2025-12-12T10:30:00Z

🟠 API Response Time Degraded
Priority: HIGH | ID: def456
Opened: 2025-12-12T11:15:00Z

... (8 more incidents)

Generated at 2025-12-12 13:30:00
```

---

## Prerequisites

Make sure you have:

1. **Python Dependencies Installed:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables Set** (in `.env` file):
   ```bash
   # New Relic
   NEW_RELIC_API_KEY=your_api_key
   NEW_RELIC_ACCOUNT_ID=your_account_id
   
   # Slack
   SLACK_WEBHOOK_URL=your_webhook_url
   
   # WatsonX (for AI)
   WATSONX_URL=your_watsonx_url
   WATSONX_APIKEY=your_api_key
   WATSONX_PROJECT_ID=your_project_id
   ```

---

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "No incidents found"
- Check your New Relic API key is correct
- Verify your account ID is correct
- Make sure there are actual open incidents in New Relic

### "Failed to send to Slack"
- Verify your Slack webhook URL
- Check the webhook has permissions to post
- Test the webhook with: `curl -X POST -H 'Content-type: application/json' --data '{"text":"Test"}' YOUR_WEBHOOK_URL`

### "WatsonX initialization failed"
- Check your WatsonX credentials in `.env`
- Verify project ID is correct
- Agent will use fallback summary if AI fails

---

## Command Comparison

| Command | What It Does | AI Summary | Slack Notification |
|---------|--------------|------------|-------------------|
| `python main.py` | Full workflow | ✅ Yes | ✅ Yes |
| `python run_summary.py` | Full workflow | ✅ Yes | ✅ Yes |
| `python view_incidents.py` | View only | ❌ No | ❌ No |

---

## Scheduling (Optional)

### Run Every Hour with Cron
```bash
# Edit crontab
crontab -e

# Add this line (runs at the top of every hour)
0 * * * * cd /Users/HarshSaini_1/Code/untitled && /usr/bin/python3 main.py >> /tmp/incident_summary.log 2>&1
```

### Run Every 4 Hours
```bash
0 */4 * * * cd /Users/HarshSaini_1/Code/untitled && /usr/bin/python3 main.py >> /tmp/incident_summary.log 2>&1
```

### Run Daily at 9 AM
```bash
0 9 * * * cd /Users/HarshSaini_1/Code/untitled && /usr/bin/python3 main.py >> /tmp/incident_summary.log 2>&1
```

---

## What Changed from Original

**OLD Behavior (Removed):**
- ❌ Webhook server listening for alerts
- ❌ Polling for new incidents continuously
- ❌ Alert-based trigger system
- ❌ NRQL query analysis

**NEW Behavior:**
- ✅ Run once and exit
- ✅ Fetch all open incidents
- ✅ AI-powered summary
- ✅ Send to Slack
- ✅ Simple and fast

---

## Next Steps

1. **Test it now:**
   ```bash
   python main.py
   ```

2. **Check Slack** for the summary message

3. **Optional:** Set up cron job for automatic summaries

4. **Done!** 🎉

---

## Need Help?

- Check `AGENT_PIVOT_GUIDE.md` for detailed architecture
- Review `.env` file for configuration
- Look at terminal output for specific errors
- Verify New Relic and Slack credentials

---

**Pro Tip:** Run `python view_incidents.py` first to see if incidents are being fetched correctly before running the full workflow.

