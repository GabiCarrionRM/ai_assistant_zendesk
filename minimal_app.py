import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Create a minimal FastAPI app that we can expand with Langflow features
app = FastAPI()

# Create a basic endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>AI Assistant</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #333; }
            </style>
        </head>
        <body>
            <h1>AI Assistant</h1>
            <p>Service is running. Full Langflow interface is being configured.</p>
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