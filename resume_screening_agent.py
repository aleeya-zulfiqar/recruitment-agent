"""
Agent 1: Resume Screening Agent (OpenRouterAI)
--------------------------------------------------------
Screens a resume against a job description.
Returns a strict JSON object with match_score, decision, etc.
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
    raise ValueError("OpenRouterAI API key missing. Please set OPENROUTER_API_KEY in .env")

def screen_candidate(job_description: str, resume_text: str) -> dict:

    system_prompt = """
You are a Resume Screening Agent for hiring teams.

Your task is to evaluate a candidate resume strictly against a provided job description.

Rules:
- Do NOT infer skills that are not explicitly mentioned.
- Penalize missing core requirements.
- Use only the information provided.
- Follow the scoring rubric exactly.
- If information is missing or unclear, mark it as "uncertain".
- Return output in VALID JSON ONLY.
- Do NOT include explanations outside the JSON.

- Return a STRICT JSON object with:
    - match_score (0–100)
    - matched_skills (list)
    - missing_skills (list)
    - experience_level (Junior / Mid / Senior)
    - decision (Strong Fit / Partial Fit / Reject)
    - reasoning (short explanation)

If the resume or job description is empty, return an error object.
DO NOT include anything outside JSON.
"""

    user_prompt = f"""
JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}
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

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        raw_output = data["choices"][0]["message"]["content"]

        return json.loads(raw_output)

    except requests.exceptions.HTTPError as http_err:
        return {"error": f"HTTP error: {http_err}", "status_code": response.status_code}
    except requests.exceptions.RequestException as req_err:
        return {"error": f"Request error: {req_err}"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON returned by model", "raw_output": raw_output}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def main():
    """
    Test run Agent 1
    """

    try:
        with open("sample_data/resume.txt", "r") as f:
            resume_text = f.read()

        with open("sample_data/job_description.txt", "r") as f:
            job_description = f.read()

    except FileNotFoundError as e:
        print(f"File error: {e}")
        return

    print("\nScreening Candidate...\n")

    result = screen_candidate(job_description, resume_text)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()