"use client"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Bot, Volume2, MessageSquare, Clock, BarChart3 } from "lucide-react"

interface Message {
  id: string
  type: "ai" | "user"
  content: string
  timestamp: Date
  score?: number
  analysis?: any
}

interface InterviewSession {
  id: string
  candidateName: string
  position: string
  type: string
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

interface InterviewerPanelProps {
  session: InterviewSession
  messages: Message[]
  isSpeaking: boolean
  isProcessing: boolean
}

export function InterviewerPanel({ session, messages, isSpeaking, isProcessing }: InterviewerPanelProps) {
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, "0")}`
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600"
    if (score >= 60) return "text-yellow-600"
    return "text-red-600"
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b bg-blue-50">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
            <Bot className="h-6 w-6 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-lg">AI Interviewer</h3>
            <p className="text-sm text-gray-600">Conducting {session.type} interview</p>
          </div>
          {isSpeaking && (
            <div className="flex items-center space-x-2 text-blue-600">
              <Volume2 className="h-4 w-4" />
              <span className="text-sm">Speaking...</span>
            </div>
          )}
        </div>
      </div>

      {/* Interview Progress */}
      <div className="p-4 border-b bg-gray-50">
        <div className="grid grid-cols-2 gap-4 mb-4">
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
              <span>Duration</span>
              <span>{formatTime(session.duration)}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">In progress</span>
            </div>
          </div>
        </div>

        {/* Real-time Scores */}
        <div className="grid grid-cols-4 gap-2 text-xs">
          <div className="text-center">
            <div className="font-medium">Communication</div>
            <div className={`font-bold ${getScoreColor(session.aiAnalysis.communication)}`}>
              {session.aiAnalysis.communication.toFixed(1)}
            </div>
          </div>
          <div className="text-center">
            <div className="font-medium">Technical</div>
            <div className={`font-bold ${getScoreColor(session.aiAnalysis.technical)}`}>
              {session.aiAnalysis.technical.toFixed(1)}
            </div>
          </div>
          <div className="text-center">
            <div className="font-medium">Cultural Fit</div>
            <div className={`font-bold ${getScoreColor(session.aiAnalysis.cultural_fit)}`}>
              {session.aiAnalysis.cultural_fit.toFixed(1)}
            </div>
          </div>
          <div className="text-center">
            <div className="font-medium">Overall</div>
            <div className={`font-bold ${getScoreColor(session.aiAnalysis.overall)}`}>
              {session.aiAnalysis.overall.toFixed(1)}
            </div>
          </div>
        </div>
      </div>

      {/* Conversation */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.type === "ai" ? "justify-start" : "justify-end"}`}>
            <div
              className={`max-w-[80%] p-3 rounded-lg ${
                message.type === "ai" ? "bg-blue-100 text-blue-900" : "bg-gray-100 text-gray-900"
              }`}
            >
              <div className="flex items-center space-x-2 mb-1">
                {message.type === "ai" ? <Bot className="h-4 w-4" /> : <MessageSquare className="h-4 w-4" />}
                <span className="text-xs font-medium">
                  {message.type === "ai" ? "AI Interviewer" : session.candidateName}
                </span>
                {message.score && (
                  <Badge variant="secondary" className="text-xs">
                    Score: {message.score}/100
                  </Badge>
                )}
              </div>
              <div className="text-sm whitespace-pre-wrap">{message.content}</div>
              <div className="text-xs opacity-60 mt-1">{message.timestamp.toLocaleTimeString()}</div>
            </div>
          </div>
        ))}

        {isProcessing && (
          <div className="flex justify-start">
            <div className="bg-blue-100 text-blue-900 p-3 rounded-lg">
              <div className="flex items-center space-x-2">
                <Bot className="h-4 w-4" />
                <span className="text-xs font-medium">AI Interviewer</span>
              </div>
              <div className="flex items-center space-x-2 mt-1">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                  <div
                    className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
                    style={{ animationDelay: "0.1s" }}
                  ></div>
                  <div
                    className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
                    style={{ animationDelay: "0.2s" }}
                  ></div>
                </div>
                <span className="text-sm">Analyzing response...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Current Question Display */}
      <div className="p-4 border-t bg-blue-50">
        <div className="flex items-start space-x-2">
          <BarChart3 className="h-5 w-5 text-blue-600 mt-0.5" />
          <div>
            <h4 className="font-medium text-sm text-blue-900 mb-1">Current Question</h4>
            <p className="text-sm text-blue-800">
              Tell me about a challenging project you've worked on recently and how you overcame the obstacles.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
