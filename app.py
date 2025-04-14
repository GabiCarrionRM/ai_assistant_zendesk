import os
import json
import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure the app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates and static files
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Get configuration from environment variables
LANGFLOW_FLOW_ID = os.getenv("LANGFLOW_FLOW_ID")
LANGFLOW_API_URL = os.getenv("LANGFLOW_API_URL", "http://localhost:7860")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Simple homepage with status information"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "flow_id": LANGFLOW_FLOW_ID,
        "api_url": LANGFLOW_API_URL
    })

@app.post("/process")
async def process(request: Request):
    """Process a request by forwarding it to the configured Langflow flow"""
    # Check if we have the required configuration
    if not LANGFLOW_FLOW_ID:
        raise HTTPException(status_code=500, detail="LANGFLOW_FLOW_ID not configured")
    
    # Get the request data
    data = await request.json()
    
    try:
        # Extract the input from the incoming request
        user_input = data.get("input", "")
        
        # Forward to Langflow API
        langflow_endpoint = f"{LANGFLOW_API_URL}/api/v1/run/{LANGFLOW_FLOW_ID}"
        
        # Prepare payload according to Langflow's API requirements
        payload = {
            "input_value": user_input,
            "input_type": "chat",
            "output_type": "chat"
        }
        
        # Allow additional parameters to be passed through
        for key, value in data.items():
            if key != "input":
                payload[key] = value
        
        # Log the request
        logger.info(f"Forwarding request to Langflow: {langflow_endpoint}")
        
        # Make the request to Langflow
        response = requests.post(
            langflow_endpoint,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # If the request fails, raise an exception
        response.raise_for_status()
        
        # Get the response data
        result = response.json()
        
        # Log the result type
        logger.info(f"Response type: {type(result)}, content: {result}")
        
        # Extract the response based on Langflow's response format
        if isinstance(result, dict):
            # If it's a dictionary, look for common response fields
            if "result" in result:
                return {"response": result["result"]}
            elif "output" in result:
                return {"response": result["output"]}
            else:
                # Return the whole result if we can't find a specific field
                return {"response": str(result)}
        else:
            # If it's not a dictionary, just return it directly
            return {"response": str(result)}
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to Langflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error connecting to Langflow: {str(e)}")
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        if not LANGFLOW_FLOW_ID:
            return {"status": "warning", "message": "LANGFLOW_FLOW_ID not configured"}
        
        # Try to connect to the Langflow API
        response = requests.get(f"{LANGFLOW_API_URL}/api/v1/flows/{LANGFLOW_FLOW_ID}")
        if response.status_code == 200:
            return {"status": "healthy", "flow_id": LANGFLOW_FLOW_ID}
        else:
            return {"status": "unhealthy", "message": f"Langflow API returned status code {response.status_code}"}
    
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    
    # Get the port from environment variable (Render sets this)
    port = int(os.getenv("PORT", 8000))
    
    # Start the server
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
