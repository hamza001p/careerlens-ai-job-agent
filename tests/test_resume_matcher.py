
from resume_matcher import match_skills


def test_rest_api_variations():
    result = match_skills(
        ["REST API"],
        ["REST APIs"],
    )
    assert result["match_percentage"] == 100.0


def test_react_variations():
    result = match_skills(
        ["React"],
        ["React.js"],
    )
    assert result["match_percentage"] == 100.0


def test_missing_skills():
    result = match_skills(
        ["Python", "SQL"],
        ["Python"],
    )
    assert result["matched_skills"] == ["Python"]
    assert result["missing_skills"] == ["SQL"]
    assert result["match_percentage"] == 50.0


def test_empty_requirements():
    result = match_skills([], ["Python"])
    assert result["match_percentage"] == 0.0
