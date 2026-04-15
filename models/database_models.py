from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    resume_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    scores = relationship("Score", back_populates="candidate", uselist=False, cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="candidate", cascade="all, delete-orphan")


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    technical_skills = Column(Float, nullable=False)
    experience_depth = Column(Float, nullable=False)
    education_relevance = Column(Float, nullable=False)
    communication = Column(Float, nullable=False)
    leadership = Column(Float, nullable=False)
    overall = Column(Float, nullable=False)

    candidate = relationship("Candidate", back_populates="scores")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    hiring_decision = Column(String(20), nullable=False)
    recommendation = Column(Text, nullable=False)
    full_report = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    candidate = relationship("Candidate", back_populates="reports")
