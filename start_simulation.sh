#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WIDGET_SIM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🏭 Starting 30-Day Manufacturing Simulation"
echo "=========================================="
echo "With restocking DISABLED (agent will handle it)"
echo ""
cd "$WIDGET_SIM_DIR"
./venv/bin/python run_simulation.py 30 "2026-04-15" --disable restock --delay 5
