#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WIDGET_SIM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🎮 STEP MODE: Manual Day-by-Day Control"
echo "========================================"
echo ""
echo "Instructions:"
echo "  1. Simulation will pause after each day"
echo "  2. Press ENTER to advance to next day"
echo "  3. Agent will check inventory on each day"
echo "  4. Press 'q' to quit early"
echo ""
echo "Starting in 3 seconds..."
sleep 3
cd "$WIDGET_SIM_DIR"
./venv/bin/python run_simulation.py 7 "2026-04-15" --disable restock --step
