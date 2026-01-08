"""
Agent 4: Action Agent
------------------------------------------------
Decides next action based on screening + interview evaluation.
"""

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key missing in .env")

MODEL = "openai/gpt-4o-mini"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def decide_next_action(screening_result: dict, evaluation_result: dict) -> dict:
    system_prompt = """
You are a senior hiring decision agent.

Your task:
- Analyze resume screening results
- Analyze interview evaluation results
- Decide the NEXT ACTION

Allowed decisions:
- PROCEED
- OFFER
- HOLD
- REJECT
- ESCALATE

Rules:
- Base decision strictly on provided data
- Be conservative with OFFER
- Use ESCALATE if signals conflict
- Return STRICT JSON only

JSON format:
{
  "decision": "...",
  "confidence": "high | medium | low",
  "reasoning": "...",
  "recommended_action": "..."
}
"""

    user_prompt = f"""
RESUME SCREENING RESULT:
{json.dumps(screening_result, indent=2)}

INTERVIEW EVALUATION RESULT:
{json.dumps(evaluation_result, indent=2)}
"""

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2
    }

    response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
    response.raise_for_status()

    raw_output = response.json()["choices"][0]["message"]["content"]

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        return {
            "error": "Invalid JSON returned",
            "raw_output": raw_output
        }


def main():
    """Run Action Agent"""

    # Mock Agent 1 output
    screening_result = {
        "match_score": 82,
        "matched_skills": ["React", "JavaScript", "REST APIs"],
        "missing_skills": ["TypeScript"],
        "experience_level": "Mid",
        "decision": "Strong Fit",
        "reasoning": "Relevant frontend experience with production apps"
    }

    # Mock Agent 3 output
    evaluation_result = {
        "overall_score": 78,
        "strengths": ["Problem solving", "React knowledge"],
        "weaknesses": ["Limited system design depth"],
        "communication": "good",
        "final_assessment": "Positive"
    }

    print("\nDeciding next action...\n")

    decision = decide_next_action(screening_result, evaluation_result)
    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()