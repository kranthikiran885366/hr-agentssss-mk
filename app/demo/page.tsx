"use client"

import { useState } from "react"
import { AppShell } from "@/components/layout/app-shell"
import {
  Zap, Brain, MessageSquare, FileText, TrendingUp,
  UserCheck, Send, Loader2, CheckCircle, ChevronRight
} from "lucide-react"

type AgentType = "resume" | "interview" | "onboarding" | "performance"

const AGENTS = [
  { id: "resume" as AgentType,      icon: FileText,      name: "Resume Analyzer",     desc: "Parse and score a resume with AI",            color: "blue" },
  { id: "interview" as AgentType,   icon: MessageSquare, name: "Interview AI",         desc: "Run a sample AI screening interview",          color: "purple" },
  { id: "onboarding" as AgentType,  icon: UserCheck,     name: "Onboarding Agent",    desc: "Simulate a 24-step onboarding workflow",       color: "emerald" },
  { id: "performance" as AgentType, icon: TrendingUp,    name: "Performance Agent",   desc: "Generate AI-powered performance insights",     color: "amber" },
]

const SAMPLE_RESUME = `John Doe
Senior Software Engineer | john.doe@email.com | GitHub: /johndoe

EXPERIENCE
Staff Engineer, Stripe (2021–2024)
• Led migration of payment processing to distributed microservices (99.99% uptime)
• Mentored 8 engineers, improved team velocity by 40%
• Built fraud detection ML pipeline reducing false positives by 62%

Senior Engineer, Airbnb (2018–2021)
• Architected real-time search service handling 500K QPS
• Led React Native mobile team, shipped 3 major releases

SKILLS: Python, Go, TypeScript, Kubernetes, AWS, PostgreSQL, Redis, Kafka

EDUCATION: BS Computer Science, Stanford University`

const INTERVIEW_QUESTIONS = [
  "Tell me about yourself and your most recent role.",
  "Describe a technically complex project you led. What were the key challenges?",
  "How do you approach mentoring junior engineers?",
  "Tell me about a time you had to make a hard technical trade-off.",
  "Where do you see yourself in 3 years?",
]

const ONBOARD_STEPS = [
  "Welcome email sent with portal login credentials",
  "Identity verification via document OCR completed",
  "Offer letter e-signed via DocuSign integration",
  "NDA and company policies acknowledged",
  "Background check initiated (ETA: 48 hours)",
  "IT equipment order placed (MacBook Pro, monitors)",
  "System accounts created (Email, Slack, GitHub, JIRA)",
  "Buddy mentor assigned: Sarah Chen (Engineering)",
]

const PERF_INSIGHTS = [
  { metric: "Goal Completion Rate", value: "87%", trend: "+12% vs last quarter", color: "emerald" },
  { metric: "Communication Score",  value: "9.2/10", trend: "Top 8% of team",   color: "blue" },
  { metric: "Technical Impact",     value: "High",  trend: "3 key projects shipped", color: "purple" },
  { metric: "Collaboration Index",  value: "94",    trend: "+5 points this month",   color: "amber" },
]

