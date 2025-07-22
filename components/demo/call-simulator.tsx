"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Phone, PhoneOff, X, Bot, Clock, CheckCircle, Mic, Volume2 } from "lucide-react"
import { useVoice } from "@/components/providers/voice-provider"

interface CallSimulatorProps {
  onClose: () => void
}

interface CallLog {
  id: string
  type: "outbound" | "inbound"
  contact: string
  purpose: string
  duration: string
  status: "completed" | "in-progress" | "failed"
  summary: string
  timestamp: Date
}

export function CallSimulator({ onClose }: CallSimulatorProps) {
  const { speak, isSpeaking } = useVoice()
  const [isCallActive, setIsCallActive] = useState(false)
  const [currentCall, setCurrentCall] = useState<CallLog | null>(null)
  const [callLogs, setCallLogs] = useState<CallLog[]>([
    {
      id: "1",
      type: "outbound",
      contact: "John Doe (Candidate)",
      purpose: "Interview scheduling",
      duration: "3:45",
      status: "completed",
      summary: "Successfully scheduled interview for tomorrow at 2 PM. Candidate confirmed availability.",
      timestamp: new Date(Date.now() - 3600000),
    },
    {
      id: "2",
      type: "outbound",
      contact: "Sarah Manager (Hiring Manager)",
      purpose: "Candidate update",
      duration: "2:15",
      status: "completed",
      summary: "Updated manager on top 3 candidates. Discussed interview panel composition.",
      timestamp: new Date(Date.now() - 7200000),
    },
  ])
  const [phoneNumber, setPhoneNumber] = useState("")
  const [callPurpose, setCallPurpose] = useState("")

  const callScenarios = [
    {
      contact: "Jane Smith (Candidate)",
      phone: "+1 (555) 123-4567",
      purpose: "Interview follow-up",
      script:
        "Hi Jane, this is the AI HR assistant from TechCorp. I'm calling to follow up on your interview yesterday. Do you have a moment to discuss next steps?",
    },
    {
      contact: "Mike Johnson (Reference)",
      phone: "+1 (555) 987-6543",
      purpose: "Reference check",
      script:
        "Hello Mike, I'm calling from TechCorp regarding John Doe who listed you as a reference. Could you spare a few minutes to discuss his work performance?",
    },
    {
      contact: "Lisa Chen (Hiring Manager)",
      phone: "+1 (555) 456-7890",
      purpose: "Candidate recommendation",
      script:
        "Hi Lisa, I wanted to update you on the candidates we've screened for the Senior Developer position. I have three strong recommendations to discuss.",
    },
  ]

  const startCall = async (scenario?: any) => {
    const callData = scenario || {
      contact: phoneNumber || "Unknown Contact",
      purpose: callPurpose || "General inquiry",
      script: "Hello, this is the AI HR assistant. How can I help you today?",
    }

    const newCall: CallLog = {
      id: Date.now().toString(),
      type: "outbound",
      contact: callData.contact,
      purpose: callData.purpose,
      duration: "0:00",
      status: "in-progress",
      summary: "",
      timestamp: new Date(),
    }

    setCurrentCall(newCall)
    setIsCallActive(true)

    // Simulate dialing
    await new Promise((resolve) => setTimeout(resolve, 2000))

    // Start speaking
    await speak(callData.script)

    // Simulate call duration
    let duration = 0
    const timer = setInterval(() => {
      duration += 1
      const minutes = Math.floor(duration / 60)
      const seconds = duration % 60
      setCurrentCall((prev) =>
        prev
          ? {
              ...prev,
              duration: `${minutes}:${seconds.toString().padStart(2, "0")}`,
            }
          : null,
      )
    }, 1000)

    // Auto-end call after demo
    setTimeout(() => {
      clearInterval(timer)
      endCall("Successfully completed call. All information gathered and next steps confirmed.")
    }, 15000)
  }

  const endCall = (summary: string) => {
    if (currentCall) {
      const completedCall: CallLog = {
        ...currentCall,
        status: "completed",
        summary,
      }

      setCallLogs((prev) => [completedCall, ...prev])
      setCurrentCall(null)
    }

    setIsCallActive(false)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "text-green-600"
      case "in-progress":
        return "text-blue-600"
      case "failed":
        return "text-red-600"
      default:
        return "text-gray-600"
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge className="bg-green-100 text-green-800">Completed</Badge>
      case "in-progress":
        return <Badge className="bg-blue-100 text-blue-800">In Progress</Badge>
      case "failed":
        return <Badge variant="destructive">Failed</Badge>
      default:
        return <Badge variant="secondary">Unknown</Badge>
    }
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center space-x-2">
          <Phone className="h-6 w-6 text-orange-600" />
          <h2 className="text-2xl font-bold">AI Call Simulator</h2>
        </div>
        <Button variant="ghost" size="sm" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Call Interface */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Make a Call</CardTitle>
              <p className="text-gray-600">AI agent will make outbound calls with natural conversation</p>
            </CardHeader>
            <CardContent>
              {!isCallActive ? (
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Phone Number</label>
                    <Input
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value)}
                      placeholder="+1 (555) 123-4567"
                    />
                  </div>

                  <div>
                    <label className="text-sm font-medium">Call Purpose</label>
                    <Input
                      value={callPurpose}
                      onChange={(e) => setCallPurpose(e.target.value)}
                      placeholder="Interview scheduling, reference check, etc."
                    />
                  </div>

                  <Button
                    onClick={() => startCall()}
                    className="w-full bg-green-600 hover:bg-green-700"
                    disabled={!phoneNumber || !callPurpose}
                  >
                    <Phone className="h-4 w-4 mr-2" />
                    Start Call
                  </Button>
                </div>
              ) : (
                <div className="text-center space-y-4">
                  <div className="w-20 h-20 bg-green-500 rounded-full flex items-center justify-center mx-auto animate-pulse">
                    <Phone className="h-8 w-8 text-white" />
                  </div>

                  {currentCall && (
                    <div>
                      <h3 className="font-semibold">{currentCall.contact}</h3>
                      <p className="text-sm text-gray-600">{currentCall.purpose}</p>
                      <p className="text-lg font-mono">{currentCall.duration}</p>
                    </div>
                  )}

                  <div className="flex items-center justify-center space-x-2">
                    {isSpeaking ? (
                      <>
                        <Volume2 className="h-5 w-5 text-blue-600" />
                        <span className="text-sm">AI Speaking...</span>
                      </>
                    ) : (
                      <>
                        <Mic className="h-5 w-5 text-green-600" />
                        <span className="text-sm">Listening...</span>
                      </>
                    )}
                  </div>

                  <Button onClick={() => endCall("Call ended by user")} variant="destructive" className="w-full">
                    <PhoneOff className="h-4 w-4 mr-2" />
                    End Call
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quick Call Scenarios */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Call Scenarios</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {callScenarios.map((scenario, index) => (
                  <div key={index} className="p-3 border rounded-lg">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="font-medium text-sm">{scenario.contact}</h4>
                        <p className="text-xs text-gray-600">{scenario.purpose}</p>
                      </div>
                      <Button size="sm" onClick={() => startCall(scenario)} disabled={isCallActive}>
                        Call
                      </Button>
                    </div>
                    <p className="text-xs text-gray-500 italic">"{scenario.script.substring(0, 60)}..."</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Call Logs */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Call History</CardTitle>
              <p className="text-gray-600">Recent AI-powered calls and their outcomes</p>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {callLogs.map((call) => (
                  <div key={call.id} className="p-4 border rounded-lg">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="font-medium">{call.contact}</h4>
                        <p className="text-sm text-gray-600">{call.purpose}</p>
                      </div>
                      <div className="text-right">
                        {getStatusBadge(call.status)}
                        <p className="text-xs text-gray-500 mt-1">{call.duration}</p>
                      </div>
                    </div>

                    <p className="text-sm text-gray-700 mb-2">{call.summary}</p>

                    <div className="flex justify-between items-center text-xs text-gray-500">
                      <span>{call.timestamp.toLocaleString()}</span>
                      <span className="flex items-center">
                        <Clock className="h-3 w-3 mr-1" />
                        {call.type}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Call Features */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle>AI Calling Capabilities</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              {
                title: "Natural Conversation",
                description: "AI speaks naturally and understands context",
                icon: Bot,
              },
              {
                title: "Call Recording",
                description: "Automatic recording and transcription",
                icon: Mic,
              },
              {
                title: "Smart Summaries",
                description: "AI generates detailed call summaries",
                icon: CheckCircle,
              },
            ].map((feature, index) => (
              <div key={index} className="text-center p-4 border rounded-lg">
                <feature.icon className="h-8 w-8 text-orange-600 mx-auto mb-2" />
                <h3 className="font-medium mb-1">{feature.title}</h3>
                <p className="text-sm text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
