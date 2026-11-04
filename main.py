
"""CLI entry point for the Resume Matcher and Job Agent."""

import argparse
import json
import re
from pathlib import Path
from resume_matcher import analyze_resume
from keyword_analyzer import analyze_keyword_coverage
from resume_parser import extract_resume_text

from docx import Document
from docx.shared import Inches, Pt

from cover_letter_writer import (
    load_profile,
    run as write_cover_letter,
)
from skill_extractor import run as extract_skills
from resume_matcher import analyze_resume


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"

DEFAULT_RESUME = (
    Path.home() / "Downloads" / "Hamza_Asif_Resume.pdf"
)


def safe_filename(value: str) -> str:
    """Convert a title into a safe filename."""
    value = re.sub(r'[<>:"/\\|?*]', "", value)
    value = re.sub(r"\s+", "_", value.strip())
    return value or "Job"


def save_cover_letter(text: str, job_title: str) -> Path:
    """Save the generated cover letter as a Word document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    filename = (
        f"{safe_filename(job_title)}_Cover_Letter.docx"
    )
    file_path = OUTPUT_DIR / filename

    document = Document()
    section = document.sections[0]
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)

    normal = document.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(11)

    document.add_heading("Cover Letter", level=1)

    for paragraph in text.splitlines():
        paragraph = paragraph.strip()
        if paragraph:
            document.add_paragraph(paragraph)

    document.save(file_path)
    return file_path


def save_match_reports(
    report: dict,
    job_title: str,
) -> tuple[Path, Path]:
    """Save the resume matching report in TXT and JSON formats."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    filename = (
        f"{safe_filename(job_title)}_Resume_Match_Report"
    )

    json_path = OUTPUT_DIR / f"{filename}.json"
    txt_path = OUTPUT_DIR / f"{filename}.txt"

    # Save structured JSON report.
    json_path.write_text(
        json.dumps(report, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

    # Build a readable text report.
    matched = report.get("matched_skills", [])
    missing = report.get("missing_skills", [])
    candidate = report.get("candidate_skills", [])
    required = report.get("required_skills", [])
    percentage = report.get("match_percentage", 0.0)

    lines = [
        "RESUME-TO-JOB SKILLS MATCH REPORT",
        "=" * 38,
        f"Job title: {report.get('job_title', job_title)}",
        f"Resume: {report.get('resume_path', 'Not specified')}",
        "",
        f"Skills match: {percentage}%",
        f"Matched skills: {len(matched)}",
        f"Missing skills: {len(missing)}",
        f"Total required skills: {len(required)}",
        "",
        "CANDIDATE SKILLS",
        "-" * 20,
        ", ".join(candidate) or "None detected",
        "",
        "MATCHED SKILLS",
        "-" * 20,
        ", ".join(matched) or "None",
        "",
        "MISSING FROM RESUME",
        "-" * 20,
        ", ".join(missing) or "None",
        "",
        "Note: This is a skills-match estimate, not an official ATS score.",
        "A missing skill means it was not detected in the resume.",
    ]

    txt_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    return txt_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze a resume against a job posting "
            "and generate a cover letter."
        )
    )

    parser.add_argument(
        "source",
        nargs="?",
        default=str(ROOT / "data" / "sample_job.txt"),
        help="Local .txt job posting or public URL",
    )

    parser.add_argument(
        "--profile",
        default=str(ROOT / "data" / "my_skills.json"),
        help="Candidate profile JSON file",
    )

    parser.add_argument(
        "--resume",
        default=str(DEFAULT_RESUME),
        help="Path to the candidate's PDF or DOCX resume",
    )

    args = parser.parse_args()

    try:
        # Step 1: Extract the job title and required skills.
        print("\n[1/5] Reading job posting and extracting skills...")

        extracted = extract_skills(args.source)

        job_title = (
            extracted.get("job_title") or "Job"
        )

        required_skills = extracted.get(
            "required_skills", []
        )

        print(f"\nJob title: {job_title}")
        print(
            "Required skills:",
            ", ".join(required_skills) or "None extracted",
        )

        if not required_skills:
            print(
                "\nWARNING: No required skills were extracted. "
                "The match percentage will be 0%."
            )

        # Step 2: Analyze the actual resume.
        print("\n[2/5] Reading resume and matching skills...")

        resume_path = Path(args.resume).expanduser().resolve()

        report = analyze_resume(
            resume_path,
            required_skills,
        )
        
        # Step 2B: Analyze job keywords against the resume text.
        print("\n[ATS] Analyzing resume keyword coverage...")

        job_description = extracted.get("job_description", "")

        # Read the original posting text using the existing scanner.
        from tools.job_scanner import read_job_posting
        job_description = read_job_posting.invoke(
            {"source": args.source}
        )

        resume_text = extract_resume_text(resume_path)

        keyword_report = analyze_keyword_coverage(
            job_description=job_description,
            resume_text=resume_text,
            required_skills=required_skills,
        )

        report["ats_keyword_analysis"] = keyword_report

        print(
            "Keyword coverage:",
            f"{keyword_report['keyword_coverage_percentage']}%",
        )
        print(
            "Matched keywords:",
            ", ".join(keyword_report["matched_keywords"]) or "None",
        )
        print(
            "Missing keywords:",
            ", ".join(keyword_report["missing_keywords"]) or "None",
        )


        # Add job and resume information to the report.
        report["job_title"] = job_title
        report["required_skills"] = required_skills
        report["resume_path"] = str(resume_path)
        report["report_type"] = "skills_match_estimate"

        print(
            "\nCandidate skills:",
            ", ".join(report["candidate_skills"]) or "None detected",
        )

        print(
            "Matched skills:",
            ", ".join(report["matched_skills"]) or "None",
        )

        print(
            "Missing skills:",
            ", ".join(report["missing_skills"]) or "None",
        )

        print(
            f"Skills match: {report['match_percentage']}%"
        )

        # Step 3: Save both report formats.
        print("\n[3/5] Saving TXT and JSON reports...")

        txt_path, json_path = save_match_reports(
            report,
            job_title,
        )

        print(f"TXT report saved: {txt_path}")
        print(f"JSON report saved: {json_path}")

        # Step 4: Load the existing candidate profile.
        print("\n[4/5] Loading candidate profile...")

        profile = load_profile(args.profile)

        # Step 5: Generate and save the cover letter.
        print("\n[5/5] Generating AI cover letter...")

        cover_letter = write_cover_letter(
            extracted,
            profile,
        )

        print("\n--- Generated Cover Letter ---\n")
        print(cover_letter)

        cover_letter_path = save_cover_letter(
            cover_letter,
            job_title,
        )

        print("\n--- All outputs saved successfully ---")
        print(f"TXT report:       {txt_path}")
        print(f"JSON report:      {json_path}")
        print(f"Cover letter:     {cover_letter_path}")

        return 0

    except Exception as exc:
        print(f"\nERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
