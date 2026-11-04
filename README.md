# Job Agent — Repaired Starter

A small CLI starter that reads a job posting, extracts its title/required skills with a Groq-hosted LLM, and drafts a truthful cover letter from your candidate profile. This is not yet the full web application; see `IMPLEMENTATION_PLAN.md` for the upgrade roadmap.

## 1. Security first

The previously uploaded archive contained a `.env` with an API key. Revoke that key in the provider dashboard and create a new one. Never commit `.env` or share it in ZIP files. This repaired archive intentionally does not include a real key.

## 2. Setup on Windows PowerShell

```powershell
cd path	o\job-agent-repaired
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
Copy-Item data\my_skills.example.json data\my_skills.json
notepad data\my_skills.json
```

Paste your newly generated key into `.env` and edit the candidate profile with only truthful information. Do not upload your real profile to GitHub.

## 3. Run

```powershell
python main.py
```

Or provide a local text file / public job URL:

```powershell
python main.py data\sample_job.txt
python main.py "https://public-site.example/job-posting"
```

Use a public URL you trust. Some job sites block automated requests or require login; paste the job description into a `.txt` file if fetching is not supported.

## 4. Tests

```powershell
pip install pytest
pytest -q
```

## Notes

- The app requires a valid Groq API key for LLM calls.
- URL safety checks are best-effort and are not a hardened production crawler. For deployment, use outbound network restrictions and a dedicated safe-fetch service.
- The starter outputs a cover letter in the terminal. DOCX/PDF export, resume parsing, job matching, ATS suggestions, database tracking and the React UI are planned in `IMPLEMENTATION_PLAN.md`.
