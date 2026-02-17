#!/usr/bin/env python3
"""
Test script for LLM Inventory Agent

This script helps verify the agent setup and test its functionality
without running the full simulation.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add widget-sim to path
WIDGET_SIM_DIR = Path(__file__).parent.parent / "widget-sim"
sys.path.insert(0, str(WIDGET_SIM_DIR))


def test_api_key():
    """Test if OpenAI API key is configured."""
    print("Testing OpenAI API key configuration...")

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("\nTo fix:")
        print("  export OPENAI_API_KEY='sk-...'")
        print("Or create a .env file with your API key")
        return False

    if not api_key.startswith("sk-"):
        print("⚠️  API key doesn't look right (should start with 'sk-')")
        return False

    print(f"✅ API key found: {api_key[:8]}...{api_key[-4:]}")
    return True


def test_database_access():
    """Test if databases are accessible."""
    print("\nTesting database access...")

    import sqlite3

    DB_DIR = WIDGET_SIM_DIR / "databases"

    databases = {
        "inventory.db": ["inventory_levels", "bom"],
        "crm.db": ["orders"],
        "erp.db": ["financial_transactions", "employees"]
    }

    all_good = True

    for db_name, tables in databases.items():
        db_path = DB_DIR / db_name

        if not db_path.exists():
            print(f"❌ {db_name} not found at {db_path}")
            all_good = False
            continue

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✅ {db_name}.{table}: {count} rows")

            conn.close()

        except Exception as e:
            print(f"❌ Error accessing {db_name}: {e}")
            all_good = False

    return all_good


def test_inventory_query():
    """Test querying inventory data."""
    print("\nTesting inventory data query...")

    import sqlite3

    DB_DIR = WIDGET_SIM_DIR / "databases"
    INVENTORY_DB = DB_DIR / "inventory.db"

    try:
        conn = sqlite3.connect(str(INVENTORY_DB))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get low stock parts
        cursor.execute("""
            SELECT part_name, quantity_available
            FROM inventory_levels
            WHERE quantity_available < 200
            ORDER BY quantity_available
            LIMIT 5
        """)

        low_stock = cursor.fetchall()

        if low_stock:
            print(f"📊 Found {len(low_stock)} parts with low stock (<200):")
            for row in low_stock:
                print(f"   - {row['part_name']}: {row['quantity_available']} units")
        else:
            print("✅ All parts have healthy stock levels (>200)")

        # Get widget types
        cursor.execute("SELECT DISTINCT widget_type FROM bom ORDER BY widget_type")
        widgets = [row[0] for row in cursor.fetchall()]

        print(f"\n📦 Widget types in system: {', '.join(widgets)}")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error querying inventory: {e}")
        return False


def test_llm_connection():
    """Test LLM API connection."""
    print("\nTesting LLM API connection...")

    try:
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ No API key to test")
            return False

        client = OpenAI(api_key=api_key)

        # Simple test query
        print("🧠 Sending test query to LLM...")

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use cheaper model for test
            messages=[
                {"role": "user", "content": "Respond with just the word 'OK' if you can read this."}
            ],
            max_tokens=10,
            temperature=0
        )

        result = response.choices[0].message.content.strip()
        print(f"📥 LLM response: {result}")

        if "OK" in result.upper():
            print("✅ LLM API connection successful!")
            return True
        else:
            print("⚠️  LLM responded but not as expected")
            return False

    except Exception as e:
        print(f"❌ Error connecting to LLM: {e}")

        if "authentication" in str(e).lower() or "api_key" in str(e).lower():
            print("\n💡 This looks like an API key issue:")
            print("   - Check your API key is correct")
            print("   - Verify it's active at https://platform.openai.com/api-keys")
            print("   - Check if you have credits/billing set up")

        return False


def run_dry_run():
    """Run agent in dry-run mode (analysis only, no execution)."""
    print("\n" + "="*60)
    print("Running Agent Dry-Run (Analysis Only)")
    print("="*60 + "\n")

    try:
        from llm_inventory_agent import LLMInventoryAgent

        agent = LLMInventoryAgent(model="gpt-3.5-turbo")  # Cheaper for testing

        # Gather data
        inventory_data = agent.get_inventory_data()
        orders = agent.get_order_backlog()

        print(f"📊 Current inventory: {len(inventory_data['inventory_levels'])} parts")
        print(f"📋 Pending orders: {len(orders)}")

        # Show low stock items
        low_stock = [(part, qty) for part, qty in inventory_data['inventory_levels'].items() if qty < 200]
        if low_stock:
            print(f"\n⚠️  Parts with stock < 200:")
            for part, qty in sorted(low_stock, key=lambda x: x[1])[:10]:
                print(f"   - {part}: {qty}")

        # Construct prompt
        prompt = agent.construct_llm_prompt(inventory_data, orders)

        print(f"\n📝 LLM Prompt length: {len(prompt)} characters")
        print("\n🧠 Querying LLM for recommendation...")

        decision = agent.query_llm(prompt)

        print(f"\n{'='*60}")
        print("LLM DECISION")
        print("="*60)
        print(f"Decision: {decision['decision'].upper()}")
        print(f"Reasoning: {decision['reasoning']}")

        if decision['parts_to_order']:
            print(f"\nRecommended restocking ({len(decision['parts_to_order'])} parts):")
            for part in decision['parts_to_order']:
                print(f"\n  {part['part_name']}:")
                print(f"    Current: {part['current_quantity']}")
                print(f"    Order: {part['order_quantity']}")
                print(f"    New total: {part['current_quantity'] + part['order_quantity']}")
                print(f"    Rationale: {part['rationale']}")

        print("\n" + "="*60)
        print("✅ Dry-run complete! (No changes made to database)")
        print("="*60)

        return True

    except Exception as e:
        print(f"\n❌ Error during dry-run: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("LLM Inventory Agent - Test Suite")
    print("="*60 + "\n")

    tests = [
        ("API Key Configuration", test_api_key),
        ("Database Access", test_database_access),
        ("Inventory Query", test_inventory_query),
        ("LLM Connection", test_llm_connection),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        result = test_func()
        results.append((test_name, result))
        print()

    # Summary
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n🎉 All tests passed!")
        print("\nReady to run dry-run? (y/n): ", end="")

        try:
            response = input().strip().lower()
            if response == 'y':
                run_dry_run()
        except KeyboardInterrupt:
            print("\n\nTest aborted.")

    else:
        print("\n⚠️  Some tests failed. Fix issues before running agent.")

    print("\n" + "="*60)


if __name__ == "__main__":
    main()
