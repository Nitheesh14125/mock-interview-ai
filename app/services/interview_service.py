import os
from openai import OpenAI
import tempfile
import io
from typing import List

class InterviewService:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client_chat = OpenAI(api_key=self.openai_key)
        self.client_whisper = OpenAI(api_key=self.openai_key)
        self.client_tts = OpenAI(api_key=self.openai_key)

    def chat_completion(self, messages, model="gpt-4o-mini"):
        response = self.client_chat.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content.strip()

    def generate_questions(self, topic: str, difficulty: str, num_questions: int = 10) -> List[str]:
        prompt = [
            {"role": "system", "content": "You are an expert interviewer."},
            {"role": "user", "content": (
                f"Generate {num_questions} {difficulty} level interview questions "
                f"for the topic '{topic}'. Number them 1 to {num_questions}."
            )}
        ]
        questions_text = self.chat_completion(prompt)
        questions = []
        for line in questions_text.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                question = line.lstrip('0123456789.- )')
                questions.append(question.strip())
        if not questions:
            questions = [questions_text]
        return questions[:num_questions]

    def whisper_transcribe(self, file_path: str) -> str:
        with open(file_path, "rb") as f:
            transcript = self.client_whisper.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        return transcript.text.strip()

    def generate_speech(self, text: str) -> io.BytesIO:
        response = self.client_tts.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        
        audio_data = io.BytesIO(response.content)
        audio_data.seek(0)
        return audio_data

    def evaluate_answers(self, student_answers: List[dict]) -> str:
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
        return self.chat_completion(eval_prompt)
