# Quick Start Guide - LLM Inventory Agent

Get up and running with the AI-powered inventory agent in 5 minutes!

## Prerequisites

Both repositories must share a parent directory. Expected layout:
```
widget-sim/                  ← manufacturing simulator
├── venv/
├── run_simulation.py
└── simple-inventory/        ← this agent (sub-directory of widget-sim)
    └── venv/
```

## Step 1: Install Dependencies

```bash
# From the widget-sim root — install simulator dependencies
cd widget-sim
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# Then install agent dependencies
cd simple-inventory
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

## Step 2: Set Up OpenAI API Key

Choose one method:

### Option A: Environment Variable (Recommended)
```bash
export OPENAI_API_KEY='sk-your-api-key-here'
```

### Option B: .env File
```bash
cd simple-inventory
cp .env.example .env
# Edit .env and add your API key
nano .env
```

Get your API key from: https://platform.openai.com/api-keys

## Step 3: Initialize the Simulation Databases

Before running the agent, the simulator databases must exist:

```bash
cd widget-sim
./venv/bin/python create_sim.py
```

## Step 4: Test Your Setup

Run the test suite to verify everything works:

```bash
cd simple-inventory
./venv/bin/python test_agent.py
```

This will:
- ✅ Check API key configuration
- ✅ Verify database access
- ✅ Test LLM connection
- ✅ Run a dry-run analysis (optional)

## Step 5: Run Your First Check

### Manual Mode (One-time check)

```bash
cd simple-inventory
./venv/bin/python llm_inventory_agent.py --once
```

This will:
1. Query inventory levels
2. Ask the LLM to analyze them
3. Show recommendations
4. Execute any necessary restocking

### View Results

The agent will display:
- Current inventory status
- LLM's reasoning
- Which parts to restock
- How many units to order

Example output:
```
🤖 LLM Inventory Agent - Daily Check
📅 Date: 2026-03-01

📊 Gathering inventory data...
   - 24 parts in inventory
   - 5 pending orders

🧠 Consulting LLM for inventory decision...

💭 LLM Decision: RESTOCK
📝 Reasoning: Critical parts Screw-1 (45 units) and Widget-Body-1 (12 units)
              are insufficient for pending demand...

📦 Executing restock for 2 parts...
   ✓ Screw-1: +355 units ($177.50)
   ✓ Widget-Body-1: +88 units ($1,320.00)

💰 Total restock cost: $1,497.50
✅ Restock completed successfully
```

## Step 6: Run with Simulation (Advanced)

Run the agent synchronized with the manufacturing simulation.

### Terminal 1: Start Simulation (from widget-sim/)
```bash
cd widget-sim
./venv/bin/python run_simulation.py 30 "2026-03-01" --disable restock --delay 5
```

### Terminal 2: Start Agent (from simple-inventory/)
```bash
cd widget-sim/simple-inventory
./venv/bin/python llm_inventory_agent.py --simulation
```

The agent will:
- Monitor the simulation
- Check inventory each simulation day
- Let the LLM make restocking decisions
- Auto-execute restocking
- Exit when simulation completes

### Or use the helper scripts (from simple-inventory/)
```bash
# Terminal 1:
./start_simulation.sh

# Terminal 2:
./start_agent.sh
```

## Common Commands

```bash
# Run single check with specific date
./venv/bin/python llm_inventory_agent.py --once --date 2026-03-15

# Use cheaper/faster model
./venv/bin/python llm_inventory_agent.py --once --model gpt-3.5-turbo

# Run with simulation using specific model
./venv/bin/python llm_inventory_agent.py --simulation --model gpt-4-turbo

# Test without running
./venv/bin/python test_agent.py
```

## Troubleshooting

### "OpenAI API key must be provided"
- Run: `export OPENAI_API_KEY='sk-...'`
- Or create `.env` file with your key

### "Database not found"
- Run `create_sim.py` from the widget-sim directory first
- Ensure `simple-inventory` is a subdirectory of `widget-sim`

### "Authentication error"
- Verify API key is correct
- Check OpenAI account has credits
- Visit: https://platform.openai.com/account/billing

### "JSON decode error"
- LLM returned invalid format
- Try using `gpt-4` instead of `gpt-3.5-turbo`
- Model outputs are shown for debugging

## Understanding the Output

### Decision Types
- **restock**: LLM recommends ordering parts
- **no_action**: Inventory levels are healthy

### Reasoning
The LLM explains why it made its decision, considering:
- Current stock levels
- Pending orders
- Future demand estimates
- Cost vs. risk tradeoffs

### Parts to Order
For each part to restock:
- **part_name**: Which part
- **current_quantity**: Stock before ordering
- **order_quantity**: How much to order
- **rationale**: Why this amount

## Next Steps

1. **Experiment with Models**: Try different OpenAI models to see how decisions change
2. **Adjust Parameters**: Edit the agent to change restock thresholds
3. **Run Full Simulation**: Test the agent over 30 simulation days
4. **Compare Results**: Run simulation with and without the agent
5. **Monitor Costs**: Track API usage and simulation performance

## Cost Management

Estimated costs per check:
- GPT-4: $0.03-0.05
- GPT-4 Turbo: $0.01-0.02
- GPT-3.5 Turbo: $0.002-0.005

For a 30-day simulation (30 checks):
- GPT-4: ~$1.50
- GPT-4 Turbo: ~$0.60
- GPT-3.5 Turbo: ~$0.15

## Support

- Read `README.md` for detailed documentation
- Check `../AGENT_DEVELOPER_GUIDE.md` in the simulator for database schemas

## Example Session

```bash
# 1. Set up environment
export OPENAI_API_KEY='sk-proj-...'

# 2. Initialize databases (from widget-sim/)
cd widget-sim
./venv/bin/python create_sim.py

# 3. Test everything (from simple-inventory/)
cd simple-inventory
./venv/bin/python test_agent.py

# 4. Run a single check
./venv/bin/python llm_inventory_agent.py --once

# 5. Run with simulation
# Terminal 1 (from simple-inventory/):
./start_simulation.sh

# Terminal 2 (from simple-inventory/):
./start_agent.sh

# 6. Watch it work!
```

That's it! You now have an AI agent managing your inventory! 🤖📦
