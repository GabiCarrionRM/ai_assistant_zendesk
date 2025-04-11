#!/bin/bash
set -e

# Upgrade pip
pip install --upgrade pip

# Install dependencies with constraints
pip install -r requirements.txt

# Apply any necessary patches
if [ -f patch_langflow.py ]; then
  python patch_langflow.py || echo "Skipping patch_langflow.py due to errors"
fi
