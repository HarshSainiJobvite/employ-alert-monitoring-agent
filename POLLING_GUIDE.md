# Polling-Based Alert Monitoring (No Webhook Needed!)

## 🎯 Overview

Instead of using webhooks, this approach **polls the New Relic API** to check for open incidents. Perfect for:
- ✅ **Local development** - No need to expose your server to the internet
- ✅ **No ngrok required** - Everything runs locally
- ✅ **Simple setup** - Just run one command
- ✅ **Testing** - Easy to start/stop

## 🚀 Quick Start

### Step 1: Configure Your API Keys
```bash
cp .env.example .env
# Edit .env with your credentials
```

### Step 2: Run the Polling Server
```bash
cd /Users/HarshSaini_1/Code/untitled
source .venv/bin/activate
python polling_server.py
```

That's it! The server will now check New Relic every 60 seconds for new incidents.

## 📊 How It Works

```
┌─────────────────────────────────────────┐
│  Your Local Machine                     │
│                                         │
│  ┌────────────────────────────────┐   │
│  │  Polling Server                │   │
│  │  (polling_server.py)           │   │
│  └────────┬───────────────────────┘   │
│           │ Every 60 seconds           │
│           ▼                            │
│  ┌────────────────────────────────┐   │
│  │  Query New Relic API           │   │
│  │  "Any new open incidents?"     │   │
│  └────────┬───────────────────────┘   │
│           │ New incident found!        │
│           ▼                            │
│  ┌────────────────────────────────┐   │
│  │  Agent Workflow                │   │
│  │  1. Execute NRQL query         │   │
│  │  2. Analyze with GPT-4         │   │
│  │  3. Send to Slack              │   │
│  └────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## 🔧 Usage

### Basic Usage (Default settings)
```bash
python polling_server.py
```
- Polls every 60 seconds
- Filters for "NullPointerException" in condition name
- Processes new incidents automatically

### Custom Poll Interval
```bash
# Poll every 30 seconds
python polling_server.py --interval 30

# Poll every 2 minutes
python polling_server.py --interval 120
```

### Filter by Condition Name
```bash
# Only process incidents with "NullPointer" in condition name
python polling_server.py --condition "NullPointer"

# Only process incidents with "Error Rate" in condition name
python polling_server.py --condition "Error Rate"
```

### Process All Incidents (No Filter)
```bash
python polling_server.py --no-filter
```

## 📝 What You'll See

When running, you'll see output like this:

```
============================================================
🚀 New Relic Alert Poller - Starting
============================================================

This server polls New Relic API for open incidents
No webhook needed - perfect for local development!

✅ Configuration validated

Poll Interval: 60 seconds
Condition Filter: NullPointerException

============================================================

🔄 Starting New Relic Alert Poller
============================================================
Account ID: 123456
Poll Interval: 60 seconds
Filter Pattern: NullPointerException

Polling for incidents... Press Ctrl+C to stop
============================================================

[2025-12-12 10:30:00] ✓ No new incidents

🔔 Found 1 new incident(s)!

============================================================
📨 New Incident Detected
============================================================
Incident ID: 12345
Title: NullPointerException in jhire app
Condition: NullPointerException Alert
Policy: Production Alerts
Priority: CRITICAL
Opened At: 2025-12-12T10:29:45Z
============================================================

🤖 Processing Incident with Agent
============================================================

🔍 Detecting alert...
✅ Alert detected: NullPointerException in jhire application

📊 Executing NRQL analysis query...
✅ Query executed successfully. Found 23 affected users

🤖 Analyzing with LLM to generate recommendations...
✅ LLM analysis complete. Generated 4 recommendations

📢 Sending notifications...
✅ Slack notification sent successfully
✅ Opsgenie notification sent

