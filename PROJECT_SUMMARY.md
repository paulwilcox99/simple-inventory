# LLM-Powered Inventory Agent - Project Summary

## What Was Built

An intelligent AI agent that uses OpenAI's Large Language Models (LLM) to manage inventory for a manufacturing simulation. The agent monitors inventory levels daily and makes data-driven restocking decisions using advanced AI reasoning.

## Key Features

✅ **LLM-Driven Intelligence**: Uses GPT-4 or other OpenAI models to analyze inventory and make decisions
✅ **Daily Monitoring**: Runs once per simulation day to check inventory status
✅ **Smart Decisions**: LLM determines which parts to restock and optimal order quantities
✅ **ERP Integration**: Automatically updates inventory database and financial transactions
✅ **Simulation Sync**: Integrates seamlessly with the widget manufacturing simulation
✅ **Detailed Reasoning**: Shows LLM's thought process and decision rationale
✅ **Flexible Operation**: Can run standalone or synchronized with simulation
✅ **Multiple Models**: Supports GPT-4, GPT-4 Turbo, and GPT-3.5 Turbo

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   LLM Inventory Agent                        │
│                                                              │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────┐  │
│  │ Data Reader  │──────│ LLM Analyzer │──────│ Executor │  │
│  └──────────────┘      └──────────────┘      └──────────┘  │
│         │                      │                     │       │
└─────────┼──────────────────────┼─────────────────────┼───────┘
          │                      │                     │
          ▼                      ▼                     ▼
  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
  │ inventory.db │      │  OpenAI API  │      │    erp.db    │
  │  - levels    │      │   (GPT-4)    │      │ - financials │
  │  - BOM       │      └──────────────┘      └──────────────┘
  └──────────────┘
          │
          ▼
  ┌──────────────┐
  │   crm.db     │
  │  - orders    │
  └──────────────┘
```

## How It Works

### 1. Data Collection Phase
- Reads current inventory levels from `inventory.db`
- Retrieves bill of materials (parts needed per widget)
- Checks pending orders from `crm.db` to gauge demand

### 2. LLM Analysis Phase
- Constructs a detailed prompt with all inventory data
- Sends to OpenAI API (GPT-4 or selected model)
- LLM analyzes stock levels vs. demand
- Identifies parts at risk of stockout
- Calculates optimal reorder quantities
- Provides reasoning for decisions

### 3. Execution Phase
- If LLM recommends restocking:
  - Updates `inventory_levels` table with new quantities
  - Records purchase in `financial_transactions` table
  - Logs all actions with details
- If no action needed:
  - Logs that inventory is healthy
  - Waits for next check

### 4. Integration with Simulation
- Monitors `sim_state.json` for simulation status
- Runs check once per simulation day
- Exits when simulation completes

## Files Created

```
simple_inventory/
├── llm_inventory_agent.py    # Main agent (18KB)
│   └── LLMInventoryAgent class with:
│       - get_inventory_data() - queries databases
│       - construct_llm_prompt() - builds LLM prompt
│       - query_llm() - calls OpenAI API
│       - execute_restock() - updates databases
│       - run_daily_check() - main logic
│       - run_with_simulation() - sync mode
│
├── test_agent.py              # Test suite (8KB)
│   └── Tests for:
│       - API key configuration
│       - Database access
│       - LLM connection
│       - Dry-run analysis
│
├── requirements.txt           # Dependencies
│   ├── openai>=1.0.0
│   └── python-dotenv>=1.0.0
│
├── .env.example              # Configuration template
├── .gitignore                # Protects secrets
├── README.md                 # Full documentation (9KB)
├── QUICKSTART.md             # 5-minute guide (5KB)
└── PROJECT_SUMMARY.md        # This file
```

## Database Integration

### Databases Accessed:

**inventory.db** (Read & Write):
- `inventory_levels` - current stock (READ + UPDATE)
- `bom` - bill of materials (READ)

**crm.db** (Read Only):
- `orders` - pending customer orders (READ)

**erp.db** (Write):
- `financial_transactions` - purchase records (INSERT)

### Transaction Flow:
1. READ inventory levels and BOM
2. READ pending orders
3. LLM ANALYSIS (external API call)
4. UPDATE inventory quantities
5. INSERT financial transaction
6. COMMIT all changes

## Usage Modes

### Mode 1: Manual Single Check
```bash
python llm_inventory_agent.py --once
```
- Run one inventory check
- Good for testing and ad-hoc analysis
- Uses current date or specify with `--date`

### Mode 2: Simulation Integration
```bash
# Terminal 1: Start simulation (from widget-sim/)
./venv/bin/python run_simulation.py 30 --disable restock --delay 5

