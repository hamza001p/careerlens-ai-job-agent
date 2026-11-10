
import { useState } from 'react'
import axios from 'axios'
import {
  FileText,
  LayoutDashboard,
  ChartNoAxesCombined,
  Settings,
  UploadCloud,
  BriefcaseBusiness,
  Sparkles,
  ArrowUpRight,
  FileCheck2,
  Menu,
  X,
} from 'lucide-react'
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5001";

const features = [
  {
    icon: FileCheck2,
    title: 'Skills matching',
    description: 'Compare your resume skills with job requirements.',
  },
  {
    icon: ChartNoAxesCombined,
    title: 'Keyword analysis',
    description: 'Find relevant keywords and identify missing terms.',
  },
  {
    icon: Sparkles,
    title: 'AI cover letter',
    description: 'Generate a tailored cover letter for your application.',
  },
  
    {
  icon: Sparkles,
  title: 'AI Resume Improver',
  description: 'Improve your resume with AI-powered suggestions and export your optimized CV as PDF or DOCX.',
}
  
]

export default function App() {
  const [resume, setResume] = useState(null)
  const [letterLoading, setLetterLoading] = useState(false)
  const [coverLetter, setCoverLetter] = useState('')
const [coverLetterJobTitle, setCoverLetterJobTitle] = useState('Job')
  const [jobDescription, setJobDescription] = useState('')
  const [menuOpen, setMenuOpen] = useState(false)
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  
const [detectedSections, setDetectedSections] = useState([])
const [detectionLoading, setDetectionLoading] = useState(false)
const [detectionMessage, setDetectionMessage] = useState('')
const [showConfirmation, setShowConfirmation] = useState(false)
const [improvementConfirmed, setImprovementConfirmed] = useState(false)
const [improvementMode, setImprovementMode] = useState('')

const [result, setResult] = useState(null)
const [sectionName, setSectionName] = useState('Professional Summary')
const [originalSection, setOriginalSection] = useState('')
const [improvedSection, setImprovedSection] = useState('')
const [improveLoading, setImproveLoading] = useState(false)
const [improveMessage, setImproveMessage] = useState('')
const [improvedSections, setImprovedSections] = useState([])
const [entireCvLoading, setEntireCvLoading] = useState(false)
const [currentSectionIndex, setCurrentSectionIndex] = useState(0)

  function handleResumeChange(event) {
    const file = event.target.files?.[0]

    if (!file) return

    const allowed = /\.(pdf|docx)$/i.test(file.name)

    if (!allowed) {
      setResume(null)
      setMessage('Please upload a PDF or DOCX resume.')
      return
    }

    setResume(file)
    setMessage('')
  }

 

    

async function handleAnalyze() {
  if (!resume) {
    setMessage('Please upload your resume first.')
    return
  }

  if (!jobDescription.trim()) {
    setMessage('Please paste the job description first.')
    return
  }

  const formData = new FormData()
  formData.append('resume', resume)
  formData.append('job_description', jobDescription)

  setLoading(true)
  setMessage('')
  setResult(null)

  try {
    const response = await axios.post(
     `${API_BASE_URL}/api/analyze`,
      formData,
    )

    setResult(response.data)
    setMessage('Resume analysis completed successfully!')
  } catch (error) {
    const errorMessage =
      error.response?.data?.error ||
      'Could not connect to the backend. Check whether Flask is running.'

    setMessage(errorMessage)
  } finally {
    setLoading(false)
  }
}


async function handleDetectResume() {
  if (!resume) {
    setDetectionMessage('Please upload your resume first.')
    return
  }

  if (!jobDescription.trim()) {
    setDetectionMessage('Please paste the job description first.')
    return
  }

  const formData = new FormData()
  formData.append('resume', resume)
  formData.append('job_description', jobDescription)

  setDetectionLoading(true)
  setDetectionMessage('')
  setDetectedSections([])
  setShowConfirmation(false)
  setImprovementConfirmed(false)
  setImprovementMode('')

  try {
    const response = await axios.post(
     	`${API_BASE_URL}/api/detect-resume-sections`,
      formData,
    )

    setDetectedSections(response.data.sections || [])
    setDetectionMessage(response.data.message)
    setShowConfirmation(true)
    setImprovementConfirmed(false)
    setImprovementMode('')
  } catch (error) {
    setDetectionMessage(
      error.response?.data?.error ||
        'Could not detect resume sections. Check whether Flask is running.',
    )
  } finally {
    setDetectionLoading(false)
  }
}


async function handleImproveEntireCV() {
  if (!improvementConfirmed) {
    setDetectionMessage('Please confirm CV improvement first.')
    return
  }

  if (!detectedSections.length || !jobDescription.trim()) {
    setDetectionMessage('Please detect your CV sections first.')
    return
  }

  setEntireCvLoading(true)
  setDetectionMessage('')
  setImprovedSections([])

  try {
    const response = await axios.post(
     `${API_BASE_URL}/api/improve-entire-cv`,
      {
        sections: detectedSections,
        job_description: jobDescription,
      },
    )

    setImprovedSections(response.data.sections || [])
    setCurrentSectionIndex(0)
    setDetectionMessage(response.data.message)
  } catch (error) {
    setDetectionMessage(
      error.response?.data?.error ||
        'Could not improve the CV. Check Flask and Ollama.',
    )
  } finally {
    setEntireCvLoading(false)
  }
}


async function handleImproveCurrentSection() {
  if (!improvementConfirmed) {
    setDetectionMessage('Please confirm CV improvement first.')
    return
  }

  if (!detectedSections.length || !jobDescription.trim()) {
    setDetectionMessage('Please detect your CV sections first.')
    return
  }

  const currentSection = detectedSections[currentSectionIndex]

  if (!currentSection) {
    setDetectionMessage('No more sections to improve.')
    return
  }

  setEntireCvLoading(true)
  setDetectionMessage('')

  try {
    const response = await axios.post(
     `${API_BASE_URL}/api/improve-resume-section`,
      {
        section_name: currentSection.section_name,
        original_text: currentSection.original_text,
        job_description: jobDescription,
      },
    )

    const improvedSection = {
      section_name: response.data.section_name,
      original_text: response.data.original_text,
      improved_text: response.data.improved_text,
    }

    setImprovedSections((previous) => {
  const updated = [...previous]

  const existingIndex = updated.findIndex(
    (section) =>
      section?.section_name === improvedSection.section_name,
  )

  if (existingIndex !== -1) {
    updated[existingIndex] = improvedSection
  } else {
    updated.push(improvedSection)
  }

  return updated
})

    setDetectionMessage(
      `${currentSection.section_name} improved successfully!`,
    )
  } catch (error) {
    setDetectionMessage(
      error.response?.data?.error ||
        'Could not improve this section. Check Flask and Ollama.',
    )
  } finally {
    setEntireCvLoading(false)
  }
}



async function handleExportCV(format) {
  if (!improvedSections.length) {
    setDetectionMessage('Generate your improved CV draft first.')
    return
  }

  try {
    // Original CV ke tamam sections se export draft banao.
    const exportSections = detectedSections.map((originalSection) => {
      const improvedSection = improvedSections.find(
        (section) =>
          section.section_name === originalSection.section_name,
      )

      return {
        section_name: originalSection.section_name,
        original_text: originalSection.original_text ?? '',
        improved_text: improvedSection
          ? improvedSection.improved_text
          : originalSection.original_text ?? '',
      }
    })

    const response = await axios.post(
     `${API_BASE_URL}/api/export-cv/${format}`,
      { sections: exportSections },
      { responseType: 'blob' },
    )

    const mimeType =
      format === 'pdf'
        ? 'application/pdf'
        : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

    const blob = new Blob([response.data], { type: mimeType })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')

    link.href = url
    link.download = `improved_resume.${format}`
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch {
    setDetectionMessage(
      `Could not export ${format.toUpperCase()}. Please try again.`,
    )
  }
}





async function handleCoverLetter() {
  if (!jobDescription.trim()) {
    setMessage('Please paste the job description first.')
    return
  }

  setLetterLoading(true)
  setMessage('')
  setCoverLetter('')

  try {
    const formData = new FormData()
    formData.append('job_description', jobDescription)

    const response = await axios.post(
     	`${API_BASE_URL}/api/cover-letter`,
      formData,
    )

    setCoverLetter(response.data.cover_letter)
    setCoverLetterJobTitle(response.data.job_title || 'Job')
    setMessage('Cover letter generated. Review it below.')
  } catch (error) {
    setMessage(
      error.response?.data?.error ||
      'Cover letter generation failed. Check whether Flask is running.'
    )
  } finally {
    setLetterLoading(false)
  }
}


async function handleImproveSection() {
  if (!originalSection.trim()) {
    setImproveMessage('Please enter your original resume section.')
    return
  }

  if (!jobDescription.trim()) {
    setImproveMessage('Please enter a job description above first.')
    return
  }

  setImproveLoading(true)
  setImproveMessage('')
  setImprovedSection('')

  try {
    const response = await axios.post(
     	`${API_BASE_URL}/api/improve-resume-section`,
      {
        section_name: sectionName,
        original_text: originalSection,
        job_description: jobDescription,
      }
    )

    setImprovedSection(response.data.improved_text)
    setImproveMessage('Section improved. Review it before using it.')
  } catch (error) {
    setImproveMessage(
      error.response?.data?.error ||
      'Could not improve the section. Check the backend and Ollama.'
    )
  } finally {
    setImproveLoading(false)
  }
}


async function handleDownloadCoverLetter() {
  if (!coverLetter) return

  try {
    const response = await axios.post(
      	`${API_BASE_URL}/api/cover-letter/download`,
      {
        cover_letter: coverLetter,
        job_title: coverLetterJobTitle,
      },
      { responseType: 'blob' },
    )

    const url = window.URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = url
    link.download = 'Cover_Letter.docx'
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch {
    setMessage('Could not download the cover letter.')
  }
}

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      {menuOpen && (
        <button
          aria-label="Close navigation overlay"
          onClick={() => setMenuOpen(false)}
          className="fixed inset-0 z-40 bg-slate-950/30 lg:hidden"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-slate-200 bg-white p-5 transition-transform lg:translate-x-0 ${
          menuOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="mb-10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-blue-600 text-white">
              <FileCheck2 size={23} />
            </div>
            <div>
              <h1 className="font-bold tracking-tight text-slate-900">
                CareerLens AI
              </h1>
              <p className="text-xs text-slate-500">Resume intelligence</p>
            </div>
          </div>

          <button
            onClick={() => setMenuOpen(false)}
            className="rounded-lg p-2 hover:bg-slate-100 lg:hidden"
            aria-label="Close menu"
          >
            <X size={20} />
          </button>
        </div>

        <p className="mb-3 px-3 text-xs font-semibold uppercase tracking-widest text-slate-400">
          Workspace
        </p>

        <nav className="space-y-2">
          <a
            href="#dashboard"
            className="flex items-center gap-3 rounded-xl bg-blue-50 px-3 py-3 font-medium text-blue-700"
          >
            <LayoutDashboard size={19} />
            Dashboard
          </a>
          <a
            href="#analyzer"
            className="flex items-center gap-3 rounded-xl px-3 py-3 text-slate-600 transition hover:bg-slate-100"
          >
            <FileText size={19} />
            Resume Analyzer
          </a>
          <a
            href="#features"
            className="flex items-center gap-3 rounded-xl px-3 py-3 text-slate-600 transition hover:bg-slate-100"
          >
            <ChartNoAxesCombined size={19} />
            Features
          </a>
        </nav>

        <div className="mt-auto rounded-2xl bg-slate-900 p-4 text-white">
          <Sparkles size={22} className="mb-3 text-blue-300" />
          <h3 className="font-semibold">Your next opportunity</h3>
          <p className="mt-2 text-sm leading-6 text-slate-300">
            Understand your resume before you apply.
          </p>
          <a
            href="#analyzer"
            className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-blue-300"
          >
            Start analysis <ArrowUpRight size={16} />
          </a>
        </div>

        <div className="mt-5 flex items-center gap-3 border-t border-slate-200 pt-5">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 font-bold text-blue-700">
            U
          </div>
          <div>
            <p className="text-sm font-semibold">Your workspace</p>
            <p className="text-xs text-slate-500">Resume analysis</p>
          </div>
          <Settings size={18} className="ml-auto text-slate-400" />
        </div>
      </aside>

      <div className="min-w-0 lg:pl-64">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white/90 px-5 backdrop-blur md:px-8">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMenuOpen(true)}
              aria-label="Open navigation"
              className="rounded-lg p-2 hover:bg-slate-100 lg:hidden"
            >
              <Menu size={21} />
            </button>
            <span className="text-sm text-slate-500">
              Workspace / <strong className="text-slate-800">Dashboard</strong>
            </span>
          </div>

          <div className="hidden items-center gap-2 rounded-full border border-slate-200 px-3 py-2 text-sm text-slate-600 sm:flex">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            Local development
          </div>
        </header>

        <main id="dashboard" className="mx-auto max-w-7xl p-5 md:p-8">
          <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-950 via-blue-950 to-blue-800 p-7 text-white md:p-10">
            <div className="relative z-10 max-w-2xl">
              <span className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-medium text-blue-100">
                <Sparkles size={14} />
                AI-powered career tools
              </span>

              <h2 className="mt-5 text-3xl font-bold leading-tight tracking-tight md:text-4xl">
                Make your next application count.
              </h2>

              <p className="mt-4 max-w-xl text-sm leading-7 text-blue-100 md:text-base">
                Match your resume with a job description, uncover missing
                skills, and prepare a stronger application.
              </p>

              <a
                href="#analyzer"
                className="mt-6 inline-flex items-center gap-2 rounded-xl bg-white px-5 py-3 font-semibold text-blue-950 transition hover:bg-blue-50"
              >
                Analyze my resume <ArrowUpRight size={18} />
              </a>
            </div>

            <div className="pointer-events-none absolute -right-12 -top-16 h-72 w-72 rounded-full border border-white/10" />
            <div className="pointer-events-none absolute -right-2 -top-6 h-52 w-52 rounded-full border border-white/10" />
          </section>

          <section className="mt-8 grid gap-4 sm:grid-cols-3">
            {[
              {
                label: 'Resume analysis',
                value: 'Ready to start',
                icon: FileText,
              },
              {
                label: 'Job requirements',
                value: 'Awaiting input',
                icon: BriefcaseBusiness,
              },
              {
                label: 'Generated reports',
                value: 'No reports yet',
                icon: ChartNoAxesCombined,
              },
            ].map(({ label, value, icon: Icon }) => (
              <div
                key={label}
                className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-200/40"
              >
                <div className="flex items-center justify-between">
                  <p className="text-sm text-slate-500">{label}</p>
                  <Icon size={20} className="text-blue-600" />
                </div>
                <p className="mt-3 text-lg font-semibold text-slate-900">
                  {value}
                </p>
              </div>
            ))}
          </section>

          <section id="analyzer" className="mt-10 scroll-mt-24">
            <div className="mb-5">
              <h2 className="text-xl font-bold text-slate-900">
                Resume analyzer
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                Add your resume and the job description to prepare an analysis.
              </p>
            </div>

            <div className="grid items-start gap-6 xl:grid-cols-2">
              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex items-center gap-3">
                  <div className="rounded-xl bg-blue-50 p-3 text-blue-700">
                    <UploadCloud size={22} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">
                      Upload resume
                    </h3>
                    <p className="text-sm text-slate-500">
                      PDF or DOCX file
                    </p>
                  </div>
                </div>

                <label
                  htmlFor="resume-file"
                  className="mt-6 flex min-h-48 cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-300 bg-slate-50 px-5 text-center transition hover:border-blue-400 hover:bg-blue-50/50"
                >
                  <UploadCloud size={32} className="text-blue-600" />
                  <span className="mt-3 font-semibold text-slate-800">
                    Click to select your resume
                  </span>
                  <span className="mt-2 text-sm text-slate-500">
                    Choose a PDF or DOCX from your computer
                  </span>
                  <input
                    id="resume-file"
                    type="file"
                    accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    onChange={handleResumeChange}
                    className="sr-only"
                  />
                </label>

                {resume && (
                  <div className="mt-4 flex items-center gap-3 rounded-xl bg-emerald-50 p-3 text-emerald-800">
                    <FileCheck2 size={21} />
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold">
                        {resume.name}
                      </p>
                      <p className="text-xs">
                        {(resume.size / 1024).toFixed(1)} KB · Selected locally
                      </p>
                    </div>
                    <button
                      onClick={() => setResume(null)}
                      className="ml-auto rounded-lg p-2 hover:bg-emerald-100"
                      aria-label="Remove selected resume"
                    >
                      <X size={17} />
                    </button>
                  </div>
                )}
              </div>

              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex items-center gap-3">
                  <div className="rounded-xl bg-violet-50 p-3 text-violet-700">
                    <BriefcaseBusiness size={22} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">
                      Job description
                    </h3>
                    <p className="text-sm text-slate-500">
                      Paste the target job posting
                    </p>
                  </div>
                </div>

                <label
                  htmlFor="job-description"
                  className="mt-6 mb-2 block text-sm font-medium text-slate-700"
                >
                  Job requirements
                </label>
                <textarea
                  id="job-description"
                  value={jobDescription}
                  onChange={(event) => setJobDescription(event.target.value)}
                  placeholder="Paste the complete job description here..."
                  rows={8}
                  className="w-full resize-y rounded-xl border border-slate-300 bg-slate-50 p-4 text-sm leading-6 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
                />

                <p className="mt-2 text-right text-xs text-slate-400">
                  {jobDescription.length} characters
                </p>
              </div>
            </div>

            {message && (
              <div
                role="status"
                className="mt-5 rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-800"
              >
                {message}
              </div>
            )}

            
<button
  onClick={handleAnalyze}
  disabled={loading}
  className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-6 py-3.5 font-semibold text-white shadow-lg shadow-blue-600/20 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
>
  <Sparkles size={18} />
  {loading ? 'Analyzing resume...' : 'Prepare resume analysis'}
</button>

<button
  onClick={handleCoverLetter}
  disabled={letterLoading}
  className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-6 py-3.5 font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60 sm:ml-3 sm:w-auto"
>
  <FileText size={18} />
  {letterLoading
  ? 'Generating cover letter...'
  : 'Generate Cover Letter'} 
</button>

{coverLetter && (
  <section className="mt-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
    <h2 className="text-xl font-bold text-slate-900">
      Cover Letter Preview
    </h2>

    <p className="mt-1 text-sm text-slate-500">
      Review your cover letter before downloading.
    </p>

    <div className="mt-5 whitespace-pre-wrap rounded-xl bg-slate-50 p-5 text-sm leading-7 text-slate-700">
      {coverLetter}
    </div>

    <button
      onClick={handleDownloadCoverLetter}
      className="mt-5 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700"
    >
      Download DOCX
    </button>
  </section>
)}



{result && (
  <section className="mt-8 space-y-6">
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div className="rounded-2xl border border-slate-200 bg-white p-5">
        <p className="text-sm text-slate-500">Job title</p>
        <h3 className="mt-2 font-semibold text-slate-900">
          {result.job_title || 'Not identified'}
        </h3>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-5">
        <p className="text-sm text-slate-500">Skills match</p>
        <p className="mt-2 text-3xl font-bold text-blue-600">
          {result.match_percentage ?? 0}%
        </p>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-5">
        <p className="text-sm text-slate-500">Keyword coverage</p>
        <p className="mt-2 text-3xl font-bold text-violet-600">
          {result.ats_keyword_analysis?.keyword_coverage_percentage ?? 0}%
        </p>
      </div>
    </div>

    <div className="grid gap-5 md:grid-cols-2">
      <div className="rounded-2xl border border-slate-200 bg-white p-5">
        <h3 className="font-semibold text-slate-900">Matched skills</h3>
        <div className="mt-4 flex flex-wrap gap-2">
          {(result.matched_skills || []).length > 0 ? (
            result.matched_skills.map((skill, index) => (
              <span
                key={`${skill}-${index}`}
                className="rounded-full bg-emerald-50 px-3 py-1.5 text-sm text-emerald-700"
              >
                {skill}
              </span>
            ))
          ) : (
            <p className="text-sm text-slate-500">No matched skills found.</p>
          )}
        </div>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-5">
        <h3 className="font-semibold text-slate-900">Missing skills</h3>
        <div className="mt-4 flex flex-wrap gap-2">
          {(result.missing_skills || []).length > 0 ? (
            result.missing_skills.map((skill, index) => (
              <span
                key={`${skill}-${index}`}
                className="rounded-full bg-rose-50 px-3 py-1.5 text-sm text-rose-700"
              >
                {skill}
              </span>
            ))
          ) : (
            <p className="text-sm text-slate-500">No missing skills reported.</p>
          )}
        </div>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-5">
        <h3 className="font-semibold text-slate-900">Required skills</h3>
        <div className="mt-4 flex flex-wrap gap-2">
          {(result.required_skills || []).map((skill, index) => (
            <span
              key={`${skill}-${index}`}
              className="rounded-full bg-blue-50 px-3 py-1.5 text-sm text-blue-700"
            >
              {skill}
            </span>
          ))}
        </div>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-5">
        <h3 className="font-semibold text-slate-900">Missing keywords</h3>
        <div className="mt-4 flex flex-wrap gap-2">
          {(result.ats_keyword_analysis?.missing_keywords || []).length > 0 ? (
            result.ats_keyword_analysis.missing_keywords.map(
              (keyword, index) => (
                <span
                  key={`${keyword}-${index}`}
                  className="rounded-full bg-amber-50 px-3 py-1.5 text-sm text-amber-800"
                >
                  {keyword}
                </span>
              ),
            )
          ) : (
            <p className="text-sm text-slate-500">No missing keywords reported.</p>
          )}
        </div>
      </div>
    </div>

    {result.suggestions?.length > 0 && (
      <div className="rounded-2xl border border-slate-200 bg-white p-5">
        <h3 className="font-semibold text-slate-900">
          Improvement suggestions
        </h3>
        <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-slate-600">
          {result.suggestions.map((suggestion, index) => (
            <li key={index}>{suggestion}</li>
          ))}
        </ul>
      </div>
    )}

    <p className="text-xs leading-5 text-slate-500">
      {result.note || 'These are estimated matching metrics, not an official ATS score.'}
    </p>
  </section>
)}


            <p className="mt-3 text-xs leading-5 text-slate-500">
              Frontend preview: analysis is not sent to the backend yet.
              Your selected file remains in the browser until API integration.
            </p>
          </section>


<section id="resume-improver" className="mt-12 scroll-mt-24">
  <div className="mb-6">
    <div className="flex items-center gap-3">
      <div className="rounded-xl bg-violet-100 p-3 text-violet-700">
        <Sparkles size={24} />
      </div>
      <div>
        <h2 className="text-2xl font-bold text-slate-900">
          AI Resume Improver
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          Improve your existing CV for your target job using local AI.
        </p>
      </div>
    </div>
  </div>

  <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h3 className="font-semibold text-slate-900">
          Review your CV
        </h3>
        <p className="mt-1 text-sm text-slate-500">
          Reuses your uploaded resume and the job description above.
          Your original file will not be overwritten.
        </p>
      </div>

      <button
        type="button"
        onClick={handleDetectResume}
        disabled={detectionLoading || !resume || !jobDescription.trim()}
        className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        <Sparkles size={18} />
        {detectionLoading ? 'Reviewing CV...' : 'Detect CV Improvements'}
      </button>
    </div>

    {!resume && (
      <p className="mt-4 rounded-xl bg-amber-50 p-3 text-sm text-amber-800">
        Upload your PDF or DOCX resume in Resume Analyzer first.
      </p>
    )}

    {detectionMessage && (
      <div
        role="status"
        className="mt-5 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700"
      >
        {detectionMessage}
      </div>
    )}

    {detectedSections.length > 0 && (
      <div className="mt-6 space-y-5">
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4">
          <div className="flex items-start gap-3">
            <FileCheck2 className="mt-0.5 text-emerald-700" size={22} />
            <div>
              <h3 className="font-semibold text-emerald-900">
                Your CV can be improved
              </h3>
              <p className="mt-1 text-sm leading-6 text-emerald-800">
                We detected {detectedSections.length} resume sections.
                Review the original content before choosing how to improve it.
                No changes have been made.
              </p>
            </div>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          {detectedSections.map((section, index) => (
            <article
              key={`${section.section_name}-${index}`}
              className="rounded-xl border border-slate-200 p-4"
            >
              <div className="mb-3 flex items-center gap-2">
                <FileText size={18} className="text-blue-600" />
                <h4 className="font-semibold text-slate-900">
                  {section.section_name}
                </h4>
              </div>

              <p className="whitespace-pre-wrap break-words text-sm leading-6 text-slate-600">
                {section.original_text}
              </p>
            </article>
          ))}
        </div>

        {!improvementConfirmed ? (
          <div className="rounded-xl border border-blue-200 bg-blue-50/60 p-5">
            <h3 className="font-semibold text-slate-900">
              Ready to improve your CV?
            </h3>
            <p className="mt-1 text-sm leading-6 text-slate-600">
              Confirm to continue. Your original resume stays unchanged;
              you will review the AI-generated draft before exporting it.
            </p>

            <div className="mt-4 flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => {
                  setImprovementConfirmed(true)
                  setImprovementMode('')
                }}
                className="rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700"
              >
                Yes, Improve My CV
              </button>

              <button
                type="button"
                onClick={() => {
                  setDetectedSections([])
                  setShowConfirmation(false)
                  setImprovementConfirmed(false)
                  setImprovementMode('')
                  setDetectionMessage('CV improvement cancelled. Your original resume is unchanged.')
                }}
                className="rounded-xl border border-slate-300 bg-white px-5 py-3 font-semibold text-slate-700 hover:bg-slate-50"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div className="rounded-xl border border-slate-200 p-5">
            <h3 className="font-semibold text-slate-900">
              Choose your improvement mode
            </h3>
            <p className="mt-1 text-sm text-slate-500">
              Choose one workflow. Both will use your detected sections and
              the job description already provided.
            </p>

            <div className="mt-4 grid gap-4 md:grid-cols-2">
              <button
                type="button"
                onClick={() => setImprovementMode('entire')}
                className={`rounded-xl border p-5 text-left transition ${
                  improvementMode === 'entire'
                    ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-100'
                    : 'border-slate-200 hover:border-blue-300 hover:bg-slate-50'
                }`}
              >
                <Sparkles size={22} className="mb-3 text-blue-600" />
                <span className="block font-semibold text-slate-900">
                  Improve Entire CV
                </span>
                <span className="mt-2 block text-sm leading-6 text-slate-500">
                  Prepare a draft in order: Summary, Experience, Projects,
                  Skills, and Education.
                </span>
              </button>

              <button
                type="button"
                onClick={() => setImprovementMode('step')}
                className={`rounded-xl border p-5 text-left transition ${
                  improvementMode === 'step'
                    ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-100'
                    : 'border-slate-200 hover:border-blue-300 hover:bg-slate-50'
                }`}
              >
                <FileCheck2 size={22} className="mb-3 text-violet-600" />
                <span className="block font-semibold text-slate-900">
                  Improve Step by Step
                </span>
                <span className="mt-2 block text-sm leading-6 text-slate-500">
                  Review and decide on each detected section separately.
                </span>
              </button>
            </div>

            {improvementMode && (
              <p className="mt-4 rounded-lg bg-slate-50 p-3 text-sm text-slate-600">
                {improvementMode === 'entire'
                  ? 'Improve Entire CV selected.'
                  : 'Improve Step by Step selected.'}
                {' '}Next, we will connect this selection to the AI improvement
                workflow.
              </p>
            )}

            
{improvementMode === 'entire' && (
  <button
    type="button"
    onClick={handleImproveEntireCV}
    disabled={entireCvLoading || improvedSections.length > 0}
    className="mt-4 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
  >
    {entireCvLoading
      ? 'Improving CV...'
      : improvedSections.length > 0
        ? 'CV Draft Generated'
        : 'Generate Improved CV Draft'}
  </button>
)}


{improvementMode === 'step' && (
  <div className="mt-4 rounded-xl border border-violet-200 bg-violet-50/50 p-5">
    <h3 className="font-semibold text-slate-900">
      Improve CV Step by Step
    </h3>

    <p className="mt-2 text-sm text-slate-600">
      Section {currentSectionIndex + 1} of {detectedSections.length}
      {' — '}
      {detectedSections[currentSectionIndex]?.section_name}
    </p>

    <div className="mt-4 flex flex-wrap gap-3">
      <button
        type="button"
        onClick={handleImproveCurrentSection}
        disabled={entireCvLoading || currentSectionIndex >= detectedSections.length}
        className="rounded-xl bg-violet-600 px-5 py-3 font-semibold text-white hover:bg-violet-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {entireCvLoading
          ? 'Improving Section...'
          : 'Improve Current Section'}
      </button>

      <button
        type="button"
        onClick={() =>
          setCurrentSectionIndex((index) => Math.max(0, index - 1))
        }
        disabled={currentSectionIndex === 0 || entireCvLoading}
        className="rounded-xl border border-slate-300 bg-white px-4 py-3 font-medium text-slate-700 disabled:opacity-50"
      >
        Previous Section
      </button>

      <button
        type="button"
        onClick={() =>
          setCurrentSectionIndex((index) =>
            Math.min(detectedSections.length - 1, index + 1)
          )
        }
        disabled={
          currentSectionIndex >= detectedSections.length - 1 ||
          entireCvLoading
        }
        className="rounded-xl border border-slate-300 bg-white px-4 py-3 font-medium text-slate-700 disabled:opacity-50"
      >
        Next Section
      </button>
    </div>
  </div>
)}



{improvedSections.length > 0 &&
  (improvementMode === 'entire' || improvementMode === 'step') && (
  <div className="mt-6 space-y-5">
    <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4">
      <h3 className="font-semibold text-emerald-900">
        Your Improved CV Draft
      </h3>
      <p className="mt-1 text-sm text-emerald-800">
        Review the improved content below. Your original resume is unchanged.
      </p>
    </div>

    
{improvedSections
  .filter((section) => section && typeof section === 'object')
  .map((section, index) => (
    <div
      key={`${section.section_name}-${index}`}
      className="rounded-xl border border-slate-200 bg-white p-5"
    >
      <h4 className="mb-3 font-semibold text-slate-900">
        {section.section_name}
      </h4>

      <label className="mb-2 block text-sm font-medium text-slate-500">
        Original content
      </label>

      <p className="mb-4 whitespace-pre-wrap text-sm leading-6 text-slate-600">
        {section.original_text}
      </p>

      <label className="mb-2 block text-sm font-medium text-emerald-700">
        AI-improved draft
      </label>

      <textarea
        value={section.improved_text ?? ''}
        onChange={(e) => {
          setImprovedSections((previous) =>
            previous.map((item) =>
              item?.section_name === section.section_name
                ? { ...item, improved_text: e.target.value }
                : item
            )
          )
        }}
        rows={Math.max(
          5,
          (section.improved_text ?? '').split('\n').length
        )}
        className="w-full rounded-xl border border-slate-300 p-3 text-sm leading-6 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
      />

      <div className="mt-3 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => {
            setImprovedSections((previous) =>
              previous.map((item) =>
                item?.section_name === section.section_name
                  ? {
                      ...item,
                      improved_text: item.original_text ?? '',
                    }
                  : item
              )
            )
          }}
          className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Revert to Original
        </button>
      </div>
    </div>
  ))}


<div className="flex flex-wrap gap-3 pt-4">
  <button
    type="button"
    onClick={() => handleExportCV('pdf')}
    className="rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700"
  >
    Download PDF
  </button>

  <button
    type="button"
    onClick={() => handleExportCV('docx')}
    className="rounded-xl border border-slate-300 bg-white px-5 py-3 font-semibold text-slate-700 hover:bg-slate-50"
  >
    Download DOCX
  </button>
</div>

  </div>
)}

          </div>
        )}
      </div>
    )}
  </div>
</section>



          
<section id="features" className="mt-8 scroll-mt-24 pb-6">
  <h2 className="text-xl font-bold text-slate-900">
    What you can analyze
  </h2>

  <p className="mt-1 text-xs text-slate-500">
    The planned workflow uses your existing Python backend.
  </p>

  <div className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-4">
    {features.map(({ icon: Icon, title, description }) => (
      <article
        key={title}
        className="rounded-xl border border-slate-200 bg-white p-3 transition hover:-translate-y-0.5 hover:shadow-sm"
      >
        <div className="mb-2 inline-flex rounded-lg bg-blue-50 p-2 text-blue-700">
          <Icon size={16} />
        </div>

        <h3 className="text-sm font-semibold text-slate-900">
          {title}
        </h3>

        <p className="mt-1 text-xs leading-5 text-slate-500">
          {description}
        </p>
      </article>
    ))}
  </div>
</section>

          <footer className="border-t border-slate-200 py-6 text-center text-xs text-slate-500">
            CareerLens AI · Resume analysis estimates are not official ATS scores.
          </footer>
        </main>
      </div>
    </div>
  )
}


