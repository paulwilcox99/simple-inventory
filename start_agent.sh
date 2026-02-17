#!/bin/bash
echo "🤖 Starting LLM Inventory Agent in Simulation Mode"
echo "=================================================="
echo ""
cd /home/paul/code/widget_sim1/simple_inventory
./venv/bin/python llm_inventory_agent.py --simulation --model gpt-3.5-turbo
