#!/usr/bin/env python
import sys
import os
import sqlite3
import importlib
from pathlib import Path

# Print the current SQLite version
print(f"Current SQLite version: {sqlite3.sqlite_version}")

# Create a mock for the chromadb module
class MockChromaModule:
    def __getattr__(self, name):
        raise ImportError("ChromaDB is disabled due to SQLite version incompatibility")

# Function to execute the real app with patched modules
def run_with_patched_modules():
    # Create directory for logging
    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)
    
    # Log the environment
    with open(log_dir / "env.log", "w") as f:
        for key, value in os.environ.items():
            f.write(f"{key}={value}\n")
    
    # Create a mock module finder to intercept chromadb imports
    class MockFinder:
        def find_spec(self, fullname, path, target=None):
            if fullname == 'chromadb' or fullname.startswith('chromadb.'):
                # Return None for missing module to fallback to other finders
                return None
            return None
    
    # Install our finder at the beginning of the sys.meta_path
    sys.meta_path.insert(0, MockFinder())
    
    # Patch the sys.modules to mock chromadb
    sys.modules['chromadb'] = MockChromaModule()
    
    # Also mock langchain_chroma
    sys.modules['langchain_chroma'] = MockChromaModule()
    
    # Print out all installed packages for debugging
    print("Installed packages:")
    import pkg_resources
    for dist in pkg_resources.working_set:
        print(f"  {dist.project_name} {dist.version}")
    
    # Run the actual application
    from app import app
    
    # Return the app for ASGI servers
    return app

# This will be used by the ASGI server
app = run_with_patched_modules()

# If this script is run directly, start the server
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("startup_wrapper:app", host="0.0.0.0", port=port, reload=False)