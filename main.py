import os
from dotenv import load_dotenv
from openai import OpenAI
import sounddevice as sd
import numpy as np
import soundfile as sf
import tempfile
import time

# Load environment variables from .env file
load_dotenv()

# ===============================
# CONFIGURATION – SINGLE KEY FROM ENVIRONMENT VARIABLE
# ===============================

OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# Check if API key is available
if not OPENAI_KEY:
    print("❌ Error: OPENAI_API_KEY environment variable is not set.")
    print("Please set it in your .env file or export it in your shell.")
    print("Example: export OPENAI_API_KEY='your-api-key-here'")
    print("\n💡 Make sure your .env file is in the same directory as this script.")
    exit(1)

print("✅ OpenAI API key loaded successfully")

client_chat = OpenAI(api_key=OPENAI_KEY)
client_whisper = OpenAI(api_key=OPENAI_KEY)
client_tts = OpenAI(api_key=OPENAI_KEY)

DURATION = 10
FS = 16000
LATENCY_SECONDS = 3

# ===============================
# AUDIO HELPERS
# ===============================
def record_audio(duration=DURATION, fs=FS):
    print(f"\n🎤 Recording for {duration} seconds... Speak now!")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    return np.squeeze(audio)

def save_temp_wav(audio_data, fs):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    sf.write(temp_file.name, audio_data, fs, subtype='PCM_16')
    return temp_file.name

def whisper_transcribe(file_path):
    with open(file_path, "rb") as f:
        transcript = client_whisper.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
    return transcript.text.strip()

# ===============================
# TTS HELPER
# ===============================
def speak_text_tts(text):
    temp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_out_path = temp_out.name
    temp_out.close()

    with client_tts.audio.speech.with_streaming_response.create(
        model="tts-1",  # Updated model name
        voice="alloy",
        input=text
    ) as response:
        response.stream_to_file(temp_out_path)

    data, samplerate = sf.read(temp_out_path, dtype="float32")
    sd.play(data, samplerate)
    sd.wait()
    os.remove(temp_out_path)

# ===============================
# CHAT HELPERS
# ===============================
def chat_completion(messages, model="gpt-4o-mini"):
    response = client_chat.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content.strip()

def generate_questions(topic, difficulty, num_questions=10):
    prompt = [
        {"role": "system", "content": "You are an expert interviewer."},
        {"role": "user", "content": (
            f"Generate {num_questions} {difficulty} level interview questions "
            f"for the topic '{topic}'. Number them 1 to {num_questions}."
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
    return questions[:num_questions]

# ===============================
# MAIN INTERVIEW FLOW
# ===============================
if __name__ == "__main__":
    print("🚀 Starting Mock Interview CLI Application")
    print("=" * 50)
    
    difficulty = "simple"  # simple / medium / hard
    topic = "Computer networks"
    num_questions = 2

    full_session_log = ""
    student_answers = []
    questions = generate_questions(topic, difficulty, num_questions)

    # Step 1: Greeting
    greeting = f"Hello! Welcome to your {difficulty} level mock interview for {topic}. Let's begin."
    print("AI:", greeting)
    speak_text_tts(greeting)
    full_session_log += f"AI Greeting: {greeting}\n"

    # Step 2: Student greeting
    print("\nPlease greet back:")
    audio = record_audio()
    wav_path = save_temp_wav(audio, FS)
    student_greeting = whisper_transcribe(wav_path)
    os.remove(wav_path)
    print("Student:", student_greeting)
    full_session_log += f"Student Greeting: {student_greeting}\n"

    # Step 3: Acknowledge
    ack_msg = f"Great! I will now ask you {num_questions} questions, one by one."
    print("AI:", ack_msg)
    speak_text_tts(ack_msg)
    full_session_log += f"AI Acknowledgement: {ack_msg}\n"

    # Step 4: Interview Rounds
    for i, question in enumerate(questions, 1):
        print(f"\n--- Round {i} ---")
        print(f"Question {i}: {question}")
        speak_text_tts(f"Question {i}. {question}")
        time.sleep(LATENCY_SECONDS)

        audio = record_audio()
        wav_path = save_temp_wav(audio, FS)
        student_answer = whisper_transcribe(wav_path)
        os.remove(wav_path)

        # Handle empty or very short answer
        if not student_answer or len(student_answer.strip()) < 3:
            student_answer = "No answer provided."

        print("Student:", student_answer)
        student_answers.append({"question": question, "answer": student_answer})
        full_session_log += f"Q{i}: {question}\nA: {student_answer}\n"

    # Step 5: Final Evaluation with detailed feedback for missing/wrong answers
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
        {"role": "user", "content": str(student_answers)}
    ]
    final_feedback = chat_completion(eval_prompt)

    # Step 6: Summary
    summary_text = f"Interview completed. Here is your feedback: {final_feedback}"
    print("\nFinal Summary:", summary_text)
    speak_text_tts(summary_text)
    full_session_log += f"\nSummary: {summary_text}\n"

    # Step 7: Save log
    with open("mock_interview_session.txt", "w", encoding="utf-8") as f:
        f.write(full_session_log)

    print("\nSession log saved to 'mock_interview_session.txt'")