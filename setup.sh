#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_NAME="service-mock-interview"
VENV_NAME="venv"
PYTHON_VERSION="python3"

echo -e "${GREEN}🚀 Setting up FastAPI Mock Interview Service${NC}"
echo "=================================================="

# Check if Python is installed
if ! command -v $PYTHON_VERSION &> /dev/null; then
    echo -e "${RED}❌ Python3 is not installed. Please install Python3 first.${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_NAME" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    $PYTHON_VERSION -m venv $VENV_NAME
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}📦 Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}🔄 Activating virtual environment...${NC}"
source $VENV_NAME/bin/activate

# Upgrade pip
echo -e "${YELLOW}⬆️ Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements
echo -e "${YELLOW}📚 Installing packages...${NC}"
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}🔑 Creating .env file...${NC}"
    cat > .env << 'EOF'
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# FastAPI Configuration
HOST=0.0.0.0
PORT=8000
EOF
    echo -e "${GREEN}✅ .env file created${NC}"
else
    echo -e "${YELLOW}🔑 .env file already exists${NC}"
fi

# Create run scripts
echo -e "${YELLOW}🏃 Creating run scripts...${NC}"

# FastAPI run script
cat > run_api.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting FastAPI Mock Interview Service..."
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
EOF

# CLI run script
cat > run_cli.sh << 'EOF'
#!/bin/bash
echo "🎤 Starting CLI Mock Interview..."
source venv/bin/activate
python main.py
EOF

# Development script with auto-reload
cat > run_dev.sh << 'EOF'
#!/bin/bash
echo "🔧 Starting FastAPI in development mode..."
source venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 --log-level debug
EOF

chmod +x run_api.sh run_cli.sh run_dev.sh

# Create test script
cat > test_api.sh << 'EOF'
#!/bin/bash
echo "🧪 Testing API endpoints..."

BASE_URL="http://localhost:8000"

echo "1. Testing health check..."
curl -X GET "$BASE_URL/health" | jq '.'

echo -e "\n2. Testing question generation..."
curl -X POST "$BASE_URL/generate-questions" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Python Programming", "difficulty": "simple", "num_questions": 3}' | jq '.'

echo -e "\n3. Testing text-to-speech..."
curl -X POST "$BASE_URL/text-to-speech" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test message"}' \
  --output test_speech.mp3

echo -e "\nAPI tests completed!"
EOF

chmod +x test_api.sh

echo ""
echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
echo "=================================================="
echo -e "${BLUE}📋 How to run the APIs:${NC}"
echo ""
echo -e "${YELLOW}1. Set up your OpenAI API key:${NC}"
echo "   Edit .env file and add your API key"
echo ""
echo -e "${YELLOW}2. Run FastAPI server:${NC}"
echo "   ./run_api.sh"
echo "   Access API docs at: http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}3. Run CLI version:${NC}"
echo "   ./run_cli.sh"
echo ""
echo -e "${YELLOW}4. Run in development mode:${NC}"
echo "   ./run_dev.sh"
echo ""
echo -e "${YELLOW}5. Test the API:${NC}"
echo "   ./test_api.sh"
echo ""
echo -e "${BLUE}📚 Available API endpoints:${NC}"
echo "   GET  /              - API status"
echo "   GET  /health        - Health check"
echo "   POST /generate-questions - Generate interview questions"
echo "   POST /transcribe-audio   - Convert audio to text"
echo "   POST /text-to-speech     - Convert text to audio"
echo "   POST /evaluate-answers   - Evaluate student answers"
echo "   POST /start-interview    - Start full interview session"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
