# 🔌 Mock Interview API - Complete Usage Guide

## 🚀 Quick Start

1. **Start the API server:**
   ```bash
   ./run_api.sh
   ```

2. **Access interactive docs:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 📊 Interview Flow Diagram

```
Start Interview → Submit Answer → Next Question → ... → Complete + Feedback
     ↓               ↓              ↓                      ↓
  Session ID     Question 2     Question N          Final Evaluation
  Question 1     Status         Status              Session Complete
```

## 🔄 Step-by-Step Interview Process

### Step 1: Initialize Interview
**Endpoint:** `POST /start-interview`

**Request:**
```json
{
  "topic": "Data Structures",
  "difficulty": "medium",
  "num_questions": 5
}
```

**Response:**
```json
{
  "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "greeting": "Hello! Welcome to your medium level mock interview for Data Structures.",
  "current_question": "What is a binary tree and how does it differ from a binary search tree?",
  "question_number": 1,
  "total_questions": 5,
  "status": "waiting_for_answer"
}
```

### Step 2: Submit Answer (Text)
**Endpoint:** `POST /submit-answer`

**Request:**
```json
{
  "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "answer": "A binary tree is a hierarchical data structure where each node has at most two children. A binary search tree is a special binary tree where left child values are smaller and right child values are larger than the parent node."
}
```

**Response (Next Question):**
```json
{
  "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "message": "Answer recorded successfully",
  "next_question": "Explain the time complexity of searching in a balanced binary search tree.",
  "question_number": 2,
  "total_questions": 5,
  "status": "waiting_for_answer"
}
```

**Response (Interview Complete):**
```json
{
  "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "message": "Interview completed!",
  "feedback": "Excellent performance! Your understanding of data structures is solid. You correctly explained binary trees and BSTs. For improvement, consider mentioning specific algorithms like AVL or Red-Black trees for balanced BSTs.",
  "total_answered": 5,
  "status": "completed"
}
```

### Step 3: Submit Answer (Audio)
**Endpoint:** `POST /audio-answer/{session_id}`

**Request:** Multipart form with audio file

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/audio-answer/f47ac10b-58cc-4372-a567-0e02b2c3d479" \
  -F "audio_file=@answer.wav"
```

**Response:**
```json
{
  "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "transcript": "Arrays are linear data structures that store elements in contiguous memory locations",
  "message": "Answer recorded successfully",
  "next_question": "What are the advantages and disadvantages of linked lists?",
  "question_number": 3,
  "total_questions": 5,
  "status": "waiting_for_answer"
}
```

## 📝 All API Endpoints

### Core Interview Endpoints

#### 1. Health Check
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "service": "Mock Interview API",
  "openai_configured": true
}
```

#### 2. Start Interview Session
```http
POST /start-interview
Content-Type: application/json

{
  "topic": "string",
  "difficulty": "simple|medium|hard",
  "num_questions": 1-10
}
```

#### 3. Submit Text Answer
```http
POST /submit-answer
Content-Type: application/json

{
  "session_id": "uuid",
  "answer": "string"
}
```

#### 4. Submit Audio Answer
```http
POST /audio-answer/{session_id}
Content-Type: multipart/form-data

audio_file: file (wav, mp3, m4a, flac)
```

#### 5. Get Session Status
```http
GET /session/{session_id}
```
**Response:**
```json
{
  "session_id": "uuid",
  "topic": "string",
  "difficulty": "string",
  "status": "active|completed",
  "current_question_number": 2,
  "total_questions": 5,
  "answers_submitted": 1,
  "current_question": "What is...?" // only if active
}
```

#### 6. List All Sessions
```http
GET /sessions
```
**Response:**
```json
{
  "active_sessions": 3,
  "completed_sessions": 12,
  "total_sessions": 15
}
```

### Utility Endpoints

#### 7. Generate Questions Only
```http
POST /generate-questions
Content-Type: application/json

{
  "topic": "Python Programming",
  "difficulty": "simple",
  "num_questions": 3
}
```

#### 8. Transcribe Audio
```http
POST /transcribe-audio
Content-Type: multipart/form-data

audio_file: file
```

#### 9. Text-to-Speech
```http
POST /text-to-speech
Content-Type: application/json

{
  "text": "Hello, this will be converted to speech"
}
```

#### 10. Evaluate Answers
```http
POST /evaluate-answers
Content-Type: application/json

[
  {
    "question": "What is Python?",
    "answer": "Python is a programming language"
  }
]
```

## 🎯 Example Scenarios

### Scenario 1: Technical Interview Preparation

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Start technical interview
response = requests.post(f"{BASE_URL}/start-interview", json={
    "topic": "System Design",
    "difficulty": "hard",
    "num_questions": 3
})

session_data = response.json()
session_id = session_data["session_id"]
print(f"First question: {session_data['current_question']}")

# Answer questions
answers = [
    "Load balancing distributes incoming requests across multiple servers to ensure no single server is overwhelmed.",
    "Microservices architecture breaks down applications into small, independent services that communicate via APIs.",
    "Caching improves performance by storing frequently accessed data in fast storage layers like Redis or Memcached."
]

for answer in answers:
    response = requests.post(f"{BASE_URL}/submit-answer", json={
        "session_id": session_id,
        "answer": answer
    })
    
    result = response.json()
    if result["status"] == "completed":
        print(f"Interview complete! Feedback: {result['feedback']}")
        break
    else:
        print(f"Next question: {result['next_question']}")
