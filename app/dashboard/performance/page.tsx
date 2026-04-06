"use client"

import { useState } from "react"
import { AppShell } from "@/components/layout/app-shell"
import {
  Plus, Target, TrendingUp, CheckCircle, Clock,
  Star, Award, ChevronRight, X, BarChart2, Users
} from "lucide-react"

const TEAM_MEMBERS = [
  { id:"t1", name:"Sarah Chen",    role:"Sr. Engineer",   dept:"Engineering", score:94, trend:+3, goals:5, done:4, avatar:"S", color:"from-blue-600 to-blue-800" },
  { id:"t2", name:"Marcus Johnson",role:"Product Mgr",    dept:"Product",     score:88, trend:+1, goals:4, done:3, avatar:"M", color:"from-purple-600 to-purple-800" },
  { id:"t3", name:"Aisha Okonkwo", role:"DevOps Engr",    dept:"Infra",       score:91, trend:+5, goals:6, done:5, avatar:"A", color:"from-emerald-600 to-emerald-800" },
  { id:"t4", name:"Daniel Park",   role:"Data Scientist", dept:"Data",        score:97, trend:+2, goals:5, done:5, avatar:"D", color:"from-amber-600 to-amber-800" },
  { id:"t5", name:"Sofia Rossi",   role:"UX Designer",    dept:"Design",      score:82, trend:-2, goals:4, done:3, avatar:"S2",color:"from-rose-600 to-rose-800" },
]

const GOALS = [
  { id:"g1", owner:"Sarah Chen",    title:"Launch auth microservice",         due:"Apr 30", progress:80, status:"on-track",  priority:"high",   category:"technical" },
  { id:"g2", owner:"Sarah Chen",    title:"Reduce API p99 latency < 100ms",   due:"May 15", progress:55, status:"at-risk",   priority:"medium", category:"performance" },
  { id:"g3", owner:"Marcus Johnson",title:"Ship Q2 product roadmap",           due:"Apr 15", progress:90, status:"on-track",  priority:"high",   category:"strategy" },
  { id:"g4", owner:"Marcus Johnson",title:"NPS improvement to 72+",            due:"Jun 30", progress:40, status:"at-risk",   priority:"medium", category:"growth" },
  { id:"g5", owner:"Aisha Okonkwo", title:"99.9% infrastructure uptime",       due:"Jun 30", progress:95, status:"on-track",  priority:"high",   category:"reliability" },
  { id:"g6", owner:"Daniel Park",   title:"Build churn prediction model",      due:"May 20", progress:100,status:"complete",  priority:"high",   category:"data" },
  { id:"g7", owner:"Sofia Rossi",   title:"Design system v3 launch",           due:"May 01", progress:30, status:"at-risk",   priority:"high",   category:"design" },
  { id:"g8", owner:"Aisha Okonkwo", title:"Zero-downtime deployment pipeline", due:"Apr 20", progress:70, status:"on-track",  priority:"medium", category:"devops" },
]

const REVIEWS = [
  { id:"r1", reviewer:"AI + Manager", reviewee:"Sarah Chen",    period:"Q1 2026", status:"complete", score:94, date:"Mar 31" },
  { id:"r2", reviewer:"AI + Manager", reviewee:"Daniel Park",   period:"Q1 2026", status:"complete", score:97, date:"Mar 31" },
  { id:"r3", reviewer:"AI + Manager", reviewee:"Aisha Okonkwo", period:"Q1 2026", status:"draft",    score:91, date:"Apr 10" },
  { id:"r4", reviewer:"AI + Manager", reviewee:"Marcus Johnson", period:"Q1 2026", status:"draft",    score:88, date:"Apr 10" },
  { id:"r5", reviewer:"AI + Manager", reviewee:"Sofia Rossi",   period:"Q1 2026", status:"pending",  score:0,  date:"Apr 15" },
]

const STATUS_PILL: Record<string, string> = {
  "on-track": "pill pill-green",
  "at-risk":  "pill pill-amber",
  "complete": "pill pill-blue",
  "pending":  "pill pill-gray",
  "draft":    "pill pill-purple",
}

type View = "goals" | "team" | "reviews"

