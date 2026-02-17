# LLM-Powered Inventory Agent

An intelligent inventory management agent that uses Large Language Models (OpenAI) to make data-driven restocking decisions for a manufacturing simulation.

## Overview

This agent monitors inventory levels in a widget manufacturing simulation and uses an LLM to:
1. **Analyze** current inventory levels and demand patterns
2. **Decide** which parts need restocking and when
3. **Determine** optimal order quantities for each part
4. **Execute** restocking operations and update the ERP system

The LLM makes intelligent decisions by considering:
- Current stock levels for all parts
- Bill of Materials (which parts are needed for each widget)
- Pending orders (demand indicators)
- Balancing stockout risk vs. carrying costs

## Features

✨ **LLM-Driven Decisions**: Uses GPT-4 or other OpenAI models to analyze inventory
📊 **Real-time Monitoring**: Syncs with simulation via `sim_state.json`
💰 **Cost Tracking**: Records all inventory purchases in financial transactions
🔄 **Flexible Operation**: Run standalone or integrated with simulation
📝 **Detailed Logging**: Shows LLM reasoning and decisions

## Installation

### 1. Install Dependencies

```bash
cd /home/paul/code/widget_sim1/simple_inventory
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key

Create a `.env` file with your OpenAI API key:

```bash
cp .env.example .env
# Edit .env and add your API key
```

Or export it as an environment variable:

```bash
export OPENAI_API_KEY='sk-your-api-key-here'
```

## Usage

### Mode 1: Single Manual Check

Run a one-time inventory check and get LLM recommendations:

```bash
python llm_inventory_agent.py --once
```

With specific date:
```bash
python llm_inventory_agent.py --once --date 2026-03-15
```

### Mode 2: Synchronized with Simulation

Run the agent in sync with the manufacturing simulation:

**Terminal 1** - Start simulation with restocking disabled:
```bash
cd /home/paul/code/widget_sim1/widget-sim
./venv/bin/python run_simulation.py 30 "2026-03-01" --disable restock --step
```

**Terminal 2** - Start the LLM agent:
```bash
cd /home/paul/code/widget_sim1/simple_inventory
python llm_inventory_agent.py --simulation
```

The agent will:
- Wait for the simulation to start
- Check inventory once per simulation day
- Let the LLM decide when to restock
- Execute restocking automatically
- Exit when simulation completes

## Model Selection

Use different OpenAI models based on your needs:

### GPT-4 (Default - Most Intelligent)
```bash
python llm_inventory_agent.py --simulation --model gpt-4
```
- Best reasoning capabilities
- Most accurate decisions
- Higher cost per API call

### GPT-4 Turbo (Faster)
```bash
python llm_inventory_agent.py --simulation --model gpt-4-turbo
```
- Faster response time
- Good reasoning
- Lower cost than GPT-4

### GPT-3.5 Turbo (Budget)
```bash
python llm_inventory_agent.py --simulation --model gpt-3.5-turbo
```
- Fastest and cheapest
- Acceptable for simple decisions
- May be less nuanced

## How It Works

### 1. Data Collection
The agent queries the SQLite databases to gather:
- Current inventory levels (`inventory.db`)
- Bill of Materials - parts needed per widget (`inventory.db`)
- Pending orders to gauge demand (`crm.db`)

### 2. LLM Analysis
The agent constructs a detailed prompt with all inventory data and asks the LLM to:
- Analyze stock levels relative to demand
- Identify parts at risk of stockout
- Recommend which parts to order
- Determine optimal order quantities
- Provide reasoning for decisions

### 3. Decision Execution
If the LLM recommends restocking:
- Updates `inventory_levels` table with new quantities
- Records purchase in `financial_transactions`
- Logs all actions with detailed output

### Example LLM Interaction

**Input to LLM:**
```
Current Inventory Levels:
- Screw-1: 45 units
- Screw-2: 230 units
- Widget-Body-1: 12 units
...

Bill of Materials:
Widget_Pro needs:
  - Screw-1: 4 units @ $0.50/unit
  - Widget-Body-1: 1 unit @ $15.00/unit
...

