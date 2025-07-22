"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Send } from "lucide-react"
import { InterviewerPanel } from "./interviewer-panel"
import { CandidatePanel } from "./candidate-panel"
import { InterviewControls } from "./interview-controls"
import { InterviewAnalytics } from "./interview-analytics"

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

interface Message {
  id: string
  type: "ai" | "user"
  content: string
  timestamp: Date
  score?: number
  analysis?: any
}

interface InterviewCallScreenProps {
  session: InterviewSession
  onSessionUpdate: (session: InterviewSession) => void
}

export function InterviewCallScreen({ session, onSessionUpdate }: InterviewCallScreenProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "ai",
      content: `Hello ${session.candidateName}! Welcome to your ${session.type} interview for the ${session.position} position. I'm your AI interviewer and I'll be conducting this session with you today. Are you ready to begin?`,
      timestamp: new Date(),
    },
  ])
  const [currentMessage, setCurrentMessage] = useState("")
  const [isRecording, setIsRecording] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [isVideoEnabled, setIsVideoEnabled] = useState(session.mode === "video")
  const [isAudioEnabled, setIsAudioEnabled] = useState(true)
  const [transcript, setTranscript] = useState("")
  const [isProcessing, setIsProcessing] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (session.mode === "video" && videoRef.current) {
      startVideo()
    }
  }, [session.mode])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const startVideo = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      })
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }
    } catch (error) {
      console.error("Error accessing camera:", error)
    }
  }

  const toggleRecording = () => {
    setIsRecording(!isRecording)
    if (!isRecording) {
      // Start recording
      startSpeechRecognition()
    } else {
      // Stop recording
      stopSpeechRecognition()
    }
  }

  const startSpeechRecognition = () => {
    if ("webkitSpeechRecognition" in window) {
      const recognition = new (window as any).webkitSpeechRecognition()
      recognition.continuous = true
      recognition.interimResults = true
      recognition.lang = "en-US"

      recognition.onresult = (event: any) => {
        let finalTranscript = ""
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript
          }
        }
        if (finalTranscript) {
          setTranscript(finalTranscript)
          handleSpeechInput(finalTranscript)
        }
      }

      recognition.start()
    }
  }

  const stopSpeechRecognition = () => {
    // Implementation for stopping speech recognition
  }

  const handleSpeechInput = async (speechText: string) => {
    if (!speechText.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: speechText,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setIsProcessing(true)

    try {
      // Send to AI for processing
      const response = await fetch(`/api/interviews/${session.id}/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: speechText, type: "speech" }),
      })

      const aiResponse = await response.json()

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "ai",
        content: aiResponse.message,
        timestamp: new Date(),
        analysis: aiResponse.analysis,
      }

      setMessages((prev) => [...prev, aiMessage])

      // Update session with new analysis
      if (aiResponse.sessionUpdate) {
        onSessionUpdate(aiResponse.sessionUpdate)
      }

      // Speak the AI response
      if (session.mode === "voice" || session.mode === "video") {
        speakText(aiResponse.message)
      }
    } catch (error) {
      console.error("Error processing message:", error)
    } finally {
      setIsProcessing(false)
      setTranscript("")
    }
  }

  const handleTextMessage = async () => {
    if (!currentMessage.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: currentMessage,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setCurrentMessage("")
    setIsProcessing(true)

    try {
      const response = await fetch(`/api/interviews/${session.id}/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: currentMessage, type: "text" }),
      })

      const aiResponse = await response.json()

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "ai",
        content: aiResponse.message,
        timestamp: new Date(),
        analysis: aiResponse.analysis,
      }

      setMessages((prev) => [...prev, aiMessage])

      if (aiResponse.sessionUpdate) {
        onSessionUpdate(aiResponse.sessionUpdate)
      }
    } catch (error) {
      console.error("Error processing message:", error)
    } finally {
      setIsProcessing(false)
    }
  }

  const speakText = async (text: string) => {
    setIsSpeaking(true)
    try {
      const response = await fetch("/api/voice/synthesize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, voice: "en-US-AriaNeural" }),
      })

      const audioData = await response.blob()
      const audio = new Audio(URL.createObjectURL(audioData))

      audio.onended = () => setIsSpeaking(false)
      await audio.play()
    } catch (error) {
      console.error("Error speaking text:", error)
      setIsSpeaking(false)
    }
  }

  const handleSessionControl = async (action: "pause" | "resume" | "end") => {
    try {
      await fetch(`/api/interviews/${session.id}/${action}`, {
        method: "POST",
      })

      const updatedSession = {
        ...session,
        status: action === "end" ? "completed" : action === "pause" ? "paused" : "active",
      }
      onSessionUpdate(updatedSession)
    } catch (error) {
      console.error(`Error ${action}ing session:`, error)
    }
  }

  return (
    <div className="h-[calc(100vh-80px)] flex">
      {/* Left Panel - Interviewer/AI Side */}
      <div className="w-1/2 border-r bg-white flex flex-col">
        <InterviewerPanel session={session} messages={messages} isSpeaking={isSpeaking} isProcessing={isProcessing} />
      </div>

      {/* Right Panel - Candidate Side */}
      <div className="w-1/2 bg-gray-50 flex flex-col">
        <CandidatePanel
          session={session}
          isVideoEnabled={isVideoEnabled}
          isAudioEnabled={isAudioEnabled}
          isRecording={isRecording}
          transcript={transcript}
          videoRef={videoRef}
          onToggleVideo={() => setIsVideoEnabled(!isVideoEnabled)}
          onToggleAudio={() => setIsAudioEnabled(!isAudioEnabled)}
          onToggleRecording={toggleRecording}
        />
      </div>

      {/* Bottom Panel - Controls and Chat */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t p-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Interview Controls */}
            <div className="lg:col-span-1">
              <InterviewControls
                session={session}
                onSessionControl={handleSessionControl}
                isRecording={isRecording}
                isVideoEnabled={isVideoEnabled}
                isAudioEnabled={isAudioEnabled}
                onToggleRecording={toggleRecording}
                onToggleVideo={() => setIsVideoEnabled(!isVideoEnabled)}
                onToggleAudio={() => setIsAudioEnabled(!isAudioEnabled)}
              />
            </div>

            {/* Chat Input */}
            <div className="lg:col-span-1">
              <div className="flex space-x-2">
                <Textarea
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  placeholder="Type your response here..."
                  className="flex-1 min-h-[40px] max-h-[120px]"
                  onKeyPress={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault()
                      handleTextMessage()
                    }
                  }}
                />
                <Button onClick={handleTextMessage} disabled={!currentMessage.trim() || isProcessing}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Analytics Preview */}
            <div className="lg:col-span-1">
              <InterviewAnalytics session={session} compact />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
