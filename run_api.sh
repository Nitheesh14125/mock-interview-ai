#!/bin/bash
echo "🚀 Starting FastAPI Mock Interview Service..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please run ./setup.sh first"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first"
    exit 1
fi

echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Load environment variables
echo "🔧 Loading environment variables..."
export $(cat .env | grep -v '^#' | xargs)

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY is not set in .env file"
    echo "Please edit .env and add your OpenAI API key"
    exit 1
fi

echo "✅ OpenAI API key loaded"
echo "🚀 Starting server on http://localhost:8000"
echo "📚 API docs will be available at: http://localhost:8000/docs"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
