#!/bin/bash
echo "🏭 Starting 30-Day Manufacturing Simulation"
echo "=========================================="
echo "With restocking DISABLED (agent will handle it)"
echo ""
cd /home/paul/code/widget_sim1/widget-sim
./venv/bin/python run_simulation.py 30 "2026-04-15" --disable restock
