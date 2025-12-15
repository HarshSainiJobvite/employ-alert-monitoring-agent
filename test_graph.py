#!/usr/bin/env python
"""Test script to verify LangGraph setup."""
import sys

print("Starting graph test...")
sys.stdout.flush()

try:
    print("Importing agent_graph...")
    sys.stdout.flush()
    from agent_graph import create_agent_graph

    print("Creating graph...")
    sys.stdout.flush()
    graph = create_agent_graph()

    print(f"✅ Graph created successfully!")
    print(f"   Type: {type(graph)}")
    print(f"   Graph is ready for langgraph dev")
    sys.stdout.flush()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.stdout.flush()

