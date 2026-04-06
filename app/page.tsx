"use client"

import Link from "next/link"
import { useEffect, useState } from "react"
import {
  Zap, ArrowRight, GitBranch, MessageSquare, UserCheck,
  TrendingUp, BarChart3, Shield, ChevronRight, Activity,
  Brain, Clock, CheckCircle, Target, Users
} from "lucide-react"

const WORKFLOW_STEPS = [
  { step: "01", title: "Resume Ingested",     sub: "AI extracts & scores 200+ signals",         color: "text-blue-400" },
  { step: "02", title: "Interview Triggered", sub: "Autonomous multi-round AI interview",        color: "text-purple-400" },
  { step: "03", title: "Decision Generated",  sub: "Ensemble model produces hire confidence",    color: "text-emerald-400" },
  { step: "04", title: "Offer Dispatched",    sub: "Personalized offer, automated negotiation",  color: "text-amber-400" },
  { step: "05", title: "Onboarding Starts",   sub: "24-step journey launched automatically",     color: "text-rose-400" },
]

const FEATURES = [
  { icon: GitBranch, label: "Talent Pipeline",    desc: "AI scores and routes candidates automatically through every hiring stage.", accent: "blue" },
  { icon: MessageSquare, label: "AI Interviews",  desc: "Autonomous interviews with real-time scoring and transcript analysis.", accent: "purple" },
  { icon: UserCheck, label: "Smart Onboarding",   desc: "24-step onboarding journeys fully orchestrated by AI agents.", accent: "emerald" },
  { icon: TrendingUp, label: "Performance AI",    desc: "Continuous goal tracking, check-ins, and automated review cycles.", accent: "amber" },
  { icon: BarChart3, label: "Deep Analytics",     desc: "Real-time workforce intelligence across every HR dimension.", accent: "rose" },
  { icon: Shield, label: "Compliance Engine",     desc: "Automated policy enforcement, audit trails, and regulatory tracking.", accent: "blue" },
]

const STATS = [
  { value: "94%",   label: "Reduction in time-to-hire" },
  { value: "12x",   label: "Faster onboarding" },
  { value: "3.2M+", label: "Resumes processed" },
  { value: "99.7%", label: "Agent uptime" },
]

const ACCENT_CLASSES: Record<string, string> = {
  blue:   "text-blue-400 bg-blue-500/10 border border-blue-500/20",
  purple: "text-purple-400 bg-purple-500/10 border border-purple-500/20",
  emerald:"text-emerald-400 bg-emerald-500/10 border border-emerald-500/20",
  amber:  "text-amber-400 bg-amber-500/10 border border-amber-500/20",
  rose:   "text-rose-400 bg-rose-500/10 border border-rose-500/20",
}

