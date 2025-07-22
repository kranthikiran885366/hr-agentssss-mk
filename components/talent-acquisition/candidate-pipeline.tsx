"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Users, TrendingUp, Clock, Star, Mail, Phone, MapPin, Briefcase, Calendar, ArrowRight } from "lucide-react"
import { useSession } from "next-auth/react"
import { CandidateProfile } from "./CandidateProfile"

interface Candidate {
  id: string
  name: string
  email: string
  phone: string
  location: string
  current_position: string
  experience_years: number
  skills: string[]
  education: string
  resume_url: string
  application_date: string
  current_stage: string
  overall_score: number
  screening_scores: {
    technical: number
    experience: number
    cultural_fit: number
    communication: number
  }
  source: string
  job_id: string
  match_score: number // Added for match score
}

interface PipelineStage {
  id: string
  name: string
  count: number
  candidates: Candidate[]
  color: string
}

export function CandidatePipeline() {
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [selectedJob, setSelectedJob] = useState<string>("all")
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null)
  const [loading, setLoading] = useState(true)
  const [sourcingResult, setSourcingResult] = useState<any>(null)
  const [sourcingLoading, setSourcingLoading] = useState(false)
  const [screeningResult, setScreeningResult] = useState<any>(null)
  const [screeningLoading, setScreeningLoading] = useState(false)
  const [schedulingCandidate, setSchedulingCandidate] = useState<string | null>(null)
  const [availableSlots, setAvailableSlots] = useState<any[]>([])
  const [selectedSlot, setSelectedSlot] = useState<any>(null)
  const [scheduleResult, setScheduleResult] = useState<any>(null)
  const [scheduling, setScheduling] = useState(false)
  const [selectedCandidates, setSelectedCandidates] = useState<string[]>([])
  const [bulkAction, setBulkAction] = useState<string>("")
  const [bulkLoading, setBulkLoading] = useState(false)
  const [bulkResult, setBulkResult] = useState<string>("")
  const [profileCandidateId, setProfileCandidateId] = useState<string | null>(null)

  const pipelineStages: PipelineStage[] = [
    { id: "applied", name: "Applied", count: 0, candidates: [], color: "bg-blue-500" },
    { id: "screening", name: "Screening", count: 0, candidates: [], color: "bg-yellow-500" },
    { id: "phone_screen", name: "Phone Screen", count: 0, candidates: [], color: "bg-orange-500" },
    { id: "technical_interview", name: "Technical", count: 0, candidates: [], color: "bg-purple-500" },
    { id: "final_interview", name: "Final", count: 0, candidates: [], color: "bg-green-500" },
    { id: "offer", name: "Offer", count: 0, candidates: [], color: "bg-emerald-500" },
    { id: "hired", name: "Hired", count: 0, candidates: [], color: "bg-teal-500" },
  ]

  const { data: session } = useSession()
  const userRole = session?.user?.role || "hr" // TODO: Use real session role

  useEffect(() => {
    fetchCandidates()
  }, [selectedJob])

  useEffect(() => {
    let ws: WebSocket | null = null
    let reconnectTimeout: NodeJS.Timeout | null = null
    function connectWS() {
      ws = new WebSocket("ws://localhost:8000/ws/talent-acquisition/updates") // TODO: Use correct backend URL
      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)
          if (msg.type === "pipeline_update") {
            fetchCandidates()
            // Optionally, show a toast/notification
          }
        } catch {}
      }
      ws.onclose = () => {
        // Reconnect after 2s
        reconnectTimeout = setTimeout(connectWS, 2000)
      }
    }
    connectWS()
    return () => {
      if (ws) ws.close()
      if (reconnectTimeout) clearTimeout(reconnectTimeout)
    }
    // eslint-disable-next-line
  }, [])

  const fetchCandidates = async () => {
    try {
      setLoading(true)
      const params = selectedJob !== "all" ? `?jobId=${selectedJob}` : ""
      const response = await fetch(`/api/talent-acquisition/candidates${params}`)
      const data = await response.json()
      setCandidates(data)
    } catch (error) {
      console.error("Failed to fetch candidates:", error)
    } finally {
      setLoading(false)
    }
  }

  // Group candidates by stage
  const stagesWithCandidates = pipelineStages.map((stage) => ({
    ...stage,
    candidates: candidates.filter((c) => c.current_stage === stage.id),
    count: candidates.filter((c) => c.current_stage === stage.id).length,
  }))

  const totalCandidates = candidates.length
  const averageScore =
    candidates.length > 0 ? candidates.reduce((sum, c) => sum + c.overall_score, 0) / candidates.length : 0

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600"
    if (score >= 60) return "text-yellow-600"
    return "text-red-600"
  }

  const getScoreBadgeVariant = (score: number) => {
    if (score >= 80) return "default"
    if (score >= 60) return "secondary"
    return "destructive"
  }

  const handleCandidateAction = async (candidateId: string, action: string) => {
    try {
      let endpoint = "/api/talent-acquisition/candidates"
      let body: any = {}
      if (action === "advance") {
        // Advance candidate to next stage (implement in backend if needed)
        body = { action: "advance", candidateId }
      } else if (action === "reject") {
        body = { action: "reject", candidateId }
      } else if (action === "schedule_interview") {
        body = { action: "schedule_interview", candidateId }
      } else if (action === "screen") {
        body = { action: "screen", applicationId: candidateId }
      } else {
        return
      }
      await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      })
      fetchCandidates() // Refresh after action
    } catch (error) {
      console.error(`Failed to perform action ${action} for candidate ${candidateId}:`, error)
    }
  }

  const handleSourceCandidates = async () => {
    setSourcingLoading(true)
    setSourcingResult(null)
    try {
      const res = await fetch("/api/talent-acquisition/candidates", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "source", jobId: selectedJob, strategy: {} }),
      })
      const data = await res.json()
      setSourcingResult(data)
      fetchCandidates()
    } catch (error) {
      setSourcingResult({ error: "Failed to source candidates" })
    } finally {
      setSourcingLoading(false)
    }
  }

  const handleScreenCandidate = async (candidateId: string) => {
    setScreeningLoading(true)
    setScreeningResult(null)
    try {
      const res = await fetch("/api/talent-acquisition/candidates", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "screen", applicationId: candidateId }),
      })
      const data = await res.json()
      setScreeningResult(data)
      fetchCandidates()
    } catch (error) {
      setScreeningResult({ error: "Failed to screen candidate" })
    } finally {
      setScreeningLoading(false)
    }
  }

  const fetchSlots = async (jobId: string) => {
    setAvailableSlots([])
    setSelectedSlot(null)
    setScheduleResult(null)
    const res = await fetch(`/api/talent-acquisition/interviews/slots?job_id=${jobId}`)
    const data = await res.json()
    setAvailableSlots(data)
  }

  const handleScheduleInterview = async (candidate: Candidate) => {
    if (!selectedSlot) return
    setScheduling(true)
    setScheduleResult(null)
    try {
      const res = await fetch("/api/talent-acquisition/interviews/schedule", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          candidate_id: candidate.id,
          job_id: candidate.job_id,
          slot: selectedSlot,
          interviewer_email: "interviewer@company.com", // TODO: Use real interviewer
          candidate_email: candidate.email,
        }),
      })
      const data = await res.json()
      setScheduleResult(data)
      fetchCandidates()
    } catch (error) {
      setScheduleResult({ error: "Failed to schedule interview" })
    } finally {
      setScheduling(false)
    }
  }

  const handleSelectCandidate = (id: string) => {
    setSelectedCandidates((prev) => prev.includes(id) ? prev.filter(cid => cid !== id) : [...prev, id])
  }

  const handleBulkAction = async () => {
    if (!bulkAction || selectedCandidates.length === 0) return
    setBulkLoading(true)
    setBulkResult("")
    try {
      const res = await fetch("/api/talent-acquisition/candidates/bulk", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: bulkAction, candidateIds: selectedCandidates }),
      })
      const data = await res.json()
      setBulkResult(data.status || data.error || "Done")
      setSelectedCandidates([])
      fetchCandidates()
    } catch (error) {
      setBulkResult("Bulk action failed")
    } finally {
      setBulkLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Candidate Sourcing UI */}
      <div className="flex items-center gap-4 mb-4">
        <Button onClick={handleSourceCandidates} disabled={sourcingLoading || selectedJob === "all"}>
          {sourcingLoading ? "Sourcing..." : "Source Candidates"}
        </Button>
        {sourcingResult && (
          <span className={sourcingResult.error ? "text-red-600" : "text-green-600"}>
            {sourcingResult.error || "Sourcing complete!"}
          </span>
        )}
      </div>
      {/* Pipeline Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Candidates</p>
                <p className="text-2xl font-bold">{totalCandidates}</p>
              </div>
              <Users className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Average Score</p>
                <p className={`text-2xl font-bold ${getScoreColor(averageScore)}`}>{averageScore.toFixed(1)}</p>
              </div>
              <Star className="h-8 w-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">In Process</p>
                <p className="text-2xl font-bold">
                  {candidates.filter((c) => !["hired", "rejected"].includes(c.current_stage)).length}
                </p>
              </div>
              <Clock className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Conversion Rate</p>
                <p className="text-2xl font-bold text-green-600">12.5%</p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Bulk Actions */}
      {['admin', 'hr'].includes(userRole) && (
        <div className="mb-4 flex gap-2 items-center">
          <select value={bulkAction} onChange={e => setBulkAction(e.target.value)} className="border rounded px-2 py-1">
            <option value="">Bulk Action</option>
            <option value="advance">Advance</option>
            <option value="reject">Reject</option>
            <option value="send_email">Send Email</option>
          </select>
          <Button onClick={handleBulkAction} disabled={!bulkAction || selectedCandidates.length === 0 || bulkLoading}>
            {bulkLoading ? "Processing..." : "Apply"}
          </Button>
          {bulkResult && <span className="ml-2 text-green-600">{bulkResult}</span>}
        </div>
      )}

      {/* Pipeline Visualization */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Hiring Pipeline
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col space-y-4">
            {/* Pipeline Flow */}
            <div className="flex items-center justify-between overflow-x-auto pb-4">
              {stagesWithCandidates.map((stage, index) => (
                <div key={stage.id} className="flex items-center">
                  <div className="flex flex-col items-center min-w-[120px]">
                    <div
                      className={`w-12 h-12 rounded-full ${stage.color} flex items-center justify-center text-white font-bold`}
                    >
                      {stage.count}
                    </div>
                    <p className="text-sm font-medium mt-2 text-center">{stage.name}</p>
                    <p className="text-xs text-gray-500">{stage.count} candidates</p>
                  </div>
                  {index < stagesWithCandidates.length - 1 && <ArrowRight className="h-6 w-6 text-gray-400 mx-4" />}
                </div>
              ))}
            </div>

            {/* Stage Details */}
            <Tabs defaultValue="screening" className="w-full">
              <TabsList className="grid w-full grid-cols-7">
                {stagesWithCandidates.map((stage) => (
                  <TabsTrigger key={stage.id} value={stage.id} className="text-xs">
                    {stage.name} ({stage.count})
                  </TabsTrigger>
                ))}
              </TabsList>

              {stagesWithCandidates.map((stage) => (
                <TabsContent key={stage.id} value={stage.id} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {stage.candidates.map((candidate) => (
                      <Card
                        key={candidate.id}
                        className="hover:shadow-md transition-shadow cursor-pointer"
                        onClick={() => setProfileCandidateId(candidate.id)}
                      >
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex items-center space-x-3">
                              <Avatar>
                                <AvatarImage src={`/avatars/${candidate.id}.jpg`} />
                                <AvatarFallback>
                                  {candidate.name
                                    .split(" ")
                                    .map((n) => n[0])
                                    .join("")}
                                </AvatarFallback>
                              </Avatar>
                              <div>
                                <h4 className="font-semibold">{candidate.name}</h4>
                                <p className="text-sm text-gray-600">{candidate.current_position}</p>
                              </div>
                            </div>
                            <Badge variant={getScoreBadgeVariant(candidate.overall_score)}>
                              {candidate.overall_score}
                            </Badge>
                            {candidate.match_score >= 80 && (
                              <Badge variant="default" className="ml-2">
                                Match: {candidate.match_score}
                              </Badge>
                            )}
                          </div>

                          <div className="space-y-2 text-sm">
                            <div className="flex items-center gap-2">
                              <Mail className="h-4 w-4 text-gray-400" />
                              <span className="truncate">{candidate.email}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <MapPin className="h-4 w-4 text-gray-400" />
                              <span>{candidate.location}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Briefcase className="h-4 w-4 text-gray-400" />
                              <span>{candidate.experience_years} years exp</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Calendar className="h-4 w-4 text-gray-400" />
                              <span>Applied {new Date(candidate.application_date).toLocaleDateString()}</span>
                            </div>
                          </div>

                          <div className="mt-3">
                            <div className="flex flex-wrap gap-1">
                              {candidate.skills.slice(0, 3).map((skill) => (
                                <Badge key={skill} variant="outline" className="text-xs">
                                  {skill}
                                </Badge>
                              ))}
                              {candidate.skills.length > 3 && (
                                <Badge variant="outline" className="text-xs">
                                  +{candidate.skills.length - 3}
                                </Badge>
                              )}
                            </div>
                          </div>

                          <div className="mt-3 pt-3 border-t">
                            <div className="flex justify-between text-xs text-gray-600 mb-1">
                              <span>Overall Score</span>
                              <span>{candidate.overall_score}%</span>
                            </div>
                            <Progress value={candidate.overall_score} className="h-2" />
                          </div>

                          <div className="mt-3 flex gap-2">
                            <Button size="sm" variant="outline" className="flex-1 bg-transparent">
                              View Profile
                            </Button>
                            <Button size="sm" onClick={() => handleCandidateAction(candidate.id, "advance")}>Advance</Button>
                            <Button size="sm" onClick={() => handleCandidateAction(candidate.id, "reject")}>Reject</Button>
                            {['admin', 'hr'].includes(userRole) && (
                              <Button size="sm" onClick={() => { setSchedulingCandidate(candidate.id); fetchSlots(candidate.job_id); }}>Schedule Interview</Button>
                            )}
                            {schedulingCandidate === candidate.id && availableSlots.length > 0 && (
                              <div className="mt-2">
                                <div className="mb-2">Pick a slot:</div>
                                {availableSlots.map((slot, idx) => (
                                  <Button key={idx} size="sm" variant={selectedSlot === slot ? "default" : "outline"} onClick={() => setSelectedSlot(slot)}>
                                    {new Date(slot.start).toLocaleString()} - {new Date(slot.end).toLocaleTimeString()}
                                  </Button>
                                ))}
                                <Button size="sm" className="ml-2" onClick={() => handleScheduleInterview(candidate)} disabled={!selectedSlot || scheduling}>
                                  {scheduling ? "Scheduling..." : "Confirm"}
                                </Button>
                                {scheduleResult && (
                                  <div className="mt-2 text-green-600">Scheduled! <a href={scheduleResult.event_link} target="_blank" rel="noopener noreferrer" className="underline">View Event</a></div>
                                )}
                              </div>
                            )}
                            <Button size="sm" onClick={() => handleScreenCandidate(candidate.id)} disabled={screeningLoading}>Screen</Button>
                            {screeningResult && selectedCandidate?.id === candidate.id && (
                              <span className={screeningResult.error ? "text-red-600" : "text-green-600"}>{screeningResult.error || "Screened!"}</span>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>

                  {stage.candidates.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No candidates in this stage</p>
                    </div>
                  )}
                </TabsContent>
              ))}
            </Tabs>
          </div>
        </CardContent>
      </Card>

      {/* Candidate Detail Modal would go here */}
      {profileCandidateId && (
        <CandidateProfile candidateId={profileCandidateId} onClose={() => setProfileCandidateId(null)} />
      )}
    </div>
  )
}
