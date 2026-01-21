# Recruitment AI System (Multi-Agent Backend + n8n Automation)

This project is an end-to-end **AI-powered recruitment automation system** built using:
- **FastAPI** (backend orchestration)
- **Multiple AI agents** (resume screening, interview question generation, answer evaluation)
- **n8n** (workflow automation)
- **Cloudflare Tunnel** (public URL for local backend)
- **OpenRouter / LLM APIs** (model inference)

The system automates:
1. Resume screening
2. Interview question generation
3. Candidate answer evaluation
4. Workflow orchestration via n8n

---

Cloudflare is used to expose the local FastAPI backend so that **n8n can call it using public URLs**.

---

## 📁 Project Structure
.
├── main.py # FastAPI backend
├── resume_screening_agent.py # Agent 1
├── interviewer_agent.py # Agent 2
├── evaluation_agent.py # Agent 3
├── sample_data/
│ ├── job_description.txt
│ └── resume.txt
├── Recruitment.json # n8n workflow export
├── requirements.txt
├── .env
└── README.md

---

## ⚙️ Environment Setup

### 1️⃣ Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate        # Windows
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Environment Variables

Create a .env file similar to the provided .env.example.


## 🧪 Running Agents Individually (Test Mode)

Each agent file contains a test run section for isolated execution.

### ▶️ Agent 1 – Resume Screening
```bash
python resume_screening_agent.py
```

### ▶️ Agent 2 – Interview Question Generation
```bash
python interviewer_agent.py
```

### ▶️ Agent 3 – Answer Evaluation
```bash
python evaluation_agent.py
```


## 🚀 Running the FastAPI Backend

Start the API server:
```bash
uvicorn main:app --reload --port 8000
```

FastAPI will be available locally at: http://localhost:8000


## 🌐 Exposing Backend via Cloudflare Tunnel

To allow n8n (or any external service) to access your local FastAPI backend:
```bash
cloudflared tunnel --url http://localhost:8000
```

Cloudflare will generate a public URL like: https://random-name.trycloudflare.com


## 🔗 n8n Integration

Use the Cloudflare public URL in n8n HTTP Request nodes
Append the agent endpoints defined in main.py
Example n8n HTTP URLs:
https://random-name.trycloudflare.com/screen
https://random-name.trycloudflare.com/generate_questions
https://random-name.trycloudflare.com/evaluate

Each corresponds to:
/screen → Agent 1 (Resume Screening)
/generate_questions → Agent 2 (Interview Questions)
/evaluate → Agent 3 (Answer Evaluation)

## 🔁 n8n Workflow

The file Recruitment.json contains the complete n8n workflow.
Import it directly into n8n.


## 🧠 Notes & Best Practices

- Cloudflare tunnel URLs change every time unless you use a named tunnel
- Ensure the FastAPI backend is running before executing n8n workflows
- All agents are stateless and can be tested independently
- Designed for extensibility (emailing results, logging, ATS integration)


# Happy building 🚀