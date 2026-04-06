"use client"

import { useState } from "react"
import { AppShell } from "@/components/layout/app-shell"
import {
  Plus, Upload, Search, ChevronRight, Star, User,
  FileText, MessageSquare, CheckCircle, X, Clock, Filter
} from "lucide-react"

type Stage = "sourced" | "screening" | "interview" | "offer" | "hired"

interface Candidate {
  id: string
  name: string
  role: string
  email: string
  source: string
  score: number
  stage: Stage
  skills: string[]
  applied: string
  avatar: string
  color: string
  resumeScore?: number
  interviewScore?: number
}

const STAGES: { id: Stage; label: string; color: string }[] = [
  { id: "sourced",   label: "Sourced",   color: "text-zinc-400" },
  { id: "screening", label: "Screening", color: "text-blue-400" },
  { id: "interview", label: "Interview", color: "text-purple-400" },
  { id: "offer",     label: "Offer",     color: "text-amber-400" },
  { id: "hired",     label: "Hired",     color: "text-emerald-400" },
]

const INITIAL_CANDIDATES: Candidate[] = [
  { id:"c1",  name:"Priya Sharma",    role:"Senior Frontend Eng",   email:"priya@example.com",   source:"LinkedIn",   score:87, stage:"interview", skills:["React","TypeScript","Node.js"],  applied:"Apr 3",  avatar:"P", color:"from-blue-600 to-blue-800",    resumeScore:89, interviewScore:87 },
  { id:"c2",  name:"Marcus Williams", role:"Product Manager",        email:"marcus@example.com",  source:"Referral",   score:91, stage:"offer",     skills:["Strategy","Analytics","SQL"],    applied:"Apr 1",  avatar:"M", color:"from-purple-600 to-purple-800", resumeScore:93, interviewScore:91 },
  { id:"c3",  name:"Aisha Patel",     role:"DevOps Engineer",       email:"aisha@example.com",   source:"Indeed",     score:76, stage:"screening",  skills:["K8s","AWS","Terraform"],         applied:"Apr 5",  avatar:"A", color:"from-emerald-600 to-emerald-800",resumeScore:78, interviewScore:0 },
  { id:"c4",  name:"Daniel Kim",      role:"Data Scientist",         email:"daniel@example.com",  source:"LinkedIn",   score:95, stage:"hired",     skills:["Python","ML","Spark"],           applied:"Mar 28", avatar:"D", color:"from-amber-600 to-amber-800",   resumeScore:96, interviewScore:95 },
  { id:"c5",  name:"Sofia Müller",    role:"UX Designer",            email:"sofia@example.com",   source:"Portfolio",  score:82, stage:"interview", skills:["Figma","Research","Design Sys"], applied:"Apr 4",  avatar:"S", color:"from-rose-600 to-rose-800",    resumeScore:84, interviewScore:82 },
  { id:"c6",  name:"Raj Krishnan",    role:"Backend Engineer",       email:"raj@example.com",     source:"LinkedIn",   score:79, stage:"sourced",   skills:["Java","Kafka","Postgres"],       applied:"Apr 6",  avatar:"R", color:"from-blue-600 to-blue-800",    resumeScore:0, interviewScore:0 },
  { id:"c7",  name:"Mei Lin",         role:"ML Engineer",            email:"mei@example.com",     source:"GitHub",     score:93, stage:"screening",  skills:["PyTorch","CUDA","LLMs"],         applied:"Apr 5",  avatar:"L", color:"from-violet-600 to-violet-800", resumeScore:94, interviewScore:0 },
  { id:"c8",  name:"Omar Hassan",     role:"Senior Frontend Eng",   email:"omar@example.com",    source:"AngelList",  score:85, stage:"offer",     skills:["Vue","GraphQL","AWS"],           applied:"Apr 2",  avatar:"O", color:"from-sky-600 to-sky-800",      resumeScore:87, interviewScore:85 },
]

