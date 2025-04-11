import os
import sys
import importlib

# Configure environment variables to use in-memory storage for Chroma
os.environ["LANGCHAIN_CHROMA_IMPL"] = "in-memory"
os.environ["LANGCHAIN_TRACING"] = "false"

# Now we can safely import langflow
from langflow.server import create_app

# Get the port from environment variable
port = int(os.environ.get("PORT", 7860))

# Create the FastAPI app
app = create_app()

# Langflow will handle the serving through its internal setup
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)