import re
from loguru import logger
from models.schemas import ParsedResume, ContactInfo


class ResumeAgent:
    """
    Parses raw resume text into structured data using regex + NLP heuristics.
    """

    # ── Regex Patterns ─────────────────────────────────────────────────────────

    _EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}")
    _PHONE_RE = re.compile(r"(\+?\d[\d\s\-().]{7,}\d)")
    _LINKEDIN_RE = re.compile(r"linkedin\.com/in/[\w\-]+", re.IGNORECASE)
    _SECTION_RE = re.compile(
        r"(?i)^(summary|objective|profile|skills|technical skills|experience|"
        r"work experience|education|certifications?|projects?|awards?|publications?)"
        r"[\s:]*$",
        re.MULTILINE,
    )

    _SKILL_KEYWORDS = [
        "python", "java", "javascript", "typescript", "react", "angular", "vue",
        "node", "django", "fastapi", "flask", "sql", "postgresql", "mysql",
        "mongodb", "redis", "docker", "kubernetes", "aws", "gcp", "azure",
        "git", "ci/cd", "machine learning", "deep learning", "nlp", "data science",
        "tensorflow", "pytorch", "spark", "kafka", "graphql", "rest", "api",
        "linux", "bash", "golang", "rust", "c++", "c#", "ruby", "php", "swift",
        "kotlin", "flutter", "terraform", "ansible", "jenkins", "github actions",
        "agile", "scrum", "leadership", "communication", "project management",
    ]

    def run(self, resume_text: str) -> ParsedResume:
        logger.info("ResumeAgent: Parsing resume text ({} chars)", len(resume_text))

        name = self._extract_name(resume_text)
        contact = self._extract_contact(resume_text)
        sections = self._split_sections(resume_text)

        summary = self._extract_summary(sections, resume_text)
        skills = self._extract_skills(resume_text)
        experience = self._extract_section_bullets(sections, ["experience", "work experience"])
        education = self._extract_section_bullets(sections, ["education"])
        certifications = self._extract_section_bullets(sections, ["certifications", "certification"])

        result = ParsedResume(
            name=name,
            contact=contact,
            summary=summary,
            skills=skills,
            experience=experience,
            education=education,
            certifications=certifications,
        )

        logger.success("ResumeAgent: Parsed → name={}, skills={}", name, len(skills))
        return result

    # ── Private Helpers ────────────────────────────────────────────────────────

    def _extract_name(self, text: str) -> str:
        """First non-empty line is usually the candidate's name."""
        for line in text.strip().splitlines():
            line = line.strip()
            if line and len(line) < 60 and not self._EMAIL_RE.search(line):
                if not any(kw in line.lower() for kw in ["resume", "curriculum", "cv", "profile"]):
                    return line
        return "Unknown Candidate"

    def _extract_contact(self, text: str) -> ContactInfo:
        email_match = self._EMAIL_RE.search(text)
        phone_matches = self._PHONE_RE.findall(text)
        linkedin_match = self._LINKEDIN_RE.search(text)

        phone = None
        for p in phone_matches:
            cleaned = re.sub(r"[^\d+]", "", p)
            if 7 <= len(cleaned) <= 15:
                phone = p.strip()
                break

        return ContactInfo(
            email=email_match.group() if email_match else None,
            phone=phone,
            linkedin=linkedin_match.group() if linkedin_match else None,
        )

    def _split_sections(self, text: str) -> dict[str, str]:
        """Split resume into named sections."""
        sections: dict[str, str] = {}
        lines = text.splitlines()
        current_section = "header"
        current_lines: list[str] = []

        for line in lines:
            if self._SECTION_RE.match(line.strip()):
                sections[current_section] = "\n".join(current_lines).strip()
                current_section = line.strip().lower().rstrip(":")
                current_lines = []
            else:
                current_lines.append(line)

        sections[current_section] = "\n".join(current_lines).strip()
        return sections

    def _extract_summary(self, sections: dict, full_text: str) -> str:
        for key in ["summary", "objective", "profile"]:
            for section_key, content in sections.items():
                if key in section_key.lower() and content:
                    return content[:500]
        # Fallback: grab second paragraph
        paras = [p.strip() for p in full_text.split("\n\n") if p.strip()]
        return paras[1][:500] if len(paras) > 1 else paras[0][:300]

    def _extract_skills(self, text: str) -> list[str]:
        lower = text.lower()
        found = [skill for skill in self._SKILL_KEYWORDS if skill in lower]

        # Also pick up comma-separated skill lines
        skill_section_re = re.compile(
            r"(?i)(?:skills?|technologies|tools?)[\s:]+(.+?)(?:\n\n|\Z)", re.DOTALL
        )
        match = skill_section_re.search(text)
        if match:
            raw = match.group(1)
            extras = [s.strip() for s in re.split(r"[,|•\n]", raw) if 2 < len(s.strip()) < 40]
            for e in extras:
                if e.lower() not in [f.lower() for f in found]:
                    found.append(e)

        return list(dict.fromkeys(found))[:30]  # deduplicate, cap at 30

    def _extract_section_bullets(self, sections: dict, keys: list[str]) -> list[str]:
        for key in keys:
            for section_key, content in sections.items():
                if key in section_key.lower() and content:
                    lines = [
                        re.sub(r"^[•\-*>\s]+", "", l).strip()
                        for l in content.splitlines()
                        if l.strip() and len(l.strip()) > 5
                    ]
                    return [l for l in lines if l][:15]
        return []
