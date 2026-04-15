import re
from loguru import logger
from models.schemas import ParsedResume, ScoreResult


class ScoringAgent:
    """
    Scores a parsed resume across five dimensions using heuristic NLP.
    Each dimension: 0–10 float.
    """

    _SENIOR_TITLES = re.compile(
        r"(?i)(senior|lead|principal|staff|head|director|vp|vice president|"
        r"manager|architect|chief|founder|co-founder|cto|ceo|cfo)"
    )
    _DEGREE_SCORE = {
        "phd": 10, "ph.d": 10, "doctorate": 10,
        "master": 8, "msc": 8, "mba": 8, "m.s": 8,
        "bachelor": 6, "b.s": 6, "b.e": 6, "b.tech": 6, "b.sc": 6,
        "associate": 4, "diploma": 3,
    }
    _COMM_INDICATORS = [
        "presented", "communicated", "collaborated", "negotiated",
        "facilitated", "mentored", "authored", "documented", "wrote",
        "designed", "led meetings", "stakeholder",
    ]
    _LEADERSHIP_INDICATORS = [
        "led", "managed", "supervised", "directed", "oversaw",
        "mentored", "built team", "hired", "grew team", "spearheaded",
        "founded", "launched", "scaled", "transformed", "strategy",
    ]

    def run(self, parsed: ParsedResume) -> ScoreResult:
        logger.info("ScoringAgent: Scoring candidate '{}'", parsed.name)

        tech_score = self._score_technical(parsed)
        exp_score = self._score_experience(parsed)
        edu_score = self._score_education(parsed)
        comm_score = self._score_communication(parsed)
        lead_score = self._score_leadership(parsed)

        overall = round(
            tech_score * 0.30
            + exp_score * 0.25
            + edu_score * 0.20
            + comm_score * 0.15
            + lead_score * 0.10,
            2,
        )

        result = ScoreResult(
            technical_skills=round(tech_score, 2),
            experience_depth=round(exp_score, 2),
            education_relevance=round(edu_score, 2),
            communication_clarity=round(comm_score, 2),
            leadership_potential=round(lead_score, 2),
            overall=overall,
        )

        logger.success("ScoringAgent: overall={}", overall)
        return result

    # ── Dimension Scorers ──────────────────────────────────────────────────────

    def _score_technical(self, parsed: ParsedResume) -> float:
        """More recognized skills → higher score."""
        skill_count = len(parsed.skills)
        if skill_count >= 20:
            return 10.0
        elif skill_count >= 15:
            return 8.5
        elif skill_count >= 10:
            return 7.0
        elif skill_count >= 7:
            return 5.5
        elif skill_count >= 4:
            return 4.0
        elif skill_count >= 2:
            return 2.5
        return 1.0

    def _score_experience(self, parsed: ParsedResume) -> float:
        """Senior title keywords and years of experience boost score."""
        exp_text = " ".join(parsed.experience).lower()
        full_text = exp_text + " " + parsed.summary.lower()

        score = 4.0  # baseline

        # Count years
        years = re.findall(r"(\d+)\s*\+?\s*years?", full_text)
        total_years = sum(int(y) for y in years) if years else 0

        if total_years >= 10:
            score += 4.0
        elif total_years >= 7:
            score += 3.0
        elif total_years >= 5:
            score += 2.5
        elif total_years >= 3:
            score += 1.5
        elif total_years >= 1:
            score += 0.5

        # Senior role bonus
        if self._SENIOR_TITLES.search(full_text):
            score += 1.5

        # Number of roles
        role_count = len(parsed.experience)
        score += min(role_count * 0.2, 1.0)

        return min(score, 10.0)

    def _score_education(self, parsed: ParsedResume) -> float:
        edu_text = " ".join(parsed.education).lower()
        best = 3.0  # no degree baseline

        for degree, s in self._DEGREE_SCORE.items():
            if degree in edu_text:
                best = max(best, s)

        # Certifications bonus
        cert_bonus = min(len(parsed.certifications) * 0.5, 2.0)
        return min(best + cert_bonus, 10.0)

    def _score_communication(self, parsed: ParsedResume) -> float:
        all_text = " ".join(parsed.experience + [parsed.summary]).lower()
        hits = sum(1 for kw in self._COMM_INDICATORS if kw in all_text)
        summary_length_bonus = min(len(parsed.summary) / 200, 1.0)
        score = 4.0 + min(hits * 0.6, 4.0) + summary_length_bonus
        return min(score, 10.0)

    def _score_leadership(self, parsed: ParsedResume) -> float:
        all_text = " ".join(parsed.experience + [parsed.summary]).lower()
        hits = sum(1 for kw in self._LEADERSHIP_INDICATORS if kw in all_text)
        senior_bonus = 2.0 if self._SENIOR_TITLES.search(all_text) else 0.0
        score = 3.0 + min(hits * 0.7, 5.0) + senior_bonus
        return min(score, 10.0)
