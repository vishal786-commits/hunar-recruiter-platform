"use client"

import { useState } from "react"
import {
  Upload,
  Users,
  Phone,
  CheckCircle,
  Briefcase,
  ChevronRight,
  RefreshCw,
  FileText,
} from "lucide-react"

import {
  analyzeJob,
  approveCandidates,
  startScreenings,
  syncScreening,
} from "@/lib/api"

export default function Home() {
  const [job, setJob] = useState<any>(null)
  const [file, setFile] = useState<File | null>(null)
  const [selected, setSelected] = useState<string[]>([])
  const [screenings, setScreenings] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [activeSection, setActiveSection] = useState("jobs")

  function navigateTo(section: string) {
    setActiveSection(section)

    if (!job && section !== "jobs") {
      setError("Analyze a job description to view this section.")
      return
    }

    const targetSection = section === "jobs" && job
      ? "dashboard"
      : section

    document.getElementById(`${targetSection}-section`)
      ?.scrollIntoView({ behavior: "smooth", block: "start" })
  }

  async function handleAnalyze() {
    if (!file) return

    setLoading(true)
    setError("")

    try {
      const data = await analyzeJob(file)
      setJob({
        ...data,
        candidates: data.candidates?.map((candidate: any) => ({
          ...candidate,
          years_experience: candidate.years_experience ?? "Not specified",
        })),
        job_description: {
          ...data.job_description,
          job_title: data.job_description?.title,
        },
      })
      setActiveSection("dashboard")
    } catch (e: any) {
      setError(e.message || "Unable to analyze job description.")
    } finally {
      setLoading(false)
    }
  }

  async function handleApprove() {
    if (!job || !selected.length) return

    setLoading(true)
    setError("")

    try {
      await approveCandidates(job.job_id, selected)

      setJob({
        ...job,
        candidates: job.candidates.map((c: any) =>
          selected.includes(c.id)
            ? { ...c, approved: true }
            : c
        ),
      })

      setSelected([])
    } catch (e: any) {
      setError(e.message || "Could not approve candidates.")
    } finally {
      setLoading(false)
    }
  }

  async function handleStartScreening() {
    const approved = (job.candidates || [])
      .filter((c: any) => c.approved)
      .map((c: any) => c.id)

    if (!approved.length) return

    setLoading(true)
    setError("")

    try {
      const data = await startScreenings(
        job.job_id,
        approved
      )

      setScreenings(
        data.screenings ||
        data.results ||
        data ||
        []
      )
    } catch (e: any) {
      setError(e.message || "Could not start voice screening.")
    } finally {
      setLoading(false)
    }
  }

  async function handleSync(id: string) {
    try {
      const data = await syncScreening(id)

      setScreenings((current) =>
        current.map((s) =>
          s.screening_id === id ? data : s
        )
      )
    } catch (e: any) {
      setError(e.message || "Could not sync screening.")
    }
  }

  const candidates = job?.candidates || []
  const approved = candidates.filter(
    (c: any) => c.approved
  )

  if (activeSection === "how-it-works") {
    return (
      <div className="min-h-screen bg-[#f7f8fa] text-slate-900">
        <Sidebar activeSection={activeSection} onNavigate={navigateTo} />
        <main className="ml-64 min-h-screen">
          <Topbar />
          <div className="mx-auto max-w-6xl px-10 py-12">
            <HowItWorks />
          </div>
        </main>
      </div>
    )
  }

  if (!job) {
    return (
      <div className="min-h-screen bg-[#f7f8fa] text-slate-900">
        <Sidebar activeSection={activeSection} onNavigate={navigateTo} />

        <main className="ml-64 min-h-screen">
          <Topbar />

          <div id="jobs-section" className="mx-auto max-w-6xl px-10 py-12">
            <div className="mb-10">
              <p className="text-sm font-medium text-slate-400">
                RECRUITING
              </p>

              <h1 className="mt-2 text-3xl font-semibold tracking-tight">
                Create a new job
              </h1>

              <p className="mt-2 text-slate-500">
                Upload a job description to source and screen candidates.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-10 shadow-sm">

              <div
                className="flex min-h-[420px] flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-200 bg-slate-50 px-6 text-center"
              >
                <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-white shadow-sm">
                  <Upload size={24} className="text-slate-500" />
                </div>

                <h2 className="mt-5 text-lg font-semibold">
                  Upload job description
                </h2>

                <p className="mt-2 max-w-md text-sm text-slate-500">
                  Upload your JD as a PDF, DOCX or TXT file.
                  Hunar will analyze the role and find matching candidates.
                </p>

                <label className="mt-6 cursor-pointer rounded-lg border bg-white px-5 py-2.5 text-sm font-medium shadow-sm hover:bg-slate-50">
                  {file ? file.name : "Choose file"}

                  <input
                    type="file"
                    accept=".pdf,.docx,.txt"
                    className="hidden"
                    onChange={(e) =>
                      setFile(e.target.files?.[0] || null)
                    }
                  />
                </label>
              </div>

              {error && (
                <div className="mt-5 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {error}
                </div>
              )}

              <div className="mt-6 flex justify-end">
                <button
                  onClick={handleAnalyze}
                  disabled={!file || loading}
                  className="rounded-lg bg-slate-900 px-6 py-3 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {loading
                    ? "Analyzing..."
                    : "Analyze job description"}
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#f7f8fa] text-slate-900">
      <Sidebar activeSection={activeSection} onNavigate={navigateTo} />

      <main className="ml-64 min-h-screen">
        <Topbar />

        <div className="mx-auto max-w-7xl px-10 py-8">

          <div id="dashboard-section" className="flex items-start justify-between scroll-mt-20">
            <div>
              <p className="text-sm text-slate-400">
                JOB
              </p>

              <h1 className="mt-1 text-3xl font-semibold">
                  {job.job_description?.title || "Not specified"}
              </h1>

              <p className="mt-2 text-sm text-slate-500">
                {job.job_description?.company || "Company"}{" "}
                {job.job_description?.location?.city
                  ? `${job.job_description.location.city}, ${job.job_description.location.country || ""}`
                  : "Location not specified"}
              </p>
            </div>

            <button
              onClick={() => {
                setJob(null)
                setFile(null)
                setScreenings([])
              }}
              className="rounded-lg border bg-white px-4 py-2 text-sm font-medium shadow-sm"
            >
              + New Job
            </button>
          </div>

          {/* STATS */}

          <div className="mt-8 grid grid-cols-4 gap-4">

            <Stat
              icon={<Users size={18} />}
              label="Candidates"
              value={candidates.length}
            />

            <Stat
              icon={<CheckCircle size={18} />}
              label="Approved"
              value={approved.length}
            />

            <Stat
              icon={<Phone size={18} />}
              label="Screenings"
              value={screenings.length}
            />

            <Stat
              icon={<Briefcase size={18} />}
              label="Agent"
              value={
                job.agent_routing?.selected_agent_code || "ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬‚ ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ¢¢‚¬Å¾‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€š‚¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ¢¢€š¬‚¦ƒÆ’¢‚¬Å¡ƒ€š‚¡ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€š‚¢ƒÆ’‚¢ƒ¢¢€š¬…¡ƒ€š‚¬ƒÆ’¢‚¬¦ƒ€š‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚"
              }
            />

          </div>

          <section id="results-section" className="mt-6 scroll-mt-20 rounded-xl border bg-white p-6 shadow-sm">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                    Results dashboard
                  </p>
                  <h2 className="mt-1 text-xl font-semibold">
                    Screening performance
                  </h2>
                  <p className="mt-1 text-sm text-slate-500">
                    Track every call from launch through final result.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => navigateTo("screenings")}
                  className="rounded-lg border px-3 py-2 text-xs font-medium hover:bg-slate-50"
                >
                  View call details
                </button>
              </div>

              <div className="mt-6 grid gap-3 sm:grid-cols-4">
                <ResultMetric label="Total calls" value={screenings.length} />
                <ResultMetric
                  label="Completed"
                  value={screenings.filter((s: any) => String(s.status || s.lifecycle_status || "").toLowerCase() === "completed").length}
                />
                <ResultMetric
                  label="In progress"
                  value={screenings.filter((s: any) => !["completed", "failed"].includes(String(s.status || s.lifecycle_status || "").toLowerCase())).length}
                />
                <ResultMetric
                  label="Failed"
                  value={screenings.filter((s: any) => String(s.status || s.lifecycle_status || "").toLowerCase() === "failed").length}
                />
              </div>

              {screenings.length > 0 ? (
                <div className="mt-6 divide-y border-t">
                  {screenings.map((screening: any, index: number) => (
                    <div key={`result-${screening.screening_id || screening.candidate_id || index}`} className="flex items-center justify-between gap-4 py-3 text-sm">
                      <span className="font-medium">{screening.candidate_name || "Candidate"}</span>
                      <Status text={screening.status || screening.lifecycle_status || "Pending"} />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="mt-6 rounded-lg border border-dashed bg-slate-50 px-5 py-8 text-center">
                  <p className="text-sm font-medium">No screening results yet</p>
                  <p className="mt-1 text-sm text-slate-500">
                    Approve candidates and start voice screening to populate this dashboard.
                  </p>
                </div>
              )}
            </section>

          {/* JOB / AGENT */}

          <div className="mt-6 grid grid-cols-3 gap-5">

            <Card title="Job overview">
              <Info
                label="Title"
                value={
                  job.job_description?.job_title || "ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬‚ ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ¢¢‚¬Å¾‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€š‚¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ¢¢€š¬‚¦ƒÆ’¢‚¬Å¡ƒ€š‚¡ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€š‚¢ƒÆ’‚¢ƒ¢¢€š¬…¡ƒ€š‚¬ƒÆ’¢‚¬¦ƒ€š‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚"
                }
              />

              <Info
                label="Company"
                value={
                  job.job_description?.company || "ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬‚ ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ¢¢‚¬Å¾‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€š‚¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ¢¢€š¬‚¦ƒÆ’¢‚¬Å¡ƒ€š‚¡ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€š‚¢ƒÆ’‚¢ƒ¢¢€š¬…¡ƒ€š‚¬ƒÆ’¢‚¬¦ƒ€š‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚"
                }
              />

              <Info
                label="Location"
                value={
                  (job.job_description?.location?.city ? `${job.job_description.location.city}, ${job.job_description.location.country || ""}` : "¢‚¬€")
                }
              />

              <Info
                label="Experience"
                value={
                  job.job_description?.experience ||
                  job.job_description?.experience_range ||
                  "ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬‚ ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ¢¢‚¬Å¾‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€š‚¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ¢¢€š¬‚¦ƒÆ’¢‚¬Å¡ƒ€š‚¡ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€š‚¢ƒÆ’‚¢ƒ¢¢€š¬…¡ƒ€š‚¬ƒÆ’¢‚¬¦ƒ€š‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚"
                }
              />
            </Card>

            <Card title="Voice agent">
              <p className="text-2xl font-semibold">
                {job.agent_routing?.selected_agent_code || "ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬‚ ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ¢¢‚¬Å¾‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€š‚¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ¢¢€š¬‚¦ƒÆ’¢‚¬Å¡ƒ€š‚¡ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€š‚¢ƒÆ’‚¢ƒ¢¢€š¬…¡ƒ€š‚¬ƒÆ’¢‚¬¦ƒ€š‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚"}
              </p>

              <p className="mt-1 text-sm text-slate-500">
                Selected Hunar screening agent
              </p>

              <div className="mt-6">
                <p className="text-xs uppercase text-slate-400">
                  Confidence
                </p>

                <p className="mt-1 text-3xl font-semibold">
                  {Math.round(
                    (job.agent_routing?.confidence || 0) * 100
                  )}%
                </p>
              </div>
            </Card>

            <Card title="Workflow">
              <WorkflowStep
                number="01"
                label="JD analyzed"
                done
              />

              <WorkflowStep
                number="02"
                label="Candidates sourced"
                done
              />

              <WorkflowStep
                number="03"
                label="Human approval"
                done={approved.length > 0}
              />

              <WorkflowStep
                number="04"
                label="Voice screening"
                done={screenings.length > 0}
              />

              <WorkflowStep
                number="05"
                label="Results"
                done={screenings.some(
                  (s: any) =>
                    s.status === "completed" ||
                    s.lifecycle_status === "completed" ||
                    s.result
                )}
              />
            </Card>

          </div>

          {/* CANDIDATES */}

          <div id="candidates-section" className="mt-6 scroll-mt-20 overflow-hidden rounded-xl border bg-white shadow-sm">

            <div className="flex items-center justify-between border-b px-6 py-5">

              <div>
                <h2 className="font-semibold">
                  Candidates
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Review AI-ranked candidates before calling.
                </p>
              </div>

              <div className="flex gap-3">

                <button
                  onClick={handleApprove}
                  disabled={!selected.length || loading}
                  className="rounded-lg border px-4 py-2 text-sm font-medium disabled:opacity-40"
                >
                  Approve {selected.length || ""} selected
                </button>

                <button
                  onClick={handleStartScreening}
                  disabled={!approved.length || loading}
                  className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-40"
                >
                  Start voice screening
                </button>

              </div>
            </div>

            <table className="w-full text-sm">

              <thead className="bg-slate-50 text-xs uppercase text-slate-400">
                <tr>
                  <th className="px-6 py-4 text-left"></th>
                  <th className="px-4 py-4 text-left">Candidate</th>
                  <th className="px-4 py-4 text-left">Title</th>
                  <th className="px-4 py-4 text-left">Location</th>
                  <th className="px-4 py-4 text-left">Experience</th>
                  <th className="px-4 py-4 text-left">Match</th>
                  <th className="px-4 py-4 text-left">Source</th>
                  <th className="px-4 py-4 text-left">Approval</th>
                </tr>
              </thead>

              <tbody className="divide-y">

                {candidates.map((c: any) => (
                  <tr
                    key={c.id}
                    className="hover:bg-slate-50"
                  >
                    <td className="px-6 py-5">
                      <input
                        type="checkbox"
                        checked={selected.includes(c.id)}
                        disabled={c.approved}
                        onChange={(e) =>
                          setSelected((ids) =>
                            e.target.checked
                              ? [...ids, c.id]
                              : ids.filter(id => id !== c.id)
                          )
                        }
                      />
                    </td>

                    <td className="px-4 py-5">
                      <p className="font-medium">
                        {c.name}
                      </p>

                      <p className="mt-1 text-xs text-slate-400">
                        {c.email || c.phone_number || ""}
                      </p>
                    </td>

                    <td className="px-4 py-5 text-slate-600">
                      {c.current_title || "ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬‚ ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ¢¢‚¬Å¾‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€š‚¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ¢¢€š¬‚¦ƒÆ’¢‚¬Å¡ƒ€š‚¡ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€š‚¢ƒÆ’‚¢ƒ¢¢€š¬…¡ƒ€š‚¬ƒÆ’¢‚¬¦ƒ€š‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚"}
                    </td>

                    <td className="px-4 py-5 text-slate-600">
                      {c.location || "Not specified"}
                    </td>

                    <td className="px-4 py-5">
                      {c.years_experience ?? "ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬‚ ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ¢¢‚¬Å¾‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€š‚¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ¢¢€š¬‚¦ƒÆ’¢‚¬Å¡ƒ€š‚¡ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€š‚¢ƒÆ’‚¢ƒ¢¢€š¬…¡ƒ€š‚¬ƒÆ’¢‚¬¦ƒ€š‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚"}
                    </td>

                    <td className="px-4 py-5">
                      <span className="rounded-full bg-slate-100 px-3 py-1 font-semibold">
                        {c.match_score ?? 0}%
                      </span>
                    </td>

                    <td className="px-4 py-5 text-slate-500">
                      {c.source || "Demo"}
                    </td>

                    <td className="px-4 py-5">
                      {c.approved
                        ? <Status text="Approved" />
                        : <Status text="Pending" />}
                    </td>
                  </tr>
                ))}

              </tbody>
            </table>
          </div>

          {/* SCREENINGS */}

          {screenings.length > 0 && (
            <div id="screenings-section" className="mt-6 scroll-mt-20 rounded-xl border bg-white shadow-sm">

              <div className="border-b px-6 py-5">
                <h2 className="font-semibold">
                  Voice screenings
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Live screening status and call results.
                </p>
              </div>

              <div className="divide-y">

                {screenings.map((s: any, index: number) => (
                  <Screening
                    key={`screening-${s.screening_id || s.candidate_id || index}`}
                    screening={s}
                    onSync={() =>
                      handleSync(s.screening_id)
                    }
                  />
                ))}

              </div>
            </div>
          )}

          {error && (
            <div className="mt-5 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

        </div>
      </main>
    </div>
  )
}

function Sidebar({
  activeSection,
  onNavigate,
}: {
  activeSection: string
  onNavigate: (section: string) => void
}) {
  return (
    <aside className="fixed inset-y-0 left-0 w-64 border-r bg-white">

      <div className="border-b px-6 py-5">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-900 text-sm font-bold text-white">
            H
          </div>

          <div>
            <p className="font-semibold">
              Hunar
            </p>
            <p className="text-xs text-slate-400">
              Recruiter
            </p>
          </div>
        </div>
      </div>

      <nav className="p-4">
        {[
          ["dashboard", "Dashboard"],
          ["jobs", "Jobs"],
          ["candidates", "Candidates"],
          ["screenings", "Screenings"],
          ["how-it-works", "How it works"],
        ].map(([section, label]) => (
          <button
            key={section}
            type="button"
            onClick={() => onNavigate(section)}
            className={`block w-full rounded-lg px-4 py-3 text-left text-sm font-medium transition-colors ${
              activeSection === section
                ? "bg-slate-100 text-slate-900"
                : "text-slate-500 hover:bg-slate-50 hover:text-slate-900"
            }`}
          >
            {label}
          </button>
        ))}
      </nav>

    </aside>
  )
}

function HowItWorks() {
  return (
    <section>
      <div className="max-w-3xl">
        <p className="text-sm font-medium uppercase tracking-wide text-slate-400">
          How it works
        </p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight">
          From job description to recruiter-ready screening
        </h1>
        <p className="mt-3 text-sm leading-6 text-slate-500">
          Hunar extracts the role, finds and ranks candidates, routes the role to the right voice agent, and keeps the recruiter in control before any screening begins.
        </p>
      </div>

      <div className="mt-8 grid gap-4 md:grid-cols-5">
        {[
          ["01", "Upload", "Add a TXT, PDF, or DOCX job description."],
          ["02", "Understand", "Extract and structure the role with AI."],
          ["03", "Match", "Source, normalize, and rank candidates."],
          ["04", "Approve", "Review the shortlist before outreach."],
          ["05", "Screen", "Run voice calls and review results."],
        ].map(([number, title, description]) => (
          <div key={number} className="rounded-xl border bg-white p-5 shadow-sm">
            <p className="text-xs font-semibold text-slate-400">{number}</p>
            <h2 className="mt-2 text-sm font-semibold">{title}</h2>
            <p className="mt-1 text-xs leading-5 text-slate-500">{description}</p>
          </div>
        ))}
      </div>

      <div className="mt-8 rounded-xl border border-amber-200 bg-amber-50 p-5">
        <p className="text-sm font-semibold text-amber-950">Demo-mode tradeoff</p>
        <p className="mt-2 text-sm leading-6 text-amber-900">
          People Data Labs search requires a paid Pro plan for the production API access this workflow would normally use. For this demo, the live PDL call is replaced with local dummy candidate data so the sourcing, ranking, approval, and screening flow can be evaluated without paid credentials. The integration boundary remains in place for a production PDL account.
        </p>
      </div>

      <div className="mt-8 overflow-hidden rounded-xl border border-slate-200 bg-slate-50">
        <img
          src="/architecture.png"
          alt="Hunar Recruiter Platform architecture"
          className="h-auto w-full"
        />
      </div>
    </section>
  )
}

function Topbar() {
  return (
    <header className="h-16 border-b bg-white">
      <div className="flex h-full items-center justify-between px-8">
        <p className="text-sm text-slate-500">
          Recruiter workspace
        </p>

        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-200 text-xs font-medium">
          R
        </div>
      </div>
    </header>
  )
}

function Card({
  title,
  children,
}: {
  title: string
  children: React.ReactNode
}) {
  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">
      <h3 className="mb-5 text-sm font-semibold">
        {title}
      </h3>

      {children}
    </div>
  )
}

function cleanText(v: string) { let x=v ?? ''; for(let i=0;i<3;i++){ try { const y=decodeURIComponent(escape(x)); if(y===x) break; x=y } catch { break } } return x }

function Info({
  label,
  value,
}: {
  label: string
  value: any
}) {
  const display =
    value === null || value === undefined
      ? "-"
      : typeof value === "object"
        ? Array.isArray(value)
          ? value.join(", ")
          : Object.entries(value)
              .map(([key, val]) => `${key.replace(/_/g, " ")}: ${val}`)
              .join(" | ")
        : cleanText(String(value))

  return (
    <div>
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </p>
      <p className="mt-1 text-sm font-medium text-slate-900">
        {display}
      </p>
    </div>
  )
}

function Stat({
  icon,
  label,
  value,
}: any) {
  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm">
      <div className="flex items-center gap-2 text-slate-400">
        {icon}
        <span className="text-xs font-medium uppercase">
          {label}
        </span>
      </div>

      <p className="mt-3 text-2xl font-semibold">
        {value}
      </p>
    </div>
  )
}

function ResultMetric({
  label,
  value,
}: {
  label: string
  value: number
}) {
  return (
    <div className="rounded-lg bg-slate-50 p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
        {label}
      </p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
    </div>
  )
}

function Status({ text }: { text: string }) {
  return (
    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium">
      {text}
    </span>
  )
}

function WorkflowStep({
  number,
  label,
  done,
}: {
  number: string
  label: string
  done?: boolean
}) {
  return (
    <div className="mb-4 flex items-center gap-3">
      <span
        className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-medium ${
          done
            ? "bg-slate-900 text-white"
            : "bg-slate-100 text-slate-400"
        }`}
      >
        {number}
      </span>

      <span
        className={
          done
            ? "text-sm font-medium"
            : "text-sm text-slate-400"
        }
      >
        {label}
      </span>
    </div>
  )
}

function Screening({
  screening: s,
  onSync,
}: any) {
  const status =
    s.status ||
    s.lifecycle_status ||
    "Pending"

  return (
    <div className="p-6">

      <div className="flex items-center justify-between">

        <div>
          <p className="font-medium">
            Screening {s.screening_id}
          </p>

          <p className="mt-1 text-xs text-slate-400">
            Hunar Call ID: {s.hunar_call_id || "ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬‚ ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ¢¢‚¬Å¾‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€š‚¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ¢¢€š¬‚¦ƒÆ’¢‚¬Å¡ƒ€š‚¡ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬ ƒ¢¢€š¬¢€ž¢ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’¢‚¬Å¡ƒ€š‚¢ƒÆ’†€™ƒ€š‚¢ƒÆ’‚¢ƒ¢¢€š¬…¡ƒ€š‚¬ƒÆ’¢‚¬¦ƒ€š‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚¬ƒÆ’†€™ƒ€ ¢‚¬„¢ƒÆ’‚¢ƒ¢¢‚¬Å¡‚¬ƒ€¦‚¡ƒÆ’†€™ƒ¢¢€š¬…¡ƒÆ’¢‚¬Å¡ƒ€š‚"}
          </p>
        </div>

        <div className="flex items-center gap-3">

          <Status text={status} />

          <button
            onClick={onSync}
            className="flex items-center gap-2 rounded-lg border px-3 py-2 text-xs"
          >
            <RefreshCw size={14} />
            Sync
          </button>

        </div>
      </div>

      {s.result && (
        <div className="mt-5 rounded-lg bg-slate-50 p-5">
          <p className="mb-3 text-sm font-semibold">
            Screening result
          </p>

          <pre className="max-h-72 overflow-auto text-xs leading-5">
            {JSON.stringify(s.result, null, 2)}
          </pre>
        </div>
      )}

      {s.transcript && (
        <div className="mt-5">
          <p className="mb-2 text-sm font-semibold">
            Transcript
          </p>

          <div className="max-h-72 overflow-auto rounded-lg border bg-white p-5 text-sm leading-6 whitespace-pre-wrap">
            {typeof s.transcript === "string"
              ? s.transcript
              : JSON.stringify(s.transcript, null, 2)}
          </div>
        </div>
      )}

      {s.recording_url && (
        <a
          href={s.recording_url}
          target="_blank"
          rel="noreferrer"
          className="mt-4 inline-flex items-center gap-2 text-sm font-medium underline"
        >
          <FileText size={15} />
          Open call recording
        </a>
      )}
    </div>
  )
}







