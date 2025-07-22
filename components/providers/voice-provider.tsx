"use client"

import React, { createContext, useContext, useState, useRef } from 'react'

interface VoiceContextType {
  isRecording: boolean
  isPlaying: boolean
  startRecording: () => Promise<void>
  stopRecording: () => Promise<Blob | null>
  playAudio: (audioUrl: string) => Promise<void>
  synthesizeSpeech: (text: string) => Promise<string>
}

const VoiceContext = createContext<VoiceContextType | undefined>(undefined)

export function VoiceProvider({ children }: { children: React.ReactNode }) {
  const [isRecording, setIsRecording] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorderRef.current = new MediaRecorder(stream)
      audioChunksRef.current = []

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorderRef.current.start()
      setIsRecording(true)
    } catch (error) {
      console.error('Error starting recording:', error)
    }
  }

  const stopRecording = async (): Promise<Blob | null> => {
    return new Promise((resolve) => {
      if (mediaRecorderRef.current && isRecording) {
        mediaRecorderRef.current.onstop = () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
          resolve(audioBlob)
        }

        mediaRecorderRef.current.stop()
        setIsRecording(false)

        // Stop all tracks
        mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop())
      } else {
        resolve(null)
      }
    })
  }

  const playAudio = async (audioUrl: string) => {
    setIsPlaying(true)
    const audio = new Audio(audioUrl)

    return new Promise<void>((resolve) => {
      audio.onended = () => {
        setIsPlaying(false)
        resolve()
      }
      audio.onerror = () => {
        setIsPlaying(false)
        resolve()
      }
      audio.play()
    })
  }

  const synthesizeSpeech = async (text: string): Promise<string> => {
    const response = await fetch('/api/voice/synthesize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, voice: 'default', language: 'en' })
    })

    const data = await response.json()
    return data.audio_url
  }

  return (
    <VoiceContext.Provider value={{ 
      isRecording, 
      isPlaying, 
      startRecording, 
      stopRecording, 
      playAudio, 
      synthesizeSpeech 
    }}>
      {children}
    </VoiceContext.Provider>
  )
}

export function useVoice() {
  const context = useContext(VoiceContext)
  if (context === undefined) {
    throw new Error('useVoice must be used within a VoiceProvider')
  }
  return context
}