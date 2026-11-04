
import re


def normalize_text(text: str) -> str:
    """Convert text into a consistent searchable format."""
    text = text.casefold()
    text = re.sub(r"[^a-z0-9+#.]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


 

def contains_keyword(text: str, keyword: str) -> bool:
    """Check keywords, including common plural variations."""
    normalized_text = normalize_text(text)
    normalized_keyword = normalize_text(keyword)

    if not normalized_keyword:
        return False

    # Support common singular/plural variations.
    variations = {normalized_keyword}

    if normalized_keyword.endswith("s"):
        variations.add(normalized_keyword[:-1])
    else:
        variations.add(normalized_keyword + "s")

    for variation in variations:
        pattern = (
            r"(?<!\w)"
            + re.escape(variation)
            + r"(?!\w)"
        )

        if re.search(pattern, normalized_text):
            return True

    return False



def analyze_keyword_coverage(
    job_description: str,
    resume_text: str,
    required_skills: list[str] | None = None,
) -> dict:
    """Compare job keywords with the candidate's resume."""

    # Start with the skills extracted from the job posting.
    keywords = list(required_skills or [])

    # Common professional keywords worth checking.
    extra_keywords = [
        "API development",
        "backend development",
        "software development",
        "object-oriented programming",
        "problem solving",
        "teamwork",
        "debugging",
        "testing",
        "database",
        "version control",
        "communication",
    ]

    # Include additional keywords only when they occur in the job posting.
    for keyword in extra_keywords:
        if contains_keyword(job_description, keyword):
            keywords.append(keyword)

    # Remove duplicates without changing the original order.
    unique_keywords = []
    seen = set()

    for keyword in keywords:
        normalized = normalize_text(keyword)

        if normalized and normalized not in seen:
            seen.add(normalized)
            unique_keywords.append(keyword)

    matched = [
        keyword
        for keyword in unique_keywords
        if contains_keyword(resume_text, keyword)
    ]

    missing = [
        keyword
        for keyword in unique_keywords
        if not contains_keyword(resume_text, keyword)
    ]

    total = len(unique_keywords)
    coverage = round(len(matched) / total * 100, 2) if total else 0.0

    return {
        "total_keywords": total,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "keyword_coverage_percentage": coverage,
        "note": (
            "Keyword coverage is an estimate, not an official ATS score."
        ),
    }
