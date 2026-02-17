#!/bin/bash
cd /home/paul/code/widget_sim1/simple_inventory
echo "🚀 Running LLM Inventory Agent - Single Check"
echo "=============================================="
echo ""
./venv/bin/python llm_inventory_agent.py --once
