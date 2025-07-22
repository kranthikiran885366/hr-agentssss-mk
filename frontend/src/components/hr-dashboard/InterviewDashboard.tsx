"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import {
  MessageSquare,
  Phone,
  Video,
  Clock,
  CheckCircle,
  TrendingUp,
  Users,
  BarChart3,
  Pause,
  Square,
} from "lucide-react"

interface InterviewSession {
  id: string
  candidateName: string
  candidateEmail: string
  position: string
  type: "technical" | "behavioral" | "screening" | "comprehensive"
  mode: "chat" | "voice" | "video"
  status: "active" | "completed" | "scheduled" | "cancelled"
  startTime: string
  duration: number
  currentScore: number
  questionsAnswered: number
  totalQuestions: number
  aiAnalysis: {
    communication: number
    technical: number
    cultural_fit: number
    overall: number
  }
}

interface InterviewStats {
  totalInterviews: number
  activeInterviews: number
  completedToday: number
  averageScore: number
  averageDuration: number
  conversionRate: number
  byType: Record<string, number>
  byMode: Record<string, number>
}

export function InterviewDashboard() {
  const [sessions, setSessions] = useState<InterviewSession[]>([])
  const [stats, setStats] = useState<InterviewStats>({
    totalInterviews: 0,
    activeInterviews: 0,
    completedToday: 0,
    averageScore: 0,
    averageDuration: 0,
    conversionRate: 0,
    byType: {},
    byMode: {},
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchInterviewData()
    const interval = setInterval(fetchInterviewData, 10000)
    return () => clearInterval(interval)
  }, [])

  const fetchInterviewData = async () => {
    try {
      const [sessionsResponse, statsResponse] = await Promise.all([
        fetch("/api/interviews/sessions"),
        fetch("/api/interviews/stats"),
      ])

      const sessionsData = await sessionsResponse.json()
      const statsData = await statsResponse.json()

      setSessions(sessionsData)
      setStats(statsData)
    } catch (error) {
      console.error("Failed to fetch interview data:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleInterviewAction = async (sessionId: string, action: "pause" | "resume" | "end") => {
    try {
      await fetch(`/api/interviews/${sessionId}/${action}`, {
        method: "POST",
      })
      fetchInterviewData()
    } catch (error) {
      console.error(`Failed to ${action} interview:`, error)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800"
      case "completed":
        return "bg-blue-100 text-blue-800"
      case "scheduled":
        return "bg-yellow-100 text-yellow-800"
      case "cancelled":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "technical":
        return <BarChart3 className="h-4 w-4" />
      case "behavioral":
        return <Users className="h-4 w-4" />
      case "screening":
        return <CheckCircle className="h-4 w-4" />
      case "comprehensive":
        return <TrendingUp className="h-4 w-4" />
      default:
        return <MessageSquare className="h-4 w-4" />
    }
  }

  const getModeIcon = (mode: string) => {
    switch (mode) {
      case "voice":
        return <Phone className="h-4 w-4" />
      case "video":
        return <Video className="h-4 w-4" />
      default:
        return <MessageSquare className="h-4 w-4" />
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600"
    if (score >= 60) return "text-yellow-600"
    return "text-red-600"
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Interview Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Interviews</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalInterviews}</div>
            <p className="text-xs text-muted-foreground">All time interviews conducted</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Now</CardTitle>
            <Clock className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.activeInterviews}</div>
            <p className="text-xs text-muted-foreground">Currently in progress</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed Today</CardTitle>
            <CheckCircle className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.completedToday}</div>
            <p className="text-xs text-muted-foreground">Finished interviews today</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Score</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${getScoreColor(stats.averageScore)}`}>
              {stats.averageScore.toFixed(1)}
            </div>
            <p className="text-xs text-muted-foreground">Out of 100 points</p>
          </CardContent>
        </Card>
      </div>

      {/* Active Interview Sessions */}
      <Card>
        <CardHeader>
          <CardTitle>Active Interview Sessions</CardTitle>
          <p className="text-sm text-gray-600">Real-time interview monitoring and control</p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {sessions
              .filter((s) => s.status === "active")
              .map((session) => (
                <div key={session.id} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <div className="flex items-center space-x-2">
                        {getModeIcon(session.mode)}
                        {getTypeIcon(session.type)}
                      </div>
                      <div>
                        <h4 className="font-medium">{session.candidateName}</h4>
                        <p className="text-sm text-gray-600">{session.position}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className={getStatusColor(session.status)}>{session.status}</Badge>
                      <span className="text-sm text-gray-500">
                        {Math.floor(session.duration / 60)}:{(session.duration % 60).toString().padStart(2, "0")}
                      </span>
                      <div className="flex space-x-1">
                        <Button size="sm" variant="outline" onClick={() => handleInterviewAction(session.id, "pause")}>
                          <Pause className="h-3 w-3" />
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => handleInterviewAction(session.id, "end")}>
                          <Square className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Progress</span>
                        <span>
                          {session.questionsAnswered}/{session.totalQuestions}
                        </span>
                      </div>
                      <Progress value={(session.questionsAnswered / session.totalQuestions) * 100} />
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Current Score</span>
                        <span className={getScoreColor(session.currentScore)}>{session.currentScore.toFixed(1)}</span>
                      </div>
                      <Progress value={session.currentScore} />
                    </div>
                  </div>

                  <div className="grid grid-cols-4 gap-4 text-sm">
                    <div className="text-center">
                      <div className="font-medium">Communication</div>
                      <div className={getScoreColor(session.aiAnalysis.communication)}>
                        {session.aiAnalysis.communication.toFixed(1)}
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="font-medium">Technical</div>
                      <div className={getScoreColor(session.aiAnalysis.technical)}>
                        {session.aiAnalysis.technical.toFixed(1)}
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="font-medium">Cultural Fit</div>
                      <div className={getScoreColor(session.aiAnalysis.cultural_fit)}>
                        {session.aiAnalysis.cultural_fit.toFixed(1)}
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="font-medium">Overall</div>
                      <div className={getScoreColor(session.aiAnalysis.overall)}>
                        {session.aiAnalysis.overall.toFixed(1)}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            {sessions.filter((s) => s.status === "active").length === 0 && (
              <div className="text-center py-8 text-gray-500">No active interviews at the moment</div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Recent Completed Interviews */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Completed Interviews</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {sessions
              .filter((s) => s.status === "completed")
              .slice(0, 5)
              .map((session) => (
                <div key={session.id} className="flex items-center justify-between p-3 border rounded">
                  <div className="flex items-center space-x-3">
                    <div className="flex items-center space-x-2">
                      {getModeIcon(session.mode)}
                      {getTypeIcon(session.type)}
                    </div>
                    <div>
                      <div className="font-medium">{session.candidateName}</div>
                      <div className="text-sm text-gray-600">{session.position}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`font-medium ${getScoreColor(session.aiAnalysis.overall)}`}>
                      {session.aiAnalysis.overall.toFixed(1)}/100
                    </div>
                    <div className="text-sm text-gray-500">
                      {Math.floor(session.duration / 60)}m {session.duration % 60}s
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
