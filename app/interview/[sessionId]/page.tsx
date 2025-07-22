"use client"

import { useState, useEffect } from "react"
import { useParams } from "next/navigation"
import { InterviewCallScreen } from "@/components/interview/interview-call-screen"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Settings } from "lucide-react"
import Link from "next/link"

interface InterviewSession {
  id: string
  candidateName: string
  candidateEmail: string
  position: string
  type: "technical" | "behavioral" | "screening" | "comprehensive"
  mode: "chat" | "voice" | "video"
  status: "active" | "completed" | "scheduled" | "paused"
  startTime: string
  duration: number
  currentScore: number
  questionsAnswered: number
  totalQuestions: number
  currentQuestion: string
  aiAnalysis: {
    communication: number
    technical: number
    cultural_fit: number
    overall: number
  }
}

export default function InterviewSessionPage() {
  const params = useParams()
  const sessionId = params.sessionId as string
  const [session, setSession] = useState<InterviewSession | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchSession()
  }, [sessionId])

  const fetchSession = async () => {
    try {
      const response = await fetch(`/api/interviews/sessions/${sessionId}`)
      if (!response.ok) {
        throw new Error("Session not found")
      }
      const sessionData = await response.json()
      setSession(sessionData)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load session")
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error || !session) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-6 text-center">
            <h2 className="text-xl font-semibold mb-2">Session Not Found</h2>
            <p className="text-gray-600 mb-4">{error || "The interview session could not be found."}</p>
            <Link href="/dashboard">
              <Button>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/dashboard">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Dashboard
              </Button>
            </Link>
            <div>
              <h1 className="text-xl font-semibold">Interview Session</h1>
              <p className="text-sm text-gray-600">
                {session.candidateName} - {session.position}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </Button>
          </div>
        </div>
      </div>

      {/* Interview Call Screen */}
      <InterviewCallScreen session={session} onSessionUpdate={setSession} />
    </div>
  )
}
