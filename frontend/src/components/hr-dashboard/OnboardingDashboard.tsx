"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import {
  Users,
  Clock,
  CheckCircle,
  AlertTriangle,
  FileText,
  UserCheck,
  Calendar,
  TrendingUp,
  Pause,
  RotateCcw,
} from "lucide-react"

interface OnboardingSession {
  id: string
  candidateName: string
  candidateEmail: string
  position: string
  startDate: string
  status: "initiated" | "in_progress" | "completed" | "delayed" | "cancelled"
  currentStep: string
  completionPercentage: number
  daysRemaining: number
  documentsSubmitted: number
  totalDocuments: number
  accountsCreated: number
  totalAccounts: number
  assignedMentor?: string
  estimatedCompletion: string
}

interface OnboardingStats {
  totalSessions: number
  activeSessions: number
  completedThisMonth: number
  averageCompletionTime: number
  completionRate: number
  documentVerificationRate: number
  byStatus: Record<string, number>
  byStep: Record<string, number>
}

export function OnboardingDashboard() {
  const [sessions, setSessions] = useState<OnboardingSession[]>([])
  const [stats, setStats] = useState<OnboardingStats>({
    totalSessions: 0,
    activeSessions: 0,
    completedThisMonth: 0,
    averageCompletionTime: 0,
    completionRate: 0,
    documentVerificationRate: 0,
    byStatus: {},
    byStep: {},
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchOnboardingData()
    const interval = setInterval(fetchOnboardingData, 15000)
    return () => clearInterval(interval)
  }, [])

  const fetchOnboardingData = async () => {
    try {
      const [sessionsResponse, statsResponse] = await Promise.all([
        fetch("/api/onboarding/sessions"),
        fetch("/api/onboarding/stats"),
      ])

      const sessionsData = await sessionsResponse.json()
      const statsData = await statsResponse.json()

      setSessions(sessionsData)
      setStats(statsData)
    } catch (error) {
      console.error("Failed to fetch onboarding data:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleSessionAction = async (sessionId: string, action: "pause" | "resume" | "restart") => {
    try {
      await fetch(`/api/onboarding/${sessionId}/${action}`, {
        method: "POST",
      })
      fetchOnboardingData()
    } catch (error) {
      console.error(`Failed to ${action} onboarding:`, error)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-100 text-green-800"
      case "in_progress":
        return "bg-blue-100 text-blue-800"
      case "initiated":
        return "bg-yellow-100 text-yellow-800"
      case "delayed":
        return "bg-orange-100 text-orange-800"
      case "cancelled":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case "in_progress":
        return <Clock className="h-4 w-4 text-blue-600" />
      case "delayed":
        return <AlertTriangle className="h-4 w-4 text-orange-600" />
      default:
        return <Users className="h-4 w-4 text-gray-600" />
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
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
      {/* Onboarding Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalSessions}</div>
            <p className="text-xs text-muted-foreground">All onboarding sessions</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Sessions</CardTitle>
            <Clock className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats.activeSessions}</div>
            <p className="text-xs text-muted-foreground">Currently in progress</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed This Month</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.completedThisMonth}</div>
            <p className="text-xs text-muted-foreground">Successfully onboarded</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completion Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.completionRate.toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">Success rate</p>
          </CardContent>
        </Card>
      </div>

      {/* Process Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Process Efficiency</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Average Completion Time</span>
                  <span>{stats.averageCompletionTime} days</span>
                </div>
                <Progress value={Math.max(0, 100 - (stats.averageCompletionTime / 14) * 100)} />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Document Verification Rate</span>
                  <span>{stats.documentVerificationRate.toFixed(1)}%</span>
                </div>
                <Progress value={stats.documentVerificationRate} />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Automation Rate</span>
                  <span>92%</span>
                </div>
                <Progress value={92} />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Status Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(stats.byStatus).map(([status, count]) => (
                <div key={status} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(status)}
                    <span className="text-sm capitalize">{status.replace("_", " ")}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium">{count}</span>
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${(count / stats.totalSessions) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Active Onboarding Sessions */}
      <Card>
        <CardHeader>
          <CardTitle>Active Onboarding Sessions</CardTitle>
          <p className="text-sm text-gray-600">Real-time onboarding progress monitoring</p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {sessions
              .filter((s) => ["initiated", "in_progress", "delayed"].includes(s.status))
              .map((session) => (
                <div key={session.id} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <div>
                        <h4 className="font-medium">{session.candidateName}</h4>
                        <p className="text-sm text-gray-600">{session.position}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className={getStatusColor(session.status)}>{session.status.replace("_", " ")}</Badge>
                      <span className="text-sm text-gray-500">
                        {session.daysRemaining > 0 ? `${session.daysRemaining} days left` : "Overdue"}
                      </span>
                      <div className="flex space-x-1">
                        <Button size="sm" variant="outline" onClick={() => handleSessionAction(session.id, "pause")}>
                          <Pause className="h-3 w-3" />
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => handleSessionAction(session.id, "restart")}>
                          <RotateCcw className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Overall Progress</span>
                        <span>{session.completionPercentage.toFixed(1)}%</span>
                      </div>
                      <Progress value={session.completionPercentage} />
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Documents</span>
                        <span>
                          {session.documentsSubmitted}/{session.totalDocuments}
                        </span>
                      </div>
                      <Progress value={(session.documentsSubmitted / session.totalDocuments) * 100} />
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Accounts</span>
                        <span>
                          {session.accountsCreated}/{session.totalAccounts}
                        </span>
                      </div>
                      <Progress value={(session.accountsCreated / session.totalAccounts) * 100} />
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-1">
                        <FileText className="h-4 w-4 text-gray-500" />
                        <span>Current: {session.currentStep.replace("_", " ")}</span>
                      </div>
                      {session.assignedMentor && (
                        <div className="flex items-center space-x-1">
                          <UserCheck className="h-4 w-4 text-gray-500" />
                          <span>Mentor: {session.assignedMentor}</span>
                        </div>
                      )}
                    </div>
                    <div className="flex items-center space-x-1">
                      <Calendar className="h-4 w-4 text-gray-500" />
                      <span>Start: {formatDate(session.startDate)}</span>
                    </div>
                  </div>
                </div>
              ))}
            {sessions.filter((s) => ["initiated", "in_progress", "delayed"].includes(s.status)).length === 0 && (
              <div className="text-center py-8 text-gray-500">No active onboarding sessions at the moment</div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Recent Completions */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Completions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {sessions
              .filter((s) => s.status === "completed")
              .slice(0, 5)
              .map((session) => (
                <div key={session.id} className="flex items-center justify-between p-3 border rounded">
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <div>
                      <div className="font-medium">{session.candidateName}</div>
                      <div className="text-sm text-gray-600">{session.position}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-green-600">Completed</div>
                    <div className="text-sm text-gray-500">{formatDate(session.estimatedCompletion)}</div>
                  </div>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
