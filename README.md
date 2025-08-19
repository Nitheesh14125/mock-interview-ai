# 🎤 Mock Interview Service

An AI-powered mock interview system with speech recognition and text-to-speech capabilities using OpenAI's GPT, Whisper, and TTS models.

## 📋 Table of Contents
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Usage](#-usage)
  - [CLI Version](#cli-version)
  - [API Version](#api-version)
- [API Endpoints](#-api-endpoints)
- [Example Usage](#-example-usage)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

## 🌟 Features

- **AI-Powered Questions**: Generate interview questions based on topic and difficulty
- **Speech Recognition**: Convert audio responses to text using Whisper
- **Text-to-Speech**: Convert AI responses to audio
- **Real-time Feedback**: Get instant evaluation of your answers
- **Session Management**: Track interview progress step-by-step
- **Multiple Interfaces**: Both CLI and REST API versions available

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Audio device (microphone and speakers/headphones)
- Linux/macOS/Windows with audio support

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
cd /service-mock-interview
```

### 2. Run Automated Setup
```bash
chmod +x setup.sh
./setup.sh
```

This script will:
- Create a virtual environment
- Install all required packages
- Create necessary configuration files
- Set up run scripts

### 3. Configure OpenAI API Key

Edit the `.env` file:
```bash
nano .env
```

Update your API key:
```env
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 4. Verify Installation
```bash
# Test CLI version
./run_cli.sh

# Test API version
./run_api.sh
```

## 📖 Usage

### CLI Version

The CLI version provides an interactive interview experience directly in your terminal.

```bash
./run_cli.sh
```

**Features:**
- Voice recording and playback
- Real-time transcription
- Spoken questions and feedback
- Session logging

**Flow:**
1. AI greets you and explains the interview
2. You respond with voice
3. AI asks questions one by one
4. You answer each question with voice
5. AI provides comprehensive feedback
6. Session is saved to `mock_interview_session.txt`

### API Version

The API version provides REST endpoints for building custom applications.

```bash
./run_api.sh
```

Access the API documentation at: http://localhost:8000/docs

## 🔌 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API status |
| `GET` | `/health` | Health check |
| `POST` | `/start-interview` | Start new interview session |
| `POST` | `/submit-answer` | Submit text answer |
| `POST` | `/audio-answer/{session_id}` | Submit audio answer |
| `GET` | `/session/{session_id}` | Get session status |
| `GET` | `/sessions` | List all sessions |

### Utility Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/generate-questions` | Generate questions only |
| `POST` | `/transcribe-audio` | Audio to text |
| `POST` | `/text-to-speech` | Text to audio |
| `POST` | `/evaluate-answers` | Evaluate answers |

## 💡 Example Usage

### Complete Interview Flow (API)

#### 1. Start Interview Session
```bash
curl -X POST "http://localhost:8000/start-interview" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python Programming",
    "difficulty": "simple",
    "num_questions": 3
  }'
```

**Response:**
```json
{
  "session_id": "abc123-def456-ghi789",
  "greeting": "Hello! Welcome to your simple level mock interview for Python Programming.",
  "current_question": "What is Python and what are its main advantages?",
  "question_number": 1,
  "total_questions": 3,
  "status": "waiting_for_answer"
}
```

#### 2. Submit Answer
```bash
curl -X POST "http://localhost:8000/submit-answer" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc123-def456-ghi789",
    "answer": "Python is a high-level programming language known for its simplicity and readability."
  }'
```

**Response:**
```json
{
  "session_id": "abc123-def456-ghi789",
  "message": "Answer recorded successfully",
  "next_question": "What is the difference between a list and a tuple in Python?",
  "question_number": 2,
  "total_questions": 3,
  "status": "waiting_for_answer"
}
```

#### 3. Continue Until Complete
Repeat step 2 for each question. On the final question:

**Final Response:**
```json
{
  "session_id": "abc123-def456-ghi789",
  "message": "Interview completed!",
  "feedback": "Great job! Your answers show good understanding...",
  "total_answered": 3,
  "status": "completed"
}
```

### Audio Answer Submission
```bash
curl -X POST "http://localhost:8000/audio-answer/abc123-def456-ghi789" \
  -F "audio_file=@your_answer.wav"
```

### Using the Example Client
```bash
# Run automated example
./run_example.sh
```

## 📁 Project Structure

```
service-mock-interview/
├── app/                          # FastAPI application
│   ├── __init__.py
│   ├── main.py                   # API routes and logic
│   ├── models/                   # Pydantic models
│   │   ├── __init__.py
│   │   └── schemas.py
│   └── services/                 # Business logic
│       ├── __init__.py
│       └── interview_service.py  # Core interview service
├── main.py                       # CLI version
├── example_client.py             # API usage examples
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables
├── .gitignore                   # Git ignore rules
├── setup.sh                     # Automated setup script
├── run_api.sh                   # Start API server
├── run_cli.sh                   # Start CLI version
├── run_example.sh               # Run example client
└── README.md                    # This file
```

## 🧪 Testing the APIs

### Quick Health Check
```bash
curl http://localhost:8000/health
```

### Generate Questions Only
```bash
curl -X POST "http://localhost:8000/generate-questions" \
  -H "Content-Type: application/json" \
  -d '{"topic": "JavaScript", "difficulty": "medium", "num_questions": 2}'
```

### Text-to-Speech Test
```bash
curl -X POST "http://localhost:8000/text-to-speech" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test"}' \
  --output test_speech.mp3
```

### Run All Tests
```bash
./test_api.sh
```

## 🔧 Configuration Options

### Environment Variables (.env)
```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional API Configuration
HOST=0.0.0.0
PORT=8000
```

### CLI Configuration (main.py)
```python
# Interview Settings
difficulty = "simple"  # simple / medium / hard
topic = "Computer networks"
num_questions = 2

# Audio Settings
DURATION = 10          # Recording duration in seconds
FS = 16000            # Sample rate
LATENCY_SECONDS = 3   # Pause between question and recording
```

## 🐛 Troubleshooting

### Common Issues

#### 1. OpenAI API Key Not Found
```
❌ Error: OPENAI_API_KEY environment variable is not set.
```
**Solution:** Check your `.env` file and ensure the API key is set without quotes.

#### 2. Audio Device Issues
```
❌ Error: No audio input/output device found
```
**Solution:** 
- Check microphone/speaker connections
- Install audio drivers
- For Linux: `sudo apt install portaudio19-dev`

#### 3. Package Conflicts
```
TypeError: Client.__init__() got an unexpected keyword argument 'proxies'
```
**Solution:** Reinstall packages with correct versions:
```bash
./setup.sh
```

#### 4. Port Already in Use
```
❌ Error: Port 8000 is already in use
```
**Solution:** Kill existing process or use different port:
```bash
# Kill existing process
pkill -f uvicorn

# Or use different port
uvicorn app.main:app --port 8001
```

### Debug Mode
Run API in debug mode for detailed logging:
```bash
./run_dev.sh
```

### Logs and Session Data
- CLI sessions saved to: `mock_interview_session.txt`
- API logs: Check terminal output where server is running
- Audio files: Temporary files are auto-cleaned

## 🚀 Advanced Usage

### Custom Question Generation
```python
# In your application
import requests

response = requests.post("http://localhost:8000/generate-questions", json={
    "topic": "Machine Learning",
    "difficulty": "hard",
    "num_questions": 5
})
questions = response.json()["questions"]
```

### Audio Processing Pipeline
```python
# Record -> Transcribe -> Evaluate
audio_file = record_audio()
transcript = transcribe_audio(audio_file)
feedback = evaluate_answer(transcript)
```

### Session Management
```python
# Check session status
session_status = requests.get(f"http://localhost:8000/session/{session_id}")

# Resume interview
if session_status.json()["status"] == "active":
    # Continue with next question
    pass
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- OpenAI for GPT, Whisper, and TTS APIs
- FastAPI for the web framework
- SoundDevice for audio handling

---

**Need help?** Check the troubleshooting section or create an issue in the repository.

**Happy interviewing! 🎤✨**
