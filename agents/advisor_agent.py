from loguru import logger
from models.schemas import ParsedResume, ScoreResult, AdvisorResult


class AdvisorAgent:
    """
    Generates strengths, improvement areas, action items, and career path
    suggestions based on parsed resume and scores.
    """

    def run(self, parsed: ParsedResume, scores: ScoreResult) -> AdvisorResult:
        logger.info("AdvisorAgent: Generating advice for '{}'", parsed.name)

        strengths = self._identify_strengths(parsed, scores)
        improvement_areas = self._identify_improvements(parsed, scores)
        action_items = self._generate_action_items(improvement_areas, parsed)
        career_paths = self._suggest_career_paths(parsed, scores)

        result = AdvisorResult(
            strengths=strengths,
            improvement_areas=improvement_areas,
            action_items=action_items,
            career_path_suggestions=career_paths,
        )

        logger.success("AdvisorAgent: {} strengths, {} improvements", len(strengths), len(improvement_areas))
        return result

    # ── Strength Detection ─────────────────────────────────────────────────────

    def _identify_strengths(self, parsed: ParsedResume, scores: ScoreResult) -> list[str]:
        strengths = []

        if scores.technical_skills >= 7:
            strengths.append(
                f"Strong technical foundation with {len(parsed.skills)} identified skills including "
                f"{', '.join(parsed.skills[:3]) if parsed.skills else 'diverse technologies'}."
            )
        if scores.experience_depth >= 7:
            strengths.append("Extensive real-world experience demonstrating depth across roles.")
        if scores.education_relevance >= 7:
            strengths.append("Solid academic credentials that reinforce domain expertise.")
        if scores.communication_clarity >= 7:
            strengths.append("Articulate communicator with clear, compelling resume narrative.")
        if scores.leadership_potential >= 7:
            strengths.append("Demonstrated leadership capabilities with team or project ownership.")
        if len(parsed.certifications) > 0:
            strengths.append(
                f"Proactive learner with {len(parsed.certifications)} professional certification(s): "
                f"{', '.join(parsed.certifications[:2])}."
            )
        if scores.overall >= 8:
            strengths.append("Consistently high performance across all evaluated dimensions.")

        if not strengths:
            strengths.append("Shows initiative in pursuing a career in this field.")

        return strengths

    # ── Improvement Detection ──────────────────────────────────────────────────

    def _identify_improvements(self, parsed: ParsedResume, scores: ScoreResult) -> list[str]:
        improvements = []

        if scores.technical_skills < 6:
            improvements.append(
                "Technical skill breadth is below average — fewer than 7 recognizable technologies detected."
            )
        if scores.experience_depth < 5:
            improvements.append(
                "Limited professional experience. Consider gaining more hands-on exposure or side projects."
            )
        if scores.education_relevance < 5:
            improvements.append(
                "Educational background may not align closely with the target role. "
                "Supplemental certifications are recommended."
            )
        if scores.communication_clarity < 6:
            improvements.append(
                "Resume narrative lacks strong action verbs and communication indicators. "
                "Rewrite experience bullets to be achievement-oriented."
            )
        if scores.leadership_potential < 5:
            improvements.append(
                "No clear leadership signals found. Highlight team leadership, mentorship, or ownership experiences."
            )
        if len(parsed.certifications) == 0:
            improvements.append(
                "No professional certifications found. Adding industry certifications can significantly boost credibility."
            )

        return improvements

    # ── Action Items ───────────────────────────────────────────────────────────

    def _generate_action_items(self, improvements: list[str], parsed: ParsedResume) -> list[str]:
        actions = []

        skill_map = {
            "technical": [
                "Complete an online specialization (Coursera, Udemy, or Pluralsight) in a high-demand technology.",
                "Build 2–3 portfolio projects on GitHub showcasing relevant technical skills.",
                "Contribute to open-source projects to demonstrate real-world coding ability.",
            ],
            "experience": [
                "Pursue freelance or contract roles to accelerate experience accumulation.",
                "Document all side projects, hackathons, and volunteer work in your resume.",
                "Seek an internship or apprenticeship to bridge the experience gap.",
            ],
            "education": [
                "Enroll in a relevant certification program (AWS, Google, Microsoft, or domain-specific).",
                "Consider a part-time graduate program or executive education course.",
            ],
            "communication": [
                "Rewrite each experience bullet using the CAR format: Challenge → Action → Result.",
                "Quantify achievements (%, $, users, time saved) wherever possible.",
                "Have a professional review or use a resume review service.",
            ],
            "leadership": [
                "Volunteer to lead a team project or internal initiative at your current role.",
                "Mentor junior developers or peers to establish leadership track record.",
                "Add a 'Leadership & Impact' section highlighting any cross-functional work.",
            ],
        }

        for area in improvements:
            lower = area.lower()
            if "technical" in lower:
                actions.extend(skill_map["technical"][:2])
            elif "experience" in lower:
                actions.extend(skill_map["experience"][:2])
            elif "education" in lower or "certification" in lower:
                actions.extend(skill_map["education"])
            elif "communication" in lower or "narrative" in lower:
                actions.extend(skill_map["communication"][:2])
            elif "leadership" in lower:
                actions.extend(skill_map["leadership"][:2])

        actions.append("Update LinkedIn profile to mirror an improved resume.")
        return list(dict.fromkeys(actions))[:8]  # deduplicate, cap at 8

    # ── Career Path Suggestions ────────────────────────────────────────────────

    def _suggest_career_paths(self, parsed: ParsedResume, scores: ScoreResult) -> list[str]:
        skills_lower = [s.lower() for s in parsed.skills]

        paths = []

        if any(s in skills_lower for s in ["machine learning", "deep learning", "nlp", "tensorflow", "pytorch"]):
            paths.append("Senior ML Engineer → Principal AI Scientist → Head of AI")
        if any(s in skills_lower for s in ["python", "django", "fastapi", "flask"]):
            paths.append("Backend Engineer → Senior Backend Engineer → Engineering Manager → CTO")
        if any(s in skills_lower for s in ["react", "angular", "vue", "javascript", "typescript"]):
            paths.append("Frontend Developer → Senior Frontend Engineer → Full-Stack Lead → VP Engineering")
        if any(s in skills_lower for s in ["docker", "kubernetes", "aws", "terraform", "ansible"]):
            paths.append("DevOps Engineer → Site Reliability Engineer → Cloud Architect → VP Infrastructure")
        if any(s in skills_lower for s in ["data science", "spark", "sql", "postgresql", "mongodb"]):
            paths.append("Data Analyst → Data Scientist → Lead Data Scientist → Chief Data Officer")
        if scores.leadership_potential >= 7:
            paths.append("Technical Lead → Engineering Manager → Director of Engineering → VP Engineering")

        if not paths:
            paths.append("Junior Developer → Mid-level Engineer → Senior Engineer → Tech Lead")

        paths.append("Consider specialization + leadership track to maximize compensation trajectory.")
        return paths
