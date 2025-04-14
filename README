# Langflow API for Zendesk

This repository contains a FastAPI application that serves a Langflow flow for integration with Zendesk.

## Setup

1. Replace `flow.json` with your exported Langflow flow
2. Set up environment variables for any API keys or credentials needed
3. Deploy to Render using the provided configuration

## Local Development

To run locally:

```bash
pip install -r requirements.txt
python app.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /`: Check if the API is running
- `POST /process`: Process a request through your Langflow flow
  - Request body: `{"input": "your input text"}`
  - Response: `{"response": "processed output"}`
- `POST /reload`: Reload the flow (useful for updates)

## Deployment

This repository is configured for easy deployment on Render. Connect your GitHub repository to Render and use the Web Service deployment type.

## Environment Variables

- `FLOW_PATH`: Path to your flow.json file (default: "flow.json")
- `PORT`: Port to run the application (default: 8000)
- Add any API keys required by your flow as environment variables in Render
