import os
import sys
import subprocess
import importlib.util
from pathlib import Path

# Configure environment variables to bypass SQLite requirements
os.environ["LANGCHAIN_TRACING"] = "false"

# Run the patch script to disable Chroma-related components
patch_script = Path(__file__).parent / "patch_chroma.py"
print(f"Running patch script: {patch_script}")
subprocess.run([sys.executable, str(patch_script)], check=True)

# Now import langflow after patching
try:
    from langflow.server import create_app
    from fastapi.responses import JSONResponse
    from fastapi import Request, FastAPI
    
    # Get the port from environment variable
    port = int(os.environ.get("PORT", 7860))
    
    # Create the FastAPI app
    base_app = create_app()
    
    # Add custom error handlers for SQLite errors
    @base_app.exception_handler(Exception)
    async def sqlite_exception_handler(request: Request, exc: Exception):
        error_message = str(exc)
        if "sqlite3" in error_message.lower() and "requires" in error_message.lower():
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Database compatibility issue: This deployment has SQLite version limitations. Some vector store features are disabled."
                },
            )
        raise exc  # Re-raise other exceptions
    
    app = base_app
    
    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=port)
        
except Exception as e:
    print(f"Error loading Langflow: {str(e)}")
    # Fallback to minimal app if Langflow can't load
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse
    
    app = FastAPI()
    
    @app.get("/", response_class=HTMLResponse)
    async def root():
        return """
        <html>
            <head>
                <title>AI Assistant</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    h1 { color: #333; }
                    .error { color: #cc0000; }
                </style>
            </head>
            <body>
                <h1>AI Assistant</h1>
                <p>Service is running, but encountered startup issues.</p>
                <p class="error">Error: SQLite version compatibility issues with Chroma components</p>
                <p>Some features are currently disabled. Please contact support for assistance.</p>
            </body>
        </html>
        """
    
    # Health check endpoint for Render
    @app.get("/health")
    async def health_check():
        return {"status": "ok"}
    
    if __name__ == "__main__":
        import uvicorn
        port = int(os.environ.get("PORT", 7860))
        uvicorn.run(app, host="0.0.0.0", port=port)