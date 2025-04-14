import os
import json
import importlib
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import requests
import traceback
import logging
import time
from langchain.agents import initialize_agent, Tool
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

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

# Store for creating chains
llm_chains = {}
processor = None

# Load the Langflow flow
@app.on_event("startup")
async def startup_event():
    global flow_data, processor
    try:
        flow_path = os.getenv("FLOW_PATH", "flow.json")
        logger.info(f"Loading flow from {flow_path}")
        
        # Check if the file exists
        if os.path.exists(flow_path):
            with open(flow_path, "r") as f:
                flow_data = json.load(f)
            logger.info("Flow loaded successfully")
            
            # Initialize processor
            processor = FlowProcessor(flow_data)
            
        else:
            logger.error(f"Flow file not found: {flow_path}")
            flow_data = None
    except Exception as e:
        logger.error(f"Error loading flow: {str(e)}")
        logger.error(traceback.format_exc())
        flow_data = None

class FlowProcessor:
    def __init__(self, flow_data):
        self.flow_data = flow_data
        self.components = {}
        self.initialize_components()
        
    def initialize_components(self):
        # Initialize a simple LLM chain as fallback
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            try:
                llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
                prompt_template = PromptTemplate(
                    input_variables=["input"],
                    template="You are a helpful assistant. Answer the following question: {input}"
                )
                self.components["default_chain"] = LLMChain(llm=llm, prompt=prompt_template)
            except Exception as e:
                logger.error(f"Error initializing OpenAI LLM: {str(e)}")
                self.components["default_chain"] = None
        else:
            logger.warning("No OpenAI API key found. Default chain will not be available.")
            self.components["default_chain"] = None
    
    def process(self, user_input):
        try:
            # For now, use the default chain
            if self.components["default_chain"]:
                result = self.components["default_chain"].run(user_input)
                return result
            else:
                return f"I received your message: '{user_input}', but I'm not configured with an LLM yet."
        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            return f"I encountered an error while processing your message. Please try again later."

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/process")
async def process_input(request: Request):
    data = await request.json()
    user_input = data.get("input", "")
    
    # Check if we're in development/debug mode
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    try:
        # If we're in debug mode, return a test response
        if debug_mode:
            logger.info(f"Debug mode: returning test response for input: {user_input}")
            return {"response": f"DEBUG MODE: I received your message: '{user_input}'. This is a test response."}
        
        # Process with our direct integration
        if processor is not None:
            result = processor.process(user_input)
            return {"response": result}
        else:
            logger.warning("No processor available")
            return {"response": f"I received your message: '{user_input}', but the flow processor is not initialized yet."}
            
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
