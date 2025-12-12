# 🚀 Quick Start Guide

## Starting the New Relic Alert Agent

### ✅ Prerequisites Check

Before starting, make sure you have:
1. ✅ Configured your `.env` file with credentials
2. ✅ Virtual environment activated
3. ✅ Dependencies installed

### 🎯 Three Ways to Start the Server

---

## Option 1: Quick Start Script (Recommended)

```bash
./start_polling.sh
```

**What this does:**
- ✅ Checks if `.env` file exists
- ✅ Starts the polling server automatically
- ✅ Polls New Relic every 60 seconds
- ✅ Filters for "NullPointerException" alerts
- ✅ Triggers WatsonX analysis when alerts found
- ✅ Sends to Slack

**Example output:**
```
==================================================
🔄 New Relic Alert Poller - Quick Start
==================================================

This polls New Relic API for alerts - no webhook needed!
Perfect for local development!

✅ .env file found

==================================================
Starting Alert Poller
==================================================

🤖 Using IBM WatsonX for AI reasoning
🔄 Starting New Relic Alert Poller
==================================================
Account ID: 123456
Poll Interval: 60 seconds
Filter Pattern: NullPointerException

Polling for incidents... Press Ctrl+C to stop
==================================================

[2025-12-12 10:30:00] ✓ No new incidents
```

---

## Option 2: Direct Python Command

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Start the server
python polling_server.py
```

**With custom options:**
```bash
# Poll every 30 seconds
python polling_server.py --interval 30

# Different condition filter
python polling_server.py --condition "Error Rate"

# Process all incidents (no filter)
python polling_server.py --no-filter
```

---

## Option 3: Step-by-Step (First Time Setup)

### Step 1: Navigate to project directory
```bash
cd /Users/HarshSaini_1/Code/untitled
```

### Step 2: Activate virtual environment
```bash
source .venv/bin/activate
```

### Step 3: Install dependencies (if needed)
```bash
pip install -r requirements.txt
```

### Step 4: Configure environment
```bash
# Copy template if you haven't already
cp .env.example .env

# Edit with your credentials
nano .env
```

Required in `.env`:
```env
NEW_RELIC_API_KEY=your_key_here
NEW_RELIC_ACCOUNT_ID=your_account_id
SLACK_WEBHOOK_URL=your_slack_webhook
WATSONX_APIKEY=your_watsonx_key
WATSONX_PROJECT_ID=your_project_id
```

### Step 5: Start the server
```bash
./start_polling.sh
```

---

## 🎛️ Server Options

### Default Settings
```bash
./start_polling.sh
```
- Poll interval: 60 seconds
- Filter: "NullPointerException"
- LLM: WatsonX Granite

### Custom Interval
```bash
python polling_server.py --interval 30
```
Polls every 30 seconds instead of 60

### Different Alert Type
```bash
python polling_server.py --condition "High CPU"
```
Filters for different condition name

### Process All Alerts
```bash
python polling_server.py --no-filter
```
Processes all open incidents regardless of condition

---

## 📊 What Happens When You Start

1. **Server Initialization**
   - Loads configuration from `.env`
   - Validates credentials
   - Initializes WatsonX LLM
   - Connects to New Relic API

2. **Polling Loop Starts**
   - Queries New Relic every 60 seconds
   - Checks for open incidents
   - Filters by condition name

3. **When Alert Found**
   ```
   🔔 New incident detected!
      ↓
   📊 Execute NRQL query
      ↓
   🤖 WatsonX analyzes data
      ↓
   📢 Send to Slack
      ↓
   📧 Email Opsgenie
      ↓
   ✅ Continue polling
   ```

4. **Console Output**
   ```
   [2025-12-12 10:30:00] ✓ No new incidents
   [2025-12-12 10:31:00] ✓ No new incidents
   
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
   🔍 Detecting alert...
   ✅ Alert detected
   📊 Executing NRQL analysis query...
   ✅ Found 23 affected users
   🤖 Analyzing with IBM WatsonX...
   ✅ Generated 4 recommendations
   📢 Sending notifications...
   ✅ Slack sent
   ✅ Opsgenie sent
   ```

---

## 🛑 Stopping the Server

Press `Ctrl+C` to stop polling gracefully:

```
^C
🛑 Polling stopped by user
Goodbye!
```

---

## 🔧 Running in Background

### Using screen (keeps running after logout)
```bash
# Start screen session
screen -S newrelic-agent

# Run the server
./start_polling.sh

# Detach: Press Ctrl+A, then D

# Re-attach later
screen -r newrelic-agent

# Kill session
screen -X -S newrelic-agent quit
```

### Using nohup
```bash
# Start in background
nohup ./start_polling.sh > agent.log 2>&1 &

# Check if running
ps aux | grep polling_server

# View logs
tail -f agent.log

# Stop
pkill -f polling_server.py
```

---

## 🐛 Troubleshooting

### ".env file not found"
```bash
cp .env.example .env
# Then edit .env with your credentials
```

### "Missing required configuration"
Check that `.env` has all required values:
```bash
cat .env | grep -E "NEW_RELIC|SLACK|WATSONX"
```

### "Module not found" errors
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Server starts but no alerts
- ✅ Verify you have active alerts in New Relic
- ✅ Check filter matches your alert condition names
- ✅ Try `--no-filter` to see all incidents

### WatsonX errors
```bash
# Test WatsonX connection
python test_watsonx.py
```

---

## ✅ Verification Checklist

Before starting, verify:
- [ ] `.env` file exists and is configured
- [ ] Virtual environment is activated
- [ ] Dependencies are installed
- [ ] New Relic API key is valid
- [ ] WatsonX credentials are correct
- [ ] Slack webhook URL is set

---

## 🎉 You're Ready!

**Start now:**
```bash
./start_polling.sh
```

The server will:
- ✅ Poll New Relic every 60 seconds
- ✅ Detect NullPointerException alerts
- ✅ Analyze with WatsonX
- ✅ Send formatted alerts to Slack
- ✅ Email Opsgenie

**All automatic - just let it run!** 🚀

