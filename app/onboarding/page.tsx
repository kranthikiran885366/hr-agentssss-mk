"use client"

import { useState } from "react"
import { AppShell } from "@/components/layout/app-shell"
import {
  CheckCircle, Clock, AlertCircle, Plus, User,
  FileText, Laptop, Shield, Users, Award, Mail,
  ChevronRight, X, Upload
} from "lucide-react"

const ONBOARDING_STEPS = [
  { id: 1,  icon: Mail,        label: "Welcome Email Sent",           auto: true,  duration: "auto" },
  { id: 2,  icon: User,        label: "Identity Verification (OCR)",  auto: true,  duration: "auto" },
  { id: 3,  icon: FileText,    label: "Offer Letter e-Signed",        auto: true,  duration: "auto" },
  { id: 4,  icon: FileText,    label: "NDA & Policy Docs",            auto: true,  duration: "auto" },
  { id: 5,  icon: Shield,      label: "Background Check Initiated",   auto: true,  duration: "48hr" },
  { id: 6,  icon: Laptop,      label: "IT Equipment Provisioned",     auto: false, duration: "manual" },
  { id: 7,  icon: Shield,      label: "System Accounts Created",      auto: true,  duration: "auto" },
  { id: 8,  icon: Users,       label: "Buddy / Mentor Assigned",      auto: false, duration: "manual" },
  { id: 9,  icon: FileText,    label: "Benefits Enrollment",          auto: true,  duration: "auto" },
  { id: 10, icon: Award,       label: "Role Training Scheduled",      auto: true,  duration: "auto" },
  { id: 11, icon: Users,       label: "Team Introduction Meeting",    auto: false, duration: "manual" },
  { id: 12, icon: CheckCircle, label: "Day-1 Checklist Complete",     auto: true,  duration: "auto" },
]

const EMPLOYEES = [
  {
    id: "e1", name: "Sarah Chen", role: "Senior Engineer", dept: "Engineering",
    startDate: "2026-04-08", progress: 7, avatar: "S", color: "from-blue-600 to-blue-800",
    stepsComplete: [1,2,3,4,5,7,9],
    stepStatus: { 1:"done",2:"done",3:"done",4:"done",5:"done",6:"pending",7:"done",8:"pending",9:"done",10:"running",11:"pending",12:"pending" }
  },
  {
    id: "e2", name: "Marcus Johnson", role: "Product Manager", dept: "Product",
    startDate: "2026-04-08", progress: 12, avatar: "M", color: "from-purple-600 to-purple-800",
    stepsComplete: [1,2,3,4,5,6,7,8,9,10,11,12],
    stepStatus: { 1:"done",2:"done",3:"done",4:"done",5:"done",6:"done",7:"done",8:"done",9:"done",10:"done",11:"done",12:"done" }
  },
  {
    id: "e3", name: "Aisha Okonkwo", role: "DevOps Engineer", dept: "Infrastructure",
    startDate: "2026-04-10", progress: 3, avatar: "A", color: "from-emerald-600 to-emerald-800",
    stepsComplete: [1,2,3],
    stepStatus: { 1:"done",2:"done",3:"done",4:"running",5:"pending",6:"pending",7:"pending",8:"pending",9:"pending",10:"pending",11:"pending",12:"pending" }
  },
]

type StepStatus = "done" | "running" | "pending"

const STEP_DOT: Record<StepStatus, string> = {
  done:    "timeline-dot done",
  running: "timeline-dot active",
  pending: "timeline-dot",
}

