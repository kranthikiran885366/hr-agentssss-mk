"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { BarChart3, TrendingUp, MessageSquare, Clock } from "lucide-react"

interface InterviewSession {
  id: string
  currentScore: number
  questionsAnswered: number
  totalQuestions: number
  duration: number
  aiAnalysis: {
    communication: number
    technical: number
    cultural_fit: number
    overall: number
  }
}

interface InterviewAnalyticsProps {
  session: InterviewSession
  compact?: boolean
}

export function InterviewAnalytics({ session, compact = false }: InterviewAnalyticsProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600"
    if (score >= 60) return "text-yellow-600"
    return "text-red-600"
  }

  const getScoreBadge = (score: number) => {
    if (score >= 90) return "Excellent"
    if (score >= 80) return "Good"
    if (score >= 70) return "Average"
    return "Needs Improvement"
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, "0")}`
  }

  if (compact) {
    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Overall Score</span>
          <span className={`font-bold ${getScoreColor(session.aiAnalysis.overall)}`}>
            {session.aiAnalysis.overall.toFixed(1)}/100
          </span>
        </div>
        <Progress value={session.aiAnalysis.overall} className="h-2" />
        <div className="flex justify-between text-xs text-gray-500">
          <span>
            Progress: {session.questionsAnswered}/{session.totalQuestions}
          </span>
          <span>Time: {formatTime(session.duration)}</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Overall Score */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-lg flex items-center space-x-2">
            <BarChart3 className="h-5 w-5" />
            <span>Interview Analytics</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center mb-4">
            <div className={`text-3xl font-bold ${getScoreColor(session.aiAnalysis.overall)}`}>
              {session.aiAnalysis.overall.toFixed(1)}
            </div>
            <div className="text-sm text-gray-600">Overall Score</div>
            <Badge variant="outline" className={getScoreColor(session.aiAnalysis.overall)}>
              {getScoreBadge(session.aiAnalysis.overall)}
            </Badge>
          </div>
          <Progress value={session.aiAnalysis.overall} className="h-3" />
        </CardContent>
      </Card>

      {/* Detailed Scores */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Detailed Analysis</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span>Communication Skills</span>
              <span className={getScoreColor(session.aiAnalysis.communication)}>
                {session.aiAnalysis.communication.toFixed(1)}/100
              </span>
            </div>
            <Progress value={session.aiAnalysis.communication} className="h-2" />
          </div>

          <div>
            <div className="flex justify-between text-sm mb-1">
              <span>Technical Competency</span>
              <span className={getScoreColor(session.aiAnalysis.technical)}>
                {session.aiAnalysis.technical.toFixed(1)}/100
              </span>
            </div>
            <Progress value={session.aiAnalysis.technical} className="h-2" />
          </div>

          <div>
            <div className="flex justify-between text-sm mb-1">
              <span>Cultural Fit</span>
              <span className={getScoreColor(session.aiAnalysis.cultural_fit)}>
                {session.aiAnalysis.cultural_fit.toFixed(1)}/100
              </span>
            </div>
            <Progress value={session.aiAnalysis.cultural_fit} className="h-2" />
          </div>
        </CardContent>
      </Card>

      {/* Session Stats */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Session Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center space-x-2">
              <MessageSquare className="h-4 w-4 text-gray-500" />
              <div>
                <div className="font-medium">
                  {session.questionsAnswered}/{session.totalQuestions}
                </div>
                <div className="text-gray-600">Questions</div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-gray-500" />
              <div>
                <div className="font-medium">{formatTime(session.duration)}</div>
                <div className="text-gray-600">Duration</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Real-time Insights */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base flex items-center space-x-2">
            <TrendingUp className="h-4 w-4" />
            <span>Live Insights</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <div className="flex items-center justify-between">
              <span>Response Quality</span>
              <Badge variant="secondary">Improving</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span>Confidence Level</span>
              <Badge variant="secondary">High</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span>Technical Depth</span>
              <Badge variant="secondary">Good</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
