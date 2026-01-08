"""
Agent 1: Resume Screening Agent (OpenRouter API)
-----------------------------------------------------
Screens a resume against a job description and returns
a structured hiring decision in JSON.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key missing. Please set OPENAI_API_KEY in .env")

MODEL = "gpt-4o-mini"

API_URL = "https://openrouter.ai/api/v1/chat/completions"


def screen_candidate(job_description: str, resume_text: str) -> dict:
    """
    Screen a resume against a job description using OpenRouter API.
    Returns a strict JSON object with match_score, decision, etc.
    """

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
        "Authorization": f"Bearer {OPENAI_API_KEY}",
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
    """Run Resume Screening Agent"""

    jd_file_path = 'sample_data/job_description.txt'

    try:
        with open(jd_file_path, 'r') as jd:
            job_description = jd.read()
    except FileNotFoundError:
        print(f"Error: The file '{jd_file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    res_file_path = 'sample_data/resume.txt'

    try:
        with open(res_file_path, 'r') as res:
            resume_text = res.read()
    except FileNotFoundError:
        print(f"Error: The file '{res_file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    print("\nScreening Candidate...\n")

    result = screen_candidate(job_description, resume_text)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()