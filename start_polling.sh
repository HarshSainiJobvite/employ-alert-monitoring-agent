#!/bin/bash

# Quick start script for polling-based alert monitoring
# No webhook or ngrok needed!

echo "=================================================="
echo "🔄 New Relic Alert Poller - Quick Start"
echo "=================================================="
echo ""
echo "This polls New Relic API for alerts - no webhook needed!"
echo "Perfect for local development!"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please run: cp .env.example .env"
    echo "Then edit .env with your API keys"
    exit 1
fi

echo "✅ .env file found"
echo ""

echo "=================================================="
echo "Starting Alert Poller"
echo "=================================================="
echo ""
echo "How it works:"
echo "  1. Polls New Relic API every 60 seconds"
echo "  2. Checks for new open incidents"
echo "  3. Triggers agent workflow for new incidents"
echo "  4. Sends alerts to Slack"
echo ""
echo "Configuration:"
echo "  Poll Interval: 60 seconds"
echo "  Condition Filter: NullPointerException"
echo ""
echo "To customize:"
echo "  python polling_server.py --interval 30"
echo "  python polling_server.py --condition 'Error Rate'"
echo "  python polling_server.py --no-filter"
echo ""
echo "Press Ctrl+C to stop"
echo "=================================================="
echo ""

# Start the polling server
.venv/bin/python polling_server.py "$@"
