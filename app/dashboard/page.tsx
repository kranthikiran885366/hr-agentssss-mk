"use client"

import { useState, useEffect } from "react"
import { AppShell } from "@/components/layout/app-shell"
import {
  Users, MessageSquare, Zap, TrendingUp, Activity,
  RefreshCw, ArrowUp, ArrowDown, Bot, FileText,
  Clock, CheckCircle, AlertCircle, GitBranch
} from "lucide-react"

const ACTIVITY_FEED = [
  { id:1,  time:"2 min ago",  actor:"Resume Agent",   action:"Scored 12 new applications for Senior Engineer",  status:"done",    icon:FileText,     color:"blue" },
  { id:2,  time:"8 min ago",  actor:"Interview AI",   action:"Completed screening call with Priya Sharma (87%)", status:"done",    icon:MessageSquare,color:"purple" },
  { id:3,  time:"14 min ago", actor:"Onboard Agent",  action:"Provisioned accounts for Marcus Johnson",           status:"done",    icon:CheckCircle,  color:"emerald" },
  { id:4,  time:"31 min ago", actor:"Perf Agent",     action:"Sent quarterly review reminders to 42 managers",   status:"done",    icon:TrendingUp,   color:"amber" },
  { id:5,  time:"1hr ago",    actor:"Resume Agent",   action:"Flagged duplicate application — auto-merged",       status:"alert",   icon:AlertCircle,  color:"rose" },
  { id:6,  time:"2hr ago",    actor:"Interview AI",   action:"No-show detected — rescheduled automatically",     status:"alert",   icon:Clock,        color:"amber" },
  { id:7,  time:"3hr ago",    actor:"Onboard Agent",  action:"Completed 5/24 onboarding steps for Sarah Chen",   status:"running", icon:Activity,     color:"blue" },
  { id:8,  time:"5hr ago",    actor:"Interview AI",   action:"Generated 3 offer letters pending approval",        status:"done",    icon:FileText,     color:"emerald" },
]

const AGENT_MODULES = [
  { name: "Resume Agent",    tasks: 47,  queue: 12, status: "active", latency: "120ms" },
  { name: "Interview AI",    tasks: 23,  queue: 4,  status: "active", latency: "89ms"  },
  { name: "Onboard Agent",   tasks: 8,   queue: 2,  status: "active", latency: "210ms" },
  { name: "Perf Agent",      tasks: 156, queue: 0,  status: "active", latency: "55ms"  },
  { name: "Comms Agent",     tasks: 342, queue: 18, status: "active", latency: "67ms"  },
  { name: "Exit Agent",      tasks: 2,   queue: 1,  status: "active", latency: "180ms" },
]

