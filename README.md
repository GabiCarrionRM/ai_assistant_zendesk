# Langflow Bridge for Zendesk

This application serves as a bridge between Langflow and Zendesk, allowing you to deploy your Langflow flows in a simple, stable way and make them accessible to Zendesk via a webhook.

## How It Works

1. The bridge connects to your Langflow instance and forwards requests to your specified flow ID
2. It handles the API translation between Zendesk's webhook format and Langflow's API
3. It provides a stable, simple API endpoint that Zendesk can connect to

## Requirements

- A running Langflow instance (local or cloud)
- A flow ID from your Langflow instance
- Docker (for local development) or a Render account (for deployment)

## Environment Variables

Set these environment variables to configure the bridge:

- `LANGFLOW_FLOW_ID`: The ID of your Langflow flow (required)
- `LANGFLOW_API_URL`: The URL of your Langflow API (default: http://localhost:7860)
- `PORT`: The port to run the application on (default: 8000)

## Deployment on Render

1. Fork this repository
2. Create a new Web Service on Render, connected to your fork
3. Choose "Docker" as the environment
4. Set the required environment variables
5. Deploy

## Local Development

```bash
# Clone the repository
git clone <your-fork-url>
cd langflow-bridge

# Set environment variables
export LANGFLOW_FLOW_ID=your-flow-id
export LANGFLOW_API_URL=http://localhost:7860

# Run with Docker
docker build -t langflow-bridge .
docker run -p 8000:8000 -e LANGFLOW_FLOW_ID -e LANGFLOW_API_URL langflow-bridge

# Or run directly with Python
pip install -r requirements.txt
python app.py
```

## Zendesk Integration

1. In Zendesk Admin Center, create a new webhook
2. Set the URL to your deployed Render instance: `https://your-app.onrender.com/process`
3. Set the method to POST
4. Set the content type to application/json
5. Create a trigger in Zendesk that uses this webhook

## API Endpoint

**POST /process**

Payload:
```json
{
  "input": "Your message here"
}
```

Response:
```json
{
  "response": "AI response here"
}
```

You can add additional fields to the payload, and they will be forwarded to Langflow.

## Advantages of This Approach

1. **Simplified Deployment**: Minimal dependencies and stable connection
2. **Flow Flexibility**: Change your Langflow flow without redeploying the bridge
3. **Model Switching**: Easily switch between different LLMs in Langflow
4. **Error Handling**: Built-in error handling and logging
5. **Testing Interface**: Built-in UI for testing your flow
