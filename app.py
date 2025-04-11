import os
import sys
import importlib

# Apply the SQLite fix BEFORE any other imports
# This is the recommended approach from Chroma documentation
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    print("Successfully replaced sqlite3 with pysqlite3")
except ImportError:
    print("pysqlite3 not available, using built-in sqlite3")

# Now import Langflow after SQLite fix
from langflow.server import create_app

# Get the port from environment variable
port = int(os.environ.get("PORT", 7860))

# Create the FastAPI app
app = create_app()

# Langflow will handle the serving through its internal setup
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)