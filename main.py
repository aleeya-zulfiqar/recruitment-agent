from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any, Union
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from resume_screening_agent import screen_candidate
from interviewer_agent import generate_questions
from evaluation_agent import evaluate_answers

load_dotenv()

app = FastAPI(title="Recruitment AI Backend")

# CORS for browser, cloudflare & n8n
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://localhost",
        "https://guarantee-yesterday-matt-may.trycloudflare.com",
    ], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ScreeningRequest(BaseModel):
    candidate_name: str
    candidate_email: str
    resume_text: str
    job_title: str
    job_description: str

class QuestionRequest(BaseModel):
    candidate_info: Dict[str, Any]
    job: Dict[str, Any]
    screening: Dict[str, Any]

class EvaluationRequest(BaseModel):
    candidate_info: Union[List[Dict[str, Any]], Dict[str, Any]]
    job_info: Union[List[Dict[str, Any]], Dict[str, Any]]
    screening_info: Union[List[Dict[str, Any]], Dict[str, Any]]
    questions: List[str]

    answer1: str | None = None
    answer2: str | None = None
    answer3: str | None = None
    answer4: str | None = None
    answer5: str | None = None

    submission_time: str | None = None


# Agent 1 - Resume Screening
@app.post("/screen")
def screen_candidate_endpoint(payload: ScreeningRequest):
    screening_result = screen_candidate(
        payload.job_description,
        payload.resume_text
    )
    return {
        "candidate": {
            "name": payload.candidate_name,
            "email": payload.candidate_email,
            "resume_text": payload.resume_text
        },
        "job": {
            "title": payload.job_title,
            "description": payload.job_description
        },
        "screening": screening_result
    }
    

# Agent 2 - Questions Generation
@app.post("/generate_questions")
def generate_questions_endpoint(payload: QuestionRequest):
    return generate_questions(
        candidate_info=payload.candidate_info,
        job=payload.job,
        screening=payload.screening
    )
    

# Agent 3 - Answers Evaluation
@app.post("/evaluate")
def evaluate_answers_endpoint(payload: EvaluationRequest):

    def unwrap(value):
        return value[0] if isinstance(value, list) else value

    candidate = unwrap(payload.candidate_info)
    job = unwrap(payload.job_info)
    screening = unwrap(payload.screening_info)

    answers = [
        payload.answer1,
        payload.answer2,
        payload.answer3,
        payload.answer4,
        payload.answer5,
    ]

    return evaluate_answers(
        candidate=candidate,
        job=job,
        screening=screening,
        questions=payload.questions,
        answers=answers
    )