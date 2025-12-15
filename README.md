# New Relic Alert Agent - Polling-Based

An intelligent agent that monitors New Relic alerts via API polling, performs NRQL queries, analyzes error patterns using AI, and sends actionable notifications to Slack.

## 🚀 Quick Start
cd /Users/HarshSaini_1/Code/employ-alert-monitoring-agent && source .venv/bin/activate && langgraph dev
```bash
# 1. Configure your API keys
cd /Users/HarshSaini_1/Code/untitled
cp .env.example .env
# Edit .env with your credentials

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Start the polling server
./start_polling.sh

# Or manually:
python polling_server.py
```

**That's it!** The server will check New Relic every 60 seconds for new incidents.

## 🎯 How It Works

The agent **polls the New Relic API** every 60 seconds to check for open incidents:

```
Every 60 seconds:
  → Query New Relic API for open incidents
  → Find new incidents with "NullPointerException"
  → Run your NRQL analysis query
  → Analyze with GPT-4
  → Send to Slack with recommendations
  → Email Opsgenie
```

**Benefits:**
- ✅ **No webhook needed** - runs completely locally
- ✅ **No ngrok or public URL** - perfect for development
- ✅ **Simple setup** - just one command
- ✅ **Easy to debug** - see everything in your terminal

## 📋 Prerequisites

- Python 3.8+
- New Relic account with API access
- OpenAI API key
- Slack webhook URL

## ⚙️ Configuration

Create a `.env` file with your credentials:

```env
# New Relic Configuration
NEW_RELIC_API_KEY=your_new_relic_api_key
NEW_RELIC_ACCOUNT_ID=your_account_id
NEW_RELIC_REGION=US  # or EU

# Slack Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
OPSGENIE_SLACK_EMAIL=opsgenie-jv-aaaapspxg6qkfwmd4rye7f46na@grid-employinc.org.slack.com

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
```

### Getting API Keys

**New Relic API Key:**
1. Go to https://one.newrelic.com/launcher/api-keys-ui.api-keys-launcher
2. Create a User API key with NerdGraph permissions
3. Copy to `.env`

**New Relic Account ID:**
- Check the URL: `https://one.newrelic.com/accounts/{ACCOUNT_ID}/...`
- Or find in account dropdown

**Slack Webhook:**
1. Go to https://api.slack.com/apps
2. Create app → Incoming Webhooks
3. Create webhook for your channel
4. Copy URL to `.env`

**OpenAI API Key:**
1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy to `.env`

## 🎛️ Usage Options

### Basic Usage
```bash
python polling_server.py
```
Default: Polls every 60 seconds for "NullPointerException" incidents

### Custom Poll Interval
```bash
# Poll every 30 seconds
python polling_server.py --interval 30

# Poll every 2 minutes
python polling_server.py --interval 120
```

### Filter by Different Condition
```bash
# Filter for different alert types
python polling_server.py --condition "Error Rate"
python polling_server.py --condition "High Latency"
```

### Process All Incidents
```bash
# No filter - process all open incidents
python polling_server.py --no-filter
```

## 📊 What Happens When Alert Fires

1. **Polling detects** new open incident in New Relic
2. **Agent extracts** incident details and time window
3. **NRQL query executes** to get affected users:
   ```sql
   SELECT count(*) FROM TransactionError 
   WHERE appName='jhire' 
   AND error.class = 'java.lang.NullPointerException'
   FACET USER_COMPANY_ID, USER_EMAIL_ID
   SINCE 7 days ago
   ```
4. **GPT-4 analyzes** the data and generates 3-5 actionable recommendations
5. **Slack notification** sent with:
   - Total errors, affected users, companies
   - Top 10 affected users with error counts
   - AI-generated recommendations
6. **Email sent** to Opsgenie

## 📁 Project Structure

```
.
├── README.md                 # This file
├── SETUP_COMPLETE.md        # Complete setup guide
├── POLLING_GUIDE.md         # Detailed polling documentation
├── QUICKSTART.md            # Quick start instructions
│
├── polling_server.py        # Main entry point - run this!
├── alert_poller.py          # Polls New Relic API
├── start_polling.sh         # Quick start script
│
├── agent_graph.py           # Workflow orchestration
├── agent_nodes.py           # Processing nodes
├── agent_state.py           # State definitions
│
├── newrelic_client.py       # New Relic NerdGraph API client
├── slack_client.py          # Slack notifications
├── config.py                # Configuration management
│
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── .env                    # Your credentials (create this)
```

## 🔧 Your Configured Queries

### Alert Detection Query
Monitors for NullPointerExceptions in the jhire application, excluding specific test users.

### Analysis Query
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

## 🎨 Customization

### Modify Queries
Edit `config.py`:
```python
ANALYSIS_QUERY = """
    Your custom NRQL query
"""
```

### Change Slack Message Format
Edit `slack_client.py` → `format_alert_message()` method

### Adjust Workflow
Edit `agent_graph.py` to add/modify workflow nodes

## 🐛 Troubleshooting

### "No new incidents" always showing
- ✅ Verify you have active alerts in New Relic
- ✅ Check condition filter matches your alert names
- ✅ Try `--no-filter` to see all incidents
- ✅ Verify API key has NerdGraph permissions

### API errors
- ✅ Check `NEW_RELIC_API_KEY` is correct
- ✅ Check `NEW_RELIC_ACCOUNT_ID` is correct
- ✅ Verify region (US/EU) is correct

### Agent workflow fails
- ✅ Verify `OPENAI_API_KEY` is valid
- ✅ Verify `SLACK_WEBHOOK_URL` is correct
- ✅ Test NRQL queries in New Relic query builder

### Import errors
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## 🚀 Running in Background

### Using screen
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
ExecStart=/path/to/untitled/.venv/bin/python polling_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📚 Documentation

- **`SETUP_COMPLETE.md`** - Complete setup guide with examples
- **`POLLING_GUIDE.md`** - Detailed polling documentation
- **`QUICKSTART.md`** - Quick start instructions
- **`README.md`** - This file

## 🎯 Features

- ✅ **Polls New Relic API** - No webhook needed
- ✅ **Auto-detects incidents** - Filters by condition name
- ✅ **NRQL Analysis** - Queries for affected users/companies
- ✅ **AI-Powered** - GPT-4 generates recommendations
- ✅ **Rich Slack Alerts** - Formatted with detailed breakdowns
- ✅ **Opsgenie Integration** - Email notifications
- ✅ **Easy to Test** - Runs completely locally
- ✅ **Customizable** - Adjust queries, intervals, filters

## 🔗 Resources

- [New Relic NerdGraph API](https://docs.newrelic.com/docs/apis/nerdgraph/get-started/introduction-new-relic-nerdgraph/)
- [New Relic NRQL Reference](https://docs.newrelic.com/docs/nrql/nrql-syntax-clauses-functions/)
- [Slack API Documentation](https://api.slack.com/messaging/webhooks)
- [LangChain Documentation](https://python.langchain.com/)

## 💡 Tips

- **Start with default settings** to see it work
- **Monitor the logs** to understand the workflow
- **Test with `--interval 30`** for faster feedback during development
- **Use `--no-filter`** to process all incidents while testing
- **Check New Relic** to ensure you have open incidents

## 🎉 Success!

Once configured, your agent will:
- ✅ Automatically detect New Relic alerts
- ✅ Analyze error patterns across users and companies
- ✅ Generate intelligent recommendations
- ✅ Send formatted, actionable alerts to Slack
- ✅ Keep your team informed with minimal manual intervention

---

**Start now:** `./start_polling.sh` 🚀

