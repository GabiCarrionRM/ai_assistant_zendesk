FROM python:3.10.8-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install uv and use it to install dependencies
RUN pip install uv && \
    uv pip install -r requirements.txt

# Copy application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "app:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120"]
