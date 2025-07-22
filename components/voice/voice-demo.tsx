"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Mic, MicOff, Volume2, X, Bot, User, Phone, PhoneOff } from "lucide-react"
import { useVoice } from "@/components/providers/voice-provider"
import { useAI } from "@/components/providers/ai-provider"

interface VoiceDemoProps {
  onClose: () => void
}

interface Message {
  id: string
  type: "ai" | "user"
  content: string
  timestamp: Date
  confidence?: number
}

export function VoiceDemo({ onClose }: VoiceDemoProps) {
  const { isListening, isSpeaking, startListening, stopListening, speak, transcript, confidence } = useVoice()
  const { generateResponse, isProcessing } = useAI()

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "ai",
      content:
        "Hello! I'm your AI HR interviewer. I'll be conducting a voice interview with you today. Are you ready to begin?",
      timestamp: new Date(),
    },
  ])
  const [isCallActive, setIsCallActive] = useState(false)
  const [currentQuestion, setCurrentQuestion] = useState(0)

  const interviewQuestions = [
    "Tell me about yourself and your background in software development.",
    "What interests you most about this position and our company?",
    "Can you describe a challenging project you've worked on recently?",
    "How do you handle working in a team environment?",
    "Where do you see yourself in your career in the next 5 years?",
  ]

  useEffect(() => {
    // Auto-speak the first message
    if (messages.length === 1) {
      speak(messages[0].content)
    }
  }, [])

  useEffect(() => {
    // Process user speech when transcript is available
    if (transcript && !isListening && transcript.length > 10) {
      handleUserResponse(transcript)
    }
  }, [transcript, isListening])

  const startCall = async () => {
    setIsCallActive(true)
    const welcomeMessage = "Great! Let's start the interview. " + interviewQuestions[0]

    const newMessage: Message = {
      id: Date.now().toString(),
      type: "ai",
      content: welcomeMessage,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, newMessage])
    await speak(welcomeMessage)
  }

  const endCall = () => {
    setIsCallActive(false)
    stopListening()

    const endMessage: Message = {
      id: Date.now().toString(),
      type: "ai",
      content: "Thank you for the interview! I'll process your responses and get back to you soon. Have a great day!",
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, endMessage])
    speak(endMessage.content)
  }

  const handleUserResponse = async (userText: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: userText,
      timestamp: new Date(),
      confidence,
    }

    setMessages((prev) => [...prev, userMessage])

    // Generate AI response
    const aiResponse = await generateResponse(`Interview response: ${userText}`, {
      question: interviewQuestions[currentQuestion],
      questionNumber: currentQuestion + 1,
    })

    // Determine next question or conclusion
    let nextContent = ""
    if (currentQuestion < interviewQuestions.length - 1) {
      setCurrentQuestion((prev) => prev + 1)
      nextContent = `${aiResponse} Now, let me ask you: ${interviewQuestions[currentQuestion + 1]}`
    } else {
      nextContent = `${aiResponse} That concludes our interview. Thank you for your time and thoughtful responses. We'll be in touch soon!`
    }

    const aiMessage: Message = {
      id: Date.now().toString(),
      type: "ai",
      content: nextContent,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, aiMessage])
    await speak(nextContent)
  }

  const toggleListening = () => {
    if (isListening) {
      stopListening()
    } else {
      startListening()
    }
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center space-x-2">
          <Bot className="h-6 w-6 text-blue-600" />
          <h2 className="text-2xl font-bold">AI Voice Interview</h2>
        </div>
        <Button variant="ghost" size="sm" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Call Status */}
      <div className="mb-6">
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${isCallActive ? "bg-green-500" : "bg-gray-400"}`} />
            <span className="font-medium">{isCallActive ? "Interview in Progress" : "Ready to Start"}</span>
            {isCallActive && (
              <Badge variant="secondary">
                Question {currentQuestion + 1} of {interviewQuestions.length}
              </Badge>
            )}
          </div>

          {!isCallActive ? (
            <Button onClick={startCall} className="bg-green-600 hover:bg-green-700">
              <Phone className="h-4 w-4 mr-2" />
              Start Interview
            </Button>
          ) : (
            <Button onClick={endCall} variant="destructive">
              <PhoneOff className="h-4 w-4 mr-2" />
              End Interview
            </Button>
          )}
        </div>
      </div>

      {/* Voice Controls */}
      {isCallActive && (
        <div className="mb-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Voice Controls</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-center space-x-4">
                <Button
                  onClick={toggleListening}
                  className={`w-16 h-16 rounded-full ${
                    isListening ? "bg-red-500 hover:bg-red-600 animate-pulse" : "bg-blue-500 hover:bg-blue-600"
                  }`}
                >
                  {isListening ? <MicOff className="h-6 w-6 text-white" /> : <Mic className="h-6 w-6 text-white" />}
                </Button>

                <div className="flex-1 text-center">
                  {isListening && (
                    <div className="space-y-2">
                      <div className="text-sm text-gray-600">Listening...</div>
                      <div className="flex justify-center space-x-1">
                        {[1, 2, 3, 4, 5].map((i) => (
                          <div
                            key={i}
                            className="w-1 bg-blue-500 voice-wave"
                            style={{
                              height: `${Math.random() * 20 + 10}px`,
                              animationDelay: `${i * 0.1}s`,
                            }}
                          />
                        ))}
                      </div>
                    </div>
                  )}

                  {isSpeaking && (
                    <div className="flex items-center justify-center space-x-2">
                      <Volume2 className="h-5 w-5 text-blue-600" />
                      <span className="text-sm text-gray-600">AI Speaking...</span>
                    </div>
                  )}

                  {!isListening && !isSpeaking && (
                    <div className="text-sm text-gray-500">Click the microphone to respond</div>
                  )}
                </div>
              </div>

              {transcript && (
                <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                  <div className="text-sm text-gray-600 mb-1">Your response:</div>
                  <div className="text-gray-900">{transcript}</div>
                  {confidence > 0 && (
                    <div className="mt-2">
                      <div className="flex justify-between text-xs text-gray-500 mb-1">
                        <span>Confidence</span>
                        <span>{Math.round(confidence * 100)}%</span>
                      </div>
                      <Progress value={confidence * 100} className="h-1" />
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Conversation History */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Interview Conversation</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 max-h-96 overflow-y-auto">
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
                    {message.confidence && (
                      <Badge variant="secondary" className="text-xs">
                        {Math.round(message.confidence * 100)}% confidence
                      </Badge>
                    )}
                  </div>
                  <div className="text-sm">{message.content}</div>
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
                    <div className="typing-indicator">
                      <div className="w-2 h-2 bg-gray-500 rounded-full"></div>
                    </div>
                    <span className="text-sm text-gray-600">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Interview Progress */}
      {isCallActive && (
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
    </div>
  )
}
