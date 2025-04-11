import os
import json
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Dict, Any, Optional
import uvicorn
from langflow import get_flow_from_json

# Set environment variable to avoid SQLite issues
os.environ["LANGCHAIN_TRACING"] = "false"

# Create a FastAPI app
app = FastAPI(title="AI Assistant Zendesk")

# Directory for storing flows
FLOWS_DIR = Path("flows")
FLOWS_DIR.mkdir(exist_ok=True)

# Load Langflow chat template
DEFAULT_FLOW_PATH = FLOWS_DIR / "default_chat.json"

# Templates for HTML rendering
templates_dir = Path("templates")
templates_dir.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))

# Create a basic chat interface template
chat_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Zendesk AI Assistant</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            height: 100vh;
            background-color: #f5f5f5;
        }
        .header {
            background-color: #03363d;
            color: white;
            padding: 15px 20px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
            width: 100%;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .messages {
            flex: 1;
            overflow-y: auto;
            margin-bottom: 20px;
            padding: 15px;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            background-color: #f9f9f9;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 18px;
            max-width: 80%;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            position: relative;
            clear: both;
        }
        .user-message {
            background-color: #e1f5fe;
            color: #333;
            float: right;
            border-bottom-right-radius: 4px;
        }
        .assistant-message {
            background-color: #f0f0f0;
            color: #333;
            float: left;
            border-bottom-left-radius: 4px;
        }
        .input-area {
            display: flex;
            margin-top: 10px;
            border-top: 1px solid #e0e0e0;
            padding-top: 15px;
        }
        #user-input {
            flex: 1;
            padding: 12px 15px;
            border: 1px solid #ccc;
            border-radius: 30px;
            margin-right: 10px;
            font-size: 16px;
        }
        button {
            padding: 12px 20px;
            background-color: #03363d;
            color: white;
            border: none;
            border-radius: 30px;
            cursor: pointer;
            font-weight: bold;
            transition: background-color 0.2s;
        }
        button:hover {
            background-color: #025158;
        }
        .typing-indicator {
            display: none;
            padding: 10px 15px;
            background-color: #f0f0f0;
            border-radius: 18px;
            margin-bottom: 15px;
            float: left;
            clear: both;
        }
        .dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #888;
            margin-right: 3px;
            animation: wave 1.3s linear infinite;
        }
        .dot:nth-child(2) {
            animation-delay: -1.1s;
        }
        .dot:nth-child(3) {
            animation-delay: -0.9s;
        }
        @keyframes wave {
            0%, 60%, 100% { transform: initial; }
            30% { transform: translateY(-5px); }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Zendesk AI Assistant</h1>
    </div>
    <div class="chat-container">
        <div class="messages" id="messages">
            <div class="message assistant-message">
                Hello! I'm your Zendesk AI Assistant. How can I help you today?
            </div>
        </div>
        <div class="typing-indicator" id="typing-indicator">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
        </div>
        <div class="input-area">
            <input type="text" id="user-input" placeholder="Type your question here..." />
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        const messagesContainer = document.getElementById('messages');
        const userInput = document.getElementById('user-input');
        const typingIndicator = document.getElementById('typing-indicator');

        // Add event listener for Enter key
        userInput.addEventListener('keyup', function(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        });

        function addMessage(text, isUser) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
            messageDiv.textContent = text;
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        function showTypingIndicator() {
            typingIndicator.style.display = 'block';
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        function hideTypingIndicator() {
            typingIndicator.style.display = 'none';
        }

        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;
            
            // Add user message to chat
            addMessage(message, true);
            userInput.value = '';
            
            try {
                // Show typing indicator
                showTypingIndicator();
                
                // Send message to backend
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ question: message })
                });
                
                // Hide typing indicator
                hideTypingIndicator();
                
                if (!response.ok) {
                    throw new Error('Failed to get response');
                }
                
                const data = await response.json();
                // Add assistant response to chat
                addMessage(data.response, false);
            } catch (error) {
                console.error('Error:', error);
                hideTypingIndicator();
                addMessage('Sorry, there was an error processing your request. Please try again.', false);
            }
        }
    </script>
</body>
</html>
"""

# Save the chat template
with open(templates_dir / "chat.html", "w") as f:
    f.write(chat_template)

# Load the flow
def load_default_flow():
    """Load the default Langflow"""
    if not DEFAULT_FLOW_PATH.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Flow file not found at {DEFAULT_FLOW_PATH}. Please ensure you have a valid flow file."
        )
    
    with open(DEFAULT_FLOW_PATH, "r") as f:
        try:
            flow_data = json.load(f)
            return flow_data
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error loading flow file: {str(e)}"
            )

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/api/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        question = data.get("question", "")
        
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")
        
        # Load the flow
        flow_data = load_default_flow()
        
        # Get the values and keys for ChatInput and ChatOutput nodes
        input_node_id = None
        output_node_id = None
        
        for node_id, node_data in flow_data.get("data", {}).get("nodes", {}).items():
            if node_data.get("type") == "ChatInput":
                input_node_id = node_id
            elif node_data.get("type") == "ChatOutput":
                output_node_id = node_id
        
        if not input_node_id:
            raise HTTPException(status_code=500, detail="ChatInput node not found in flow")
        
        # Build the flow
        try:
            flow = get_flow_from_json(flow_data, tweaks={
                input_node_id: {"input_value": question}
            })
        except Exception as e:
            print(f"Error building flow: {e}")
            raise HTTPException(status_code=500, detail=f"Error building flow: {str(e)}")
            
        # Run the flow
        try:
            result = await flow.arun()
            
            # Extract the response
            if isinstance(result, dict) and "text" in result:
                response = result["text"]
            elif output_node_id and output_node_id in result:
                output = result[output_node_id]
                if hasattr(output, "text"):
                    response = output.text
                else:
                    response = str(output)
            elif isinstance(result, str):
                response = result
            else:
                # Fallback to stringifying the result
                response = str(result)
            
            return {"response": response}
        except Exception as e:
            print(f"Error running flow: {e}")
            raise HTTPException(status_code=500, detail=f"Error running flow: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/info")
async def api_info():
    return {
        "version": "1.0.0",
        "name": "Zendesk AI Assistant",
        "status": "operational",
        "flow": "Zendesk AI Chat"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)