interface Metric {
  label: string; value: string; sub: string; trend: number; icon: any; color: string
}

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<Metric[]>([
    { label: "Total Employees",   value: "2,847", sub: "Active headcount",    trend: 4.2,  icon: Users,         color: "blue" },
    { label: "Active Processes",  value: "156",   sub: "Running automatically",trend: 12.1, icon: Bot,           color: "purple" },
    { label: "Automation Rate",   value: "98.7%", sub: "Fully automated",      trend: 1.3,  icon: Zap,           color: "emerald" },
    { label: "AI Interviews",     value: "23",    sub: "Today",                trend: 8.5,  icon: MessageSquare, color: "amber" },
    { label: "Onboardings",       value: "8",     sub: "In progress",          trend: 2.1,  icon: CheckCircle,   color: "blue" },
    { label: "Pipeline Active",   value: "94",    sub: "Candidates tracked",   trend: 15.3, icon: GitBranch,     color: "rose" },
  ])
  const [lastUpdated, setLastUpdated] = useState(new Date())
  const [loading, setLoading] = useState(false)

  const refresh = async () => {
    setLoading(true)
    try {
      const res = await fetch("http://localhost:8000/api/v1/analytics/dashboard")
      if (res.ok) {
        const data = await res.json()
        // Update with real data if available
      }
    } catch {}
    setLastUpdated(new Date())
    setTimeout(() => setLoading(false), 600)
  }

  const COLOR_MAP: Record<string, string> = {
    blue:   "text-blue-400",
    purple: "text-purple-400",
    emerald:"text-emerald-400",
    amber:  "text-amber-400",
    rose:   "text-rose-400",
  }

  const STATUS_DOT: Record<string, string> = {
    done:   "bg-emerald-500",
    alert:  "bg-amber-500",
    running:"bg-blue-500 animate-pulse-dot",
  }

  return (
    <AppShell>
      <div className="px-6 py-6">

        {/* Page header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white">Command Center</h1>
            <p className="text-sm text-zinc-500 mt-0.5">
              Updated {lastUpdated.toLocaleTimeString([], { hour:"2-digit", minute:"2-digit" })}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="agent-live text-xs text-emerald-400 font-medium">All agents live</div>
            <button
              onClick={refresh}
              disabled={loading}
              className="flex items-center gap-1.5 text-xs font-medium text-zinc-400 hover:text-white border border-zinc-800 hover:border-zinc-700 px-3 py-1.5 rounded-md transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </button>
          </div>
        </div>

        {/* Metrics — horizontal stat strip */}
        <div className="border border-zinc-800 rounded-xl overflow-hidden mb-8">
          <div className="flex overflow-x-auto divide-x divide-zinc-800">
            {metrics.map((m, i) => {
              const Icon = m.icon
              return (
                <div key={i} className="flex-1 min-w-[150px] px-5 py-4">
                  <div className="flex items-center gap-1.5 mb-2">
                    <Icon className={`w-3.5 h-3.5 ${COLOR_MAP[m.color]}`} />
                    <span className="text-[11px] text-zinc-500 font-medium">{m.label}</span>
                  </div>
                  <div className="stat-number text-2xl mb-0.5">{m.value}</div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-[11px] text-zinc-600">{m.sub}</span>
                    <span className={`text-[10px] font-semibold flex items-center gap-0.5 ${m.trend > 0 ? "text-emerald-500" : "text-rose-500"}`}>
                      {m.trend > 0 ? <ArrowUp className="w-2.5 h-2.5" /> : <ArrowDown className="w-2.5 h-2.5" />}
                      {Math.abs(m.trend)}%
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Two column layout: Activity feed + Agent status */}
        <div className="flex gap-6">

          {/* Activity timeline */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-zinc-300">Live Activity Feed</h2>
              <span className="text-xs text-zinc-600">{ACTIVITY_FEED.length} events today</span>
            </div>
            <div className="border border-zinc-800 rounded-xl overflow-hidden">
              <div className="timeline px-5 py-4">
                {ACTIVITY_FEED.map((item, i) => {
                  const Icon = item.icon
                  const ICON_MAP: Record<string, string> = {
                    blue: "text-blue-400 bg-blue-500/10",
                    purple: "text-purple-400 bg-purple-500/10",
                    emerald: "text-emerald-400 bg-emerald-500/10",
                    amber: "text-amber-400 bg-amber-500/10",
                    rose: "text-rose-400 bg-rose-500/10",
                  }
                  return (
                    <div key={item.id} className="timeline-item">
                      <div className={`timeline-dot ${item.status === "done" ? "done" : item.status === "running" ? "active" : ""}`} />
                      <div className="flex items-start gap-3">
                        <div className={`w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5 ${ICON_MAP[item.color]}`}>
                          <Icon className="w-3.5 h-3.5" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-0.5">
                            <span className="text-xs font-semibold text-zinc-300">{item.actor}</span>
                            <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${STATUS_DOT[item.status]}`} />
                          </div>
                          <p className="text-xs text-zinc-500 leading-relaxed">{item.action}</p>
                        </div>
                        <span className="text-[10px] text-zinc-700 flex-shrink-0 mt-0.5">{item.time}</span>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>

          {/* Agent status panel */}
          <div className="w-72 flex-shrink-0">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-zinc-300">Agent Status</h2>
              <span className="pill pill-green">6/6 Live</span>
            </div>
            <div className="border border-zinc-800 rounded-xl overflow-hidden">
              {AGENT_MODULES.map((agent, i) => (
                <div key={i} className="data-row flex-col items-start gap-2">
                  <div className="flex items-center justify-between w-full">
                    <div className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse-dot" />
                      <span className="text-xs font-medium text-zinc-300">{agent.name}</span>
                    </div>
                    <span className="text-[10px] text-zinc-600 font-mono">{agent.latency}</span>
                  </div>
                  <div className="flex items-center gap-3 w-full">
                    <div className="flex items-center gap-1">
                      <span className="text-[10px] text-zinc-600">Tasks:</span>
                      <span className="text-[10px] text-zinc-400 font-mono">{agent.tasks}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="text-[10px] text-zinc-600">Queue:</span>
                      <span className={`text-[10px] font-mono ${agent.queue > 10 ? "text-amber-400" : "text-zinc-400"}`}>{agent.queue}</span>
                    </div>
                  </div>
                  <div className="progress-track w-full">
                    <div
                      className="progress-fill"
                      style={{ width: `${Math.min(100, (agent.tasks / (agent.tasks + agent.queue)) * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Quick actions */}
            <div className="mt-4">
              <h3 className="text-xs font-semibold text-zinc-600 uppercase tracking-widest mb-2">Quick Actions</h3>
              <div className="space-y-1.5">
                {[
                  { label: "Upload Resume",      href: "/dashboard/pipeline" },
                  { label: "Start Interview",    href: "/interviews" },
                  { label: "View Pipeline",      href: "/dashboard/pipeline" },
                  { label: "Generate Report",    href: "/reports" },
                ].map((a, i) => (
                  <a
                    key={i}
                    href={a.href}
                    className="flex items-center justify-between px-3 py-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-xs text-zinc-400 hover:text-white transition-colors"
                  >
                    {a.label}
                    <span className="text-zinc-700">→</span>
                  </a>
                ))}
              </div>
            </div>
          </div>

        </div>
      </div>
    </AppShell>
  )
}