export default function PerformancePage() {
  const [view, setView] = useState<View>("goals")
  const [showAdd, setShowAdd] = useState(false)
  const [selectedMember, setSelectedMember] = useState<typeof TEAM_MEMBERS[0] | null>(null)

  const onTrack    = GOALS.filter(g => g.status === "on-track").length
  const atRisk     = GOALS.filter(g => g.status === "at-risk").length
  const complete   = GOALS.filter(g => g.status === "complete").length
  const avgScore   = Math.round(TEAM_MEMBERS.reduce((a,m) => a+m.score, 0) / TEAM_MEMBERS.length)

  return (
    <AppShell>
      <div className="px-6 py-6">

        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white">Performance</h1>
            <p className="text-sm text-zinc-500 mt-0.5">Goals, reviews and team analytics</p>
          </div>
          <button
            onClick={() => setShowAdd(true)}
            className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" /> New Goal
          </button>
        </div>

        {/* Stat strip */}
        <div className="border border-zinc-800 rounded-xl overflow-hidden mb-6">
          <div className="flex divide-x divide-zinc-800">
            {[
              { label: "Avg Score",     value: `${avgScore}%`, color: "text-emerald-400" },
              { label: "Goals On-Track",value: onTrack,        color: "text-blue-400" },
              { label: "At Risk",       value: atRisk,         color: "text-amber-400" },
              { label: "Completed",     value: complete,       color: "text-white" },
              { label: "Team Members",  value: TEAM_MEMBERS.length, color: "text-purple-400" },
            ].map((m, i) => (
              <div key={i} className="flex-1 min-w-[120px] px-5 py-3 text-center">
                <div className={`text-xl font-bold ${m.color}`}>{m.value}</div>
                <div className="text-[10px] text-zinc-600 mt-0.5">{m.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* View toggle */}
        <div className="flex items-center gap-1 mb-5 border border-zinc-800 rounded-lg p-1 w-fit">
          {([
            { id:"goals" as View,   icon: Target,   label: "Goals" },
            { id:"team"  as View,   icon: Users,    label: "Team Scores" },
            { id:"reviews" as View, icon: BarChart2, label: "Reviews" },
          ]).map(v => (
            <button
              key={v.id}
              onClick={() => setView(v.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                view === v.id ? "bg-zinc-800 text-white" : "text-zinc-500 hover:text-zinc-300"
              }`}
            >
              <v.icon className="w-3.5 h-3.5" /> {v.label}
            </button>
          ))}
        </div>

        {/* GOALS view */}
        {view === "goals" && (
          <div className="border border-zinc-800 rounded-xl overflow-hidden">
            <table className="data-table w-full">
              <thead>
                <tr className="bg-zinc-900/60">
                  <th>Goal</th>
                  <th>Owner</th>
                  <th>Category</th>
                  <th>Priority</th>
                  <th className="w-48">Progress</th>
                  <th>Status</th>
                  <th>Due</th>
                </tr>
              </thead>
              <tbody>
                {GOALS.map(g => (
                  <tr key={g.id}>
                    <td className="font-medium text-zinc-200 max-w-xs">{g.title}</td>
                    <td className="text-zinc-500 text-xs">{g.owner}</td>
                    <td>
                      <span className="text-[10px] text-zinc-500 bg-zinc-800 px-1.5 py-0.5 rounded capitalize">{g.category}</span>
                    </td>
                    <td>
                      <span className={`pill ${g.priority === "high" ? "pill-red" : g.priority === "medium" ? "pill-amber" : "pill-gray"}`}>
                        {g.priority}
                      </span>
                    </td>
                    <td>
                      <div className="flex items-center gap-2">
                        <div className="progress-track flex-1">
                          <div
                            className={`progress-fill ${g.progress === 100 ? "green" : g.status === "at-risk" ? "amber" : ""}`}
                            style={{ width: `${g.progress}%` }}
                          />
                        </div>
                        <span className="text-[10px] text-zinc-500 font-mono w-8 text-right">{g.progress}%</span>
                      </div>
                    </td>
                    <td><span className={STATUS_PILL[g.status]}>{g.status}</span></td>
                    <td className="text-xs text-zinc-600">{g.due}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* TEAM view — ranked list */}
        {view === "team" && (
          <div className="border border-zinc-800 rounded-xl overflow-hidden">
            <div className="px-5 py-3 border-b border-zinc-800 flex items-center justify-between">
              <span className="text-xs font-semibold text-zinc-500 uppercase tracking-widest">Team Performance Ranking</span>
              <span className="text-[10px] text-zinc-700">Q2 2026</span>
            </div>
            {TEAM_MEMBERS
              .slice()
              .sort((a, b) => b.score - a.score)
              .map((m, i) => (
                <div
                  key={m.id}
                  className="data-row cursor-pointer"
                  onClick={() => setSelectedMember(m)}
                >
                  <div className="flex items-center gap-4 w-full">
                    {/* Rank */}
                    <div className={`text-sm font-black w-8 text-center ${
                      i === 0 ? "text-amber-400" : i === 1 ? "text-zinc-400" : i === 2 ? "text-amber-700" : "text-zinc-700"
                    }`}>
                      #{i+1}
                    </div>
                    {/* Avatar */}
                    <div className={`w-9 h-9 rounded-full bg-gradient-to-br ${m.color} flex items-center justify-center text-sm font-bold text-white flex-shrink-0`}>
                      {m.avatar.charAt(0)}
                    </div>
                    {/* Name & role */}
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-semibold text-white">{m.name}</div>
                      <div className="text-[11px] text-zinc-600">{m.dept} · {m.role}</div>
                    </div>
                    {/* Goals progress */}
                    <div className="text-center mx-4">
                      <div className="text-sm font-bold text-zinc-300">{m.done}/{m.goals}</div>
                      <div className="text-[10px] text-zinc-600">Goals</div>
                    </div>
                    {/* Score bar */}
                    <div className="w-40">
                      <div className="flex items-center gap-2">
                        <div className="progress-track flex-1">
                          <div
                            className={`progress-fill ${m.score >= 90 ? "green" : ""}`}
                            style={{ width: `${m.score}%` }}
                          />
                        </div>
                        <span className="text-sm font-bold text-white w-10 text-right">{m.score}</span>
                      </div>
                    </div>
                    {/* Trend */}
                    <div className={`text-xs font-semibold w-14 text-right ${m.trend > 0 ? "text-emerald-400" : "text-red-400"}`}>
                      {m.trend > 0 ? "+" : ""}{m.trend}%
                    </div>
                    {/* Stars */}
                    <div className="flex gap-0.5 ml-2">
                      {[1,2,3,4,5].map(s => (
                        <Star key={s} className={`w-3 h-3 ${s <= Math.round(m.score/20) ? "text-amber-400 fill-amber-400" : "text-zinc-700"}`} />
                      ))}
                    </div>
                    <ChevronRight className="w-4 h-4 text-zinc-700 ml-2" />
                  </div>
                </div>
              ))
            }
          </div>
        )}

        {/* REVIEWS view */}
        {view === "reviews" && (
          <div className="border border-zinc-800 rounded-xl overflow-hidden">
            <table className="data-table w-full">
              <thead>
                <tr className="bg-zinc-900/60">
                  <th>Employee</th>
                  <th>Reviewer</th>
                  <th>Period</th>
                  <th>Status</th>
                  <th>AI Score</th>
                  <th>Due / Done</th>
                  <th className="text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {REVIEWS.map(r => (
                  <tr key={r.id}>
                    <td className="font-medium text-zinc-200">{r.reviewee}</td>
                    <td className="text-xs text-zinc-500">{r.reviewer}</td>
                    <td className="text-xs text-zinc-500">{r.period}</td>
                    <td><span className={STATUS_PILL[r.status]}>{r.status}</span></td>
                    <td>
                      {r.score > 0 ? (
                        <span className={`font-bold ${r.score >= 90 ? "text-emerald-400" : r.score >= 80 ? "text-blue-400" : "text-amber-400"}`}>{r.score}</span>
                      ) : (
                        <span className="text-zinc-700">—</span>
                      )}
                    </td>
                    <td className="text-xs text-zinc-600">{r.date}</td>
                    <td className="text-right">
                      <button className="text-xs text-blue-400 hover:text-blue-300 transition-colors">
                        {r.status === "complete" ? "View" : "Review →"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Add goal modal */}
        {showAdd && (
          <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl w-full max-w-sm">
              <div className="flex items-center justify-between px-5 py-4 border-b border-zinc-800">
                <h3 className="text-sm font-semibold text-white">New Goal</h3>
                <button onClick={() => setShowAdd(false)}><X className="w-4 h-4 text-zinc-600" /></button>
              </div>
              <div className="px-5 py-4 space-y-3">
                {["Goal title","Owner","Category","Due date"].map(f => (
                  <div key={f}>
                    <label className="block text-xs font-medium text-zinc-500 mb-1">{f}</label>
                    <input
                      type={f === "Due date" ? "date" : "text"}
                      className="w-full px-3 py-2 text-sm rounded-lg bg-zinc-800 border border-zinc-700 text-zinc-200 outline-none focus:border-blue-500"
                    />
                  </div>
                ))}
                <div>
                  <label className="block text-xs font-medium text-zinc-500 mb-1">Priority</label>
                  <select className="w-full px-3 py-2 text-sm rounded-lg bg-zinc-800 border border-zinc-700 text-zinc-200 outline-none">
                    <option>High</option><option>Medium</option><option>Low</option>
                  </select>
                </div>
                <button
                  onClick={() => setShowAdd(false)}
                  className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-colors mt-2"
                >
                  Create Goal
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </AppShell>
  )
}
