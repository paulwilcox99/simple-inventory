#!/bin/bash
# Helper script to set up OpenAI API key

echo "============================================================"
echo "OpenAI API Key Setup"
echo "============================================================"
echo ""

# Check if .env already exists with a key
if [ -f .env ]; then
    if grep -q "^OPENAI_API_KEY=sk-" .env; then
        echo "✅ .env file already exists with an API key"
        echo ""
        echo "Current key (masked): $(grep OPENAI_API_KEY .env | cut -d= -f2 | sed 's/\(sk-....\).*\(....\)/\1****\2/')"
        echo ""
        read -p "Do you want to update it? (y/n) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Keeping existing key."
            exit 0
        fi
    fi
fi

echo "Please enter your OpenAI API key:"
echo "(Get one at: https://platform.openai.com/api-keys)"
echo ""
read -p "API Key (starts with sk-): " api_key

# Validate format
if [[ ! $api_key =~ ^sk- ]]; then
    echo ""
    echo "❌ Error: API key should start with 'sk-'"
    echo "Please try again with a valid OpenAI API key"
    exit 1
fi

# Write to .env file
cat > .env << EOF
# OpenAI API Configuration
OPENAI_API_KEY=$api_key

# Uncomment and set to use a different model (optional)
# OPENAI_MODEL=gpt-4-turbo
EOF

echo ""
echo "✅ API key saved to .env file!"
echo ""
echo "Next steps:"
echo "  1. Test your setup:  ./venv/bin/python test_agent.py"
echo "  2. Run single check: ./venv/bin/python llm_inventory_agent.py --once"
echo ""
