# 🎉 New Relic Alert Agent - Setup Complete!

Your polling-based New Relic Alert Agent is ready to use!

## 🚀 Quick Start (3 Steps)

### Step 1: Configure API Keys
```bash
cd /Users/HarshSaini_1/Code/untitled
cp .env.example .env
# Edit .env with your credentials
```

Required credentials:
- `NEW_RELIC_API_KEY` - From https://one.newrelic.com/launcher/api-keys-ui.api-keys-launcher
- `NEW_RELIC_ACCOUNT_ID` - From your New Relic account URL
- `SLACK_WEBHOOK_URL` - From https://api.slack.com/apps
- `OPENAI_API_KEY` - From https://platform.openai.com/api-keys

### Step 2: Activate Virtual Environment
```bash
source .venv/bin/activate
```

### Step 3: Start Polling Server
```bash
./start_polling.sh

# Or manually:
python polling_server.py
```

**That's it!** 🎉

## 📊 How It Works

```
Every 60 seconds:
  → Query New Relic API for open incidents
  → Filter for "NullPointerException" alerts
  → Execute NRQL query for affected users
  → Analyze with GPT-4
  → Send to Slack with recommendations
  → Email Opsgenie
```

**No webhook, no ngrok, no public URL needed!**

## 🎛️ Customization Options

### Change Poll Interval
```bash
# Poll every 30 seconds
python polling_server.py --interval 30

# Poll every 2 minutes
python polling_server.py --interval 120
```

### Filter Different Alert Types
```bash
# Filter by condition name
python polling_server.py --condition "Error Rate"
python polling_server.py --condition "High Latency"

# Process all incidents (no filter)
python polling_server.py --no-filter
```

## 📝 Expected Output

When running, you'll see:

```
============================================================
🚀 New Relic Alert Poller - Starting
============================================================

✅ Configuration validated

Poll Interval: 60 seconds
Condition Filter: NullPointerException

============================================================
🔄 Starting New Relic Alert Poller
============================================================

Polling for incidents... Press Ctrl+C to stop

[2025-12-12 10:30:00] ✓ No new incidents

🔔 Found 1 new incident(s)!

============================================================
📨 New Incident Detected
============================================================
Incident ID: 12345
Title: NullPointerException in jhire app
Condition: NullPointerException Alert
Priority: CRITICAL
============================================================

🤖 Processing Incident with Agent
============================================================

🔍 Detecting alert...
✅ Alert detected

📊 Executing NRQL analysis query...
✅ Found 23 affected users

🤖 Analyzing with GPT-4...
✅ Generated 4 recommendations

📢 Sending notifications...
✅ Slack sent
✅ Opsgenie sent

============================================================
✅ Incident Processing Complete
============================================================
Total Errors: 147
Affected Users: 23
Affected Companies: 8
============================================================
```

## 📁 Project Files

### Core Files (You'll Use These)
- **`polling_server.py`** - Main entry point
- **`start_polling.sh`** - Quick start script
- **`config.py`** - Your queries and configuration
- **`.env`** - Your API credentials (create this)

### Agent Files (Auto-run by polling_server)
- **`alert_poller.py`** - Polls New Relic API
- **`agent_graph.py`** - Workflow orchestration
- **`agent_nodes.py`** - Processing steps
- **`newrelic_client.py`** - New Relic API client
- **`slack_client.py`** - Slack notifications

### Documentation
- **`README.md`** - Main documentation
- **`SETUP_COMPLETE.md`** - This file
- **`POLLING_GUIDE.md`** - Detailed guide
- **`QUICKSTART.md`** - Quick reference

## 🎯 Your Pre-Configured Settings

### Alert Filter
- Condition name contains: **"NullPointerException"**
- Application: **jhire**
- Excludes test users

### NRQL Analysis Query
```sql
SELECT count(*) 
FROM TransactionError 
WHERE appName='jhire' 
AND error.class = 'java.lang.NullPointerException' 
AND USER_EMAIL_ID!='wh-admin@jobvite-inc.com' 
AND USER_EMAIL_ID != 'jvautometa+hire+engage+poweruser@gmail.com' 
FACET USER_COMPANY_ID,USER_EMAIL_ID 
TIMESERIES 1 hour 
SINCE 7 days ago
```

### Slack Notification
- Rich formatted message with blocks
- Top 10 affected users
- AI-generated recommendations
- Total errors, users, companies

### Opsgenie Email
- To: `opsgenie-jv-aaaapspxg6qkfwmd4rye7f46na@grid-employinc.org.slack.com`

## 🐛 Troubleshooting

### "No new incidents" keeps showing
✅ Verify you have active alerts in New Relic  
✅ Check your condition filter matches alert names  
✅ Try `--no-filter` to see all incidents  

### Configuration errors
✅ Check all values in `.env` are filled in  
✅ Remove any template text like "your_api_key_here"  
✅ Verify API keys have proper permissions  

### Import errors
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### API errors
✅ Verify New Relic API key has NerdGraph access  
✅ Check account ID is correct  
✅ Verify region (US or EU) is correct  

## 🚀 Running in Background

### Using screen (recommended)
```bash
screen -S newrelic-poller
./start_polling.sh
# Press Ctrl+A, then D to detach

# Re-attach later:
screen -r newrelic-poller
```

### Using nohup
```bash
nohup python polling_server.py > poller.log 2>&1 &
tail -f poller.log
```

## 📚 Next Steps

1. **Test it:** Run `./start_polling.sh` to see it in action
2. **Create test alert:** Trigger a NullPointerException in New Relic
3. **Watch it work:** See the agent detect, analyze, and notify
4. **Customize:** Adjust queries in `config.py` or polling interval
5. **Deploy:** Run in background with screen or systemd

## ✨ What You Get

When an alert fires, your team receives a Slack message with:
- 📊 **Error summary** - Total errors, users, companies affected
- 👥 **Top affected** - Top 10 users/companies by error count
- 🤖 **AI recommendations** - 3-5 specific actions to take
- 📧 **Opsgenie alert** - Email notification for on-call team

All automatically, every 60 seconds!

---

**Ready to go! Start with:** `./start_polling.sh` 🚀

For detailed documentation, see:
- `README.md` - Main documentation
- `POLLING_GUIDE.md` - Detailed polling guide
- `QUICKSTART.md` - Quick reference
