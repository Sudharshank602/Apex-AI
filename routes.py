from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from loguru import logger
import time

from database import get_db
from workflow import Workflow
from agents.resume_agent import ResumeAgent
from agents.report_agent import ReportAgent
from models.schemas import (
    PredictRequest,
    AnalyzeRequest,
    ReportRequest,
    SkillGapRequest,
    StandardResponse,
    SkillGapResult,
)
from models.database_models import Candidate, Score, Report

router = APIRouter()
_workflow = Workflow()
_resume_agent = ResumeAgent()
_report_agent = ReportAgent()


# ── Helper ─────────────────────────────────────────────────────────────────────

def ok(data, message: str = "Success", meta: dict = None) -> StandardResponse:
    return StandardResponse(status="success", message=message, data=data, meta=meta or {})


# ── POST /predict ──────────────────────────────────────────────────────────────

@router.post("/predict", response_model=StandardResponse)
async def predict(req: PredictRequest, request: Request, db: Session = Depends(get_db)):
    """Run the full 4-stage AI pipeline and persist results."""
    t0 = time.perf_counter()
    logger.info("[{}] POST /predict", request.state.request_id)

    result = _workflow.run_pipeline(req.resume_text)

    # Persist candidate
    candidate = Candidate(
        name=result.parsed.name,
        email=result.parsed.contact.email,
        phone=result.parsed.contact.phone,
        resume_text=req.resume_text,
    )
    db.add(candidate)
    db.flush()

    # Persist scores
    score_row = Score(
        candidate_id=candidate.id,
        technical_skills=result.scores.technical_skills,
        experience_depth=result.scores.experience_depth,
        education_relevance=result.scores.education_relevance,
        communication=result.scores.communication_clarity,
        leadership=result.scores.leadership_potential,
        overall=result.scores.overall,
    )
    db.add(score_row)

    # Persist report
    report_row = Report(
        candidate_id=candidate.id,
        hiring_decision=result.report.hiring_decision.value,
        recommendation=result.report.recommendation,
        full_report=result.report.full_report_text,
    )
    db.add(report_row)
    db.commit()

    elapsed = (time.perf_counter() - t0) * 1000
    return ok(
        {
            "candidate_id": candidate.id,
            "parsed_resume": result.parsed.model_dump(),
            "scores": result.scores.model_dump(),
            "advice": result.advice.model_dump(),
            "report": result.report.model_dump(),
        },
        message="Pipeline complete",
        meta={
            "pipeline_duration_ms": result.duration_ms,
            "total_duration_ms": round(elapsed, 2),
            "hiring_decision": result.report.hiring_decision.value,
        },
    )


# ── POST /analyze ──────────────────────────────────────────────────────────────

@router.post("/analyze", response_model=StandardResponse)
async def analyze(req: AnalyzeRequest, request: Request):
    """Resume parsing only — returns structured data, no scoring."""
    logger.info("[{}] POST /analyze", request.state.request_id)
    parsed = _resume_agent.run(req.resume_text)
    return ok(parsed.model_dump(), message="Resume parsed successfully")


# ── POST /report ───────────────────────────────────────────────────────────────

@router.post("/report", response_model=StandardResponse)
async def generate_report(req: ReportRequest, request: Request):
    """Generate a hiring report from pre-computed JSON inputs."""
    logger.info("[{}] POST /report", request.state.request_id)
    report = _report_agent.run(req.parsed_resume, req.scores, req.advice)
    return ok(report.model_dump(), message="Report generated")


# ── POST /skill-gap ────────────────────────────────────────────────────────────

@router.post("/skill-gap", response_model=StandardResponse)
async def skill_gap(req: SkillGapRequest, request: Request):
    """Identify skill gaps between the resume and a required skill set."""
    logger.info("[{}] POST /skill-gap", request.state.request_id)

    parsed = _resume_agent.run(req.resume_text)
    candidate_skills_lower = [s.lower() for s in parsed.skills]
    required_lower = [s.lower() for s in req.required_skills]

    present = [r for r in req.required_skills if r.lower() in candidate_skills_lower]
    missing = [r for r in req.required_skills if r.lower() not in candidate_skills_lower]

    gap_pct = round(len(missing) / max(len(req.required_skills), 1) * 100, 1)

    # Priority = missing skills that appear frequently in job postings
    priority_order = ["python", "docker", "kubernetes", "aws", "react", "sql",
                      "machine learning", "typescript", "kubernetes", "ci/cd"]
    priority = sorted(missing, key=lambda s: priority_order.index(s.lower())
                      if s.lower() in priority_order else 999)[:5]

    hours = len(missing) * 40
    weeks = hours // 40
    est_time = f"~{weeks} weeks at 40h/week" if weeks > 0 else "< 1 week"

    result = SkillGapResult(
        present_skills=present,
        missing_skills=missing,
        gap_percentage=gap_pct,
        priority_skills_to_learn=priority,
        estimated_learning_time=est_time,
    )
    return ok(result.model_dump(), message="Skill gap analysis complete", meta={"gap_pct": gap_pct})


# ── GET /candidates ────────────────────────────────────────────────────────────

@router.get("/candidates", response_model=StandardResponse)
async def get_candidates(db: Session = Depends(get_db), skip: int = 0, limit: int = 50):
    """List all candidates with summary info."""
    rows = db.query(Candidate).offset(skip).limit(limit).all()
    total = db.query(Candidate).count()

    data = []
    for c in rows:
        entry = {
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "overall_score": c.scores.overall if c.scores else None,
            "hiring_decision": c.reports[-1].hiring_decision if c.reports else None,
        }
        data.append(entry)

    return ok(data, message=f"{len(data)} candidates retrieved", meta={"total": total, "skip": skip, "limit": limit})


# ── GET /candidates/{id} ───────────────────────────────────────────────────────

@router.get("/candidates/{candidate_id}", response_model=StandardResponse)
async def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Fetch full candidate history including scores and latest report."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")

    latest_report = candidate.reports[-1] if candidate.reports else None

    data = {
        "id": candidate.id,
        "name": candidate.name,
        "email": candidate.email,
        "phone": candidate.phone,
        "created_at": candidate.created_at.isoformat() if candidate.created_at else None,
        "scores": {
            "technical_skills": candidate.scores.technical_skills,
            "experience_depth": candidate.scores.experience_depth,
            "education_relevance": candidate.scores.education_relevance,
            "communication_clarity": candidate.scores.communication,
            "leadership_potential": candidate.scores.leadership,
            "overall": candidate.scores.overall,
        } if candidate.scores else None,
        "latest_report": {
            "hiring_decision": latest_report.hiring_decision,
            "recommendation": latest_report.recommendation,
            "created_at": latest_report.created_at.isoformat() if latest_report.created_at else None,
        } if latest_report else None,
    }

    return ok(data, message="Candidate retrieved")
