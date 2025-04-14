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
    
    if not flow_data:
        logger.error("Flow not initialized")
        raise HTTPException(status_code=500, detail="Flow not initialized")
    
    try:
        # Instead of loading the flow directly, we'll use the Langflow API
        # Assuming you have a Langflow instance running elsewhere
        langflow_api_url = os.getenv("LANGFLOW_API_URL", "https://api.langflow.com")
        
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
            raise HTTPException(status_code=response.status_code, detail=f"Langflow API error: {response.text}")
        
        result = response.json()
        return {"response": result.get("output", "No response generated")}
        
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
