#!/bin/bash

# Explicitly set environment variable to use in-memory Chroma
export LANGCHAIN_CHROMA_IMPL="in-memory"
export LANGCHAIN_TRACING="false"

# Run the application
python app.py