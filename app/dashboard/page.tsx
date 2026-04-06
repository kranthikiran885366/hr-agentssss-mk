"use client"

import { useState, useEffect } from "react"
import { AppShell } from "@/components/layout/app-shell"
import {
  Users, MessageSquare, Zap, TrendingUp, Activity,
  RefreshCw, ArrowUp, ArrowDown, Bot, FileText,
  Clock, CheckCircle, AlertCircle, GitBranch
} from "lucide-react"

interface Metric {
  label: string; value: string; sub: string; trend: number; icon: any; color: string
}

interface ActivityItem {
  id: number
  time: string
  actor: string
  action: string
  status: "done" | "alert" | "running"
  icon: any
  color: string
}

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<Metric[]>([
    { label: "Total Employees",   value: "0", sub: "Active headcount",    trend: 0,  icon: Users,         color: "blue" },
    { label: "Active Processes",  value: "0",   sub: "Running automatically",trend: 0, icon: Bot,           color: "purple" },
    { label: "Active Candidates",   value: "0", sub: "In pipeline",      trend: 0,  icon: Zap,           color: "emerald" },
    { label: "Interviews",     value: "0",    sub: "This week",                trend: 0,  icon: MessageSquare, color: "amber" },
    { label: "Jobs Open",       value: "0",     sub: "Currently hiring",          trend: 0,  icon: CheckCircle,   color: "blue" },
    { label: "Onboardings",   value: "0",    sub: "In progress",   trend: 0, icon: GitBranch,     color: "rose" },
  ])
  const [activityFeed, setActivityFeed] = useState<ActivityItem[]>([])
  const [agentModules, setAgentModules] = useState<any[]>([])
  const [lastUpdated, setLastUpdated] = useState(new Date())
  const [loading, setLoading] = useState(false)

  const loadDashboard = async () => {
    setLoading(true)
    try {
      const [candidatesRes, interviewRes, jobsRes, usersRes] = await Promise.all([
        fetch("/api/talent-acquisition/candidates"),
        fetch("/api/interviews/sessions"),
        fetch("/api/talent-acquisition/jobs"),
        fetch("/api/users")
      ])

      const candidatesData = candidatesRes.ok ? await candidatesRes.json() : { total: 0 }
      const interviewsData = interviewRes.ok ? await interviewRes.json() : []
      const jobsData = jobsRes.ok ? await jobsRes.json() : { total: 0 }
      const usersData = usersRes.ok ? await usersRes.json() : []

      const activeCandidates = candidatesData.items?.filter((c: any) => c.status === "SCREENING" || c.status === "INTERVIEW") || []
      const activeInterviews = interviewsData.filter((i: any) => i.status === "IN_PROGRESS") || []
      const openJobs = jobsData.items?.filter((j: any) => j.status === "OPEN") || []

      setMetrics([
        { label: "Total Employees", value: usersData.length?.toString() || "0", sub: "Active headcount", trend: 0, icon: Users, color: "blue" },
        { label: "Active Processes", value: activeInterviews.length?.toString() || "0", sub: "Running now", trend: 0, icon: Bot, color: "purple" },
        { label: "Active Candidates", value: activeCandidates.length?.toString() || "0", sub: "In pipeline", trend: 0, icon: Zap, color: "emerald" },
        { label: "Interviews", value: interviewsData.length?.toString() || "0", sub: "Sessions tracked", trend: 0, icon: MessageSquare, color: "amber" },
        { label: "Jobs Open", value: openJobs.length?.toString() || "0", sub: "Currently hiring", trend: 0, icon: CheckCircle, color: "blue" },
        { label: "Pipeline Candidates", value: candidatesData.total?.toString() || "0", sub: "Total tracked", trend: 0, icon: GitBranch, color: "rose" },
      ])

      // Create activity feed from real data
      const activities: ActivityItem[] = []
      interviewsData.slice(0, 4).forEach((interview: any, idx: number) => {
        activities.push({
          id: idx + 1,
          time: new Date(interview.createdAt).toLocaleDateString(),
          actor: "Interview AI",
          action: `${interview.status === "COMPLETED" ? "Completed" : "Started"} interview with ${interview.candidate?.name}`,
          status: interview.status === "COMPLETED" ? "done" : "running",
          icon: MessageSquare,
          color: interview.status === "COMPLETED" ? "emerald" : "blue"
        })
      })

      candidatesData.items?.slice(0, 3).forEach((candidate: any, idx: number) => {
        activities.push({
          id: activities.length + 1,
          time: new Date(candidate.createdAt).toLocaleDateString(),
          actor: "Resume Agent",
          action: `${candidate.name} applied - Score: ${(candidate.score * 100).toFixed(0)}%`,
          status: "done",
          icon: FileText,
          color: "blue"
        })
      })

      setActivityFeed(activities.slice(0, 8))

      setAgentModules([
        { name: "Resume Agent", tasks: candidatesData.total || 0, queue: 0, status: "active", latency: "120ms" },
        { name: "Interview AI", tasks: interviewsData.length || 0, queue: 0, status: "active", latency: "89ms" },
        { name: "Candidates", tasks: activeCandidates.length || 0, queue: 0, status: "active", latency: "210ms" },
        { name: "Jobs", tasks: openJobs.length || 0, queue: 0, status: "active", latency: "55ms" },
        { name: "Users", tasks: usersData.length || 0, queue: 0, status: "active", latency: "67ms" },
      ])
    } catch (error) {
      console.error("Error loading dashboard:", error)
    }
    setLastUpdated(new Date())
    setTimeout(() => setLoading(false), 600)
  }

  useEffect(() => {
    loadDashboard()
  }, [])

  const refresh = () => {
    loadDashboard()
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
                {activityFeed.map((item, i) => {
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
              {agentModules.map((agent, i) => (
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
