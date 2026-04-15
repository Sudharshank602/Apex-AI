import time
from loguru import logger

from agents.resume_agent import ResumeAgent
from agents.scoring_agent import ScoringAgent
from agents.advisor_agent import AdvisorAgent
from agents.report_agent import ReportAgent
from models.schemas import ParsedResume, ScoreResult, AdvisorResult, ReportResult


class PipelineResult:
    def __init__(
        self,
        parsed: ParsedResume,
        scores: ScoreResult,
        advice: AdvisorResult,
        report: ReportResult,
        duration_ms: float,
    ):
        self.parsed = parsed
        self.scores = scores
        self.advice = advice
        self.report = report
        self.duration_ms = duration_ms


class Workflow:
    """
    Orchestrates the 4-agent talent intelligence pipeline:

        ResumeAgent → ScoringAgent → AdvisorAgent → ReportAgent
    """

    def __init__(self):
        self.resume_agent = ResumeAgent()
        self.scoring_agent = ScoringAgent()
        self.advisor_agent = AdvisorAgent()
        self.report_agent = ReportAgent()

    def run_pipeline(self, resume_text: str) -> PipelineResult:
        start = time.perf_counter()
        logger.info("Workflow: Pipeline started ({} chars)", len(resume_text))

        # Stage 1 — Parse
        logger.info("→ Stage 1: ResumeAgent")
        parsed = self.resume_agent.run(resume_text)

        # Stage 2 — Score
        logger.info("→ Stage 2: ScoringAgent")
        scores = self.scoring_agent.run(parsed)

        # Stage 3 — Advise
        logger.info("→ Stage 3: AdvisorAgent")
        advice = self.advisor_agent.run(parsed, scores)

        # Stage 4 — Report
        logger.info("→ Stage 4: ReportAgent")
        report = self.report_agent.run(parsed, scores, advice)

        duration_ms = (time.perf_counter() - start) * 1000
        logger.success("Workflow: Pipeline complete in {:.1f}ms | decision={}", duration_ms, report.hiring_decision)

        return PipelineResult(
            parsed=parsed,
            scores=scores,
            advice=advice,
            report=report,
            duration_ms=round(duration_ms, 2),
        )
