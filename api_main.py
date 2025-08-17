import os
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
from openai import OpenAI

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
client_chat = OpenAI(api_key=OPENAI_KEY)
client_whisper = OpenAI(api_key=OPENAI_KEY)
client_tts = OpenAI(api_key=OPENAI_KEY)

app = FastAPI()

class InterviewRequest(BaseModel):
    topic: str
    difficulty: str = "simple"
    num_questions: int = 2

class AnswerRequest(BaseModel):
    question: str
    answer: str

class EvaluationRequest(BaseModel):
    qa_pairs: List[AnswerRequest]

@app.get("/")
def root():
    return {"message": "Mock Interview API is running!"}

@app.post("/generate_questions")
def generate_questions_api(req: InterviewRequest):
    prompt = [
        {"role": "system", "content": "You are an expert interviewer."},
        {"role": "user", "content": (
            f"Generate {req.num_questions} {req.difficulty} level interview questions "
            f"for the topic '{req.topic}'. Number them 1 to {req.num_questions}."
        )}
    ]
    questions_text = chat_completion(prompt)
    questions = []
    for line in questions_text.split('\n'):
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith('-')):
            question = line.lstrip('0123456789.- )')
            questions.append(question.strip())
    if not questions:
        questions = [questions_text]
    return {"questions": questions[:req.num_questions]}

@app.post("/transcribe_audio")
async def transcribe_audio(file: UploadFile = File(...)):
    with open("temp.wav", "wb") as buffer:
        buffer.write(await file.read())
    with open("temp.wav", "rb") as f:
        transcript = client_whisper.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
    os.remove("temp.wav")
    return {"transcript": transcript.text.strip()}

@app.post("/tts")
def tts(text: str = Form(...)):
    import tempfile
    import soundfile as sf
    temp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_out_path = temp_out.name
    temp_out.close()
    with client_tts.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    ) as response:
        response.stream_to_file(temp_out_path)
    with open(temp_out_path, "rb") as f:
        audio_bytes = f.read()
    os.remove(temp_out_path)
    return {"audio": audio_bytes.hex()}

@app.post("/evaluate")
def evaluate(req: EvaluationRequest):
    eval_prompt = [
        {"role": "system", "content": (
            "You are a friendly and constructive interviewer. "
            "For each question and answer pair, do the following:\n"
            "- If the student gave no answer or 'No answer provided', politely say "
            "'The question was not answered. Here is the correct answer:' and provide a medium-length correct answer.\n"
            "- If the student's answer is incorrect or incomplete, politely say "
            "'Your answer needs improvement. The correct answer is:' followed by the correct answer.\n"
            "- If the answer is correct or good, give positive feedback.\n"
            "Make the overall summary kind, helpful, and encouraging."
        )},
        {"role": "user", "content": str([qa.dict() for qa in req.qa_pairs])}
    ]
    feedback = chat_completion(eval_prompt)
    return {"feedback": feedback}

def chat_completion(messages, model="gpt-4o-mini"):
    response = client_chat.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content.strip()