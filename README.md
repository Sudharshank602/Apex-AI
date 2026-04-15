# ApexAI — Predictive Talent Intelligence Platform

> A production-ready, multi-agent AI backend for hiring intelligence. Built with FastAPI, SQLAlchemy, and clean architecture.

---

## Overview

ApexAI is an AI-powered hiring platform that automates resume analysis, candidate scoring, skill gap detection, and hiring decision generation through a four-stage agent pipeline.

```
ResumeAgent → ScoringAgent → AdvisorAgent → ReportAgent
```

Each stage builds on the previous, producing a full executive talent intelligence report with a clear HIRE / CONSIDER / DECLINE decision.

---

## Features

- **Resume Parsing** — NLP + regex extraction of name, contact, skills, experience, education, certifications
- **Multi-Dimensional Scoring** — 5 dimensions: Technical Skills, Experience Depth, Education Relevance, Communication Clarity, Leadership Potential
- **AI Advisor** — Strengths analysis, improvement roadmap, career path suggestions, prioritized action items
- **Hiring Reports** — Executive summary, decision rationale, full formatted talent report
- **Skill Gap Analysis** — Compare resume against required role skills, get learning time estimates
- **Candidate Database** — Full history: save, retrieve, filter candidates and their reports
- **Production-Ready** — Request ID middleware, structured Loguru logging, performance headers, global error handling

---

## Tech Stack

| Layer        | Technology                          |
|--------------|-------------------------------------|
| Framework    | FastAPI 0.111+                      |
| Validation   | Pydantic v2                         |
| Database ORM | SQLAlchemy 2.0                      |
| Database     | SQLite (default) / PostgreSQL-ready |
| Logging      | Loguru                              |
| Runtime      | Python 3.10+                        |
| Server       | Uvicorn (ASGI)                      |

---

## Project Structure

```
apexai/
├── main.py                  # App entrypoint, middleware, lifecycle
├── routes.py                # All API endpoints
├── workflow.py              # 4-agent pipeline orchestrator
├── database.py              # SQLAlchemy setup + session factory
├── config.py                # Environment-based settings
├── logging_config.py        # Loguru structured logging
├── requirements.txt
├── .env.example
│
├── agents/
│   ├── resume_agent.py      # Stage 1 — Parse resume
│   ├── scoring_agent.py     # Stage 2 — Score across 5 dimensions
│   ├── advisor_agent.py     # Stage 3 — Generate advice & career paths
│   └── report_agent.py      # Stage 4 — Executive report + hiring decision
│
└── models/
    ├── schemas.py           # Pydantic v2 request/response models
    └── database_models.py   # SQLAlchemy ORM models
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

## License

MIT — free to use, modify, and distribute.

---

*Powered by ApexAI — Predictive Talent Intelligence Platform*
