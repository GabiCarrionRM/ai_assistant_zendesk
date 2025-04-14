import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langflow import load_flow_from_json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You might want to restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load your Langflow flow
@app.on_event("startup")
async def startup_event():
    global flow_graph
    try:
        # You can either load the flow from a file or define it here
        flow_path = os.getenv("FLOW_PATH", "flow.json")
        
        # Check if the file exists
        if os.path.exists(flow_path):
            with open(flow_path, "r") as f:
                flow_data = json.load(f)
        else:
            # If you want to embed the flow directly in the code
            # This is just a placeholder - replace with your actual flow
            flow_data = {
                "nodes": [],
                "edges": []
            }
            
        # Initialize the flow
        flow_graph = load_flow_from_json(flow_data)
        print("Flow loaded successfully!")
    except Exception as e:
        print(f"Error loading flow: {str(e)}")
        flow_graph = None

@app.get("/")
async def root():
    return {"message": "Langflow API is running! Go to /docs for documentation."}

@app.post("/process")
async def process_input(request: Request):
    if flow_graph is None:
        raise HTTPException(status_code=500, detail="Flow not initialized")
    
    data = await request.json()
    user_input = data.get("input", "")
    
    try:
        # Process the input through your Langflow graph
        result = flow_graph(user_input)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing input: {str(e)}")

# Optional: Endpoint to reload the flow
@app.post("/reload")
async def reload_flow():
    try:
        await startup_event()
        return {"message": "Flow reloaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reloading flow: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Get the port from environment variable (Render sets this)
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