============================================================
✅ Incident Processing Complete
============================================================
Total Errors: 147
Affected Users: 23
Affected Companies: 8
Slack Sent: ✅
Opsgenie Sent: ✅
============================================================
```

## 🆚 Polling vs Webhook

### Polling (This Approach)
**Pros:**
- ✅ Works locally without exposing your server
- ✅ No ngrok or public URL needed
- ✅ Easy to test and debug
- ✅ Simple to start/stop
- ✅ No firewall configuration needed

**Cons:**
- ⏱️ Slight delay (based on poll interval)
- 📊 More API calls to New Relic
- 🔄 Keeps checking even when no alerts

**Best for:**
- Local development and testing
- Internal networks
- Proof of concept

### Webhook (Alternative)
**Pros:**
- ⚡ Instant notification when alert fires
- 💰 Fewer API calls
- 🎯 Only runs when needed

**Cons:**
- 🌐 Requires public URL (ngrok or deployment)
- 🔧 More complex setup
- 🛡️ Need to secure endpoint

**Best for:**
- Production deployments
- Real-time requirements
- Deployed applications

## 🎛️ Configuration

### Adjust Poll Interval
Edit in `polling_server.py`:
```python
start_polling_server(
    poll_interval=30,  # Check every 30 seconds
    condition_pattern="NullPointerException"
)
```

### Change Condition Filter
```python
start_polling_server(
    poll_interval=60,
    condition_pattern="Error Rate"  # Different alert type
)
```

### Process All Incidents
```python
start_polling_server(
    poll_interval=60,
    condition_pattern=None  # No filter
)
```

## 🔍 API Queries Used

The poller uses these New Relic NerdGraph queries:

### 1. Get Open Incidents
```graphql
query($accountId: Int!) {
  actor {
    account(id: $accountId) {
      alerts {
        incidentsSearch {
          incidents {
            incidentId
            title
            priority
            state
            openedAt
            closedAt
            conditionName
            policyName
          }
        }
      }
    }
  }
}
```

### 2. Get Incident Details
```graphql
query($accountId: Int!, $incidentId: ID!) {
  actor {
    account(id: $accountId) {
      alerts {
        incident(id: $incidentId) {
          violations {
            violationId
            label
            openedAt
            closedAt
          }
        }
      }
    }
  }
}
```

## 🚀 Running as a Service

### Using systemd (Linux)
Create `/etc/systemd/system/newrelic-poller.service`:
```ini
[Unit]
Description=New Relic Alert Poller
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/untitled
Environment="PATH=/path/to/untitled/.venv/bin"
ExecStart=/path/to/untitled/.venv/bin/python polling_server.py --interval 60
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable newrelic-poller
sudo systemctl start newrelic-poller
sudo systemctl status newrelic-poller
```

### Using screen (Background process)
```bash
screen -S newrelic-poller
python polling_server.py
# Press Ctrl+A, then D to detach

# Re-attach later:
screen -r newrelic-poller
```

### Using nohup
```bash
nohup python polling_server.py > poller.log 2>&1 &

# Check logs
tail -f poller.log
```

## 🐛 Troubleshooting

### "No new incidents" always showing
- ✅ Check that you have active alerts in New Relic
- ✅ Verify your condition filter matches your alert names
- ✅ Try running with `--no-filter` to see all incidents
- ✅ Check your New Relic API key has proper permissions

### API errors
- ✅ Verify `NEW_RELIC_API_KEY` is correct
- ✅ Verify `NEW_RELIC_ACCOUNT_ID` is correct
- ✅ Check API key has `NerdGraph` permissions
- ✅ Verify your region (US or EU) is correct

### Agent workflow fails
- ✅ Check `OPENAI_API_KEY` is valid
- ✅ Check `SLACK_WEBHOOK_URL` is correct
- ✅ Test NRQL queries manually in New Relic

## 📚 Additional Resources

- [New Relic NerdGraph API](https://docs.newrelic.com/docs/apis/nerdgraph/get-started/introduction-new-relic-nerdgraph/)
- [New Relic Alerts API](https://docs.newrelic.com/docs/apis/nerdgraph/examples/nerdgraph-api-alerts-policies/)
- [GraphQL Queries for Alerts](https://docs.newrelic.com/docs/apis/nerdgraph/examples/nerdgraph-api-alerts-incidents/)

## 🎉 Summary

**For local development, use polling:**
```bash
python polling_server.py
```

**For production, use webhooks:**
```bash
python webhook_server.py
# Configure New Relic to POST to your webhook URL
```

**Both approaches:**
- ✅ Use the same agent workflow
- ✅ Execute NRQL queries
- ✅ Analyze with GPT-4
- ✅ Send to Slack
- ✅ Email Opsgenie

Choose the approach that fits your needs! 🚀