```

### Scenario 2: Audio-Based Interview

```python
import requests
import sounddevice as sd
import soundfile as sf
import tempfile

def record_and_submit_answer(session_id, duration=10):
    # Record audio
    print("Recording... Speak now!")
    audio = sd.rec(int(duration * 16000), samplerate=16000, channels=1)
    sd.wait()
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        sf.write(f.name, audio, 16000)
        
        # Submit to API
        with open(f.name, "rb") as audio_file:
            response = requests.post(
                f"http://localhost:8000/audio-answer/{session_id}",
                files={"audio_file": audio_file}
            )
    
    return response.json()

# Start interview and handle with audio
response = requests.post("http://localhost:8000/start-interview", json={
    "topic": "JavaScript",
    "difficulty": "medium",
    "num_questions": 2
})

session_id = response.json()["session_id"]

while True:
    result = record_and_submit_answer(session_id)
    
    if result["status"] == "completed":
        print(f"Interview complete! Feedback: {result['feedback']}")
        break
    else:
        print(f"Next question: {result['next_question']}")
```

### Scenario 3: Custom Question Bank

```python
# Generate custom questions
response = requests.post("http://localhost:8000/generate-questions", json={
    "topic": "Machine Learning",
    "difficulty": "hard",
    "num_questions": 10
})

questions = response.json()["questions"]

# Use in your own application
for i, question in enumerate(questions, 1):
    print(f"Q{i}: {question}")
    # Your custom logic here
```

## 🔧 Error Handling

### Common Error Responses

#### Session Not Found (404)
```json
{
  "detail": "Session not found"
}
```

#### Service Unavailable (503)
```json
{
  "detail": "Service not available. Check OPENAI_API_KEY configuration."
}
```

#### Invalid Audio Format (400)
```json
{
  "detail": "Unsupported audio format"
}
```

#### Session Inactive (400)
```json
{
  "detail": "Session is not active"
}
```

### Error Handling in Code

```python
import requests

try:
    response = requests.post("http://localhost:8000/submit-answer", json={
        "session_id": "invalid-id",
        "answer": "Test answer"
    })
    response.raise_for_status()
    
except requests.exceptions.HTTPError as e:
    if response.status_code == 404:
        print("Session not found. Start a new interview.")
    elif response.status_code == 503:
        print("Service unavailable. Check OpenAI API key.")
    else:
        print(f"HTTP Error: {e}")
        
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

## 🎨 Frontend Integration Examples

### JavaScript/React
```javascript
// Start interview
const startInterview = async (topic, difficulty, numQuestions) => {
  const response = await fetch('http://localhost:8000/start-interview', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, difficulty, num_questions: numQuestions })
  });
  return response.json();
};

// Submit answer
const submitAnswer = async (sessionId, answer) => {
  const response = await fetch('http://localhost:8000/submit-answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, answer })
  });
  return response.json();
};

// Usage
const session = await startInterview('React.js', 'medium', 3);
console.log(session.current_question);

const result = await submitAnswer(session.session_id, 'React is a JavaScript library...');
console.log(result.next_question);
```

### Python/Streamlit
```python
import streamlit as st
import requests

st.title("Mock Interview")

if "session_id" not in st.session_state:
    topic = st.text_input("Interview Topic")
    difficulty = st.selectbox("Difficulty", ["simple", "medium", "hard"])
    
    if st.button("Start Interview"):
        response = requests.post("http://localhost:8000/start-interview", json={
            "topic": topic,
            "difficulty": difficulty,
            "num_questions": 3
        })
        
        session = response.json()
        st.session_state.session_id = session["session_id"]
        st.session_state.current_question = session["current_question"]

if "session_id" in st.session_state:
    st.write(f"Question: {st.session_state.current_question}")
    
    answer = st.text_area("Your Answer")
    
    if st.button("Submit Answer"):
        response = requests.post("http://localhost:8000/submit-answer", json={
            "session_id": st.session_state.session_id,
            "answer": answer
        })
        
        result = response.json()
        
        if result["status"] == "completed":
            st.success("Interview Complete!")
            st.write(f"Feedback: {result['feedback']}")
        else:
            st.session_state.current_question = result["next_question"]
            st.rerun()
```

## 🔍 Monitoring and Analytics

### Session Analytics
```python
# Get session statistics
response = requests.get("http://localhost:8000/sessions")
stats = response.json()

print(f"Active sessions: {stats['active_sessions']}")
print(f"Completed sessions: {stats['completed_sessions']}")
print(f"Total sessions: {stats['total_sessions']}")
```

### Performance Monitoring
- Monitor response times for each endpoint
- Track session completion rates
- Analyze common topics and difficulty levels
- Monitor OpenAI API usage and costs

## 🚀 Production Considerations

### Security
- Add authentication/authorization
- Implement rate limiting
- Validate file uploads
- Sanitize user inputs

### Scalability
- Use Redis for session storage
- Implement database for persistence
- Add load balancing
- Consider async processing for long-running tasks

### Monitoring
- Add logging and metrics
- Health checks for dependencies
- Error tracking and alerting
- Performance monitoring

---

**Ready to build amazing interview applications! 🎤🚀**
