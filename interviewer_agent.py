"""
Agent 2: Interviewer Agent (OpenRouterAI)
--------------------------------------------
Generates role-specific interview questions
based on candidate resume and screening signal.
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
    raise ValueError("OpenRouterAI API key missing in .env")

def generate_questions(candidate_info: dict, job: dict, screening: dict) -> dict:
    role = job.get("title", "the role")
    resume_text = candidate_info.get("resume_text", "")
    screening_decision = screening.get("decision", "")
    match_score = screening.get("match_score", "unknown")

    system_prompt = f"""
You are a structured interviewer for the role: {role}.

Rules:
- Ask a maximum of 5 role-specific questions.
- Focus on skills, experience, and problem-solving.
- Adjust difficulty using screening signals.
- Do NOT add explanations.
- Return ONLY a valid JSON array of strings.
"""

    user_prompt = f"""
Candidate Resume:
{resume_text}

Screening Summary:
Decision: {screening_decision}
Match Score: {match_score}

Generate interview questions now.
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

    questions = json.loads(raw_output)

    if not isinstance(questions, list):
        raise ValueError("LLM did not return a list of questions")

    return {
        "candidate": candidate_info,
        "job": job,
        "screening": screening,
        "questions": questions
    }


def main():
    """
    Test run Agent 2
    """

    try:
        with open("sample_data/resume.txt", "r") as f:
            resume_text = f.read()

        with open("sample_data/job_description.txt", "r") as f:
            job_description = f.read()

    except FileNotFoundError as e:
        print(f"File error: {e}")
        return

    # Mock inputs
    candidate_info = {
        "name": "Test Candidate",
        "email": "test@example.com",
        "resume_text": resume_text
    }

    job = {
        "title": "Frontend Developer",
        "description": job_description
    }

    screening = {
        "match_score": 95,
        "matched_skills": ["React", "JavaScript", "REST APIs"],
        "missing_skills": [],
        "experience_level": "Senior",
        "decision": "Strong Fit",
        "reasoning": "Candidate matches role well"
    }

    print("\nGenerating Interview Questions...\n")

    result = generate_questions(
        candidate_info=candidate_info,
        job=job,
        screening=screening
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()