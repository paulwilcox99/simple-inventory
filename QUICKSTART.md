# Quick Start Guide - LLM Inventory Agent

Get up and running with the AI-powered inventory agent in 5 minutes!

## Step 1: Install Dependencies

```bash
cd /home/paul/code/widget_sim1/simple_inventory
pip install -r requirements.txt
```

## Step 2: Set Up OpenAI API Key

Choose one method:

### Option A: Environment Variable (Recommended)
```bash
export OPENAI_API_KEY='sk-your-api-key-here'
```

### Option B: .env File
```bash
cp .env.example .env
# Edit .env and add your API key
nano .env
```

Get your API key from: https://platform.openai.com/api-keys

## Step 3: Test Your Setup

Run the test suite to verify everything works:

```bash
python test_agent.py
```

This will:
- ✅ Check API key configuration
- ✅ Verify database access
- ✅ Test LLM connection
- ✅ Run a dry-run analysis (optional)

## Step 4: Run Your First Check

### Manual Mode (One-time check)

```bash
python llm_inventory_agent.py --once
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

## Step 5: Run with Simulation (Advanced)

Run the agent synchronized with the manufacturing simulation.

### Terminal 1: Start Simulation
```bash
cd /home/paul/code/widget_sim1/widget-sim
./venv/bin/python run_simulation.py 30 "2026-03-01" --disable restock --step
```

### Terminal 2: Start Agent
```bash
cd /home/paul/code/widget_sim1/simple_inventory
python llm_inventory_agent.py --simulation
```

The agent will:
- Monitor the simulation
- Check inventory each simulation day
- Let the LLM make restocking decisions
- Auto-execute restocking
- Exit when simulation completes

## Common Commands

```bash
# Run single check with specific date
python llm_inventory_agent.py --once --date 2026-03-15

# Use cheaper/faster model
python llm_inventory_agent.py --once --model gpt-3.5-turbo

# Run with simulation using specific model
python llm_inventory_agent.py --simulation --model gpt-4-turbo

# Test without running
python test_agent.py
```

## Troubleshooting

### "OpenAI API key must be provided"
- Run: `export OPENAI_API_KEY='sk-...'`
- Or create `.env` file with your key

### "Database not found"
- Ensure you're running from the correct directory
- Check that widget-sim databases exist

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
- Check `/home/paul/code/widget_sim1/widget-sim/AGENT_DEVELOPER_GUIDE.md`
- Review simulation docs for database schemas

## Example Session

```bash
# 1. Set up environment
export OPENAI_API_KEY='sk-proj-...'

# 2. Test everything
python test_agent.py

# 3. Run a single check
python llm_inventory_agent.py --once

# 4. Run with simulation
# Terminal 1:
cd ../widget-sim
./venv/bin/python run_simulation.py 7 --disable restock --step

# Terminal 2:
cd /home/paul/code/widget_sim1/simple_inventory
python llm_inventory_agent.py --simulation

# 5. Watch it work!
```

That's it! You now have an AI agent managing your inventory! 🤖📦
