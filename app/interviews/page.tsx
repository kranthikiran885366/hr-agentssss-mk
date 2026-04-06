"use client"

import { useState, useEffect } from "react"
import { AppShell } from "@/components/layout/app-shell"
import {
  Plus, Search, MessageSquare, Phone, Video,
  Play, Eye, Clock, User, ChevronDown, Filter, X,
  Mic, Brain, Star
} from "lucide-react"
import Link from "next/link"

type InterviewStatus = "active" | "completed" | "scheduled" | "cancelled"
type InterviewType   = "technical" | "behavioral" | "screening" | "comprehensive"
type InterviewMode   = "chat" | "voice" | "video"

interface InterviewSession {
  id: string
  candidateName: string
  candidateEmail: string
  position: string
  type: InterviewType
  mode: InterviewMode
  status: InterviewStatus
  startTime: string
  duration: number
  score: number
  questionsAnswered: number
  totalQuestions: number
  scores: { communication: number; technical: number; cultural: number }
}

const MOCK: InterviewSession[] = [
  {
    id: "iv-001", candidateName: "Priya Sharma", candidateEmail: "priya@example.com",
    position: "Senior Frontend Engineer", type: "technical", mode: "chat", status: "completed",
    startTime: "2026-04-06T09:00:00Z", duration: 2400, score: 87.4,
    questionsAnswered: 12, totalQuestions: 12,
    scores: { communication: 91, technical: 85, cultural: 88 },
  },
  {
    id: "iv-002", candidateName: "Marcus Johnson", candidateEmail: "marcus@example.com",
    position: "Product Manager", type: "behavioral", mode: "voice", status: "active",
    startTime: "2026-04-06T11:30:00Z", duration: 1800, score: 72.1,
    questionsAnswered: 7, totalQuestions: 10,
    scores: { communication: 78, technical: 65, cultural: 74 },
  },
  {
    id: "iv-003", candidateName: "Aisha Okonkwo", candidateEmail: "aisha@example.com",
    position: "DevOps Engineer", type: "comprehensive", mode: "video", status: "scheduled",
    startTime: "2026-04-06T14:00:00Z", duration: 0, score: 0,
    questionsAnswered: 0, totalQuestions: 15,
    scores: { communication: 0, technical: 0, cultural: 0 },
  },
  {
    id: "iv-004", candidateName: "Daniel Park", candidateEmail: "daniel@example.com",
    position: "Data Scientist", type: "technical", mode: "chat", status: "completed",
    startTime: "2026-04-05T15:00:00Z", duration: 3600, score: 93.2,
    questionsAnswered: 14, totalQuestions: 14,
    scores: { communication: 89, technical: 96, cultural: 92 },
  },
  {
    id: "iv-005", candidateName: "Sofia Rossi", candidateEmail: "sofia@example.com",
    position: "UX Designer", type: "behavioral", mode: "video", status: "completed",
    startTime: "2026-04-05T10:00:00Z", duration: 2700, score: 79.6,
    questionsAnswered: 10, totalQuestions: 10,
    scores: { communication: 85, technical: 72, cultural: 82 },
  },
  {
    id: "iv-006", candidateName: "Raj Patel", candidateEmail: "raj@example.com",
    position: "Backend Engineer", type: "screening", mode: "chat", status: "cancelled",
    startTime: "2026-04-04T09:00:00Z", duration: 0, score: 0,
    questionsAnswered: 0, totalQuestions: 8,
    scores: { communication: 0, technical: 0, cultural: 0 },
  },
]

const STATUS_PILL: Record<InterviewStatus, string> = {
  active:    "pill pill-green",
  completed: "pill pill-blue",
  scheduled: "pill pill-amber",
  cancelled: "pill pill-gray",
}

const TYPE_COLOR: Record<InterviewType, string> = {
  technical:     "text-blue-400",
  behavioral:    "text-purple-400",
  screening:     "text-amber-400",
  comprehensive: "text-emerald-400",
}

const MODE_ICON: Record<InterviewMode, any> = {
  chat:  MessageSquare,
  voice: Mic,
  video: Video,
}

