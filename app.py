from langflow.server import create_app
import os

# Get the port from environment variable
port = int(os.environ.get("PORT", 7860))

# Create the FastAPI app
app = create_app()

# Langflow will handle the serving through its internal setup
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=p
