"""
Agent 3: Evaluation Agent (OpenRouter API)
-----------------------------------------------------
Scores candidate answers from Interviewer Agent (Agent 2)
and outputs a structured JSON scorecard with reasoning.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key missing in .env")

MODEL = "gpt-4o-mini"
API_URL = "https://openrouter.ai/api/v1/chat/completions"


def evaluate_candidate(candidate_info: str, questions_asked: list) -> dict:
    """
    Evaluate the candidate's answers and return a structured scorecard.
    """

    system_prompt = f"""
You are a strict technical evaluator.
Your task:
- Score each candidate answer 0–10.
- Provide reasoning/feedback for each answer.
- Calculate overall_score (0-100) based on individual scores.
- Give a final decision: Strong Fit / Partial Fit / Reject.
- Return output ONLY as JSON with keys:
  scores, overall_score, decision, evaluation_summary
"""

    user_prompt = f"""
Candidate info:
{candidate_info}

Questions and answers:
{json.dumps(questions_asked, indent=2)}

Task:
Evaluate the candidate strictly according to the rubric.
Return JSON only.
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
    except Exception as e:
        return {"error": f"Failed to evaluate candidate: {str(e)}", "raw_output": raw_output if 'raw_output' in locals() else ""}


def main():
    """Run Evaluation Agent"""

    candidate_info = """
Frontend Developer Intern with experience in React, JavaScript,
API integration, and UI development. Worked on production MVPs
using React and Tailwind CSS.
"""

    # Sample questions_asked from Agent 2
    questions_asked = [
        {"question": "Explain closures in JavaScript", "candidate_answer": "A closure is a function that remembers and has access to variables and the scope in which it was created, even after the outer function has finished executing."},
        {"question": "Describe React state management", "candidate_answer": "I use useState and useReducer to beautify web pages."}
    ]

    print("\nEvaluating candidate...\n")

    result = evaluate_candidate(candidate_info, questions_asked)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()