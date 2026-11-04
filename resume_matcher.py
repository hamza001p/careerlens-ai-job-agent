
from pathlib import Path
import json
import re

from resume_parser import extract_resume_text

ROOT = Path(__file__).resolve().parent
DEFAULT_RESUME = Path.home() / "Downloads" / "Hamza_Asif_Resume.pdf"
DEFAULT_PROFILE = ROOT / "data" / "my_skills.json"

KNOWN_SKILLS = [
    "JavaScript",
    "TypeScript",
    "React.js",
    "React",
    "Tailwind CSS",
    "HTML",
    "CSS",
    "REST APIs",
    "REST API",
    "Git",
    "GitHub",
    "Python",
    "Flask",
    "FastAPI",
    "NumPy",
    "Pandas",
    "Machine Learning",
    "Deep Learning",
    "SQL",
    "Node.js",
    "Express.js",
    "Axios",
    "PrimeReact",
    "Communication",
]


def normalize_skill(skill: str) -> str:
    """Normalize common skill-name variations."""
    skill = skill.strip().casefold()

    aliases = {
        "react": "react.js",
        "rest api": "rest apis",
        "restful api": "rest apis",
        "restful apis": "rest apis",
    }

    return aliases.get(skill, skill)


def unique_skills(skills) -> list[str]:
    """Remove duplicate skills while preserving order."""
    result = []
    seen = set()

    for skill in skills:
        if not isinstance(skill, str) or not skill.strip():
            continue

        normalized = normalize_skill(skill)

        if normalized not in seen:
            seen.add(normalized)
            result.append(skill.strip())

    return result


def extract_skills_from_text(resume_text: str) -> list[str]:
    """Detect skills explicitly mentioned in resume text."""
    found = []
    text = resume_text.casefold()

    for skill in KNOWN_SKILLS:
        pattern = (
            r"(?<!\w)"
            + re.escape(skill.casefold())
            + r"(?!\w)"
        )

        if re.search(pattern, text):
            found.append(skill)

    return unique_skills(found)


def match_skills(required_skills, candidate_skills) -> dict:
    """Compare required job skills against candidate skills."""
    required_skills = unique_skills(required_skills)
    candidate_skills = unique_skills(candidate_skills)

    candidate_map = {
        normalize_skill(skill)
        for skill in candidate_skills
    }

    matched = []
    missing = []

    for skill in required_skills:
        if normalize_skill(skill) in candidate_map:
            matched.append(skill)
        else:
            missing.append(skill)

    total = len(required_skills)
    percentage = (
        round(len(matched) / total * 100, 2)
        if total else 0.0
    )

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "match_percentage": percentage,
    }


def load_profile_skills(profile_path=DEFAULT_PROFILE) -> list[str]:
    """Load skills from the candidate profile JSON."""
    profile_path = Path(profile_path)

    if not profile_path.exists():
        return []

    with profile_path.open("r", encoding="utf-8") as file:
        profile = json.load(file)

    skills = profile.get("skills", [])

    # Also support a profile where skills are stored as a dictionary.
    if isinstance(skills, dict):
        skills = [
            key for key, value in skills.items()
            if value
        ]

    if not isinstance(skills, list):
        return []

    return unique_skills(skills)


def analyze_resume(
    resume_path,
    required_skills,
    profile_path=DEFAULT_PROFILE,
) -> dict:
    """Analyze resume evidence and compare it with the job."""
    resume_path = Path(resume_path)
    resume_text = extract_resume_text(resume_path)

    if not resume_text.strip():
        raise ValueError("No readable text found in the resume.")

    resume_skills = extract_skills_from_text(resume_text)
    profile_skills = load_profile_skills(profile_path)

    # Main job match is based on the actual resume only.
    resume_match = match_skills(required_skills, resume_skills)

    # Profile match is reported separately, not mixed into resume score.
    profile_match = match_skills(required_skills, profile_skills)

    # Skills listed in profile but not detected in resume.
    resume_skill_keys = {
        normalize_skill(skill) for skill in resume_skills
    }

    profile_skills_not_in_resume = [
        skill for skill in profile_skills
        if normalize_skill(skill) not in resume_skill_keys
    ]

    suggestions = []

    for skill in resume_match["missing_skills"]:
        if normalize_skill(skill) in {
            normalize_skill(item) for item in profile_skills
        }:
            suggestions.append(
                f"Your profile lists {skill}, but it was not detected "
                "in your resume. If accurate, add relevant evidence "
                "to your resume."
            )
        else:
            suggestions.append(
                f"Consider learning or demonstrating {skill} if it is "
                "relevant to your experience and career goals."
            )

    return {
        "resume_path": str(resume_path),
        "candidate_skills": resume_skills,
        "resume_skills": resume_skills,
        "profile_skills": profile_skills,
        "profile_skills_not_in_resume": profile_skills_not_in_resume,
        "matched_skills": resume_match["matched_skills"],
        "missing_skills": resume_match["missing_skills"],
        "match_percentage": resume_match["match_percentage"],
        "profile_matched_skills": profile_match["matched_skills"],
        "profile_missing_skills": profile_match["missing_skills"],
        "profile_match_percentage": profile_match["match_percentage"],
        "improvement_suggestions": suggestions,
    }


if __name__ == "__main__":
    required_skills = [
        "Python",
        "REST API",
        "Git",
        "SQL",
        "Communication",
    ]

    try:
        report = analyze_resume(
            DEFAULT_RESUME,
            required_skills,
        )

        print("\n--- RESUME MATCH REPORT ---")
        print("Resume skills:", ", ".join(report["resume_skills"]) or "None")
        print("Profile skills:", ", ".join(report["profile_skills"]) or "None")
        print("Matched:", ", ".join(report["matched_skills"]) or "None")
        print("Missing:", ", ".join(report["missing_skills"]) or "None")
        print("Resume match:", f"{report['match_percentage']}%")
        print(
            "Profile match:",
            f"{report['profile_match_percentage']}%",
        )

        print("\n--- PROFILE SKILLS NOT DETECTED IN RESUME ---")
        for skill in report["profile_skills_not_in_resume"]:
            print("-", skill)

        print("\n--- IMPROVEMENT SUGGESTIONS ---")
        for suggestion in report["improvement_suggestions"]:
            print("-", suggestion)

    except Exception as error:
        print(f"Error analyzing resume: {error}")
