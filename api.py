
from pathlib import Path
from tempfile import TemporaryDirectory
from resume_improver import improve_resume_section
from resume_improver import detect_resume_sections

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from cover_letter_writer import run as generate_cover_letter
from cover_letter_writer import load_profile
from io import BytesIO
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from xml.sax.saxutils import escape

from skill_extractor import run as extract_skills
from resume_matcher import analyze_resume
from resume_parser import extract_resume_text
from keyword_analyzer import analyze_keyword_coverage
from cover_letter_writer import (
    load_profile,
    run as write_cover_letter,
)
from main import save_cover_letter

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:5174",
                "http://127.0.0.1:5174",
            ]
        }
    },
)

@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "message": "Job Agent API is running",
    })


@app.post("/api/analyze")
def analyze():
    resume_file = request.files.get("resume")
    job_description = request.form.get(
        "job_description", ""
    ).strip()

    if not resume_file or not resume_file.filename:
        return jsonify({
            "error": "Please upload a resume."
        }), 400

    if not job_description:
        return jsonify({
            "error": "Please provide a job description."
        }), 400

    filename = secure_filename(resume_file.filename)
    extension = Path(filename).suffix.lower()

    if extension not in {".pdf", ".docx"}:
        return jsonify({
            "error": "Only PDF and DOCX resumes are supported."
        }), 400

    try:
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            resume_path = temp_path / filename
            job_path = temp_path / "job_description.txt"

            resume_file.save(resume_path)
            job_path.write_text(
                job_description,
                encoding="utf-8",
            )

            # 1. Extract job title and required skills.
            job_data = extract_skills(str(job_path))
            required_skills = job_data["required_skills"]

            # 2. Match resume skills with job requirements.
            report = analyze_resume(
                resume_path,
                required_skills,
            )

            # 3. Read resume text for keyword analysis.
            resume_text = extract_resume_text(resume_path)

            keyword_report = analyze_keyword_coverage(
                job_description=job_description,
                resume_text=resume_text,
                required_skills=required_skills,
            )

            # Support the skill-list key used by the matcher.
            candidate_skills = report.get(
                "candidate_skills",
                report.get("resume_skills", []),
            )

            result = {
                "job_title": job_data["job_title"],
                "required_skills": required_skills,
                "candidate_skills": candidate_skills,
                "matched_skills": report.get(
                    "matched_skills", []
                ),
                "missing_skills": report.get(
                    "missing_skills", []
                ),
                "match_percentage": report.get(
                    "match_percentage", 0
                ),
                "suggestions": report.get(
                    "suggestions", []
                ),
                "ats_keyword_analysis": keyword_report,
                "note": (
                    "These are estimated matching metrics, "
                    "not an official ATS score."
                ),
            }

            return jsonify(result)

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Resume analysis failed")
        return jsonify({
            "error": (
                "Analysis failed. Check the backend terminal "
                "for details."
            )
        }), 500
    
@app.post("/api/cover-letter")
def create_cover_letter():
    job_description = request.form.get(
        "job_description", ""
    ).strip()

    if not job_description:
        return jsonify({
            "error": "Please provide a job description."
        }), 400

    try:
        with TemporaryDirectory() as temp_dir:
            job_path = Path(temp_dir) / "job_description.txt"
            job_path.write_text(
                job_description,
                encoding="utf-8",
            )

            # Extract job title and required skills.
            extracted = extract_skills(str(job_path))

            # Load the candidate's existing profile.
            profile = load_profile()

            # Generate a truthful, personalized cover letter.
            letter_text = generate_cover_letter(
                extracted,
                profile,
            )

            # Save as DOCX using the existing project function.
            # docx_path = save_cover_letter(
            #     letter_text,
            #     extracted.get("job_title") or "Job",
            # )
            
            return jsonify({
                "job_title": extracted.get("job_title") or "Job",
                "cover_letter": letter_text,
                "message": "Cover letter generated successfully."
            })

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Cover letter generation failed")
        return jsonify({
            "error": (
                "Cover letter generation failed. "
                "Check the backend terminal."
            )
        }), 500

@app.post("/api/improve-resume-section")
def improve_resume():
    data = request.get_json(silent=True) or {}

    section_name = data.get("section_name", "").strip()
    original_text = data.get("original_text", "").strip()
    job_description = data.get("job_description", "").strip()

    if not section_name:
        return jsonify({
            "error": "Please provide a resume section name."
        }), 400

    if not original_text:
        return jsonify({
            "error": "Please provide the original resume text."
        }), 400

    if not job_description:
        return jsonify({
            "error": "Please provide a job description."
        }), 400

    try:
        improved_text = improve_resume_section(
            section_name=section_name,
            original_text=original_text,
            job_description=job_description,
        )

        return jsonify({
            "section_name": section_name,
            "original_text": original_text,
            "improved_text": improved_text,
            "message": "Resume section improved successfully."
        })

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Resume section improvement failed")
        return jsonify({
            "error": (
                "Resume improvement failed. "
                "Check that Ollama is running and the model is available."
            )
        }), 500

    
