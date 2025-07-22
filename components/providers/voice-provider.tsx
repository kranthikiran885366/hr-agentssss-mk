"use client"

import type React from "react"
import { createContext, useContext, useState, useRef } from "react"

interface VoiceContextType {
  isListening: boolean
  isSpeaking: boolean
  startListening: () => void
  stopListening: () => void
  speak: (text: string) => Promise<void>
  transcript: string
  confidence: number
}

const VoiceContext = createContext<VoiceContextType | undefined>(undefined)

export function VoiceProvider({ children }: { children: React.ReactNode }) {
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [transcript, setTranscript] = useState("")
  const [confidence, setConfidence] = useState(0)

  const recognitionRef = useRef<any>(null)
  const synthRef = useRef<SpeechSynthesis | null>(null)

  const startListening = () => {
    if (typeof window !== "undefined" && "webkitSpeechRecognition" in window) {
      const recognition = new (window as any).webkitSpeechRecognition()
      recognition.continuous = true
      recognition.interimResults = true
      recognition.lang = "en-US"

      recognition.onstart = () => {
        setIsListening(true)
      }

      recognition.onresult = (event: any) => {
        let finalTranscript = ""
        let interimTranscript = ""

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          const confidence = event.results[i][0].confidence

          if (event.results[i].isFinal) {
            finalTranscript += transcript
            setConfidence(confidence || 0.9)
          } else {
            interimTranscript += transcript
          }
        }

        setTranscript(finalTranscript || interimTranscript)
      }

      recognition.onerror = (event: any) => {
        console.error("Speech recognition error:", event.error)
        setIsListening(false)
      }

      recognition.onend = () => {
        setIsListening(false)
      }

      recognition.start()
      recognitionRef.current = recognition
    } else {
      // Fallback for browsers without speech recognition
      console.warn("Speech recognition not supported")
      setIsListening(true)

      // Simulate speech recognition for demo
      setTimeout(() => {
        setTranscript("Hello, I'm interested in the software engineer position.")
        setConfidence(0.95)
        setIsListening(false)
      }, 3000)
    }
  }

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
    }
    setIsListening(false)
  }

  const speak = async (text: string): Promise<void> => {
    return new Promise((resolve) => {
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        setIsSpeaking(true)

        const utterance = new SpeechSynthesisUtterance(text)
        utterance.rate = 0.9
        utterance.pitch = 1
        utterance.volume = 0.8

        utterance.onend = () => {
          setIsSpeaking(false)
          resolve()
        }

        utterance.onerror = () => {
          setIsSpeaking(false)
          resolve()
        }

        window.speechSynthesis.speak(utterance)
      } else {
        // Fallback for browsers without speech synthesis
        console.log("Speaking:", text)
        setIsSpeaking(true)
        setTimeout(() => {
          setIsSpeaking(false)
          resolve()
        }, text.length * 50) // Simulate speaking time
      }
    })
  }

  return (
    <VoiceContext.Provider
      value={{
        isListening,
        isSpeaking,
        startListening,
        stopListening,
        speak,
        transcript,
        confidence,
      }}
    >
      {children}
    </VoiceContext.Provider>
  )
}

export function useVoice() {
  const context = useContext(VoiceContext)
  if (context === undefined) {
    throw new Error("useVoice must be used within a VoiceProvider")
  }
  return context
}
