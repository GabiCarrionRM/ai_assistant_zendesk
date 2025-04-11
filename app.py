import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Create a basic FastAPI app
app = FastAPI(title="AI Assistant Zendesk")

# Add some basic routes
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>AI Assistant</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                h1 { color: #333; }
                .container { max-width: 800px; margin: 0 auto; }
                .info { background-color: #f8f9fa; padding: 20px; border-radius: 5px; }
                .error { color: #721c24; background-color: #f8d7da; padding: 20px; border-radius: 5px; }
                .success { color: #155724; background-color: #d4edda; padding: 20px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>AI Assistant Zendesk</h1>
                <div class="success">
                    <h2>Service is running</h2>
                    <p>The base service is operational.</p>
                </div>
                <div class="info">
                    <h2>About this deployment</h2>
                    <p>This is a minimal deployment due to SQLite version compatibility issues with ChromaDB in the Render environment.</p>
                    <p>Full Langflow functionality that depends on ChromaDB is currently unavailable.</p>
                </div>
            </div>
        </body>
    </html>
    """

# Health check endpoint for Render
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Add more API endpoints as needed
@app.get("/api/info")
async def api_info():
    return {
        "version": "1.0.0",
        "name": "AI Assistant API",
        "status": "operational",
        "limitations": [
            "ChromaDB functionality is disabled due to SQLite version compatibility"
        ]
    }