export default function PipelinePage() {
  const [candidates, setCandidates] = useState<Candidate[]>(INITIAL_CANDIDATES)
  const [selected, setSelected] = useState<Candidate | null>(null)
  const [search, setSearch] = useState("")
  const [showUpload, setShowUpload] = useState(false)
  const [dragging, setDragging] = useState<string | null>(null)

  const filtered = candidates.filter(c =>
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    c.role.toLowerCase().includes(search.toLowerCase())
  )

  const byStage = (stage: Stage) => filtered.filter(c => c.stage === stage)

  const moveCandidate = (candidateId: string, targetStage: Stage) => {
    setCandidates(prev =>
      prev.map(c => c.id === candidateId ? { ...c, stage: targetStage } : c)
    )
    setDragging(null)
  }

  const STAGE_COUNT_COLOR: Record<Stage, string> = {
    sourced:   "bg-zinc-800 text-zinc-400",
    screening: "bg-blue-500/20 text-blue-300",
    interview: "bg-purple-500/20 text-purple-300",
    offer:     "bg-amber-500/20 text-amber-300",
    hired:     "bg-emerald-500/20 text-emerald-300",
  }

  return (
    <AppShell>
      <div className="flex flex-col h-screen px-6 py-6">

        {/* Header */}
        <div className="flex items-center justify-between mb-6 flex-shrink-0">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white">Talent Pipeline</h1>
            <p className="text-sm text-zinc-500 mt-0.5">{candidates.length} candidates tracked · AI scoring enabled</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-600" />
              <input
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Search candidates..."
                className="pl-9 pr-3 py-1.5 text-sm rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-300 placeholder:text-zinc-600 focus:border-blue-500 outline-none w-52"
              />
            </div>
            <button
              onClick={() => setShowUpload(true)}
              className="flex items-center gap-1.5 border border-zinc-700 hover:border-zinc-500 text-zinc-300 hover:text-white text-sm font-medium px-3 py-1.5 rounded-lg transition-colors"
            >
              <Upload className="w-4 h-4" /> Upload Resume
            </button>
            <button className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium px-4 py-1.5 rounded-lg transition-colors">
              <Plus className="w-4 h-4" /> Add Candidate
            </button>
          </div>
        </div>

        {/* Stats strip */}
        <div className="flex items-center gap-4 mb-6 flex-shrink-0">
          {STAGES.map(s => {
            const count = byStage(s.id).length
            return (
              <div key={s.id} className="flex items-center gap-2">
                <span className={`text-xs font-medium ${s.color}`}>{s.label}</span>
                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${STAGE_COUNT_COLOR[s.id]}`}>{count}</span>
                {s.id !== "hired" && <ChevronRight className="w-3 h-3 text-zinc-800" />}
              </div>
            )
          })}
        </div>

        {/* Pipeline board */}
        <div className="flex gap-3 flex-1 overflow-x-auto pb-4">
          {STAGES.map(stage => {
            const stageCandidates = byStage(stage.id)
            return (
              <div
                key={stage.id}
                className="flex-1 min-w-[220px] flex flex-col"
                onDragOver={e => { e.preventDefault() }}
                onDrop={e => {
                  e.preventDefault()
                  if (dragging) moveCandidate(dragging, stage.id)
                }}
              >
                {/* Stage header */}
                <div className="pipeline-stage-header flex items-center justify-between mb-2 px-1">
                  <span className={`font-bold ${stage.color}`}>{stage.label}</span>
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${STAGE_COUNT_COLOR[stage.id]}`}>
                    {stageCandidates.length}
                  </span>
                </div>

                {/* Candidates */}
                <div className="flex-1 space-y-2 overflow-y-auto">
                  {stageCandidates.map(c => (
                    <div
                      key={c.id}
                      draggable
                      onDragStart={() => setDragging(c.id)}
                      onDragEnd={() => setDragging(null)}
                      onClick={() => setSelected(c)}
                      className={`p-3 rounded-xl border cursor-pointer transition-all select-none ${
                        dragging === c.id
                          ? "opacity-40 scale-95"
                          : "border-zinc-800 bg-zinc-900/60 hover:bg-zinc-900 hover:border-zinc-700"
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <div className={`w-7 h-7 rounded-full bg-gradient-to-br ${c.color} flex items-center justify-center text-xs font-bold text-white flex-shrink-0`}>
                          {c.avatar}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-xs font-semibold text-zinc-200 truncate">{c.name}</div>
                          <div className="text-[10px] text-zinc-600 truncate">{c.role}</div>
                        </div>
                      </div>

                      {c.score > 0 && (
                        <div className="flex items-center gap-1.5 mb-2">
                          <div className="progress-track flex-1">
                            <div
                              className={`progress-fill ${c.score >= 90 ? "green" : c.score >= 75 ? "" : "amber"}`}
                              style={{ width: `${c.score}%` }}
                            />
                          </div>
                          <span className="text-[10px] font-mono text-zinc-500">{c.score}</span>
                        </div>
                      )}

                      <div className="flex items-center gap-1 flex-wrap">
                        {c.skills.slice(0, 2).map(sk => (
                          <span key={sk} className="text-[9px] text-zinc-600 bg-zinc-800 px-1.5 py-0.5 rounded">{sk}</span>
                        ))}
                        {c.skills.length > 2 && (
                          <span className="text-[9px] text-zinc-700">+{c.skills.length - 2}</span>
                        )}
                      </div>

                      <div className="flex items-center justify-between mt-2">
                        <span className="text-[9px] text-zinc-700">{c.source} · {c.applied}</span>
                        {stage.id !== "hired" && stage.id !== "offer" && (
                          <button
                            onClick={e => {
                              e.stopPropagation()
                              const next = STAGES[STAGES.findIndex(s => s.id === stage.id) + 1]?.id
                              if (next) moveCandidate(c.id, next)
                            }}
                            className="text-[9px] text-blue-400 hover:text-blue-300 transition-colors"
                          >
                            Advance →
                          </button>
                        )}
                      </div>
                    </div>
                  ))}

                  {stageCandidates.length === 0 && (
                    <div className="py-8 text-center border-2 border-dashed border-zinc-800 rounded-xl">
                      <p className="text-[10px] text-zinc-700">Drop candidates here</p>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        {/* Candidate detail panel */}
        {selected && (
          <div className="fixed inset-y-0 right-0 w-96 bg-zinc-950 border-l border-zinc-800 z-50 overflow-y-auto">
            <div className="px-5 py-4 border-b border-zinc-800 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">Candidate Profile</h3>
              <button onClick={() => setSelected(null)}><X className="w-4 h-4 text-zinc-600" /></button>
            </div>
            <div className="px-5 py-5">
              {/* Avatar & name */}
              <div className="flex items-center gap-4 mb-5">
                <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${selected.color} flex items-center justify-center text-lg font-bold text-white`}>
                  {selected.avatar}
                </div>
                <div>
                  <h4 className="text-base font-bold text-white">{selected.name}</h4>
                  <p className="text-sm text-zinc-500">{selected.role}</p>
                  <p className="text-xs text-zinc-700">{selected.email}</p>
                </div>
              </div>

              {/* Stage */}
              <div className="mb-4">
                <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-600 mb-2">Move Stage</p>
                <div className="flex gap-1.5 flex-wrap">
                  {STAGES.map(s => (
                    <button
                      key={s.id}
                      onClick={() => {
                        moveCandidate(selected.id, s.id)
                        setSelected(c => c ? { ...c, stage: s.id } : null)
                      }}
                      className={`text-xs px-2.5 py-1 rounded-full border transition-colors ${
                        selected.stage === s.id
                          ? "border-blue-500 bg-blue-500/20 text-blue-300"
                          : "border-zinc-800 text-zinc-500 hover:border-zinc-600"
                      }`}
                    >
                      {s.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Scores */}
              {selected.score > 0 && (
                <div className="border border-zinc-800 rounded-xl p-4 mb-4">
                  <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-600 mb-3">AI Scores</p>
                  <div className="space-y-3">
                    {selected.resumeScore ? (
                      <div className="flex items-center gap-3">
                        <FileText className="w-3.5 h-3.5 text-zinc-600 flex-shrink-0" />
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-[10px] text-zinc-500">Resume Score</span>
                            <span className="text-[10px] font-mono text-zinc-300">{selected.resumeScore}</span>
                          </div>
                          <div className="progress-track">
                            <div className="progress-fill green" style={{ width: `${selected.resumeScore}%` }} />
                          </div>
                        </div>
                      </div>
                    ) : null}
                    {selected.interviewScore ? (
                      <div className="flex items-center gap-3">
                        <MessageSquare className="w-3.5 h-3.5 text-zinc-600 flex-shrink-0" />
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-[10px] text-zinc-500">Interview Score</span>
                            <span className="text-[10px] font-mono text-zinc-300">{selected.interviewScore}</span>
                          </div>
                          <div className="progress-track">
                            <div className="progress-fill" style={{ width: `${selected.interviewScore}%` }} />
                          </div>
                        </div>
                      </div>
                    ) : null}
                    <div className="flex items-center gap-3">
                      <Star className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-[10px] text-zinc-500">Overall</span>
                          <span className="text-[10px] font-mono text-white font-bold">{selected.score}</span>
                        </div>
                        <div className="progress-track">
                          <div className={`progress-fill ${selected.score >= 90 ? "green" : ""}`} style={{ width: `${selected.score}%` }} />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Skills */}
              <div className="mb-4">
                <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-600 mb-2">Skills</p>
                <div className="flex flex-wrap gap-1.5">
                  {selected.skills.map(sk => (
                    <span key={sk} className="text-xs text-zinc-400 bg-zinc-800 border border-zinc-700 px-2 py-0.5 rounded-full">{sk}</span>
                  ))}
                </div>
              </div>

              {/* Details */}
              <div className="border border-zinc-800 rounded-xl p-4 mb-5">
                {[
                  { label: "Source",   val: selected.source },
                  { label: "Applied",  val: selected.applied },
                  { label: "Email",    val: selected.email },
                ].map(r => (
                  <div key={r.label} className="flex items-center gap-3 py-1.5 border-b border-zinc-800/50 last:border-0">
                    <span className="text-[10px] text-zinc-600 w-16">{r.label}</span>
                    <span className="text-xs text-zinc-400">{r.val}</span>
                  </div>
                ))}
              </div>

              {/* Actions */}
              <div className="space-y-2">
                <button className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-colors">
                  Start AI Interview
                </button>
                <button className="w-full py-2.5 border border-zinc-700 hover:border-zinc-500 text-zinc-300 text-sm font-medium rounded-lg transition-colors">
                  Send Offer Letter
                </button>
                <button className="w-full py-2.5 border border-red-900/50 hover:border-red-700 text-red-400 text-sm font-medium rounded-lg transition-colors">
                  Reject Candidate
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Upload resume modal */}
        {showUpload && <UploadResumeModal onClose={() => setShowUpload(false)} />}
      </div>
    </AppShell>
  )
}

function UploadResumeModal({ onClose }: { onClose: () => void }) {
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [file, setFile] = useState<File | null>(null)

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)
    // Simulate API call
    await new Promise(r => setTimeout(r, 1500))
    setLoading(false)
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl w-full max-w-md">
        <div className="flex items-center justify-between px-5 py-4 border-b border-zinc-800">
          <h3 className="text-sm font-semibold text-white">Upload Resume for AI Analysis</h3>
          <button onClick={onClose}><X className="w-4 h-4 text-zinc-600" /></button>
        </div>
        <div className="px-5 py-5">
          <div
            onDragOver={e => { e.preventDefault(); setDragging(true) }}
            onDragLeave={() => setDragging(false)}
            onDrop={e => {
              e.preventDefault()
              setDragging(false)
              const f = e.dataTransfer.files[0]
              if (f) setFile(f)
            }}
            className={`border-2 border-dashed rounded-xl py-12 text-center transition-colors ${
              dragging ? "border-blue-500 bg-blue-500/10" : "border-zinc-700"
            }`}
          >
            <Upload className="w-8 h-8 text-zinc-600 mx-auto mb-3" />
            <p className="text-sm text-zinc-400 mb-1">
              {file ? file.name : "Drop resume here, or click to browse"}
            </p>
            <p className="text-[11px] text-zinc-700">PDF, DOCX, TXT — max 10MB</p>
            <input
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={e => e.target.files?.[0] && setFile(e.target.files[0])}
              className="absolute inset-0 opacity-0 cursor-pointer"
              style={{ position: "absolute" }}
            />
          </div>
          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className="w-full mt-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-40"
          >
            {loading ? "Analyzing with AI…" : "Analyze Resume"}
          </button>
        </div>
      </div>
    </div>
  )
}
