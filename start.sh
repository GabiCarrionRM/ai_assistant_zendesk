#!/bin/bash
set -e

# Set environment variables to avoid SQLite issues
export LANGCHAIN_TRACING="false"

# Print SQLite version info
echo "Checking SQLite version..."
python -c "import sqlite3; print(f'SQLite version: {sqlite3.sqlite_version}')"

# Try to patch if needed
echo "Running the application with patching..."
python app.py