# Terminal 2: Start agent (from simple-inventory/)
./venv/bin/python llm_inventory_agent.py --simulation
```
- Agent monitors simulation state
- Runs check each simulation day
- Fully automated operation

### Mode 3: Testing
```bash
python test_agent.py
```
- Verifies setup
- Tests API connection
- Optional dry-run (no DB changes)

## Example LLM Decision

**Input Data:**
- Screw-1: 45 units in stock
- Widget-Body-1: 12 units in stock
- Pending orders: 25 Widget_Pro units
- Each Widget_Pro needs: 4 Screw-1, 1 Widget-Body-1

**LLM Analysis:**
```json
{
  "decision": "restock",
  "reasoning": "Critical shortage: pending orders need 100 Screw-1
                (only 45 available) and 25 Widget-Body-1 (only 12
                available). Cannot fulfill demand.",
  "parts_to_order": [
    {
      "part_name": "Screw-1",
      "current_quantity": 45,
      "order_quantity": 355,
      "rationale": "Need 100 for pending + 300 buffer (75 widgets)"
    },
    {
      "part_name": "Widget-Body-1",
      "current_quantity": 12,
      "order_quantity": 88,
      "rationale": "Need 25 for pending + 75 buffer"
    }
  ]
}
```

**Execution:**
- Updates inventory: Screw-1 → 400 units, Widget-Body-1 → 100 units
- Records purchase: $177.50 + $1,320.00 = $1,497.50
- Logs transaction in ERP system

## Configuration Options

### Model Selection
```bash
# Best reasoning (default)
--model gpt-4

# Faster, cheaper
--model gpt-4-turbo

# Cheapest
--model gpt-3.5-turbo
```

### API Key Methods
1. Environment variable: `export OPENAI_API_KEY='sk-...'`
2. .env file: Create `.env` with `OPENAI_API_KEY=sk-...`
3. Command line: `--api-key sk-...`

### Timing
```bash
# Adjust state file polling interval
--check-interval 5  # Check every 5 seconds (default: 10)
```

## Cost Estimates

Based on typical inventory data (~2000 tokens per check):

| Model | Per Check | 30 Days | 365 Days |
|-------|-----------|---------|----------|
| GPT-4 | $0.03-0.05 | ~$1.50 | ~$18.00 |
| GPT-4 Turbo | $0.01-0.02 | ~$0.60 | ~$7.20 |
| GPT-3.5 Turbo | $0.002-0.005 | ~$0.15 | ~$1.80 |

*Prices approximate, subject to OpenAI rate changes*

## Advantages Over Rule-Based Systems

Traditional inventory systems use simple thresholds:
```python
if stock < 100:
    reorder(1000)  # Fixed amount
