from datetime import datetime, timezone
from loguru import logger
from models.schemas import ParsedResume, ScoreResult, AdvisorResult, ReportResult, HiringDecision


class ReportAgent:
    """
    Synthesizes all agent outputs into an executive hiring report with
    a final HIRE / CONSIDER / DECLINE decision.
    """

    def run(
        self,
        parsed: ParsedResume,
        scores: ScoreResult,
        advice: AdvisorResult,
    ) -> ReportResult:
        logger.info("ReportAgent: Generating report for '{}'", parsed.name)

        decision = self._make_decision(scores)
        executive_summary = self._write_executive_summary(parsed, scores, decision)
        recommendation = self._write_recommendation(parsed, scores, decision)
        full_report = self._write_full_report(parsed, scores, advice, decision, executive_summary, recommendation)

        result = ReportResult(
            executive_summary=executive_summary,
            hiring_decision=decision,
            recommendation=recommendation,
            scores=scores,
            advice=advice,
            full_report_text=full_report,
        )

        logger.success("ReportAgent: Decision = {}", decision.value)
        return result

    # ── Decision Engine ────────────────────────────────────────────────────────

    def _make_decision(self, scores: ScoreResult) -> HiringDecision:
        if scores.overall >= 7.5:
            return HiringDecision.HIRE
        elif scores.overall >= 5.5:
            return HiringDecision.CONSIDER
        else:
            return HiringDecision.DECLINE

    # ── Narrative Writers ──────────────────────────────────────────────────────

    def _write_executive_summary(
        self, parsed: ParsedResume, scores: ScoreResult, decision: HiringDecision
    ) -> str:
        decision_phrase = {
            HiringDecision.HIRE: "a strong match and is recommended for immediate hire",
            HiringDecision.CONSIDER: "a moderate match and warrants further evaluation",
            HiringDecision.DECLINE: "below the threshold for this role at this time",
        }[decision]

        return (
            f"{parsed.name} is {decision_phrase}. "
            f"The candidate achieved an overall ApexAI Intelligence Score of {scores.overall:.1f}/10, "
            f"reflecting {self._describe_score(scores.overall)} performance. "
            f"Key strengths include a technical skills score of {scores.technical_skills:.1f} "
            f"and experience depth of {scores.experience_depth:.1f}. "
            f"Identified {len(parsed.skills)} technical competencies across the resume."
        )

    def _write_recommendation(
        self, parsed: ParsedResume, scores: ScoreResult, decision: HiringDecision
    ) -> str:
        if decision == HiringDecision.HIRE:
            return (
                f"Proceed with {parsed.name} to the technical interview stage. "
                f"Candidate demonstrates well-rounded capabilities with an overall score of {scores.overall:.1f}/10. "
                f"Recommend fast-tracking this profile to minimize time-to-hire for a high-potential candidate."
            )
        elif decision == HiringDecision.CONSIDER:
            return (
                f"{parsed.name} shows promise but requires further evaluation. "
                f"Conduct a structured technical screening to validate depth in key areas. "
                f"An overall score of {scores.overall:.1f}/10 suggests upside with the right role fit."
            )
        else:
            return (
                f"At this time, {parsed.name} does not meet the minimum threshold for the role "
                f"(overall score: {scores.overall:.1f}/10). "
                f"Consider archiving for future openings or entry-level positions after skill development."
            )

    def _write_full_report(
        self,
        parsed: ParsedResume,
        scores: ScoreResult,
        advice: AdvisorResult,
        decision: HiringDecision,
        executive_summary: str,
        recommendation: str,
    ) -> str:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        divider = "=" * 65

        sections = [
            f"{divider}",
            f"  APEXAI PREDICTIVE TALENT INTELLIGENCE REPORT",
            f"  Generated: {now}",
            f"{divider}",
            "",
            "EXECUTIVE SUMMARY",
            "-" * 40,
            executive_summary,
            "",
            f"HIRING DECISION:  ★  {decision.value}  ★",
            "",
            "SCORING BREAKDOWN",
            "-" * 40,
            f"  Technical Skills      : {scores.technical_skills:.1f} / 10",
            f"  Experience Depth      : {scores.experience_depth:.1f} / 10",
            f"  Education Relevance   : {scores.education_relevance:.1f} / 10",
            f"  Communication Clarity : {scores.communication_clarity:.1f} / 10",
            f"  Leadership Potential  : {scores.leadership_potential:.1f} / 10",
            f"  ─────────────────────────────────",
            f"  OVERALL SCORE         : {scores.overall:.2f} / 10",
            "",
            "CANDIDATE PROFILE",
            "-" * 40,
            f"  Name    : {parsed.name}",
            f"  Email   : {parsed.contact.email or 'N/A'}",
            f"  Phone   : {parsed.contact.phone or 'N/A'}",
            f"  LinkedIn: {parsed.contact.linkedin or 'N/A'}",
            "",
            f"  Summary : {parsed.summary[:300]}",
            "",
            "TECHNICAL SKILLS",
            "-" * 40,
            "  " + " • ".join(parsed.skills) if parsed.skills else "  None detected",
            "",
            "STRENGTHS",
            "-" * 40,
        ]

        for i, s in enumerate(advice.strengths, 1):
            sections.append(f"  {i}. {s}")

        sections += ["", "IMPROVEMENT AREAS", "-" * 40]
        for i, a in enumerate(advice.improvement_areas, 1):
            sections.append(f"  {i}. {a}")

        sections += ["", "RECOMMENDED ACTION ITEMS", "-" * 40]
        for i, item in enumerate(advice.action_items, 1):
            sections.append(f"  {i}. {item}")

        sections += ["", "CAREER PATH SUGGESTIONS", "-" * 40]
        for path in advice.career_path_suggestions:
            sections.append(f"  → {path}")

        sections += [
            "",
            "RECOMMENDATION",
            "-" * 40,
            recommendation,
            "",
            divider,
            "  Powered by ApexAI — Predictive Talent Intelligence Platform",
            divider,
        ]

        return "\n".join(sections)

    def _describe_score(self, score: float) -> str:
        if score >= 9:
            return "exceptional"
        elif score >= 7.5:
            return "strong"
        elif score >= 6:
            return "above-average"
        elif score >= 5:
            return "average"
        elif score >= 3.5:
            return "below-average"
        return "poor"