export default function DemoPage() {
  const [activeAgent, setActiveAgent] = useState<AgentType>("resume")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [interviewQ, setInterviewQ] = useState(0)
  const [interviewMsg, setInterviewMsg] = useState("")
  const [interviewHistory, setInterviewHistory] = useState<{ role: "ai" | "user"; msg: string }[]>([])
  const [onboardStep, setOnboardStep] = useState(-1)

  const COLOR_MAP: Record<string, string> = {
    blue:   "text-blue-400 bg-blue-500/10 border-blue-500/20",
    purple: "text-purple-400 bg-purple-500/10 border-purple-500/20",
    emerald:"text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    amber:  "text-amber-400 bg-amber-500/10 border-amber-500/20",
  }

  const runResumeDemo = async () => {
    setLoading(true)
    setResult(null)
    await new Promise(r => setTimeout(r, 1800))
    setResult({
      type: "resume",
      candidate: "John Doe",
      overall: 91,
      breakdown: [
        { label: "Technical Skills",   score: 95 },
        { label: "Experience Match",   score: 92 },
        { label: "Leadership",         score: 88 },
        { label: "Communication",      score: 87 },
        { label: "Cultural Fit Est.",  score: 84 },
      ],
      recommendation: "Strong hire — advance to technical interview",
      highlights: [
        "Staff-level experience at Stripe (payments scale)",
        "Proven ML background (fraud detection pipeline)",
        "Stanford CS — top-tier education",
        "Mentorship track record of 8+ engineers",
      ],
    })
    setLoading(false)
  }

  const sendInterviewMsg = async () => {
    if (!interviewMsg.trim()) return
    const userMsg = interviewMsg
    setInterviewMsg("")
    setInterviewHistory(h => [...h, { role: "user", msg: userMsg }])
    setLoading(true)
    await new Promise(r => setTimeout(r, 1000))
    const nextQ = interviewQ + 1
    const aiResponse = nextQ < INTERVIEW_QUESTIONS.length
      ? `Good answer! Here's my next question: ${INTERVIEW_QUESTIONS[nextQ]}`
      : "Thank you! That concludes our AI interview. Your responses are being scored now. You'll receive feedback within 2 hours."
    setInterviewHistory(h => [...h, { role: "ai", msg: aiResponse }])
    setInterviewQ(nextQ)
    setLoading(false)
  }

  const startOnboarding = async () => {
    setOnboardStep(0)
    for (let i = 0; i < ONBOARD_STEPS.length; i++) {
      await new Promise(r => setTimeout(r, 700))
      setOnboardStep(i + 1)
    }
  }

  return (
    <AppShell>
      <div className="px-6 py-6">
        <div className="mb-6">
          <h1 className="text-xl font-bold tracking-tight text-white">AI Demo Hub</h1>
          <p className="text-sm text-zinc-500 mt-0.5">Try each AI agent live — no setup required</p>
        </div>

        {/* Agent selector */}
        <div className="flex gap-3 mb-8">
          {AGENTS.map(a => {
            const Icon = a.icon
            const active = activeAgent === a.id
            return (
              <button
                key={a.id}
                onClick={() => { setActiveAgent(a.id); setResult(null); setInterviewHistory([]); setInterviewQ(0); setOnboardStep(-1) }}
                className={`flex-1 min-w-[160px] p-4 rounded-xl border text-left transition-all ${
                  active
                    ? `border-${a.color === "blue" ? "blue" : a.color === "purple" ? "purple" : a.color === "emerald" ? "emerald" : "amber"}-500/50 ${COLOR_MAP[a.color]}`
                    : "border-zinc-800 bg-zinc-900/50 hover:bg-zinc-900 text-zinc-400"
                }`}
              >
                <Icon className={`w-5 h-5 mb-2 ${active ? "" : "text-zinc-600"}`} />
                <div className={`text-sm font-semibold mb-0.5 ${active ? "" : "text-zinc-300"}`}>{a.name}</div>
                <div className="text-[11px] opacity-70">{a.desc}</div>
              </button>
            )
          })}
        </div>

        {/* Demo panels */}
        <div className="border border-zinc-800 rounded-xl overflow-hidden">

          {/* Resume Demo */}
          {activeAgent === "resume" && (
            <div className="flex gap-0 min-h-[500px]">
              <div className="flex-1 border-r border-zinc-800 p-6">
                <p className="text-xs font-semibold uppercase tracking-widest text-zinc-600 mb-4">Sample Resume Input</p>
                <pre className="text-xs text-zinc-400 whitespace-pre-wrap leading-relaxed font-mono bg-zinc-900/50 rounded-lg p-4">{SAMPLE_RESUME}</pre>
                <button
                  onClick={runResumeDemo}
                  disabled={loading}
                  className="mt-4 flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium px-4 py-2.5 rounded-lg transition-colors disabled:opacity-50"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Brain className="w-4 h-4" />}
                  {loading ? "Analyzing…" : "Run AI Analysis"}
                </button>
              </div>
              <div className="flex-1 p-6">
                {result?.type === "resume" ? (
                  <div className="animate-fade-up">
                    <div className="flex items-center justify-between mb-4">
                      <p className="text-xs font-semibold uppercase tracking-widest text-zinc-600">AI Analysis Result</p>
                      <span className="pill pill-green">Complete</span>
                    </div>
                    <div className="flex items-center gap-4 mb-5 p-4 bg-zinc-900/50 rounded-xl border border-zinc-800">
                      <div className="text-center">
                        <div className="text-3xl font-black text-white">{result.overall}</div>
                        <div className="text-[10px] text-zinc-600">Overall Score</div>
                      </div>
                      <div className="flex-1">
                        <div className="text-sm font-semibold text-emerald-400 mb-0.5">{result.recommendation}</div>
                        <div className="text-xs text-zinc-500">AI recommendation</div>
                      </div>
                    </div>
                    <div className="space-y-3 mb-5">
                      {result.breakdown.map((b: any) => (
                        <div key={b.label} className="flex items-center gap-3">
                          <span className="text-[11px] text-zinc-500 w-36 flex-shrink-0">{b.label}</span>
                          <div className="progress-track flex-1">
                            <div className={`progress-fill ${b.score >= 90 ? "green" : ""}`} style={{ width: `${b.score}%` }} />
                          </div>
                          <span className="text-[11px] font-mono text-zinc-400 w-7 text-right">{b.score}</span>
                        </div>
                      ))}
                    </div>
                    <div>
                      <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-600 mb-2">Key Highlights</p>
                      <div className="space-y-1.5">
                        {result.highlights.map((h: string, i: number) => (
                          <div key={i} className="flex items-start gap-2">
                            <CheckCircle className="w-3.5 h-3.5 text-emerald-400 mt-0.5 flex-shrink-0" />
                            <span className="text-xs text-zinc-400">{h}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center h-full text-center">
                    <Brain className="w-12 h-12 text-zinc-800 mb-4" />
                    <p className="text-sm text-zinc-600">Click "Run AI Analysis" to see the resume scored in real-time</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Interview Demo */}
          {activeAgent === "interview" && (
            <div className="flex flex-col min-h-[500px]">
              <div className="px-6 py-4 border-b border-zinc-800 flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center">
                  <Brain className="w-4 h-4 text-purple-400" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-white">HRAgent Interview AI</div>
                  <div className="text-[11px] text-zinc-600">Screening for: Senior Frontend Engineer</div>
                </div>
                <span className="ml-auto pill pill-green">Live</span>
              </div>

              <div className="flex-1 p-6 space-y-4 overflow-y-auto min-h-[300px]">
                {interviewHistory.length === 0 && (
                  <div className="py-8 text-center">
                    <p className="text-sm text-zinc-600 mb-4">The AI interviewer is ready. Start by clicking below.</p>
                    <button
                      onClick={() => setInterviewHistory([{ role: "ai", msg: `Hi! I'm HRAgent's Interview AI. I'll be conducting your screening today for the Senior Frontend Engineer role. Let's begin. ${INTERVIEW_QUESTIONS[0]}` }])}
                      className="flex items-center gap-2 bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors mx-auto"
                    >
                      <Zap className="w-4 h-4" /> Begin Interview
                    </button>
                  </div>
                )}
                {interviewHistory.map((msg, i) => (
                  <div key={i} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}>
                    {msg.role === "ai" && (
                      <div className="w-7 h-7 rounded-full bg-purple-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <Brain className="w-3.5 h-3.5 text-purple-400" />
                      </div>
                    )}
                    <div className={`max-w-[80%] px-4 py-3 rounded-xl text-sm leading-relaxed ${
                      msg.role === "ai"
                        ? "bg-zinc-900 border border-zinc-800 text-zinc-300"
                        : "bg-blue-600 text-white"
                    }`}>
                      {msg.msg}
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex gap-3">
                    <div className="w-7 h-7 rounded-full bg-purple-500/20 flex items-center justify-center">
                      <Loader2 className="w-3.5 h-3.5 text-purple-400 animate-spin" />
                    </div>
                    <div className="bg-zinc-900 border border-zinc-800 px-4 py-3 rounded-xl">
                      <div className="flex gap-1">
                        {[0,1,2].map(i => <div key={i} className="w-1.5 h-1.5 rounded-full bg-zinc-600 animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />)}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {interviewHistory.length > 0 && interviewQ < INTERVIEW_QUESTIONS.length && (
                <div className="px-6 py-4 border-t border-zinc-800 flex gap-3">
                  <input
                    value={interviewMsg}
                    onChange={e => setInterviewMsg(e.target.value)}
                    onKeyDown={e => e.key === "Enter" && !e.shiftKey && sendInterviewMsg()}
                    placeholder="Type your answer…"
                    className="flex-1 px-4 py-2.5 text-sm rounded-lg bg-zinc-900 border border-zinc-700 text-zinc-200 placeholder:text-zinc-600 outline-none focus:border-purple-500"
                  />
                  <button
                    onClick={sendInterviewMsg}
                    disabled={loading || !interviewMsg.trim()}
                    className="flex items-center gap-1.5 bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium px-4 py-2.5 rounded-lg transition-colors disabled:opacity-40"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Onboarding Demo */}
          {activeAgent === "onboarding" && (
            <div className="p-6 min-h-[500px]">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-widest text-zinc-600 mb-1">New Hire</p>
                  <h3 className="text-lg font-bold text-white">Alex Rodriguez</h3>
                  <p className="text-sm text-zinc-500">Staff Engineer · Engineering · Start: Apr 8</p>
                </div>
                {onboardStep < 0 && (
                  <button
                    onClick={startOnboarding}
                    className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium px-4 py-2.5 rounded-lg transition-colors"
                  >
                    <Zap className="w-4 h-4" /> Launch AI Onboarding
                  </button>
                )}
                {onboardStep >= 0 && (
                  <div className="text-right">
                    <div className="text-2xl font-black text-white">{Math.round((onboardStep / ONBOARD_STEPS.length) * 100)}%</div>
                    <div className="text-xs text-zinc-600">Complete</div>
                  </div>
                )}
              </div>

              {onboardStep >= 0 && (
                <div className="progress-track mb-6" style={{ height: "4px" }}>
                  <div
                    className="progress-fill green transition-all duration-700"
                    style={{ width: `${(onboardStep / ONBOARD_STEPS.length) * 100}%`, height: "4px" }}
                  />
                </div>
              )}

              <div className="space-y-2">
                {ONBOARD_STEPS.map((step, i) => {
                  const done = onboardStep > i
                  const running = onboardStep === i
                  return (
                    <div
                      key={i}
                      className={`flex items-center gap-3 px-4 py-3 rounded-xl border transition-all duration-300 ${
                        done    ? "border-emerald-500/30 bg-emerald-500/5" :
                        running ? "border-blue-500/30 bg-blue-500/10" :
                        "border-zinc-800 bg-transparent"
                      }`}
                    >
                      {done ? (
                        <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                      ) : running ? (
                        <Loader2 className="w-4 h-4 text-blue-400 animate-spin flex-shrink-0" />
                      ) : (
                        <div className="w-4 h-4 rounded-full border border-zinc-700 flex-shrink-0" />
                      )}
                      <span className={`text-sm ${done ? "text-zinc-500 line-through" : running ? "text-white" : "text-zinc-600"}`}>
                        {step}
                      </span>
                      {done && <CheckCircle className="w-3 h-3 text-emerald-500 ml-auto" />}
                      {running && <span className="text-[10px] text-blue-300 ml-auto animate-pulse">Running</span>}
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Performance Demo */}
          {activeAgent === "performance" && (
            <div className="p-6 min-h-[500px]">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-widest text-zinc-600 mb-1">AI Performance Review</p>
                  <h3 className="text-lg font-bold text-white">Sarah Chen — Q1 2026</h3>
                  <p className="text-sm text-zinc-500">Senior Engineer · Engineering</p>
                </div>
                <span className="pill pill-green">AI Generated</span>
              </div>

              <div className="grid gap-4 mb-6" style={{ gridTemplateColumns: "1fr 1fr" }}>
                {PERF_INSIGHTS.map((p, i) => (
                  <div key={i} className={`p-4 rounded-xl border ${
                    p.color === "emerald" ? "border-emerald-500/20 bg-emerald-500/5" :
                    p.color === "blue"    ? "border-blue-500/20 bg-blue-500/5" :
                    p.color === "purple"  ? "border-purple-500/20 bg-purple-500/5" :
                    "border-amber-500/20 bg-amber-500/5"
                  }`}>
                    <div className={`text-2xl font-black mb-1 ${
                      p.color === "emerald" ? "text-emerald-400" :
                      p.color === "blue"    ? "text-blue-400" :
                      p.color === "purple"  ? "text-purple-400" :
                      "text-amber-400"
                    }`}>{p.value}</div>
                    <div className="text-xs font-semibold text-zinc-300 mb-0.5">{p.metric}</div>
                    <div className="text-[11px] text-zinc-600">{p.trend}</div>
                  </div>
                ))}
              </div>

              <div className="border border-zinc-800 rounded-xl p-5">
                <p className="text-xs font-semibold uppercase tracking-widest text-zinc-600 mb-3">AI Written Summary</p>
                <p className="text-sm text-zinc-400 leading-relaxed">
                  Sarah has had an exceptional Q1 2026, consistently delivering high-impact work on the authentication
                  infrastructure overhaul. Her technical leadership has directly contributed to a 23% improvement in
                  system reliability. Her cross-functional collaboration with the product team has been noted by 4 stakeholders.
                  Recommended for a senior-to-staff promotion review in Q2.
                </p>
                <div className="mt-4 pt-4 border-t border-zinc-800 flex items-center gap-2">
                  <span className="text-[10px] text-zinc-700">Generated by HRAgent Performance AI</span>
                  <span className="text-[10px] text-zinc-800">·</span>
                  <span className="text-[10px] text-zinc-700">94% manager alignment score</span>
                </div>
              </div>
            </div>
          )}

        </div>
      </div>
    </AppShell>
  )
}
