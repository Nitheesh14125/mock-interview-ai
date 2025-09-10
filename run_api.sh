#!/bin/bash
echo "🚀 Starting FastAPI Mock Interview Service..."
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
