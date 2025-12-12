#!/usr/bin/env python3
"""
Simple script to view all currently open incidents in New Relic.
This doesn't start continuous polling - just shows what's open right now.
"""
from alert_poller import create_poller


def main():
    print("🔍 Fetching open incidents from New Relic...\n")

    poller = create_poller()

    # Display all open incidents
    poller.display_all_open_incidents()

    print("\n✅ Done! Use 'python polling_server.py' to start continuous monitoring.")


if __name__ == "__main__":
    main()

