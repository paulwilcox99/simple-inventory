#!/usr/bin/env python3
"""
LLM-Powered Inventory Agent

This agent uses an OpenAI LLM to intelligently monitor inventory levels
and make restocking decisions. The LLM analyzes current stock levels,
bill of materials, and determines:
1. Which parts should be restocked
2. How many units to order

The agent runs once per day and integrates with the simulation.
"""

import os
import sys
import json
import sqlite3
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add widget-sim to path for imports
WIDGET_SIM_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(WIDGET_SIM_DIR))

# Database locations
DB_DIR = WIDGET_SIM_DIR / "databases"
INVENTORY_DB = DB_DIR / "inventory.db"
CRM_DB = DB_DIR / "crm.db"
STATE_FILE = WIDGET_SIM_DIR / "sim_state.json"


class LLMInventoryAgent:
    """AI agent that uses LLM to make inventory restocking decisions."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize the LLM inventory agent.

        Args:
            api_key: OpenAI API key (if None, reads from OPENAI_API_KEY env var)
            model: OpenAI model to use (default: gpt-4)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")

        # Initialize OpenAI client (new API v1.0+)
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.restock_count = 0

        print(f"🤖 LLM Agent initialized with model: {model}")

    def get_inventory_data(self) -> Dict:
        """
        Retrieve current inventory levels and bill of materials.

        Returns:
            Dict with inventory data including parts, quantities, and BOM info
        """
        conn = sqlite3.connect(str(INVENTORY_DB))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get current inventory levels
        cursor.execute("""
            SELECT part_name, quantity_available
            FROM inventory_levels
            ORDER BY part_name
        """)
        inventory_levels = {row['part_name']: row['quantity_available']
                          for row in cursor.fetchall()}

        # Get bill of materials
        cursor.execute("""
            SELECT widget_type, part_name, quantity_needed, unit_cost
            FROM bom
            ORDER BY widget_type, part_name
        """)
        bom = [dict(row) for row in cursor.fetchall()]

        conn.close()

        # Calculate requirements per widget type
        widget_requirements = {}
        for entry in bom:
            widget_type = entry['widget_type']
            if widget_type not in widget_requirements:
                widget_requirements[widget_type] = []
            widget_requirements[widget_type].append({
                'part': entry['part_name'],
                'qty_per_widget': entry['quantity_needed'],
                'unit_cost': entry['unit_cost']
            })

        return {
            'inventory_levels': inventory_levels,
            'bom': bom,
            'widget_requirements': widget_requirements
        }

    def get_order_backlog(self) -> List[Dict]:
        """
        Get pending orders to help LLM understand demand.

        Returns:
            List of pending orders
        """
        conn = sqlite3.connect(str(CRM_DB))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT widget_type, quantity, status
            FROM orders
            WHERE status IN ('order_received', 'order_processing')
            ORDER BY order_id
        """)

        orders = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return orders

    def construct_llm_prompt(self, inventory_data: Dict, orders: List[Dict]) -> str:
        """
        Construct a detailed prompt for the LLM to analyze inventory.

        Args:
            inventory_data: Current inventory and BOM data
            orders: Pending orders

        Returns:
            Formatted prompt string
        """
        prompt = """You are an expert inventory manager for a widget manufacturing company.
Your job is to analyze current inventory levels and determine which parts need to be restocked.

## Current Inventory Levels:
"""

        # Add inventory levels
        for part, qty in sorted(inventory_data['inventory_levels'].items()):
            prompt += f"- {part}: {qty} units in stock\n"

        prompt += "\n## Bill of Materials (parts needed per widget):\n"

        # Add BOM info by widget type
        for widget_type, requirements in inventory_data['widget_requirements'].items():
            prompt += f"\n### {widget_type}:\n"
            for req in requirements:
                prompt += f"  - {req['part']}: {req['qty_per_widget']} units @ ${req['unit_cost']:.2f}/unit\n"

        # Add order backlog
        if orders:
            prompt += "\n## Pending Orders (indicating demand):\n"
            order_summary = {}
            for order in orders:
                widget = order['widget_type']
                qty = order['quantity']
                order_summary[widget] = order_summary.get(widget, 0) + qty

            for widget, total_qty in sorted(order_summary.items()):
                prompt += f"- {widget}: {total_qty} units pending\n"

        prompt += """
## Your Task:
Analyze the inventory levels considering:
1. Current stock levels
2. Parts needed to fulfill pending orders
3. Expected future demand (assume steady production)
4. Risk of stockouts vs. carrying costs

Determine which parts should be restocked NOW and how many units to order for each part.

## Guidelines:
- Consider restocking when inventory is low relative to demand
- Typical restock threshold: enough for 10 widgets of each type
- Typical restock target: enough for 100 widgets of each type
- Balance between avoiding stockouts and minimizing inventory costs
- Consider that parts may be shared across multiple widget types

## Response Format:
Respond with a JSON object only (no other text). Format:
{
  "decision": "restock" or "no_action",
  "reasoning": "Brief explanation of your decision",
  "parts_to_order": [
    {
      "part_name": "exact_part_name",
      "current_quantity": current_stock_level,
      "order_quantity": units_to_order,
      "rationale": "why this amount"
    }
  ]
}

If no restocking is needed, set "decision": "no_action" and "parts_to_order": []
"""

        return prompt

    def query_llm(self, prompt: str) -> Dict:
        """
        Query the LLM for inventory restocking decisions.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            Dict with LLM's decision and recommendations
        """
        try:
            print("🧠 Consulting LLM for inventory decision...")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert inventory management assistant. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent decisions
                max_tokens=1500
            )

            # Extract response text
            response_text = response.choices[0].message.content.strip()

            # Parse JSON response
            # Sometimes LLMs wrap JSON in markdown code blocks
            if response_text.startswith("```"):
                # Remove markdown code block formatting
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            decision = json.loads(response_text)

            return decision

        except json.JSONDecodeError as e:
            print(f"⚠️  Failed to parse LLM response as JSON: {e}")
            print(f"Response was: {response_text}")
            return {
                "decision": "no_action",
                "reasoning": "Failed to parse LLM response",
                "parts_to_order": []
            }
        except Exception as e:
            print(f"❌ Error querying LLM: {e}")
            return {
                "decision": "no_action",
                "reasoning": f"Error: {str(e)}",
                "parts_to_order": []
            }

    def execute_restock(self, date: str, parts_to_order: List[Dict]) -> bool:
        """
        Execute restocking by updating the inventory database.

        Args:
            date: Simulation date (YYYY-MM-DD)
            parts_to_order: List of parts to restock

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"\n📦 Executing restock for {len(parts_to_order)} parts...")

            # Connect to databases
            inv_conn = sqlite3.connect(str(INVENTORY_DB))
            erp_conn = sqlite3.connect(str(DB_DIR / "erp.db"))

            inv_cursor = inv_conn.cursor()
            erp_cursor = erp_conn.cursor()

            total_cost = 0.0

            for part_info in parts_to_order:
                part_name = part_info['part_name']
                order_qty = part_info['order_quantity']

                # Get unit cost from BOM
                inv_cursor.execute("""
                    SELECT unit_cost FROM bom
                    WHERE part_name = ?
                    LIMIT 1
                """, (part_name,))

                result = inv_cursor.fetchone()
                if not result:
                    print(f"⚠️  Part {part_name} not found in BOM, skipping")
                    continue

                unit_cost = result[0]
                part_cost = order_qty * unit_cost
                total_cost += part_cost

                # Update inventory
                inv_cursor.execute("""
                    UPDATE inventory_levels
                    SET quantity_available = quantity_available + ?
                    WHERE part_name = ?
                """, (order_qty, part_name))

                print(f"   ✓ {part_name}: +{order_qty} units (${part_cost:,.2f})")

            # Record financial transaction
            erp_cursor.execute("""
                INSERT INTO financial_transactions
                (transaction_type, amount, date, description)
                VALUES (?, ?, ?, ?)
            """, (
                'inventory_purchase',
                total_cost,  # Positive = expense
                date,
                f'LLM Agent: Restocked {len(parts_to_order)} parts'
            ))

            # Commit changes
            inv_conn.commit()
            erp_conn.commit()

            inv_conn.close()
            erp_conn.close()

            print(f"💰 Total restock cost: ${total_cost:,.2f}")
            print("✅ Restock completed successfully")

            self.restock_count += 1
            return True

        except Exception as e:
            print(f"❌ Error executing restock: {e}")
            if 'inv_conn' in locals():
                inv_conn.rollback()
                inv_conn.close()
            if 'erp_conn' in locals():
                erp_conn.rollback()
                erp_conn.close()
            return False

    def run_daily_check(self, sim_date: Optional[str] = None) -> bool:
        """
        Run daily inventory check and make restocking decision.

        Args:
            sim_date: Simulation date (YYYY-MM-DD), defaults to today

        Returns:
            True if restocking was performed, False otherwise
        """
        date = sim_date or datetime.now().strftime("%Y-%m-%d")

        print(f"\n{'='*60}")
        print(f"🤖 LLM Inventory Agent - Daily Check")
        print(f"📅 Date: {date}")
        print(f"{'='*60}\n")

        # Get current inventory data
        print("📊 Gathering inventory data...")
        inventory_data = self.get_inventory_data()
        orders = self.get_order_backlog()

        print(f"   - {len(inventory_data['inventory_levels'])} parts in inventory")
        print(f"   - {len(orders)} pending orders")

        # Construct prompt and query LLM
        prompt = self.construct_llm_prompt(inventory_data, orders)
        decision = self.query_llm(prompt)

        # Display LLM decision
        print(f"\n💭 LLM Decision: {decision['decision'].upper()}")
        print(f"📝 Reasoning: {decision['reasoning']}")

        # Execute restock if recommended
        if decision['decision'] == 'restock' and decision['parts_to_order']:
            print(f"\n📋 LLM recommends restocking {len(decision['parts_to_order'])} parts:")
            for part in decision['parts_to_order']:
                print(f"   - {part['part_name']}: {part['current_quantity']} → {part['current_quantity'] + part['order_quantity']} units")
                print(f"     Rationale: {part['rationale']}")

            success = self.execute_restock(date, decision['parts_to_order'])
            return success
        else:
            print("\n✅ No restocking needed at this time")
            return False

    def run_with_simulation(self, check_interval: int = 10):
        """
        Run agent in sync with the simulation using sim_state.json.

        Args:
            check_interval: How often to check state file (seconds)
        """
        print("\n🚀 Starting LLM Inventory Agent in simulation mode...")
        print(f"📁 Monitoring state file: {STATE_FILE}")
        print(f"🔄 Check interval: {check_interval}s\n")

        last_day_checked = 0

        try:
            while True:
                # Check if state file exists
                if not STATE_FILE.exists():
                    time.sleep(check_interval)
                    continue

                # Read simulation state
                try:
                    with open(STATE_FILE, 'r') as f:
                        state = json.load(f)
                except (json.JSONDecodeError, IOError):
                    # File might be being written
                    time.sleep(0.5)
                    continue

                sim_status = state['simulation']['status']
                current_day = state['simulation']['day_number']
                sim_date = state['simulation']['date']

                # Check if simulation has ended
                if sim_status in ['finished', 'interrupted', 'error']:
                    print(f"\n{'='*60}")
                    print(f"🏁 Simulation ended (status: {sim_status})")
                    print(f"📊 Total restocks performed: {self.restock_count}")
                    print(f"{'='*60}")
                    break

                # Run check once per day when simulation is running or day is complete
                # (day_complete status is used in step mode when paused)
                if sim_status in ['running', 'day_complete'] and current_day > last_day_checked:
                    self.run_daily_check(sim_date)
                    last_day_checked = current_day

                time.sleep(check_interval)

        except KeyboardInterrupt:
            print(f"\n\n⚠️  Agent interrupted by user")
            print(f"📊 Total restocks performed: {self.restock_count}")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="LLM-powered inventory management agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run single check (manual mode)
  python llm_inventory_agent.py --once

  # Run with simulation (sync mode)
  python llm_inventory_agent.py --simulation

  # Use specific model
  python llm_inventory_agent.py --simulation --model gpt-3.5-turbo

  # Specify API key directly
  python llm_inventory_agent.py --once --api-key sk-...
        """
    )

    parser.add_argument(
        '--once',
        action='store_true',
        help='Run single inventory check and exit'
    )

    parser.add_argument(
        '--simulation',
        action='store_true',
        help='Run in sync with simulation (monitors sim_state.json)'
    )

    parser.add_argument(
        '--date',
        type=str,
        help='Simulation date for manual check (YYYY-MM-DD)'
    )

    parser.add_argument(
        '--model',
        type=str,
        default='gpt-4',
        help='OpenAI model to use (default: gpt-4)'
    )

    parser.add_argument(
        '--api-key',
        type=str,
        help='OpenAI API key (or set OPENAI_API_KEY env var)'
    )

    parser.add_argument(
        '--check-interval',
        type=int,
        default=10,
        help='State file check interval in seconds (default: 10)'
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.once and not args.simulation:
        parser.error("Must specify either --once or --simulation")

    try:
        # Initialize agent
        agent = LLMInventoryAgent(
            api_key=args.api_key,
            model=args.model
        )

        if args.once:
            # Run single check
            agent.run_daily_check(args.date)
        else:
            # Run with simulation
            agent.run_with_simulation(args.check_interval)

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nSet your OpenAI API key:")
        print("  export OPENAI_API_KEY='sk-...'")
        print("Or use --api-key flag")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