export default function OnboardingPage() {
  const [selected, setSelected] = useState(EMPLOYEES[0])
  const [showAdd, setShowAdd] = useState(false)

  const status = selected.stepStatus as Record<number, StepStatus>
  const pct = Math.round((selected.stepsComplete.length / ONBOARDING_STEPS.length) * 100)

  return (
    <AppShell>
      <div className="px-6 py-6 flex gap-6 h-full">

        {/* Left: employee list */}
        <div className="w-72 flex-shrink-0">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl font-bold tracking-tight text-white">Onboarding</h1>
            <button
              onClick={() => setShowAdd(true)}
              className="flex items-center gap-1 text-xs font-medium bg-blue-600 hover:bg-blue-500 text-white px-2.5 py-1.5 rounded-md transition-colors"
            >
              <Plus className="w-3.5 h-3.5" /> Add
            </button>
          </div>

          <div className="space-y-2">
            {EMPLOYEES.map(emp => {
              const pctEmp = Math.round((emp.stepsComplete.length / ONBOARDING_STEPS.length) * 100)
              const isSelected = selected.id === emp.id
              return (
                <button
                  key={emp.id}
                  onClick={() => setSelected(emp)}
                  className={`w-full text-left p-3.5 rounded-xl border transition-all ${
                    isSelected
                      ? "border-blue-500/50 bg-blue-500/10"
                      : "border-zinc-800 bg-zinc-900/50 hover:bg-zinc-900"
                  }`}
                >
                  <div className="flex items-center gap-3 mb-2.5">
                    <div className={`w-8 h-8 rounded-full bg-gradient-to-br ${emp.color} flex items-center justify-center text-xs font-bold text-white`}>
                      {emp.avatar}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-semibold text-white truncate">{emp.name}</div>
                      <div className="text-[11px] text-zinc-500 truncate">{emp.role}</div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] text-zinc-600">Progress</span>
                    <span className="text-[10px] font-mono text-zinc-400">{pctEmp}%</span>
                  </div>
                  <div className="progress-track">
                    <div
                      className={`progress-fill ${pctEmp === 100 ? "green" : ""}`}
                      style={{ width: `${pctEmp}%` }}
                    />
                  </div>
                  <div className="flex items-center gap-1.5 mt-2">
                    <span className="text-[10px] text-zinc-600">Start:</span>
                    <span className="text-[10px] text-zinc-400">
                      {new Date(emp.startDate).toLocaleDateString("en-US", { month:"short", day:"numeric" })}
                    </span>
                    {pctEmp === 100 && <span className="ml-auto pill pill-green">Complete</span>}
                    {pctEmp < 100 && pctEmp > 0 && <span className="ml-auto pill pill-blue">In progress</span>}
                  </div>
                </button>
              )
            })}
          </div>
        </div>

        {/* Right: onboarding journey timeline */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${selected.color} flex items-center justify-center text-sm font-bold text-white`}>
                {selected.avatar}
              </div>
              <div>
                <h2 className="text-lg font-bold text-white">{selected.name}</h2>
                <p className="text-sm text-zinc-500">{selected.dept} · {selected.role}</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-2xl font-black text-white">{pct}%</div>
                <div className="text-xs text-zinc-600">Complete</div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-black text-white">{selected.stepsComplete.length}/{ONBOARDING_STEPS.length}</div>
                <div className="text-xs text-zinc-600">Steps done</div>
              </div>
            </div>
          </div>

          {/* Progress bar */}
          <div className="progress-track mb-8" style={{ height: "6px" }}>
            <div
              className={`progress-fill ${pct === 100 ? "green" : ""}`}
              style={{ width: `${pct}%`, height: "6px" }}
            />
          </div>

          {/* Timeline */}
          <div className="border border-zinc-800 rounded-xl px-6 py-6">
            <div className="timeline">
              {ONBOARDING_STEPS.map((step, i) => {
                const st: StepStatus = (status[step.id] as StepStatus) || "pending"
                const Icon = step.icon
                return (
                  <div key={step.id} className="timeline-item">
                    <div className={STEP_DOT[st]} />
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                          st === "done"    ? "bg-emerald-500/15 text-emerald-400" :
                          st === "running" ? "bg-blue-500/15 text-blue-400" :
                          "bg-zinc-800 text-zinc-600"
                        }`}>
                          {st === "done" ? <CheckCircle className="w-4 h-4" /> : st === "running" ? <Clock className="w-4 h-4" /> : <Icon className="w-4 h-4" />}
                        </div>
                        <div>
                          <div className={`text-sm font-medium ${
                            st === "done" ? "text-zinc-400 line-through" : st === "running" ? "text-white" : "text-zinc-500"
                          }`}>{step.label}</div>
                          <div className="flex items-center gap-2 mt-0.5">
                            {step.auto ? (
                              <span className="text-[10px] text-blue-400/70 bg-blue-500/10 px-1.5 py-0.5 rounded">AI Automated</span>
                            ) : (
                              <span className="text-[10px] text-zinc-600 bg-zinc-800 px-1.5 py-0.5 rounded">Manual</span>
                            )}
                            <span className="text-[10px] text-zinc-700">{step.duration}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {st === "running" && (
                          <span className="text-[10px] text-blue-300 font-medium animate-pulse">In progress</span>
                        )}
                        {st === "done" && (
                          <CheckCircle className="w-4 h-4 text-emerald-500" />
                        )}
                        {st === "pending" && (
                          <span className="text-[10px] text-zinc-700">Pending</span>
                        )}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>

      </div>

      {showAdd && <AddEmployeeModal onClose={() => setShowAdd(false)} />}
    </AppShell>
  )
}

function AddEmployeeModal({ onClose }: { onClose: () => void }) {
  const [loading, setLoading] = useState(false)
  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    await new Promise(r => setTimeout(r, 1000))
    setLoading(false)
    onClose()
  }
  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl w-full max-w-sm">
        <div className="flex items-center justify-between px-5 py-4 border-b border-zinc-800">
          <h3 className="text-sm font-semibold text-white">Start Onboarding</h3>
          <button onClick={onClose}><X className="w-4 h-4 text-zinc-600" /></button>
        </div>
        <form onSubmit={submit} className="px-5 py-4 space-y-3">
          {["Full name","Role","Department","Email","Start date"].map(f => (
            <div key={f}>
              <label className="block text-xs font-medium text-zinc-500 mb-1">{f}</label>
              <input
                required
                type={f === "Start date" ? "date" : f === "Email" ? "email" : "text"}
                className="w-full px-3 py-2 text-sm rounded-lg bg-zinc-800 border border-zinc-700 text-zinc-200 outline-none focus:border-blue-500"
              />
            </div>
          ))}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-colors mt-2 disabled:opacity-50"
          >
            {loading ? "Launching…" : "Launch AI Onboarding"}
          </button>
        </form>
      </div>
    </div>
  )
}
