# ApexAI — Predictive Talent Intelligence Platform

> Intelligent Hiring Decisions Powered by AI

ApexAI is an end-to-end AI system designed to make hiring faster, more consistent, and more intelligent by combining modern techniques like LLMs, RAG, and Machine Learning.

---

## Overview

Recruitment often involves a lot of manual effort — reviewing resumes, comparing candidates, and making subjective decisions.
ApexAI aims to simplify this by building a system that can:
Understand candidate profiles
Evaluate them using structured and contextual signals
Provide clear, explainable recommendations

```
ResumeAgent → ScoringAgent → AdvisorAgent → ReportAgent
```

Each stage builds on the previous, producing a full executive talent intelligence report with a clear HIRE / CONSIDER / DECLINE decision.

---

## 💡 Why ApexAI

Evaluating candidates from resumes alone often leaves room for ambiguity, especially in the early stages.

ApexAI is built to bring more clarity and structure to this process by turning unstructured resume data into meaningful insights, consistent evaluations, and explainable hiring outcomes through a unified pipeline.

## 🚀 Features

Each part of the system is built to take raw resume data and turn it into clear, structured, and usable hiring insights.

- **Resume Parsing**  
  Extracts key information like skills, experience, education, and certifications using a mix of NLP and rule-based methods to keep it reliable.

- **Candidate Scoring**  
  Scores candidates across five important areas — technical skills, experience depth, education relevance, communication, and leadership — to make evaluations consistent.

- **AI Advisor**  
  Looks at the candidate profile and gives practical insights, including strengths, areas to improve, and possible career directions.

- **Hiring Decisions**  
  Generates clear outcomes (Hire / Consider / Decline) along with reasoning, so decisions are not just numbers but understandable.

- **Skill Gap Analysis**  
  Compares the candidate with role requirements and highlights missing skills, along with an estimate of what it would take to improve.

- **Candidate Data Management**  
  Stores and organizes candidate information and reports so they can be reused, searched, and tracked easily.

- **Production-Ready Backend**  
  Includes structured logging, error handling, and a clean API design so it can be extended or deployed in real scenarios.

---

## ⚙️ Tech Stack

### 🧠 AI & Intelligence Layer
- LLMs + LangGraph (Multi-Agent Orchestration)
- Retrieval-Augmented Generation (RAG)
- Knowledge Graphs for structured reasoning
- XGBoost for candidate success prediction

### ⚙️ Backend & API Layer
- FastAPI (high-performance API framework)
- Pydantic v2 (data validation & schema management)
- SQLAlchemy 2.0 (ORM)

### 🗄️ Data Layer
- SQLite (default) / PostgreSQL (production-ready)

### 🏗️ System & Infrastructure
- Uvicorn (ASGI server)
- Loguru (structured logging)
- Docker (containerization & deployment)
- Python 3.10+

---

## ⚙️ Key Engineering Decisions

- Designed as a modular multi-agent pipeline instead of a single monolithic function
- Separated API layer, business logic, and data models for maintainability
- Used structured logging and request tracking for debuggability
- Built database layer to be easily switchable (SQLite → PostgreSQL)
- Standardized API responses for consistency across endpoints

## 🗂️ Project Structure

The project is organized to keep the API layer, agent pipeline, and data models clearly separated, making the system easier to extend and maintain.

```
apexai/
├── main.py              # Application entry point (startup, middleware, lifecycle)
├── routes.py            # API endpoints
├── workflow.py          # Orchestrates the multi-agent pipeline
├── database.py          # Database setup and session management
├── config.py            # Environment-based configuration
├── logging_config.py    # Structured logging setup
├── requirements.txt     # Dependencies
├── .env.example         # Environment variables template

├── agents/              # Core intelligence layer
│   ├── resume_agent.py     # Parses and structures resume data
│   ├── scoring_agent.py    # Evaluates candidate across multiple dimensions
│   ├── advisor_agent.py    # Generates insights and improvement suggestions
│   ├── report_agent.py     # Produces final report and hiring decision

├── models/              # Data and schema layer
│   ├── schemas.py         # Request/response validation (Pydantic)
│   ├── database_models.py # ORM models (SQLAlchemy)
```

---

## Setup & Installation

### 1. Clone / Download

```bash
git clone https://github.com/your-org/apexai.git
cd apexai
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env as needed
```

### 5. Run the Server

```bash
uvicorn main:app --reload
```

Server runs at: `http://localhost:8000`
Interactive docs: `http://localhost:8000/docs`

---

## API Reference

### `POST /api/v1/predict`
Full pipeline — parse + score + advise + report + save to DB.

```json
{
  "resume_text": "John Doe\njohn@example.com\n...",
  "job_title": "Senior Backend Engineer"
}
```

**Returns:** candidate_id, parsed_resume, scores, advice, report

---

### `POST /api/v1/analyze`
Resume parsing only — returns structured resume data.

```json
{ "resume_text": "..." }
```

---

### `POST /api/v1/report`
Generate a hiring report from pre-scored JSON data.

```json
{
  "parsed_resume": { ... },
  "scores": { ... },
  "advice": { ... }
}
```

---

### `POST /api/v1/skill-gap`
Compare resume skills against a required skill list.

```json
{
  "resume_text": "...",
  "required_skills": ["Python", "Docker", "AWS", "Kubernetes"]
}
```

---

### `GET /api/v1/candidates`
List all candidates with summary scores and hiring decisions.

Query params: `skip`, `limit`

---

### `GET /api/v1/candidates/{id}`
Fetch full candidate history: scores, latest report, contact info.

---

### `GET /health`
Health check endpoint.

---

## Response Format

All endpoints return a standard envelope:

```json
{
  "status": "success",
  "message": "Pipeline complete",
  "data": { ... },
  "meta": {
    "pipeline_duration_ms": 12.4,
    "hiring_decision": "HIRE"
  }
}
```

---

## PostgreSQL Setup

To switch from SQLite to PostgreSQL, update `.env`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/apexai
```

No code changes required.

---

## Hiring Decision Logic

| Overall Score | Decision  |
|---------------|-----------|
| ≥ 7.5         | HIRE      |
| 5.5 – 7.4     | CONSIDER  |
| < 5.5         | DECLINE   |

Score weights:
- Technical Skills: 30%
- Experience Depth: 25%
- Education Relevance: 20%
- Communication Clarity: 15%
- Leadership Potential: 10%

---

## 🚧 Future Improvements

- Add real-time evaluation dashboard
- Improve scoring with ML-based models
- Integrate external job description parsing
- Add authentication and role-based access

## License

MIT — free to use, modify, and distribute.

---

*Built as a production-style backend system for AI-driven talent evaluation.*
