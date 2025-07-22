"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Send, X, Bot, User, MessageSquare, CheckCircle } from "lucide-react"
import { useAI } from "@/components/providers/ai-provider"

interface ChatDemoProps {
  onClose: () => void
}

interface Message {
  id: string
  type: "ai" | "user"
  content: string
  timestamp: Date
  score?: number
}

export function ChatDemo({ onClose }: ChatDemoProps) {
  const { generateResponse, isProcessing } = useAI()
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "ai",
      content:
        "Hello! I'm your AI HR interviewer. I'll be conducting a chat-based interview with you today. Let's start with: Tell me about yourself and your background.",
      timestamp: new Date(),
    },
  ])
  const [inputValue, setInputValue] = useState("")
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [interviewScore, setInterviewScore] = useState(0)
  const [isInterviewComplete, setIsInterviewComplete] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)

  const interviewQuestions = [
    "Tell me about yourself and your background.",
    "What interests you about this position?",
    "Describe a challenging project you've worked on.",
    "How do you handle working in a team?",
    "Where do you see yourself in 5 years?",
    "Do you have any questions for us?",
  ]

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isProcessing) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue("")

    // Simulate scoring the response
    const responseScore = Math.floor(Math.random() * 30) + 70 // 70-100
    userMessage.score = responseScore

    // Update overall interview score
    setInterviewScore((prev) => Math.round((prev + responseScore) / 2))

    // Generate AI response
    const aiResponse = await generateResponse(`Interview response: ${inputValue}`, {
      question: interviewQuestions[currentQuestion],
      questionNumber: currentQuestion + 1,
      score: responseScore,
    })

    let nextContent = ""
    if (currentQuestion < interviewQuestions.length - 1) {
      setCurrentQuestion((prev) => prev + 1)
      nextContent = `${aiResponse} Next question: ${interviewQuestions[currentQuestion + 1]}`
    } else {
      setIsInterviewComplete(true)
      nextContent = `${aiResponse} That concludes our interview! Thank you for your time. Your overall interview score is ${interviewScore}/100. We'll be in touch soon with next steps.`
    }

    const aiMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: "ai",
      content: nextContent,
      timestamp: new Date(),
    }

    setTimeout(() => {
      setMessages((prev) => [...prev, aiMessage])
    }, 1000)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 90) return "text-green-600"
    if (score >= 80) return "text-blue-600"
    if (score >= 70) return "text-yellow-600"
    return "text-red-600"
  }

  const getScoreBadge = (score: number) => {
    if (score >= 90) return "Excellent"
    if (score >= 80) return "Good"
    if (score >= 70) return "Average"
    return "Needs Improvement"
  }

  return (
    <div className="p-6 h-[600px] flex flex-col">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center space-x-2">
          <MessageSquare className="h-6 w-6 text-blue-600" />
          <h2 className="text-2xl font-bold">AI Chat Interview</h2>
        </div>
        <Button variant="ghost" size="sm" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Interview Status */}
      <div className="mb-4">
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${isInterviewComplete ? "bg-green-500" : "bg-blue-500"}`} />
            <span className="font-medium">{isInterviewComplete ? "Interview Complete" : "Interview in Progress"}</span>
            {!isInterviewComplete && (
              <Badge variant="secondary">
                Question {currentQuestion + 1} of {interviewQuestions.length}
              </Badge>
            )}
          </div>

          {interviewScore > 0 && (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">Score:</span>
              <span className={`font-bold ${getScoreColor(interviewScore)}`}>{interviewScore}/100</span>
              <Badge variant="outline" className={getScoreColor(interviewScore)}>
                {getScoreBadge(interviewScore)}
              </Badge>
            </div>
          )}
        </div>
      </div>

      {/* Chat Messages */}
      <Card className="flex-1 flex flex-col">
        <CardContent className="flex-1 p-4 overflow-y-auto">
          <div className="space-y-4">
            {messages.map((message) => (
              <div key={message.id} className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[80%] p-3 rounded-lg chat-bubble-enter ${
                    message.type === "user" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-900"
                  }`}
                >
                  <div className="flex items-center space-x-2 mb-1">
                    {message.type === "ai" ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
                    <span className="text-xs opacity-75">{message.type === "ai" ? "HR Agent" : "You"}</span>
                    {message.score && (
                      <Badge variant="secondary" className={`text-xs ${getScoreColor(message.score)}`}>
                        Score: {message.score}/100
                      </Badge>
                    )}
                  </div>
                  <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                  <div className="text-xs opacity-50 mt-1">{message.timestamp.toLocaleTimeString()}</div>
                </div>
              </div>
            ))}

            {isProcessing && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-900 p-3 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <Bot className="h-4 w-4" />
                    <span className="text-xs">HR Agent</span>
                  </div>
                  <div className="flex items-center space-x-2 mt-1">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                      <div
                        className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                        style={{ animationDelay: "0.1s" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-600">Analyzing your response...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </CardContent>

        {/* Input Area */}
        {!isInterviewComplete && (
          <div className="p-4 border-t">
            <div className="flex space-x-2">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your response here..."
                disabled={isProcessing}
                className="flex-1"
              />
              <Button onClick={handleSendMessage} disabled={!inputValue.trim() || isProcessing} className="px-6">
                <Send className="h-4 w-4" />
              </Button>
            </div>
            <div className="mt-2 text-xs text-gray-500">Press Enter to send • Shift+Enter for new line</div>
          </div>
        )}
      </Card>

      {/* Interview Progress */}
      {!isInterviewComplete && (
        <div className="mt-4">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Interview Progress</span>
            <span>
              {currentQuestion + 1} of {interviewQuestions.length} questions
            </span>
          </div>
          <Progress value={((currentQuestion + 1) / interviewQuestions.length) * 100} />
        </div>
      )}

      {/* Interview Complete Actions */}
      {isInterviewComplete && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center space-x-2 mb-3">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <span className="font-medium text-green-900">Interview Complete!</span>
          </div>
          <div className="text-sm text-green-700 mb-3">
            Thank you for completing the interview. Your responses have been analyzed and scored.
          </div>
          <div className="flex space-x-2">
            <Button size="sm" className="bg-green-600 hover:bg-green-700">
              View Detailed Report
            </Button>
            <Button size="sm" variant="outline">
              Schedule Follow-up
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