@app.post("/api/detect-resume-sections")
def detect_resume_sections_api():
    resume_file = request.files.get("resume")
    job_description = request.form.get(
        "job_description", ""
    ).strip()

    if not resume_file or not resume_file.filename:
        return jsonify({
            "error": "Please upload your PDF or DOCX resume."
        }), 400

    if not job_description:
        return jsonify({
            "error": "Please provide the job description."
        }), 400

    filename = secure_filename(resume_file.filename)
    extension = Path(filename).suffix.lower()

    if extension not in {".pdf", ".docx"}:
        return jsonify({
            "error": "Only PDF and DOCX resumes are supported."
        }), 400

    try:
        with TemporaryDirectory() as temp_dir:
            resume_path = Path(temp_dir) / f"resume{extension}"
            resume_file.save(resume_path)

            resume_text = extract_resume_text(str(resume_path))

            if not resume_text.strip():
                return jsonify({
                    "error": "No readable text found in the resume."
                }), 400

            sections = detect_resume_sections(resume_text)

            if not sections:
                return jsonify({
                    "error": (
                        "No standard resume sections were detected. "
                        "Check that your resume contains readable text "
                        "and recognizable section headings."
                    )
                }), 422

            return jsonify({
                "sections": sections,
                "job_description_received": True,
                "confirmation_required": True,
                "message": (
                    "Your CV can be reviewed for improvements. "
                    "Please confirm before making any changes."
                ),
            })

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Resume section detection failed")
        return jsonify({
            "error": (
                "Resume section detection failed. "
                "Check the backend terminal."
            )
        }), 500

    
@app.post("/api/improve-entire-cv")
def improve_entire_cv():
    data = request.get_json(silent=True) or {}

    sections = data.get("sections", [])
    job_description = data.get("job_description", "").strip()

    if not isinstance(sections, list) or not sections:
        return jsonify({
            "error": "Please provide detected resume sections."
        }), 400

    if not job_description:
        return jsonify({
            "error": "Please provide a job description."
        }), 400

    # Keep the CV sections in the agreed order.
    section_order = {
        "Professional Summary": 1,
        "Work Experience": 2,
        "Projects": 3,
        "Technical Skills": 4,
        "Education": 5,
    }

    ordered_sections = sorted(
        sections,
        key=lambda section: section_order.get(
            section.get("section_name", ""), 99
        ),
    )

    improved_sections = []

    try:
        for section in ordered_sections:
            if not isinstance(section, dict):
                return jsonify({
                    "error": "Each resume section must be an object."
                }), 400

            section_name = section.get("section_name", "").strip()
            original_text = section.get("original_text", "").strip()

            if not section_name or not original_text:
                return jsonify({
                    "error": "A resume section is missing its name or text."
                }), 400

            improved_text = improve_resume_section(
                section_name=section_name,
                original_text=original_text,
                job_description=job_description,
            )

            improved_sections.append({
                "section_name": section_name,
                "original_text": original_text,
                "improved_text": improved_text,
            })

        return jsonify({
            "sections": improved_sections,
            "message": "Entire CV draft generated successfully.",
            "original_file_changed": False,
        })

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Entire CV improvement failed")
        return jsonify({
            "error": (
                "CV improvement failed. Check that Ollama is running "
                "and the model is available."
            )
        }), 500

    
def create_cv_document(sections):
    if not isinstance(sections, list) or not sections:
        raise ValueError("Please provide CV sections to export.")

    for section in sections:
        if (
            not isinstance(section, dict)
            or not isinstance(section.get("section_name"), str)
            or not isinstance(section.get("improved_text"), str)
            or not section["section_name"].strip()
            or not section["improved_text"].strip()
        ):
            raise ValueError("A CV section is missing its name or text.")

    return sections


@app.post("/api/export-cv/docx")
def export_cv_docx():
    data = request.get_json(silent=True) or {}

    try:
        sections = create_cv_document(data.get("sections"))
        document = Document()
        document.add_heading("Resume", level=0)

        for section in sections:
            document.add_heading(section["section_name"], level=1)
            for paragraph in section["improved_text"].splitlines():
                if paragraph.strip():
                    document.add_paragraph(paragraph)

        output = BytesIO()
        document.save(output)
        output.seek(0)

        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            as_attachment=True,
            download_name="improved_resume.docx",
        )

    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception:
        app.logger.exception("DOCX export failed")
        return jsonify({"error": "Could not export DOCX."}), 500


@app.post("/api/export-cv/pdf")
def export_cv_pdf():
    data = request.get_json(silent=True) or {}

    try:
        sections = create_cv_document(data.get("sections"))
        output = BytesIO()
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("Resume", styles["Title"]))
        story.append(Spacer(1, 12))

        for section in sections:
            story.append(
                Paragraph(escape(section["section_name"]), styles["Heading2"])
            )
            for paragraph in section["improved_text"].splitlines():
                if paragraph.strip():
                    story.append(
                        Paragraph(escape(paragraph), styles["BodyText"])
                    )
                    story.append(Spacer(1, 6))

        pdf = SimpleDocTemplate(output, pagesize=letter)
        pdf.build(story)
        output.seek(0)

        return send_file(
            output,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="improved_resume.pdf",
        )

    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception:
        app.logger.exception("PDF export failed")
        return jsonify({"error": "Could not export PDF."}), 500




if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True,
    )
    
