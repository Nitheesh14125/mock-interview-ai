from pydantic import BaseModel
from typing import List, Optional

class InterviewRequest(BaseModel):
    topic: str
    difficulty: str = "simple"
    num_questions: int = 2

class QuestionResponse(BaseModel):
    questions: List[str]

class InterviewResponse(BaseModel):
    message: str
    questions: Optional[List[str]] = None
    feedback: Optional[str] = None

class AnswerEvaluation(BaseModel):
    question: str
    answer: str
    
class EvaluationRequest(BaseModel):
    answers: List[AnswerEvaluation]
