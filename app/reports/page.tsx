"use client"

import { useState, useEffect } from "react"
import { AppShell } from "@/components/layout/app-shell"
import { Download, RefreshCw, TrendingUp, TrendingDown, BarChart2 } from "lucide-react"

// Simple bar chart component (no recharts dependency)
function BarChart({ data, label, color = "blue" }: {
  data: { label: string; value: number }[]
  label: string
  color?: string
}) {
  const max = Math.max(...data.map(d => d.value))
  const colors: Record<string, string> = {
    blue:   "bg-blue-500",
    emerald:"bg-emerald-500",
    purple: "bg-purple-500",
    amber:  "bg-amber-500",
  }
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-widest text-zinc-600 mb-4">{label}</p>
      <div className="flex items-end gap-2 h-32">
        {data.map((d, i) => (
          <div key={i} className="flex-1 flex flex-col items-center gap-1">
            <span className="text-[9px] text-zinc-600 font-mono">{d.value}</span>
            <div
              className={`w-full ${colors[color]} rounded-t-sm transition-all duration-700 opacity-80 hover:opacity-100`}
              style={{ height: `${(d.value / max) * 100}%` }}
            />
            <span className="text-[9px] text-zinc-700">{d.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

const HIRING_DATA = [
  { label:"Oct", value:28 }, { label:"Nov", value:34 }, { label:"Dec", value:22 },
  { label:"Jan", value:41 }, { label:"Feb", value:38 }, { label:"Mar", value:52 },
  { label:"Apr", value:47 },
]

const ONBOARD_DATA = [
  { label:"Oct", value:18 }, { label:"Nov", value:24 }, { label:"Dec", value:14 },
  { label:"Jan", value:31 }, { label:"Feb", value:27 }, { label:"Mar", value:39 },
  { label:"Apr", value:33 },
]

const PERF_DATA = [
  { label:"Q2'25", value:76 }, { label:"Q3'25", value:81 }, { label:"Q4'25", value:84 },
  { label:"Q1'26", value:91 },
]

const DEPT_BREAKDOWN = [
  { dept: "Engineering", headcount: 847, hires: 23, exits: 4, engagement: 89, perf: 91 },
  { dept: "Product",     headcount: 124, hires: 6,  exits: 1, engagement: 92, perf: 88 },
  { dept: "Design",      headcount: 89,  hires: 4,  exits: 2, engagement: 87, perf: 85 },
  { dept: "Data",        headcount: 203, hires: 11, exits: 3, engagement: 93, perf: 94 },
  { dept: "Sales",       headcount: 312, hires: 18, exits: 8, engagement: 81, perf: 79 },
  { dept: "Marketing",   headcount: 156, hires: 7,  exits: 2, engagement: 88, perf: 83 },
  { dept: "Ops",         headcount: 241, hires: 9,  exits: 5, engagement: 84, perf: 87 },
  { dept: "Legal",       headcount: 67,  hires: 2,  exits: 0, engagement: 90, perf: 92 },
]

const KEY_METRICS = [
  { label: "Avg. Time to Hire",      value: "12 days",  sub: "vs 47 days industry avg", trend: -74, good: true },
  { label: "Cost per Hire",          value: "$1,240",   sub: "vs $4,700 benchmark",     trend: -74, good: true },
  { label: "Offer Acceptance Rate",  value: "91%",      sub: "+8% QoQ",                 trend: 8,   good: true },
  { label: "30-Day Retention",       value: "97.3%",    sub: "Post-onboarding",         trend: 2.1, good: true },
  { label: "Employee NPS",           value: "68",       sub: "+12 vs last quarter",     trend: 21,  good: true },
  { label: "AI Interview Accuracy",  value: "94%",      sub: "Hire prediction accuracy",trend: 3,   good: true },
]

const AGENT_REPORT = [
  { agent: "Resume Agent",    processed: 3247, success: 99.1, avg_time: "0.8s",  errors: 3 },
  { agent: "Interview AI",    processed: 847,  success: 98.7, avg_time: "2.4m",  errors: 11 },
  { agent: "Onboard Agent",   processed: 234,  success: 99.6, avg_time: "12.4s", errors: 1 },
  { agent: "Perf Agent",      processed: 12847,success: 99.9, avg_time: "0.2s",  errors: 13 },
  { agent: "Comms Agent",     processed: 87421,success: 99.8, avg_time: "0.1s",  errors: 175 },
  { agent: "Exit Agent",      processed: 47,   success: 100,  avg_time: "1.2s",  errors: 0 },
]

export default function ReportsPage() {
  const [loading, setLoading] = useState(false)
  const [period, setPeriod] = useState("Q2 2026")

  const refresh = () => {
    setLoading(true)
    setTimeout(() => setLoading(false), 800)
  }

  return (
    <AppShell>
      <div className="px-6 py-6">

        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white">Analytics & Reports</h1>
            <p className="text-sm text-zinc-500 mt-0.5">Workforce intelligence dashboard</p>
          </div>
          <div className="flex items-center gap-3">
            <select
              value={period}
              onChange={e => setPeriod(e.target.value)}
              className="px-3 py-1.5 text-xs rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-400 outline-none"
            >
              {["Q2 2026","Q1 2026","Q4 2025","Q3 2025"].map(p => <option key={p}>{p}</option>)}
            </select>
            <button
              onClick={refresh}
              className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-white border border-zinc-800 px-3 py-1.5 rounded-lg transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} /> Refresh
            </button>
            <button className="flex items-center gap-1.5 text-xs font-medium bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded-lg transition-colors">
              <Download className="w-3.5 h-3.5" /> Export
            </button>
          </div>
        </div>

        {/* Key metrics — horizontal strip */}
        <div className="border border-zinc-800 rounded-xl overflow-hidden mb-8">
          <div className="px-5 py-3 border-b border-zinc-800 flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-widest text-zinc-600">Key Metrics — {period}</span>
          </div>
          <div className="flex overflow-x-auto divide-x divide-zinc-800">
            {KEY_METRICS.map((m, i) => (
              <div key={i} className="flex-1 min-w-[160px] px-5 py-4">
                <div className="stat-number text-2xl text-white mb-1">{m.value}</div>
                <div className="text-[11px] font-medium text-zinc-400 mb-0.5">{m.label}</div>
                <div className={`flex items-center gap-1 text-[10px] font-semibold ${m.good ? "text-emerald-500" : "text-red-500"}`}>
                  {m.trend > 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                  {m.sub}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Charts row */}
        <div className="grid gap-6 mb-8" style={{ gridTemplateColumns: "2fr 1fr" }}>
          <div className="border border-zinc-800 rounded-xl p-6">
            <BarChart data={HIRING_DATA} label="Monthly Hires Processed by AI" color="blue" />
          </div>
          <div className="border border-zinc-800 rounded-xl p-6">
            <BarChart data={PERF_DATA} label="Avg Performance Score by Quarter" color="emerald" />
          </div>
        </div>

        <div className="grid gap-6 mb-8" style={{ gridTemplateColumns: "1fr 1fr" }}>
          <div className="border border-zinc-800 rounded-xl p-6">
            <BarChart data={ONBOARD_DATA} label="Onboarding Completions Per Month" color="purple" />
          </div>
          <div className="border border-zinc-800 rounded-xl p-6">
            <p className="text-xs font-semibold uppercase tracking-widest text-zinc-600 mb-4">Agent Reliability</p>
            <div className="space-y-3">
              {AGENT_REPORT.map(a => (
                <div key={a.agent} className="flex items-center gap-3">
                  <span className="text-[11px] text-zinc-500 w-32 flex-shrink-0">{a.agent}</span>
                  <div className="progress-track flex-1">
                    <div className="progress-fill green" style={{ width: `${a.success}%` }} />
                  </div>
                  <span className="text-[11px] font-mono text-emerald-400 w-12 text-right">{a.success}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Department breakdown */}
        <div className="border border-zinc-800 rounded-xl overflow-hidden mb-8">
          <div className="px-5 py-3 border-b border-zinc-800">
            <span className="text-xs font-semibold uppercase tracking-widest text-zinc-600">Department Breakdown</span>
          </div>
          <table className="data-table w-full">
            <thead>
              <tr className="bg-zinc-900/60">
                <th>Department</th>
                <th className="text-right">Headcount</th>
                <th className="text-right">Hires (QTD)</th>
                <th className="text-right">Exits (QTD)</th>
                <th className="w-40">Engagement</th>
                <th className="w-40">Performance</th>
              </tr>
            </thead>
            <tbody>
              {DEPT_BREAKDOWN.map(d => (
                <tr key={d.dept}>
                  <td className="font-medium text-zinc-200">{d.dept}</td>
                  <td className="text-right font-mono text-sm text-zinc-400">{d.headcount.toLocaleString()}</td>
                  <td className="text-right">
                    <span className="text-emerald-400 font-mono text-sm">+{d.hires}</span>
                  </td>
                  <td className="text-right">
                    <span className={`font-mono text-sm ${d.exits > 5 ? "text-red-400" : "text-zinc-500"}`}>{d.exits}</span>
                  </td>
                  <td>
                    <div className="flex items-center gap-2">
                      <div className="progress-track flex-1">
                        <div className="progress-fill" style={{ width: `${d.engagement}%` }} />
                      </div>
                      <span className="text-[10px] text-zinc-500 font-mono w-7">{d.engagement}</span>
                    </div>
                  </td>
                  <td>
                    <div className="flex items-center gap-2">
                      <div className="progress-track flex-1">
                        <div className={`progress-fill ${d.perf >= 90 ? "green" : ""}`} style={{ width: `${d.perf}%` }} />
                      </div>
                      <span className="text-[10px] text-zinc-500 font-mono w-7">{d.perf}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Agent activity table */}
        <div className="border border-zinc-800 rounded-xl overflow-hidden">
          <div className="px-5 py-3 border-b border-zinc-800">
            <span className="text-xs font-semibold uppercase tracking-widest text-zinc-600">AI Agent Performance</span>
          </div>
          <table className="data-table w-full">
            <thead>
              <tr className="bg-zinc-900/60">
                <th>Agent</th>
                <th className="text-right">Tasks Processed</th>
                <th className="text-right">Success Rate</th>
                <th className="text-right">Avg. Time</th>
                <th className="text-right">Errors</th>
              </tr>
            </thead>
            <tbody>
              {AGENT_REPORT.map(a => (
                <tr key={a.agent}>
                  <td className="font-medium text-zinc-200">{a.agent}</td>
                  <td className="text-right font-mono text-sm text-zinc-400">{a.processed.toLocaleString()}</td>
                  <td className="text-right">
                    <span className={`font-mono font-bold text-sm ${a.success >= 99.5 ? "text-emerald-400" : "text-amber-400"}`}>{a.success}%</span>
                  </td>
                  <td className="text-right font-mono text-xs text-zinc-500">{a.avg_time}</td>
                  <td className="text-right">
                    <span className={`font-mono text-sm ${a.errors > 10 ? "text-amber-400" : "text-zinc-600"}`}>{a.errors}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      </div>
    </AppShell>
  )
}
