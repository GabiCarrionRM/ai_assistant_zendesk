import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

@app.get("/")
async def root():
    return {"message": "API is running! Go to /docs for documentation."}

@app.post("/process")
async def process_input(request: Request):
    data = await request.json()
    user_input = data.get("input", "")
    
    try:
        # Here you would process the input using your Langflow logic
        # For now, we'll just echo it back as a placeholder
        # Replace this with your actual processing logic
        
        # Example: Call an LLM API (you would configure this with your API key)
        # response = call_llm_api(user_input)
        
        response = f"Processed: {user_input}"
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing input: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Get the port from environment variable (Render sets this)
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
