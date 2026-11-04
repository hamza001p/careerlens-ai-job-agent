# CareerLens AI 🚀

**AI-Powered Resume Analysis, Job Matching & Resume Improvement**

CareerLens AI is an AI-powered career assistance tool that helps job seekers analyze their resumes against job descriptions, identify missing skills, review ATS-related keywords, generate tailored cover letters, and improve their CVs using AI.

Built with React, Flask, and a locally running Ollama language model, CareerLens AI combines resume analysis with an interactive CV improvement workflow.

## ✨ Features

### 📄 Resume Analysis
- Upload resumes in PDF or DOCX format.
- Analyze your resume against a job description.
- Identify candidate skills and required job skills.
- View matched skills, missing skills, and a match percentage.
- Get suggestions for improving your job application.

### 🎯 ATS Keyword Analysis
- Identify relevant keywords from a job description.
- Review keywords found in your resume.
- Discover potentially missing keywords.
- Use the results to improve resume relevance.

*Note: The match percentage and keyword analysis are informational estimates, not an official ATS score or a guarantee of selection.*

### ✍️ AI Cover Letter Generator
- Generate a cover letter tailored to the job description.
- Preview the generated content before downloading.
- Download the cover letter when you're satisfied with it.

### 🪄 AI Resume Improver
Improve your existing CV with AI while keeping the original document unchanged.

- Detect resume sections and potential improvement opportunities.
- Review the improvement report before proceeding.
- Choose between **Improve Entire CV** and **Improve Step by Step**.
- Review and edit AI-generated suggestions.
- Revert an improved section to its original content.
- Export the complete CV as PDF or DOCX.
- Preserve unchanged sections when improving only selected sections.

### 🤖 Local AI Integration
- Uses Ollama to run the Qwen2.5 3B language model locally.
- Supports AI-powered resume improvement and text generation.
- Avoids requiring a paid hosted LLM API for the local model workflow.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| React | Frontend interface |
| Tailwind CSS | UI styling |
| Axios | Frontend-to-backend HTTP requests |
| Python | Backend development |
| Flask | REST API |
| Ollama | Local language model runtime |
| Qwen2.5:3b | Local AI model |
| PDF/DOCX processing libraries | Resume reading and document generation |

## 🏗️ Project Architecture

CareerLens AI uses a frontend/backend architecture.

```text
CareerLens-AI/
├── frontend/
│   └── src/
│       └── App.jsx
├── api.py
├── main.py
├── resume_parser.py
├── resume_matcher.py
├── skill_extractor.py
├── keyword_analyzer.py
├── cover_letter_writer.py
├── resume_improver.py
├── data/
├── output/
├── tests/
├── .venv/
└── README.md
```

*The structure above highlights the main files and folders; your local project may contain additional files.*

## ⚙️ Installation & Setup

### Prerequisites

Install the following before running the application:

- Python 3.13
- Node.js and npm
- Ollama
- Git

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd job-agent-repaired
```

Replace the placeholder with your actual GitHub repository URL.

### 2. Set up the Python backend

Open PowerShell in the project root:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the backend dependencies using your project's dependency file:

```powershell
pip install -r requirements.txt
```

If your project does not contain `requirements.txt`, install the dependencies listed in your existing project configuration instead.

### 3. Set up Ollama

Install Ollama, then download the model:

```powershell
ollama pull qwen2.5:3b
```

Verify that the model is available:

```powershell
ollama list
```

Make sure the Ollama service is running before using AI-powered features.

### 4. Start the Flask backend

From the project root, activate the virtual environment and run the backend using your existing entry point:

```powershell
python api.py
```

If your application is configured to start through `main.py` instead, use the entry point already configured in your project.

The backend API is expected to run at:

```text
http://127.0.0.1:5001
```

Health check:

```text
http://127.0.0.1:5001/api/health
```

### 5. Start the React frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite in your terminal.

## 🚀 How to Use

1. Start Ollama, the Flask backend, and the React frontend.
2. Upload your resume in PDF or DOCX format.
3. Enter or provide the relevant job description.
4. Review the resume analysis and skill-matching results.
5. Examine the ATS keyword analysis.
6. Generate and preview a tailored cover letter.
7. Open Resume Improver to review detected sections and improvement opportunities.
8. Choose **Improve Entire CV** or **Improve Step by Step**.
9. Review, edit, or revert suggested changes.
10. Export the complete resume as PDF or DOCX.

## 🧪 Testing

Run the project's tests from the root directory with the virtual environment activated:

```powershell
python -m pytest
```

Confirm that resume analysis, skill matching, ATS keyword analysis, cover letter generation, section improvement, and both export formats work correctly.

## 🔒 Privacy & Limitations

- The AI workflow uses a locally running Ollama model for supported generation tasks.
- Do not upload confidential documents to environments you do not trust.
- Resume match percentages are estimates and do not guarantee interviews or job offers.
- Always review AI-generated content before submitting a job application.
- Verify that all resume details remain accurate; AI suggestions should never invent qualifications or experience.

## 🖼️ Screenshots

Add screenshots of your actual application here to showcase its interface.

Suggested screenshots:
- Resume Analysis Dashboard
- Skills Matching & ATS Keyword Analysis
- Cover Letter Preview
- Resume Improver Modes
- Improved CV Preview and PDF/DOCX Export

## 🔮 Future Improvements

Potential future enhancements include:
- More detailed resume feedback and reporting.
- Additional resume templates.
- Improved validation and error handling.
- Deployment and production configuration.

## 👨‍💻 Author

**Hamza Asif**

GitHub: [@hamza001p](https://github.com/hamza001p)

## 📄 License

Add a license file to the repository if you intend to distribute the project under an open-source license.

---

**CareerLens AI — Analyze your resume. Identify skill gaps. Improve your CV. Apply with confidence.**