export default function LandingPage() {
  const [mounted, setMounted] = useState(false)
  useEffect(() => { setMounted(true) }, [])

  return (
    <div className="min-h-screen bg-[#09090B] text-zinc-100 overflow-x-hidden">

      {/* Top nav */}
      <header className="fixed top-0 left-0 right-0 z-50 border-b border-zinc-800/60 bg-[#09090B]/90 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 flex items-center justify-between h-14">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-sm tracking-tight">HRAgent</span>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm text-zinc-400">
            {[
              { label: "Platform",   href: "/dashboard" },
              { label: "Pipeline",   href: "/dashboard/pipeline" },
              { label: "Analytics",  href: "/reports" },
              { label: "Demo",       href: "/demo" },
            ].map(n => (
              <Link key={n.href} href={n.href} className="hover:text-white transition-colors">{n.label}</Link>
            ))}
          </nav>
          <div className="flex items-center gap-3">
            <Link href="/auth/login" className="text-sm text-zinc-400 hover:text-white transition-colors hidden sm:block">Log in</Link>
            <Link href="/dashboard" className="flex items-center gap-1.5 text-sm font-medium bg-blue-600 hover:bg-blue-500 text-white px-3.5 py-1.5 rounded-md transition-colors">
              Open app <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="hero-bg pt-36 pb-28 px-6">
        <div className="max-w-5xl mx-auto">
          <div className={`inline-flex items-center gap-2 mb-8 px-3 py-1.5 rounded-full border border-blue-500/30 bg-blue-500/10 text-blue-300 text-xs font-medium transition-all duration-700 ${mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse-dot" />
            AI agents running live — 6 specialized modules
          </div>
          <h1 className={`text-5xl md:text-7xl font-black tracking-tighter leading-[0.93] mb-6 transition-all duration-700 delay-100 ${mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
            The HR system<br />
            <span className="gradient-text">that runs itself.</span>
          </h1>
          <p className={`text-lg md:text-xl text-zinc-400 max-w-2xl mb-10 leading-relaxed transition-all duration-700 delay-200 ${mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
            HRAgent automates your entire employee lifecycle — from sourcing and interviews
            to onboarding, performance management, and exit — with a fleet of specialized AI agents.
          </p>
          <div className={`flex flex-wrap items-center gap-4 transition-all duration-700 delay-300 ${mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
            <Link href="/dashboard" className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold px-6 py-3 rounded-lg text-sm transition-colors glow-blue">
              Open Command Center <ArrowRight className="w-4 h-4" />
            </Link>
            <Link href="/demo" className="flex items-center gap-2 border border-zinc-700 hover:border-zinc-500 text-zinc-300 hover:text-white font-medium px-6 py-3 rounded-lg text-sm transition-colors">
              See a live demo
            </Link>
          </div>
        </div>
      </section>

      {/* Stats strip */}
      <section className="border-y border-zinc-800/60 bg-zinc-900/20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex overflow-x-auto">
            {STATS.map((s, i) => (
              <div key={i} className="flex-1 min-w-[150px] py-6 px-6 border-r border-zinc-800/60 last:border-r-0">
                <div className="stat-number mb-1">{s.value}</div>
                <div className="stat-label">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Horizontal workflow */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <p className="text-xs font-semibold uppercase tracking-widest text-blue-400 mb-3">End-to-end automation</p>
            <h2 className="text-3xl md:text-4xl font-black tracking-tight">Zero human bottlenecks.</h2>
          </div>
          <div className="flex overflow-x-auto gap-0 pb-4">
            {WORKFLOW_STEPS.map((s, i) => (
              <div key={i} className="flex items-stretch min-w-[190px] flex-1">
                <div className="flex-1 bg-zinc-900/60 border border-zinc-800 rounded-lg p-5 mr-1">
                  <div className={`text-xs font-mono font-bold mb-3 ${s.color}`}>{s.step}</div>
                  <div className="font-semibold text-sm text-white mb-1.5">{s.title}</div>
                  <div className="text-xs text-zinc-500 leading-relaxed">{s.sub}</div>
                </div>
                {i < WORKFLOW_STEPS.length - 1 && (
                  <div className="flex items-center px-0.5 text-zinc-700 flex-shrink-0">
                    <ChevronRight className="w-4 h-4" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features — full-width rows */}
      <section className="py-8 px-6 border-t border-zinc-800/60">
        <div className="max-w-7xl mx-auto">
          <div className="mb-10">
            <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500 mb-3">Modules</p>
            <h2 className="text-3xl font-black tracking-tight">Six agent modules.</h2>
          </div>
          <div className="divide-y divide-zinc-800/60">
            {FEATURES.map((f, i) => {
              const Icon = f.icon
              return (
                <div key={i} className="flex items-center gap-6 py-5 group cursor-default">
                  <div className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 ${ACCENT_CLASSES[f.accent]}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div className="flex-1">
                    <div className="font-semibold text-white text-sm mb-0.5">{f.label}</div>
                    <div className="text-sm text-zinc-500">{f.desc}</div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-zinc-700 group-hover:text-zinc-400 transition-colors" />
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Agent Architecture */}
      <section className="py-24 px-6 bg-zinc-900/30 border-t border-zinc-800/60">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <p className="text-xs font-semibold uppercase tracking-widest text-purple-400 mb-3">AI Architecture</p>
            <h2 className="text-3xl font-black tracking-tight">Orchestrated intelligence.</h2>
            <p className="mt-3 text-zinc-400 max-w-xl text-sm">
              A central orchestrator routes work to specialized agents in real-time,
              with memory, tool use, and human-in-the-loop escalation built in.
            </p>
          </div>
          <div className="overflow-x-auto pb-4">
            <div className="flex items-center gap-2 min-w-[650px]">
              <div className="bg-blue-600/20 border border-blue-500/40 rounded-xl px-5 py-4 flex-shrink-0 text-center min-w-[110px]">
                <Brain className="w-5 h-5 text-blue-400 mx-auto mb-2" />
                <div className="text-xs font-bold text-blue-300">Orchestrator</div>
                <div className="text-[10px] text-blue-400/60 mt-1">Routes work</div>
              </div>
              <ChevronRight className="w-4 h-4 text-zinc-700 flex-shrink-0" />
              {[
                { icon: GitBranch,  name: "Resume",      color: "blue",   detail: "Scoring" },
                { icon: MessageSquare, name: "Interview", color: "purple", detail: "Q&A + Eval" },
                { icon: UserCheck,  name: "Onboard",     color: "emerald",detail: "24 steps" },
                { icon: TrendingUp, name: "Performance",  color: "amber",  detail: "Goals + OKR" },
                { icon: Shield,     name: "Compliance",   color: "rose",   detail: "Audit" },
              ].map((a, i) => {
                const Icon = a.icon
                return (
                  <div key={i} className={`flex-1 min-w-[100px] border rounded-lg px-3 py-3 text-center ${ACCENT_CLASSES[a.color]}`}>
                    <Icon className="w-4 h-4 mx-auto mb-1.5" />
                    <div className="text-[11px] font-semibold">{a.name}</div>
                    <div className="text-[10px] opacity-60 mt-0.5">{a.detail}</div>
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mx-auto mt-2 animate-pulse-dot" />
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-28 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-black tracking-tight mb-4">
            Ready to automate<br />
            <span className="gradient-text-blue">your HR workflow?</span>
          </h2>
          <p className="text-zinc-400 mb-8 text-lg">Deploy all six AI agents in minutes.</p>
          <Link href="/dashboard" className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold px-8 py-3.5 rounded-lg text-sm transition-colors glow-blue">
            Launch HRAgent <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      <footer className="border-t border-zinc-800/60 py-8 px-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 rounded bg-blue-600 flex items-center justify-center">
              <Zap className="w-3 h-3 text-white" />
            </div>
            <span className="text-sm font-bold text-zinc-500">HRAgent</span>
          </div>
          <p className="text-xs text-zinc-700">© 2026 HRAgent AI</p>
        </div>
      </footer>
    </div>
  )
}
