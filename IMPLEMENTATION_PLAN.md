# AI Job Application Assistant — Implementation Plan

## 0. Stabilize the starter (done in this repaired baseline)
- Add a real `main.py` entry point and sample job description.
- Put `job_scanner.py` inside the `tools` package to match imports.
- Add an example candidate profile and clear missing-profile errors.
- Resolve paths from the project root rather than the current shell directory.
- Add `.env.example` and `.gitignore`; never commit `.env` or real API keys.
- Parse HTML with a parser, impose time/size limits, disable redirects, and reject local/private URL targets (best-effort URL safety; not a substitute for a hardened fetch service).
- Read the posting before LLM extraction rather than relying on the model to decide whether to call the tool.

## Target architecture

```text
React + Tailwind UI
        | HTTPS / JSON
FastAPI routes + validation + authentication
        |
Application services (use cases)
  | Resume service | Job service | Matching service | Document service | Tracker service
        |
Domain models (Pydantic) + repositories (SQLAlchemy)
        |
PostgreSQL in production / SQLite for local development
        |
LLM provider adapter (Groq first; swappable providers)
```

Keep LLM calls behind service functions. Do not let route handlers contain prompt logic or database queries directly. Treat resumes and job descriptions as untrusted input, and never let instructions embedded in documents override system prompts.

## Recommended final folder structure

```text
job-agent/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app and lifespan
│   │   ├── core/                   # settings, logging, security
│   │   ├── api/v1/routes/           # resumes, jobs, applications, documents
│   │   ├── schemas/                 # request/response Pydantic models
│   │   ├── models/                  # SQLAlchemy tables
│   │   ├── repositories/            # database access
│   │   ├── services/                # resume, jobs, match, ATS, letters, tracker
│   │   ├── llm/                     # provider adapter, prompts, output schemas
│   │   ├── document/                # DOCX/PDF renderers and templates
│   │   └── utils/                   # validation, safe filenames
│   ├── tests/                       # unit, API, security, integration
│   ├── migrations/                  # Alembic
│   ├── data/                        # example profile only; no private resumes
│   ├── .env.example
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── src/components/
│   ├── src/pages/                   # Dashboard, Resume, Jobs, Applications
│   ├── src/api/                     # typed API client
│   ├── src/hooks/
│   └── src/lib/
├── docs/                            # architecture, API, threat model
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Feature implementation order

### Phase 1 — Resume upload and parsing
- Accept only PDF and DOCX initially; limit file size (e.g. 5 MB) and validate actual file signatures, not just extensions.
- Extract text with PyMuPDF for PDF and python-docx for DOCX. Detect empty/scanned PDFs and return a clear message; OCR can be a later opt-in feature.
- Normalize into a Pydantic `CandidateProfile`: name/contact (optional), summary, skills, education, experience, projects, certifications.
- Keep original file private; do not log resume contents. Add deletion controls and retention policy.

### Phase 2 — Job ingestion
- Accept pasted description and user-supplied public URL; make fetching a separate hardened service with DNS/IP validation, redirect re-validation, allowlists/rate limits where appropriate, and outbound network restrictions.
- Extract job title, company, location, must-have skills, nice-to-have skills, experience and education requirements into a validated schema.
- Save source URL and retrieval timestamp. Do not crawl sites that prohibit it.

### Phase 3 — Evidence-based job matching
- Normalize skill synonyms (e.g. JS/JavaScript) and distinguish must-have vs nice-to-have.
- Combine deterministic weighted skill overlap with optional embedding similarity. Use the LLM to explain evidence, not to invent a score.
- Return score, matched skills, missing skills, evidence excerpts from resume, and uncertainty. Show formula and weights in UI; don't present score as a hiring prediction.

### Phase 4 — ATS optimization
- Compare resume terms with the job description; suggest truthful keyword placements and clearer bullets.
- Preserve the user's original claims and dates. Each proposed bullet must map to source evidence or require explicit user confirmation.
- Show a before/after diff and require user approval before replacing content. Avoid claiming to reproduce any proprietary ATS score.

### Phase 5 — Cover letter generation
- Use validated job and candidate schemas, configurable tone/length, and an evidence-only prompt.
- Add output checks: name, word/line limits, no placeholders, no unsupported employers/skills/metrics. Retry once or return a validation error.
- Store versions so the user can edit and compare drafts.

### Phase 6 — DOCX and PDF export
- Render editable DOCX with `python-docx` using a consistent template and safe filename.
- Produce PDF with ReportLab from the same structured content, or convert DOCX using a managed LibreOffice worker if exact visual parity is needed. Do not assume Word is installed on the server.
- Write files only into a dedicated output directory, generate random names, prevent path traversal, and return authenticated download endpoints. Clean temporary files on a schedule.
- Test special characters, long content, page breaks and fonts in both formats.

### Phase 7 — Application tracker
- Tables: users, resumes, jobs, match_reports, cover_letters, applications, document_exports.
- Track status (saved, planned, applied, assessment, interview, offer, rejected, withdrawn), dates, notes and source URL.
- Add CRUD APIs, pagination, filters and database migrations. Add authentication/authorization before multi-user deployment.

### Phase 8 — React dashboard and deployment
- Pages: Dashboard, Resume Library, Job Analyzer, Match Results, Cover Letter Editor, Application Tracker, Settings.
- Use React + Tailwind, loading/error/empty states, schema validation and API client.
- Add pytest unit/API tests, prompt regression tests, upload-security tests, rate limits, structured logs without personal content, Docker and deployment docs.

## Suggested API endpoints

- `POST /api/v1/resumes` — upload and parse resume
- `GET /api/v1/resumes` / `DELETE /api/v1/resumes/{id}` — manage resume records
- `POST /api/v1/jobs/analyze` — analyze pasted text or safe public URL
- `POST /api/v1/matches` — match a resume to a job and return evidence
- `POST /api/v1/resumes/{id}/optimize` — produce suggestions and diff
- `POST /api/v1/cover-letters` — create a draft
- `GET /api/v1/cover-letters/{id}/export?format=docx|pdf` — authenticated export
- `GET/POST/PATCH/DELETE /api/v1/applications` — application tracker CRUD

## Quality gates before calling it production-ready

- Unit tests for parsers, score calculation, validators and renderers.
- API tests for bad file types, oversized uploads, malformed URLs, auth failures and missing records.
- Prompt tests that check the model never fabricates resume claims.
- Secrets scan and `.env` exclusion from Git.
- Privacy: authentication, per-user access checks, retention/deletion, HTTPS, minimal logging.
- Observability: latency, token usage, provider errors and request IDs; never log raw resumes or API keys.
- Human approval before final resume replacement or any job application submission.
