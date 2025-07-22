"use client"

import type React from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { User, Video, VideoOff, Mic, MicOff, Volume2, VolumeX } from "lucide-react"

interface InterviewSession {
  id: string
  candidateName: string
  candidateEmail: string
  position: string
  mode: "chat" | "voice" | "video"
}

interface CandidatePanelProps {
  session: InterviewSession
  isVideoEnabled: boolean
  isAudioEnabled: boolean
  isRecording: boolean
  transcript: string
  videoRef: React.RefObject<HTMLVideoElement>
  onToggleVideo: () => void
  onToggleAudio: () => void
  onToggleRecording: () => void
}

export function CandidatePanel({
  session,
  isVideoEnabled,
  isAudioEnabled,
  isRecording,
  transcript,
  videoRef,
  onToggleVideo,
  onToggleAudio,
  onToggleRecording,
}: CandidatePanelProps) {
  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b bg-green-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center">
              <User className="h-6 w-6 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">{session.candidateName}</h3>
              <p className="text-sm text-gray-600">{session.candidateEmail}</p>
            </div>
          </div>
          <Badge variant="outline" className="bg-green-100 text-green-800">
            {session.position}
          </Badge>
        </div>
      </div>

      {/* Video/Avatar Area */}
      <div className="flex-1 relative bg-gray-900">
        {session.mode === "video" && isVideoEnabled ? (
          <video ref={videoRef} autoPlay muted className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <div className="text-center">
              <div className="w-32 h-32 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <User className="h-16 w-16 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">{session.candidateName}</h3>
              <p className="text-gray-300">{session.mode === "voice" ? "Voice Interview" : "Chat Interview"}</p>
            </div>
          </div>
        )}

        {/* Recording Indicator */}
        {isRecording && (
          <div className="absolute top-4 left-4">
            <div className="flex items-center space-x-2 bg-red-600 text-white px-3 py-1 rounded-full">
              <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
              <span className="text-sm font-medium">Recording</span>
            </div>
          </div>
        )}

        {/* Audio Level Indicator */}
        {isRecording && (
          <div className="absolute bottom-20 left-1/2 transform -translate-x-1/2">
            <div className="flex items-center space-x-1">
              {[1, 2, 3, 4, 5].map((i) => (
                <div
                  key={i}
                  className="w-1 bg-green-500 rounded-full animate-pulse"
                  style={{
                    height: `${Math.random() * 20 + 10}px`,
                    animationDelay: `${i * 0.1}s`,
                  }}
                />
              ))}
            </div>
          </div>
        )}

        {/* Media Controls */}
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
          <div className="flex items-center space-x-3">
            {session.mode === "video" && (
              <Button
                variant={isVideoEnabled ? "default" : "secondary"}
                size="sm"
                onClick={onToggleVideo}
                className="rounded-full w-12 h-12"
              >
                {isVideoEnabled ? <Video className="h-5 w-5" /> : <VideoOff className="h-5 w-5" />}
              </Button>
            )}

            {(session.mode === "voice" || session.mode === "video") && (
              <Button
                variant={isRecording ? "destructive" : "default"}
                size="sm"
                onClick={onToggleRecording}
                className="rounded-full w-12 h-12"
              >
                {isRecording ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
              </Button>
            )}

            <Button
              variant={isAudioEnabled ? "default" : "secondary"}
              size="sm"
              onClick={onToggleAudio}
              className="rounded-full w-12 h-12"
            >
              {isAudioEnabled ? <Volume2 className="h-5 w-5" /> : <VolumeX className="h-5 w-5" />}
            </Button>
          </div>
        </div>
      </div>

      {/* Transcript Area */}
      {transcript && (
        <div className="p-4 border-t bg-white">
          <div className="bg-blue-50 p-3 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <Mic className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-900">Live Transcript</span>
            </div>
            <p className="text-sm text-blue-800">{transcript}</p>
          </div>
        </div>
      )}

      {/* Interview Tips */}
      <div className="p-4 border-t bg-gray-50">
        <h4 className="font-medium text-sm mb-2">Interview Tips</h4>
        <ul className="text-xs text-gray-600 space-y-1">
          <li>• Speak clearly and at a moderate pace</li>
          <li>• Provide specific examples in your answers</li>
          <li>• Take your time to think before responding</li>
          <li>• Ask questions if you need clarification</li>
        </ul>
      </div>
    </div>
  )
}
