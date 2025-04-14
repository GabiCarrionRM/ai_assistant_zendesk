import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import requests
import traceback
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates directory
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load the Langflow flow
@app.on_event("startup")
async def startup_event():
    global flow_data
    try:
        flow_path = os.getenv("FLOW_PATH", "flow.json")
        logger.info(f"Loading flow from {flow_path}")
        
        # Check if the file exists
        if os.path.exists(flow_path):
            with open(flow_path, "r") as f:
                flow_data = json.load(f)
            logger.info("Flow loaded successfully")
        else:
            logger.error(f"Flow file not found: {flow_path}")
            flow_data = None
    except Exception as e:
        logger.error(f"Error loading flow: {str(e)}")
        logger.error(traceback.format_exc())
        flow_data = None

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/process")
async def process_input(request: Request):
    data = await request.json()
    user_input = data.get("input", "")
    
    # Check if we're in development/debug mode
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    if not flow_data and not debug_mode:
        logger.error("Flow not initialized")
        raise HTTPException(status_code=500, detail="Flow not initialized")
    
    try:
        # If we're in debug mode, return a test response
        if debug_mode:
            logger.info(f"Debug mode: returning test response for input: {user_input}")
            return {"response": f"DEBUG MODE: I received your message: '{user_input}'. This is a test response since Langflow API is not configured."}
        
        # Try to use Langflow API if available
        try:
            langflow_api_url = os.getenv("LANGFLOW_API_URL")
            
            # If no API URL is set, use fallback mode
            if not langflow_api_url:
                logger.warning("No LANGFLOW_API_URL set, using fallback mode")
                return {"response": f"I received your message: '{user_input}'. The Langflow API is not configured yet, so I'm providing this fallback response."}
            
            # Prepare the payload for Langflow API
            payload = {
                "flow": flow_data,
                "inputs": {
                    "input": user_input
                }
            }
            
            # Call the Langflow API to process the flow
            response = requests.post(
                f"{langflow_api_url}/api/v1/process",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {os.getenv('LANGFLOW_API_KEY', '')}"
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Langflow API error: {response.text}")
                # Use fallback in case of API error
                return {"response": f"I received your message, but there was an issue processing it with the Langflow API. Here's a fallback response instead."}
            
            result = response.json()
            return {"response": result.get("output", "No response generated")}
            
        except Exception as e:
            logger.error(f"Error with Langflow API: {str(e)}")
            # Use fallback in case of any exception
            return {"response": f"I received your message: '{user_input}'. There was an issue connecting to the Langflow API, so I'm providing this fallback response."}
            
    except Exception as e:
        logger.error(f"Error processing input: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing input: {str(e)}")

@app.get("/health")
async def health_check():
    """Endpoint for health checking the API"""
    if flow_data:
        return {"status": "healthy", "flow_loaded": True}
    return {"status": "unhealthy", "flow_loaded": False}

if __name__ == "__main__":
    import uvicorn
    
    # Get the port from environment variable (Render sets this)
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
