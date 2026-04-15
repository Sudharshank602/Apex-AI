from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


# ── Enums ──────────────────────────────────────────────────────────────────────

class HiringDecision(str, Enum):
    HIRE = "HIRE"
    CONSIDER = "CONSIDER"
    DECLINE = "DECLINE"


# ── Agent Output Schemas ───────────────────────────────────────────────────────

class ContactInfo(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    location: Optional[str] = None


class ParsedResume(BaseModel):
    name: str
    contact: ContactInfo
    summary: str
    skills: List[str]
    experience: List[str]
    education: List[str]
    certifications: List[str]


class ScoreResult(BaseModel):
    technical_skills: float = Field(..., ge=0, le=10)
    experience_depth: float = Field(..., ge=0, le=10)
    education_relevance: float = Field(..., ge=0, le=10)
    communication_clarity: float = Field(..., ge=0, le=10)
    leadership_potential: float = Field(..., ge=0, le=10)
    overall: float = Field(..., ge=0, le=10)


class AdvisorResult(BaseModel):
    strengths: List[str]
    improvement_areas: List[str]
    action_items: List[str]
    career_path_suggestions: List[str]


class ReportResult(BaseModel):
    executive_summary: str
    hiring_decision: HiringDecision
    recommendation: str
    scores: ScoreResult
    advice: AdvisorResult
    full_report_text: str


# ── Request Schemas ────────────────────────────────────────────────────────────

class PredictRequest(BaseModel):
    resume_text: str = Field(..., min_length=50, description="Raw resume text to analyze")
    job_title: Optional[str] = Field(None, description="Target job title for contextual scoring")


class AnalyzeRequest(BaseModel):
    resume_text: str = Field(..., min_length=50)


class ReportRequest(BaseModel):
    parsed_resume: ParsedResume
    scores: ScoreResult
    advice: AdvisorResult


class SkillGapRequest(BaseModel):
    resume_text: str
    required_skills: List[str] = Field(..., description="Skills required for the role")


# ── Response Schemas ───────────────────────────────────────────────────────────

class StandardResponse(BaseModel):
    status: str
    message: str
    data: Any
    meta: dict = {}


class CandidateListItem(BaseModel):
    id: int
    name: str
    email: Optional[str]
    overall_score: Optional[float]
    hiring_decision: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CandidateDetail(BaseModel):
    id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    resume_text: str
    created_at: datetime
    scores: Optional[ScoreResult] = None
    latest_report: Optional[dict] = None

    class Config:
        from_attributes = True


class SkillGapResult(BaseModel):
    present_skills: List[str]
    missing_skills: List[str]
    gap_percentage: float
    priority_skills_to_learn: List[str]
    estimated_learning_time: str
