"""Agent 2: writes a truthful short cover letter using the candidate profile."""
import json
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import get_llm

ROOT = Path(__file__).resolve().parent
DEFAULT_PROFILE = ROOT / "data" / "my_skills.json"


PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You write concise, professional and truthful job cover letters.

Rules:
1. Use only skills, education, experience and projects explicitly
   supported by the supplied candidate profile.
2. Do not invent qualifications, employers, dates or achievements.
3. Mention only skills relevant to the advertised role.
4. Do not claim that a skill appears in the attached resume unless
   the resume text has actually been supplied and supports that claim.
5. If the profile does not provide enough evidence for a claim,
   omit that claim.
6. Write 4-5 short lines.
7. Begin with 'Dear Hiring Manager,'.
8. End with 'Sincerely,' followed by the candidate's real name,
   if provided.
"""
    ),
    (
        "human",
        """Job title: {job_title}
Required skills: {required_skills}

Candidate profile JSON:
{profile}"""
    ),
])



def load_profile(path: str | Path = DEFAULT_PROFILE) -> dict:
    profile_path = Path(path).expanduser()
    if not profile_path.is_absolute():
        profile_path = (ROOT / profile_path).resolve()
    if not profile_path.is_file():
        raise FileNotFoundError(
            f"Candidate profile not found: {profile_path}. Copy data/my_skills.example.json to data/my_skills.json and edit it."
        )
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    if not isinstance(profile, dict):
        raise ValueError("Candidate profile must be a JSON object.")
    return profile


def run(extracted: dict, profile: dict) -> str:
    required = extracted.get("required_skills", [])
    result = (PROMPT | get_llm() | StrOutputParser()).invoke({
        "job_title": extracted.get("job_title") or "the advertised role",
        "required_skills": ", ".join(required),
        "profile": json.dumps(profile, ensure_ascii=False, indent=2),
    }).strip()
    if not result:
        raise RuntimeError("The model returned an empty cover letter.")
    return result
