from pathlib import Path
from pypdf import PdfWriter
import pytest

from resume_parser import (
    extract_resume_text,
    extract_pdf_text,
    extract_docx_text,
    save_resume_text,
)
from docx import Document


def test_missing_resume_file():
    with pytest.raises(FileNotFoundError):
        extract_resume_text("missing_resume.pdf")


def test_unsupported_file_format(tmp_path):
    file_path = tmp_path / "resume.txt"
    file_path.write_text("Sample resume")

    with pytest.raises(ValueError):
        extract_resume_text(file_path)


def test_extract_docx_text(tmp_path):
    file_path = tmp_path / "resume.docx"

    document = Document()
    document.add_paragraph("Python Developer")
    table = document.add_table(rows=1, cols=1)
    table.cell(0, 0).text = "Python"
    document.save(file_path)

    text = extract_docx_text(file_path)

    assert "Python Developer" in text
    assert "Python" in text



def test_save_resume_text(tmp_path):
    output_path = tmp_path / "output" / "resume.txt"

    save_resume_text("Python Developer", output_path)

    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8") == "Python Developer"


def test_extract_pdf_text(tmp_path):
    pdf_path = tmp_path / "resume.pdf"

    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)

    with open(pdf_path, "wb") as file:
        writer.write(file)

    # Blank PDF should return an empty string
    text = extract_pdf_text(pdf_path)

    assert text == ""
