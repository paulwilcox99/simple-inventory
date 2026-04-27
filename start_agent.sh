#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🤖 Starting LLM Inventory Agent in Simulation Mode"
echo "=================================================="
echo ""
cd "$SCRIPT_DIR"
./venv/bin/python llm_inventory_agent.py --simulation --model gpt-3.5-turbo
