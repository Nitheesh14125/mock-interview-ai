from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import List, Optional, Dict
import tempfile
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .services.interview_service import InterviewService

app = FastAPI(
    title="Mock Interview Service API",
    description="AI-powered mock interview service with speech recognition and text-to-speech",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize service with better error handling
interview_service = None
try:
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Warning: OPENAI_API_KEY environment variable is not set.")
        print("Please check your .env file or set the environment variable.")
    else:
        print("✅ OpenAI API key found, initializing service...")
        interview_service = InterviewService()
        print("✅ Interview service initialized successfully")
        
except ValueError as e:
    print(f"❌ Error initializing service: {e}")
    interview_service = None
except Exception as e:
    print(f"❌ Unexpected error during service initialization: {e}")
    interview_service = None

# In-memory session storage (use Redis/Database in production)
interview_sessions: Dict[str, dict] = {}

class InterviewSession(BaseModel):
    topic: str
    difficulty: str = "simple"
    num_questions: int = 2

class TextToSpeechRequest(BaseModel):
    text: str

class AnswerSubmission(BaseModel):
    session_id: str
    answer: str

class NextQuestionRequest(BaseModel):
    session_id: str

@app.get("/")
async def root():
    return {
        "message": "🎤 Mock Interview Service API is running",
        "status": "active",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    api_key_configured = bool(os.getenv("OPENAI_API_KEY"))
    service_ready = interview_service is not None
    
    return {
        "status": "healthy" if service_ready else "degraded",
        "service": "Mock Interview API",
        "openai_configured": api_key_configured,
        "service_ready": service_ready,
        "message": "Service ready" if service_ready else "OpenAI API key not configured or service initialization failed"
    }

@app.post("/generate-questions")
async def generate_questions(request: InterviewSession):
    if not interview_service:
        raise HTTPException(status_code=503, detail="Service not available. Check OPENAI_API_KEY configuration.")
    
    try:
        questions = interview_service.generate_questions(
            request.topic, 
            request.difficulty, 
            request.num_questions
        )
        return {
            "topic": request.topic,
            "difficulty": request.difficulty,
            "questions": questions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating questions: {str(e)}")

@app.post("/transcribe-audio")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    if not interview_service:
        raise HTTPException(status_code=503, detail="Service not available. Check OPENAI_API_KEY configuration.")
    
    try:
        # Validate file type
        if not audio_file.filename.lower().endswith(('.wav', '.mp3', '.m4a', '.flac')):
            raise HTTPException(status_code=400, detail="Unsupported audio format")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Transcribe
        transcript = interview_service.whisper_transcribe(temp_path)
        os.remove(temp_path)
        
        return {
            "transcript": transcript,
            "filename": audio_file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error transcribing audio: {str(e)}")

@app.post("/text-to-speech")
async def text_to_speech(request: TextToSpeechRequest):
    if not interview_service:
        raise HTTPException(status_code=503, detail="Service not available. Check OPENAI_API_KEY configuration.")
    
    try:
        audio_data = interview_service.generate_speech(request.text)
        return StreamingResponse(
            audio_data,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating speech: {str(e)}")

@app.post("/evaluate-answers")
async def evaluate_answers(answers: List[dict]):
    if not interview_service:
        raise HTTPException(status_code=503, detail="Service not available. Check OPENAI_API_KEY configuration.")
    
    try:
        feedback = interview_service.evaluate_answers(answers)
        return {
            "feedback": feedback,
            "evaluated_answers": len(answers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating answers: {str(e)}")

@app.post("/start-interview")
async def start_interview(request: InterviewSession):
    """Start a new interview session and get the first question"""
    if not interview_service:
        raise HTTPException(status_code=503, detail="Service not available. Check OPENAI_API_KEY configuration.")
    
    try:
        # Generate session ID and questions
        session_id = str(uuid.uuid4())
        questions = interview_service.generate_questions(
            request.topic, 
            request.difficulty, 
            request.num_questions
        )
        
        # Create session
        session_data = {
            "session_id": session_id,
            "topic": request.topic,
            "difficulty": request.difficulty,
            "questions": questions,
            "current_question": 0,
            "answers": [],
            "started_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        interview_sessions[session_id] = session_data
        
        # Greeting and first question
        greeting = f"Hello! Welcome to your {request.difficulty} level mock interview for {request.topic}."
        first_question = questions[0] if questions else "No questions generated"
        
        return {
            "session_id": session_id,
            "greeting": greeting,
            "current_question": first_question,
            "question_number": 1,
            "total_questions": len(questions),
            "status": "waiting_for_answer"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting interview: {str(e)}")

@app.post("/submit-answer")
async def submit_answer(submission: AnswerSubmission):
    """Submit an answer and get the next question"""
    if submission.session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = interview_sessions[submission.session_id]
    
    if session["status"] != "active":
        raise HTTPException(status_code=400, detail="Session is not active")
    
    try:
        # Store the answer
        current_q_index = session["current_question"]
        current_question = session["questions"][current_q_index]
        
        session["answers"].append({
            "question": current_question,
            "answer": submission.answer,
            "question_number": current_q_index + 1
        })
        
        # Move to next question
        session["current_question"] += 1
        
        # Check if interview is complete
        if session["current_question"] >= len(session["questions"]):
            session["status"] = "completed"
            
            # Generate feedback
            feedback = interview_service.evaluate_answers(session["answers"])
            
            return {
                "session_id": submission.session_id,
                "message": "Interview completed!",
                "feedback": feedback,
                "total_answered": len(session["answers"]),
                "status": "completed"
            }
        
        # Get next question
        next_question = session["questions"][session["current_question"]]
        
        return {
            "session_id": submission.session_id,
            "message": "Answer recorded successfully",
            "next_question": next_question,
            "question_number": session["current_question"] + 1,
            "total_questions": len(session["questions"]),
            "status": "waiting_for_answer"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing answer: {str(e)}")

@app.get("/session/{session_id}")
async def get_session_status(session_id: str):
    """Get current session status"""
    if session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = interview_sessions[session_id]
    
    response = {
        "session_id": session_id,
        "topic": session["topic"],
        "difficulty": session["difficulty"],
        "status": session["status"],
        "current_question_number": session["current_question"] + 1,
        "total_questions": len(session["questions"]),
        "answers_submitted": len(session["answers"])
    }
    
    if session["status"] == "active":
        if session["current_question"] < len(session["questions"]):
            response["current_question"] = session["questions"][session["current_question"]]
    
    return response

@app.post("/audio-answer/{session_id}")
async def submit_audio_answer(session_id: str, audio_file: UploadFile = File(...)):
    """Submit an audio answer (transcribe + submit)"""
    if not interview_service:
        raise HTTPException(status_code=503, detail="Service not available.")
    
    if session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Transcribe audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        transcript = interview_service.whisper_transcribe(temp_path)
        os.remove(temp_path)
        
        # Submit the transcribed answer
        submission = AnswerSubmission(session_id=session_id, answer=transcript)
        result = await submit_answer(submission)
        
        result["transcript"] = transcript
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

@app.get("/sessions")
async def list_sessions():
    """List all active sessions"""
    return {
        "active_sessions": len([s for s in interview_sessions.values() if s["status"] == "active"]),
        "completed_sessions": len([s for s in interview_sessions.values() if s["status"] == "completed"]),
        "total_sessions": len(interview_sessions)
    }