```

This LLM agent:
- 📊 **Analyzes demand patterns** from pending orders
- 🎯 **Calculates optimal quantities** per part
- ⚖️ **Balances multiple factors** (stockout risk vs. carrying costs)
- 🔄 **Adapts to context** (high demand = order more)
- 💡 **Explains reasoning** (transparent decisions)
- 🌐 **Considers dependencies** (parts shared across widgets)

## Testing Strategy

1. **Unit Tests** (`test_agent.py`):
   - API key validation
   - Database connectivity
   - LLM API connection
   - Data query correctness

2. **Dry Run**:
   - Full analysis without DB changes
   - Verify LLM responses
   - Check decision quality

3. **Manual Mode**:
   - Single check with real execution
   - Verify DB updates
   - Check financial records

4. **Simulation Integration**:
   - 7-day test run
   - Monitor behavior over time
   - Compare vs. baseline

5. **Benchmarking**:
   - Run simulation with and without agent
   - Compare: revenue, costs, stockouts
   - Measure agent performance

## Customization Points

### Adjust Restock Thresholds
Edit `construct_llm_prompt()` method:
```python
prompt += """
## Guidelines:
- Restock when inventory < 20 widgets worth  # Change from 10
- Target: 150 widgets worth                   # Change from 100
"""
```

### Change Risk Tolerance
```python
prompt += """
- Prioritize avoiding stockouts (be aggressive)
OR
- Minimize inventory costs (be conservative)
"""
```

### Add Context
```python
# Include more data in prompt:
- Historical demand trends
- Seasonal patterns
- Lead times
- Supplier constraints
```

### Alternative LLM Providers
Replace OpenAI with:
- Azure OpenAI Service
- Anthropic Claude (via API)
- Local models (via vLLM/ollama)

## Security Considerations

✅ **API Key Protection**:
- Never commit `.env` to git
- `.gitignore` prevents accidental commits
- Use environment variables in production

✅ **Database Safety**:
- Read-only connections where possible
- Transaction rollback on errors
- Validates data before writes

✅ **Error Handling**:
- Graceful LLM API failures
- Database lock handling
- JSON parsing validation

## Future Enhancements

Potential improvements:

1. **Demand Forecasting**: Use historical data to predict future needs
2. **Multi-Agent Coordination**: Combine with order processing agent
3. **Learning from Outcomes**: Track decision quality, fine-tune prompts
4. **Web Dashboard**: Visualize LLM decisions and inventory trends
5. **A/B Testing**: Compare different models and strategies
6. **Alert System**: Notify on critical situations
7. **Cost Optimization**: Minimize API calls while maintaining quality
8. **Batch Processing**: Analyze multiple days for patterns

## Troubleshooting Guide

| Issue | Solution |
|-------|----------|
| API key error | Set `OPENAI_API_KEY` environment variable |
| Database locked | Wait and retry (simulation accessing DB) |
| JSON parse error | Use `gpt-4` instead of `gpt-3.5-turbo` |
| No LLM response | Check OpenAI account credits/billing |
| Agent not running | Verify `sim_state.json` exists |
| Wrong decisions | Adjust prompt, try different model |

## Performance Metrics

Track these to evaluate agent:

**Inventory Metrics**:
- Stockout events (lower = better)
- Average inventory value (lower = better)
- Restock frequency (optimal range)

**Financial Metrics**:
- Total inventory costs
- Revenue lost to stockouts
- Return on inventory investment

**Operational Metrics**:
- LLM API latency
- Decision time
- Error rate

**Decision Quality**:
- LLM reasoning consistency
- Prediction accuracy
- Adaptation to demand changes

## Getting Help

1. **Read Documentation**:
   - `QUICKSTART.md` - 5-minute setup
   - `README.md` - Complete documentation
   - `../AGENT_DEVELOPER_GUIDE.md` (in simulator root)

2. **Run Tests**:
   ```bash
   python test_agent.py
   ```

3. **Check Logs**:
   - Agent prints detailed output
   - Shows LLM prompts and responses
   - Displays DB operations

4. **Verify Setup**:
   - OpenAI API key valid
   - Databases accessible
   - Python dependencies installed

## Quick Start Recap

```bash
# 1. Install (from simple-inventory/)
./venv/bin/pip install -r requirements.txt

# 2. Configure
export OPENAI_API_KEY='sk-...'

# 3. Test
python test_agent.py

# 4. Run
python llm_inventory_agent.py --once

# 5. Integrate with simulation
python llm_inventory_agent.py --simulation
```

## Conclusion

You now have a fully functional AI agent that:
- ✅ Uses LLM intelligence for inventory decisions
- ✅ Integrates with manufacturing simulation
- ✅ Updates ERP system automatically
- ✅ Provides transparent reasoning
- ✅ Runs daily monitoring
- ✅ Handles errors gracefully

The agent demonstrates how LLMs can be applied to operational decision-making, replacing traditional rule-based systems with intelligent, context-aware analysis.

**Next Steps**: Run the test suite, do a manual check, then try a full 30-day simulation!

---

**Project Status**: ✅ Complete and Ready to Use

**Created**: 2026-02-13
**Technology**: Python 3, OpenAI API, SQLite
**License**: Part of Widget Manufacturing Simulation

🤖 Happy AI Agent Building! 📦