Pending Orders:
- Widget_Pro: 25 units pending
- Widget: 15 units pending
```

**LLM Response:**
```json
{
  "decision": "restock",
  "reasoning": "Screw-1 (45 units) and Widget-Body-1 (12 units) are critically low given pending orders for 25 Widget_Pro units which require 100 Screw-1 and 25 Widget-Body-1. Current stock cannot fulfill demand.",
  "parts_to_order": [
    {
      "part_name": "Screw-1",
      "current_quantity": 45,
      "order_quantity": 355,
      "rationale": "Need 100 for pending orders plus buffer for 100 more widgets"
    },
    {
      "part_name": "Widget-Body-1",
      "current_quantity": 12,
      "order_quantity": 88,
      "rationale": "Need 25 for pending orders plus buffer for 75 more widgets"
    }
  ]
}
```

## Command-Line Options

```
--once                Run single check and exit
--simulation          Run in sync with simulation
--date DATE           Specify date for manual check (YYYY-MM-DD)
--model MODEL         OpenAI model: gpt-4, gpt-4-turbo, gpt-3.5-turbo
--api-key KEY         OpenAI API key (or use env var)
--check-interval N    State file polling interval in seconds (default: 10)
```

## Database Integration

### Databases Used:
- **inventory.db**:
  - `inventory_levels` - Current stock quantities
  - `bom` - Bill of materials (parts per widget)

- **crm.db**:
  - `orders` - Customer orders and demand

- **erp.db**:
  - `financial_transactions` - Purchase records

### Data Flow:
```
1. Read: inventory.db → Get current stock & BOM
2. Read: crm.db → Get pending orders
3. Process: LLM analyzes data
4. Write: inventory.db → Update quantities
5. Write: erp.db → Record purchase transaction
```

## Advanced Configuration

### Custom Thresholds
Edit the LLM prompt in `llm_inventory_agent.py` to adjust:
- Restock thresholds (default: 10 widgets worth)
- Restock targets (default: 100 widgets worth)
- Risk tolerance
- Cost sensitivity

### Alternative LLM Providers
The code uses OpenAI's API format. To use other providers:
1. Find providers with OpenAI-compatible APIs (e.g., Azure OpenAI)
2. Modify the `openai.api_base` configuration
3. Update authentication as needed

## Troubleshooting

### "OpenAI API key must be provided"
- Set `OPENAI_API_KEY` environment variable
- Or create `.env` file with API key
- Or use `--api-key` flag

### "Failed to parse LLM response as JSON"
- LLM may have returned malformed JSON
- Try using `gpt-4` instead of `gpt-3.5-turbo`
- Check the printed response for debugging

### "Database is locked"
- Simulation and agent are accessing DB simultaneously
- This is usually temporary and will resolve
- Agent retries automatically

### Agent not detecting new days
- Check that `sim_state.json` exists in widget-sim directory
- Verify simulation is running with `--step` flag
- Increase `--check-interval` if needed

## Cost Estimation

Approximate costs per inventory check:

| Model | Cost per Check | 30-Day Sim |
|-------|---------------|------------|
| GPT-4 | $0.03 - $0.05 | ~$1.50 |
| GPT-4 Turbo | $0.01 - $0.02 | ~$0.60 |
| GPT-3.5 Turbo | $0.002 - $0.005 | ~$0.15 |

*Estimates based on typical inventory data size and OpenAI pricing*

## Project Structure

```
simple_inventory/
├── llm_inventory_agent.py   # Main agent code
├── requirements.txt          # Python dependencies
├── .env.example             # Configuration template
├── .env                     # Your API key (git-ignored)
└── README.md                # This file
```

## Integration with Simulation

The agent uses the simulation's state file synchronization:

1. Simulation writes `sim_state.json` with current day/status
2. Agent monitors this file for changes
3. On each new day, agent runs inventory check
4. LLM makes restocking decision
5. Agent executes any recommended restocking
6. Cycle repeats until simulation ends

## Future Enhancements

- 📈 **Demand Forecasting**: Use historical data to predict future needs
- 🎯 **Multi-Agent**: Combine with other AI agents (order processing, etc.)
- 📊 **Dashboard**: Web UI to visualize LLM decisions
- 🧪 **A/B Testing**: Compare LLM decisions vs. traditional rules
- 💡 **Learning**: Fine-tune model on simulation outcomes
- 🔔 **Alerts**: Notify on critical inventory situations

## Contributing

To modify the agent:
1. Edit `llm_inventory_agent.py`
2. Adjust the `construct_llm_prompt()` method to change LLM instructions
3. Modify `execute_restock()` to change restocking logic
4. Update `run_daily_check()` for different scheduling

## License

Part of the Widget Manufacturing Simulation project.

## Support

For questions or issues:
1. Check the simulation's `AGENT_DEVELOPER_GUIDE.md`
2. Review `AGENT_INTEGRATION.md` for patterns
3. Check OpenAI API status and quotas
4. Verify database file permissions

---

**Happy AI Agent Building! 🤖📦**
