#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WIDGET_SIM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        STEP-BY-STEP MODE: Control Each Day Manually         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Instructions:"
echo "  1. Open TWO terminal windows side-by-side"
echo "  2. In Terminal 1: Run the SIMULATION (this script)"
echo "  3. In Terminal 2: Run the AGENT with this command:"
echo "     cd simple-inventory"
echo "     ./venv/bin/python llm_inventory_agent.py --simulation --check-interval 2"
echo ""
echo "  4. Press ENTER in Terminal 1 to advance each day"
echo "  5. Watch Terminal 2 to see agent decisions"
echo ""
read -p "Press ENTER to start the simulation... "

cd "$WIDGET_SIM_DIR"
./venv/bin/python run_simulation.py 7 "2026-04-20" --disable restock --step
