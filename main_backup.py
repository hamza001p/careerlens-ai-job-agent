
"""CLI entry point for the Job Agent."""
import argparse
import re
from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt

from cover_letter_writer import load_profile, run as write_cover_letter
from skill_extractor import run as extract_skills

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"


def save_cover_letter(text: str, job_title: str) -> Path:
    """Save the generated cover letter as a Word document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    safe_title = re.sub(r'[<>:"/\\|?*]', "", job_title)
    safe_title = re.sub(r"\s+", "_", safe_title.strip())
    file_path = OUTPUT_DIR / f"{safe_title or 'Cover_Letter'}_Cover_Letter.docx"

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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract job skills and generate a cover letter."
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
    args = parser.parse_args()

    try:
        print("[1/3] Reading job posting and extracting skills...")
        extracted = extract_skills(args.source)

        job_title = extracted.get("job_title") or "Cover Letter"
        print(f"\nJob title: {job_title}")
        print(
            "Required skills:",
            ", ".join(extracted.get("required_skills", [])) or "None extracted",
        )

        print("\n[2/3] Loading candidate profile...")
        profile = load_profile(args.profile)

        print("[3/3] Generating cover letter...\n")
        cover_letter = write_cover_letter(extracted, profile)
        print(cover_letter)

        file_path = save_cover_letter(cover_letter, job_title)
        print(f"\nWord document saved successfully:\n{file_path}")

        return 0

    except Exception as exc:
        print(f"\nERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
