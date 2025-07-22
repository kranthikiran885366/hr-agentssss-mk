"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import {
  Plus,
  Search,
  Calendar,
  Clock,
  User,
  Video,
  Phone,
  MessageSquare,
  Play,
  Eye,
  MoreHorizontal,
} from "lucide-react"
import Link from "next/link"

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

export default function InterviewsPage() {
  const [sessions, setSessions] = useState<InterviewSession[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [filterStatus, setFilterStatus] = useState<string>("all")
  const [filterType, setFilterType] = useState<string>("all")

  useEffect(() => {
    fetchSessions()
  }, [])

  const fetchSessions = async () => {
    try {
      const response = await fetch("/api/interviews/sessions")
      const data = await response.json()
      setSessions(data)
    } catch (error) {
      console.error("Failed to fetch sessions:", error)
    } finally {
      setLoading(false)
    }
  }

  const filteredSessions = sessions.filter((session) => {
    const matchesSearch =
      session.candidateName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      session.position.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = filterStatus === "all" || session.status === filterStatus
    const matchesType = filterType === "all" || session.type === filterType

    return matchesSearch && matchesStatus && matchesType
  })

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

  const getModeIcon = (mode: string) => {
    switch (mode) {
      case "video":
        return <Video className="h-4 w-4" />
      case "voice":
        return <Phone className="h-4 w-4" />
      case "chat":
        return <MessageSquare className="h-4 w-4" />
      default:
        return <MessageSquare className="h-4 w-4" />
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600"
    if (score >= 60) return "text-yellow-600"
    return "text-red-600"
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, "0")}`
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-6 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">Interview Sessions</h1>
          <p className="text-gray-600 mt-2">Manage and monitor all interview sessions</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          New Interview
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search candidates or positions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="completed">Completed</option>
          <option value="scheduled">Scheduled</option>
          <option value="cancelled">Cancelled</option>
        </select>

        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">All Types</option>
          <option value="technical">Technical</option>
          <option value="behavioral">Behavioral</option>
          <option value="screening">Screening</option>
          <option value="comprehensive">Comprehensive</option>
        </select>
      </div>

      {/* Sessions List */}
      <div className="space-y-4">
        {filteredSessions.map((session) => (
          <Card key={session.id} className="hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                    <User className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">{session.candidateName}</h3>
                    <p className="text-gray-600">{session.position}</p>
                    <p className="text-sm text-gray-500">{session.candidateEmail}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <div className="flex items-center space-x-2 mb-1">
                      {getModeIcon(session.mode)}
                      <Badge variant="outline" className="capitalize">
                        {session.type}
                      </Badge>
                      <Badge className={getStatusColor(session.status)}>{session.status}</Badge>
                    </div>
                    <div className="text-sm text-gray-500">
                      {session.status === "active" ? (
                        <span className="flex items-center">
                          <Clock className="h-3 w-3 mr-1" />
                          {formatTime(session.duration)}
                        </span>
                      ) : (
                        <span>{new Date(session.startTime).toLocaleDateString()}</span>
                      )}
                    </div>
                  </div>

                  {session.status !== "scheduled" && (
                    <div className="text-right">
                      <div className={`text-lg font-bold ${getScoreColor(session.aiAnalysis.overall)}`}>
                        {session.aiAnalysis.overall.toFixed(1)}
                      </div>
                      <div className="text-sm text-gray-500">Score</div>
                    </div>
                  )}

                  <div className="flex items-center space-x-2">
                    {session.status === "active" && (
                      <Link href={`/interview/${session.id}`}>
                        <Button size="sm">
                          <Play className="h-4 w-4 mr-1" />
                          Join
                        </Button>
                      </Link>
                    )}

                    {session.status === "completed" && (
                      <Button size="sm" variant="outline">
                        <Eye className="h-4 w-4 mr-1" />
                        View Report
                      </Button>
                    )}

                    <Button size="sm" variant="ghost">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>

              {session.status === "active" && (
                <div className="mt-4 pt-4 border-t">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <div className="text-sm text-gray-600">Progress</div>
                      <div className="font-medium">
                        {session.questionsAnswered}/{session.totalQuestions} questions
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Communication</div>
                      <div className={`font-medium ${getScoreColor(session.aiAnalysis.communication)}`}>
                        {session.aiAnalysis.communication.toFixed(1)}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Technical</div>
                      <div className={`font-medium ${getScoreColor(session.aiAnalysis.technical)}`}>
                        {session.aiAnalysis.technical.toFixed(1)}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Cultural Fit</div>
                      <div className={`font-medium ${getScoreColor(session.aiAnalysis.cultural_fit)}`}>
                        {session.aiAnalysis.cultural_fit.toFixed(1)}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ))}

        {filteredSessions.length === 0 && (
          <Card>
            <CardContent className="p-12 text-center">
              <div className="text-gray-500 mb-4">
                <Calendar className="h-12 w-12 mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No interviews found</h3>
                <p>No interviews match your current filters.</p>
              </div>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Schedule New Interview
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
