#!/bin/bash

set -e

echo "🔧 Upgrading pip..."
pip install --upgrade pip

echo "📦 Installing from requirements.txt..."
pip install -r requirements.txt

# Optional: Patch Langflow if present
if [ -f patch_langflow.py ]; then
  echo "🔧 Running Langflow patch..."
  python -c "import sys; sys.path.append('.'); import patch_langflow" || echo "⚠️ Skipping patch_langflow.py due to errors"
fi

# Optional: Debug installed packages
pip list
