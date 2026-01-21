"""
Agent 3: Interview Answers Evaluation Agent (OpenRouterAI)
-------------------------------------------
Evaluates candidate answers against interview questions
and returns structured scoring and hiring decision.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = os.getenv("OPENROUTER_API_URL")
MODEL = os.getenv("OPENROUTER_MODEL", "gpt-4o-mini")

if not OPENROUTER_API_KEY or not API_URL:
    raise ValueError("OpenRouter API config missing in .env")

def evaluate_answers(
    candidate: dict,
    job: dict,
    screening: dict,
    questions: list,
    answers: list
) -> dict:

    qa_pairs = []
    for idx, (q, a) in enumerate(zip(questions, answers), start=1):
        if a:
            qa_pairs.append({
                "question_number": idx,
                "question": q,
                "answer": a
            })

    system_prompt = """
You are a strict technical interviewer and evaluator.

Rules:
- Score EACH answer from 0–10.
- Provide short feedback per answer.
- Calculate overall_score (0–100).
- Decide one: Strong Fit / Partial Fit / Reject.
- Return ONLY valid JSON with keys:
  scores, overall_score, decision, evaluation_summary
"""

    user_prompt = f"""
Job Role:
Title: {job['title']}
Description: {job['description']}

Screening Summary:
Decision: {screening.get('decision')}
Match Score: {screening.get('match_score')}
Experience Level: {screening.get('experience_level')}

Interview Q&A:
{json.dumps(qa_pairs, indent=2)}

Evaluate now.
"""

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()

    raw_output = response.json()["choices"][0]["message"]["content"].strip()

    if raw_output.startswith("```"):
        raw_output = raw_output.replace("```json", "").replace("```", "").strip()

    return json.loads(raw_output)


def main():
    """
    Test run Agent 3
    """

    try:
        with open("sample_data/job_description.txt", "r") as f:
            job_description = f.read()

    except FileNotFoundError as e:
        print(f"File error: {e}")
        return

    # Mock inputs
    candidate = {
        "name": "Mock Candidate",
        "email": "candidate@mock.com"
    }

    job = {
        "title": "Frontend Developer",
        "description": job_description
    }

    screening = {
        "match_score": 88,
        "experience_level": "Senior",
        "decision": "Strong Fit"
    }

    questions = [
        "Explain your UI design process.",
        "How do you conduct usability testing?",
        "Describe a challenging UX problem you solved.",
        "How do you ensure accessibility?",
        "Which metrics define good UX?"
    ]

    answers = [
        "I start with user research and personas.",
        "I use moderated and unmoderated testing.",
        "A complex dashboard redesign.",
        "By following WCAG standards.",
        "Task success rate and user satisfaction."
    ]

    print("\nEvaluating Candidate Answers...\n")

    result = evaluate_answers(
        candidate=candidate,
        job=job,
        screening=screening,
        questions=questions,
        answers=answers
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()