function ScoreBar({ value, label }: { value: number; label: string }) {
  const color = value >= 85 ? "green" : value >= 70 ? "" : "amber"
  return (
    <div className="flex items-center gap-2">
      <span className="text-[10px] text-zinc-600 w-24 flex-shrink-0">{label}</span>
      <div className="progress-track flex-1">
        <div className={`progress-fill ${color}`} style={{ width: `${value}%` }} />
      </div>
      <span className="text-[10px] text-zinc-400 font-mono w-7 text-right">{value}</span>
    </div>
  )
}

export default function InterviewsPage() {
  const [sessions, setSessions] = useState<InterviewSession[]>(MOCK)
  const [search, setSearch] = useState("")
  const [filterStatus, setFilterStatus] = useState("all")
  const [filterType, setFilterType] = useState("all")
  const [expanded, setExpanded] = useState<string | null>(null)
  const [showNew, setShowNew] = useState(false)

  const filtered = sessions.filter(s => {
    const q = search.toLowerCase()
    return (
      (s.candidateName.toLowerCase().includes(q) || s.position.toLowerCase().includes(q)) &&
      (filterStatus === "all" || s.status === filterStatus) &&
      (filterType === "all"   || s.type === filterType)
    )
  })

  const formatDur = (sec: number) => `${Math.floor(sec/60)}m ${sec%60}s`

  return (
    <AppShell>
      <div className="px-6 py-6">

        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white">Interview Sessions</h1>
            <p className="text-sm text-zinc-500 mt-0.5">AI-powered screening and evaluation</p>
          </div>
          <button
            onClick={() => setShowNew(true)}
            className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" /> New Interview
          </button>
        </div>

        {/* Summary strip */}
        <div className="border border-zinc-800 rounded-xl overflow-hidden mb-6">
          <div className="flex divide-x divide-zinc-800">
            {[
              { label: "Total",     value: sessions.length,                             color: "text-white" },
              { label: "Active",    value: sessions.filter(s=>s.status==="active").length,    color: "text-emerald-400" },
              { label: "Completed", value: sessions.filter(s=>s.status==="completed").length, color: "text-blue-400" },
              { label: "Scheduled", value: sessions.filter(s=>s.status==="scheduled").length, color: "text-amber-400" },
              { label: "Avg Score", value: Math.round(sessions.filter(s=>s.score>0).reduce((a,s)=>a+s.score,0)/sessions.filter(s=>s.score>0).length) + "%", color: "text-purple-400" },
            ].map((m, i) => (
              <div key={i} className="flex-1 px-5 py-3 text-center">
                <div className={`text-xl font-bold ${m.color}`}>{m.value}</div>
                <div className="text-[10px] text-zinc-600 mt-0.5">{m.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-3 mb-5">
          <div className="relative flex-1 max-w-xs">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-600" />
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search candidates or roles..."
              className="w-full pl-9 pr-3 py-1.5 text-sm rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-300 placeholder:text-zinc-600 focus:border-blue-500 focus:ring-1 focus:ring-blue-500/20 outline-none"
            />
          </div>
          <select
            value={filterStatus}
            onChange={e => setFilterStatus(e.target.value)}
            className="px-3 py-1.5 text-sm rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-400 outline-none"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
            <option value="scheduled">Scheduled</option>
            <option value="cancelled">Cancelled</option>
          </select>
          <select
            value={filterType}
            onChange={e => setFilterType(e.target.value)}
            className="px-3 py-1.5 text-sm rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-400 outline-none"
          >
            <option value="all">All Types</option>
            <option value="technical">Technical</option>
            <option value="behavioral">Behavioral</option>
            <option value="screening">Screening</option>
            <option value="comprehensive">Comprehensive</option>
          </select>
          <span className="text-xs text-zinc-600">{filtered.length} sessions</span>
        </div>

        {/* Table */}
        <div className="border border-zinc-800 rounded-xl overflow-hidden">
          <table className="data-table w-full">
            <thead>
              <tr className="bg-zinc-900/60">
                <th className="w-8" />
                <th>Candidate</th>
                <th>Position</th>
                <th>Type · Mode</th>
                <th>Status</th>
                <th>Score</th>
                <th>Date</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(s => {
                const ModeIcon = MODE_ICON[s.mode]
                const isExpanded = expanded === s.id
                return (
                  <>
                    <tr
                      key={s.id}
                      className="cursor-pointer"
                      onClick={() => setExpanded(isExpanded ? null : s.id)}
                    >
                      <td className="text-center">
                        <ChevronDown className={`w-3.5 h-3.5 text-zinc-600 transition-transform ${isExpanded ? "rotate-180" : ""}`} />
                      </td>
                      <td>
                        <div className="flex items-center gap-2.5">
                          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center text-xs font-bold text-white flex-shrink-0">
                            {s.candidateName.charAt(0)}
                          </div>
                          <div>
                            <div className="text-sm font-medium text-zinc-200">{s.candidateName}</div>
                            <div className="text-[11px] text-zinc-600">{s.candidateEmail}</div>
                          </div>
                        </div>
                      </td>
                      <td className="text-sm text-zinc-400">{s.position}</td>
                      <td>
                        <div className="flex items-center gap-2">
                          <span className={`text-xs font-medium capitalize ${TYPE_COLOR[s.type]}`}>{s.type}</span>
                          <span className="text-zinc-700">·</span>
                          <ModeIcon className="w-3.5 h-3.5 text-zinc-500" />
                        </div>
                      </td>
                      <td>
                        <span className={STATUS_PILL[s.status]}>{s.status}</span>
                      </td>
                      <td>
                        {s.score > 0 ? (
                          <div className="flex items-center gap-1.5">
                            <span className={`text-sm font-bold ${s.score >= 85 ? "text-emerald-400" : s.score >= 70 ? "text-amber-400" : "text-red-400"}`}>
                              {s.score.toFixed(1)}
                            </span>
                            <span className="text-[10px] text-zinc-600">/ 100</span>
                          </div>
                        ) : (
                          <span className="text-zinc-700 text-xs">—</span>
                        )}
                      </td>
                      <td className="text-xs text-zinc-600">
                        {new Date(s.startTime).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                      </td>
                      <td onClick={e => e.stopPropagation()}>
                        <div className="flex items-center justify-end gap-2">
                          {s.status === "active" && (
                            <Link href={`/interview/${s.id}`}
                              className="flex items-center gap-1 text-xs font-medium bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 px-2.5 py-1 rounded-md transition-colors"
                            >
                              <Play className="w-3 h-3" /> Join
                            </Link>
                          )}
                          {s.status === "completed" && (
                            <button className="flex items-center gap-1 text-xs font-medium bg-zinc-800 hover:bg-zinc-700 text-zinc-300 px-2.5 py-1 rounded-md transition-colors">
                              <Eye className="w-3 h-3" /> Report
                            </button>
                          )}
                          {s.status === "scheduled" && (
                            <button className="flex items-center gap-1 text-xs font-medium bg-amber-500/15 hover:bg-amber-500/25 text-amber-300 px-2.5 py-1 rounded-md transition-colors">
                              <Play className="w-3 h-3" /> Start
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                    {isExpanded && s.status === "completed" && (
                      <tr key={`${s.id}-exp`} className="bg-zinc-950/50">
                        <td colSpan={8} className="px-8 py-4">
                          <div className="flex gap-8">
                            <div className="flex-1">
                              <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-600 mb-3">AI Score Breakdown</p>
                              <div className="space-y-2">
                                <ScoreBar value={s.scores.communication} label="Communication" />
                                <ScoreBar value={s.scores.technical}     label="Technical" />
                                <ScoreBar value={s.scores.cultural}      label="Cultural Fit" />
                              </div>
                            </div>
                            <div className="flex-1">
                              <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-600 mb-3">Session Info</p>
                              <div className="space-y-1.5">
                                {[
                                  { label: "Duration",    val: formatDur(s.duration) },
                                  { label: "Questions",   val: `${s.questionsAnswered}/${s.totalQuestions}` },
                                  { label: "Mode",        val: s.mode },
                                  { label: "Type",        val: s.type },
                                ].map(row => (
                                  <div key={row.label} className="flex items-center gap-4">
                                    <span className="text-[11px] text-zinc-600 w-20">{row.label}</span>
                                    <span className="text-[11px] text-zinc-400 capitalize">{row.val}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                            <div className="text-center flex flex-col items-center justify-center min-w-[100px]">
                              <div className="text-3xl font-black text-white mb-1">{s.score.toFixed(0)}</div>
                              <div className="text-[10px] text-zinc-600 uppercase tracking-widest mb-2">Overall Score</div>
                              <div className="flex">
                                {[1,2,3,4,5].map(star => (
                                  <Star key={star} className={`w-3 h-3 ${star <= Math.round(s.score/20) ? "text-amber-400 fill-amber-400" : "text-zinc-700"}`} />
                                ))}
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </>
                )
              })}
            </tbody>
          </table>

          {filtered.length === 0 && (
            <div className="py-16 text-center">
              <MessageSquare className="w-8 h-8 text-zinc-700 mx-auto mb-3" />
              <p className="text-sm text-zinc-500">No interviews found</p>
              <button
                onClick={() => setShowNew(true)}
                className="mt-4 text-sm text-blue-400 hover:text-blue-300 transition-colors"
              >
                Schedule your first interview →
              </button>
            </div>
          )}
        </div>

        {/* New interview modal */}
        {showNew && <NewInterviewModal onClose={() => setShowNew(false)} />}

      </div>
    </AppShell>
  )
}

function NewInterviewModal({ onClose }: { onClose: () => void }) {
  const [form, setForm] = useState({ name:"", email:"", position:"", type:"technical", mode:"chat" })
  const [loading, setLoading] = useState(false)

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await fetch("http://localhost:8000/interviews/start", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ candidate_name:form.name, candidate_email:form.email, position:form.position, interview_type:form.type, mode:form.mode }),
      })
    } catch {}
    setLoading(false)
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl w-full max-w-md">
        <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
          <h2 className="text-sm font-semibold text-white">Schedule Interview</h2>
          <button onClick={onClose} className="text-zinc-600 hover:text-zinc-300"><X className="w-4 h-4" /></button>
        </div>
        <form onSubmit={submit} className="px-6 py-5 space-y-4">
          {[
            { key:"name",     label:"Candidate Name", ph:"Full name" },
            { key:"email",    label:"Email",           ph:"candidate@email.com" },
            { key:"position", label:"Position",        ph:"e.g. Senior Engineer" },
          ].map(f => (
            <div key={f.key}>
              <label className="block text-xs font-medium text-zinc-400 mb-1.5">{f.label}</label>
              <input
                required
                value={(form as any)[f.key]}
                onChange={e => setForm(p => ({ ...p, [f.key]: e.target.value }))}
                placeholder={f.ph}
                className="w-full px-3 py-2 text-sm rounded-lg bg-zinc-800 border border-zinc-700 text-zinc-200 outline-none focus:border-blue-500"
              />
            </div>
          ))}
          <div className="flex gap-3">
            <div className="flex-1">
              <label className="block text-xs font-medium text-zinc-400 mb-1.5">Type</label>
              <select value={form.type} onChange={e => setForm(p=>({...p,type:e.target.value}))} className="w-full px-3 py-2 text-sm rounded-lg bg-zinc-800 border border-zinc-700 text-zinc-200 outline-none">
                <option value="technical">Technical</option>
                <option value="behavioral">Behavioral</option>
                <option value="screening">Screening</option>
                <option value="comprehensive">Comprehensive</option>
              </select>
            </div>
            <div className="flex-1">
              <label className="block text-xs font-medium text-zinc-400 mb-1.5">Mode</label>
              <select value={form.mode} onChange={e => setForm(p=>({...p,mode:e.target.value}))} className="w-full px-3 py-2 text-sm rounded-lg bg-zinc-800 border border-zinc-700 text-zinc-200 outline-none">
                <option value="chat">Chat</option>
                <option value="voice">Voice</option>
                <option value="video">Video</option>
              </select>
            </div>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
          >
            {loading ? "Starting…" : "Start AI Interview"}
          </button>
        </form>
      </div>
    </div>
  )
}
