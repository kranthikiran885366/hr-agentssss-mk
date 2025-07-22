"use client"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Play, Pause, Square, Mic, MicOff, Video, VideoOff, Volume2, VolumeX, Settings } from "lucide-react"

interface InterviewSession {
  id: string
  status: "active" | "completed" | "scheduled" | "paused"
  mode: "chat" | "voice" | "video"
  duration: number
}

interface InterviewControlsProps {
  session: InterviewSession
  onSessionControl: (action: "pause" | "resume" | "end") => void
  isRecording: boolean
  isVideoEnabled: boolean
  isAudioEnabled: boolean
  onToggleRecording: () => void
  onToggleVideo: () => void
  onToggleAudio: () => void
}

export function InterviewControls({
  session,
  onSessionControl,
  isRecording,
  isVideoEnabled,
  isAudioEnabled,
  onToggleRecording,
  onToggleVideo,
  onToggleAudio,
}: InterviewControlsProps) {
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, "0")}`
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800"
      case "paused":
        return "bg-yellow-100 text-yellow-800"
      case "completed":
        return "bg-blue-100 text-blue-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  return (
    <div className="flex items-center justify-between">
      {/* Session Status */}
      <div className="flex items-center space-x-3">
        <Badge className={getStatusColor(session.status)}>{session.status}</Badge>
        <span className="text-sm font-mono">{formatTime(session.duration)}</span>
      </div>

      {/* Media Controls */}
      <div className="flex items-center space-x-2">
        {session.mode === "video" && (
          <Button variant={isVideoEnabled ? "default" : "outline"} size="sm" onClick={onToggleVideo}>
            {isVideoEnabled ? <Video className="h-4 w-4" /> : <VideoOff className="h-4 w-4" />}
          </Button>
        )}

        {(session.mode === "voice" || session.mode === "video") && (
          <Button variant={isRecording ? "destructive" : "outline"} size="sm" onClick={onToggleRecording}>
            {isRecording ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
          </Button>
        )}

        <Button variant={isAudioEnabled ? "default" : "outline"} size="sm" onClick={onToggleAudio}>
          {isAudioEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
        </Button>
      </div>

      {/* Session Controls */}
      <div className="flex items-center space-x-2">
        {session.status === "active" ? (
          <Button variant="outline" size="sm" onClick={() => onSessionControl("pause")}>
            <Pause className="h-4 w-4 mr-1" />
            Pause
          </Button>
        ) : session.status === "paused" ? (
          <Button variant="default" size="sm" onClick={() => onSessionControl("resume")}>
            <Play className="h-4 w-4 mr-1" />
            Resume
          </Button>
        ) : null}

        <Button variant="destructive" size="sm" onClick={() => onSessionControl("end")}>
          <Square className="h-4 w-4 mr-1" />
          End
        </Button>

        <Button variant="outline" size="sm">
          <Settings className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
