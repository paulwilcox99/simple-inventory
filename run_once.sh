#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Running LLM Inventory Agent - Single Check"
echo "=============================================="
echo ""
./venv/bin/python llm_inventory_agent.py --once
