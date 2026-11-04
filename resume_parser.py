
from pathlib import Path
from pypdf import PdfReader
from docx import Document


def extract_pdf_text(pdf_path):
    """Extract text from a PDF resume."""
    reader = PdfReader(str(pdf_path))
    text = ""

    for page in reader.pages:
        page_text = page.extract_text() or ""
        text += page_text + "\n"

    return text.strip()


def extract_docx_text(docx_path):
    """Extract text from a Word resume."""
    document = Document(str(docx_path))
    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    # Also extract text from tables, if present
    for table in document.tables:
        for row in table.rows:
            text += " | ".join(
                cell.text for cell in row.cells
            ) + "\n"

    return text.strip()


def extract_resume_text(file_path):
    """Choose the correct parser based on file extension."""
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Resume file not found: {file_path}"
        )

    extension = file_path.suffix.lower()

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    elif extension == ".docx":
        return extract_docx_text(file_path)

    else:
        raise ValueError(
            "Unsupported file format. Use PDF or DOCX."
        )


def save_resume_text(text, output_path):
    """Save extracted resume text to a TXT file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(text, encoding="utf-8")
    print(f"Resume text saved to: {output_path}")


if __name__ == "__main__":
    # Change this to the path of your actual resume
    resume_path = Path(
    r"C:\Users\Hi5\Downloads\Hamza_Asif_Resume.pdf"
)
    output_path = Path("output") / "extracted_resume.txt"

    try:
        resume_text = extract_resume_text(resume_path)

        if not resume_text:
            print(
                "No text found. The PDF may be scanned "
                "and require OCR."
            )
        else:
            save_resume_text(resume_text, output_path)
            print("\n--- Extracted Resume Text ---\n")
            print(resume_text)

    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
    except Exception as error:
        print(f"Could not read resume: {error}")
