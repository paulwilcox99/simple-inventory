# LLM Inventory Agent - Command Reference

All commands below assume you are in the `simple-inventory/` directory.

## Quick Start Commands

### Test Your Setup
```bash
cd simple-inventory
./venv/bin/python test_agent.py
```

### Run Single Check (Manual Mode)
```bash
./venv/bin/python llm_inventory_agent.py --once
```

### Run with Simulation (Auto Mode)
```bash
# Terminal 1 — start the simulator (from simple-inventory/):
./start_simulation.sh

# Terminal 2 — start the agent (from simple-inventory/):
./start_agent.sh
```

Or manually:
```bash
# Terminal 1 (from widget-sim/):
./venv/bin/python run_simulation.py 30 "2026-04-15" --disable restock --delay 5

# Terminal 2 (from simple-inventory/):
./venv/bin/python llm_inventory_agent.py --simulation
```

## Model Selection

```bash
# GPT-3.5 Turbo (cheap, fast)
./venv/bin/python llm_inventory_agent.py --once --model gpt-3.5-turbo

# GPT-4 (smart, expensive)
./venv/bin/python llm_inventory_agent.py --once --model gpt-4

# GPT-4 Turbo (balanced)
./venv/bin/python llm_inventory_agent.py --once --model gpt-4-turbo
```

## Advanced Options

```bash
# Custom date
./venv/bin/python llm_inventory_agent.py --once --date 2026-05-01

# Faster polling (simulation mode)
./venv/bin/python llm_inventory_agent.py --simulation --check-interval 5

# Different API key
./venv/bin/python llm_inventory_agent.py --once --api-key sk-...
```

## Helper Scripts (Quick Access)

```bash
# Run single check
./run_once.sh

# Terminal 1: Start simulation
./start_simulation.sh

# Terminal 2: Start agent
./start_agent.sh
```

## Get Help

```bash
./venv/bin/python llm_inventory_agent.py --help
```

## Check Results

```bash
# View last simulation state (from widget-sim/)
cat ../sim_state.json

# Query inventory levels (from widget-sim/)
../venv/bin/python3 -c "
import sqlite3
conn = sqlite3.connect('databases/inventory.db')
cursor = conn.cursor()
cursor.execute('SELECT part_name, quantity_available FROM inventory_levels ORDER BY quantity_available LIMIT 10')
print('Lowest inventory levels:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]} units')
"
```

## Troubleshooting

```bash
# Check API key
grep OPENAI_API_KEY .env

# Test databases
./venv/bin/python test_agent.py

# Reset databases (fresh start) — run from widget-sim/
cd ..
rm -rf databases/
./venv/bin/python create_sim.py
```
