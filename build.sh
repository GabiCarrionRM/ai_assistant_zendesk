#!/bin/bash
set -e

pip install --upgrade pip
pip install -r requirements.txt

# Optional: patch chroma if needed
if [ -f patch_langflow.py ]; then
  python -c "import sys; sys.path.append('.'); import patch_langflow" || echo "Skipping patch_langflow.py due to errors"
fi

pip list
