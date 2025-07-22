"use client"

import React, { createContext, useContext, useState } from 'react'

interface AIContextType {
  isProcessing: boolean
  processResume: (file: File) => Promise<any>
  startInterview: (candidateId: string, type: string) => Promise<any>
  sendMessage: (sessionId: string, message: string) => Promise<any>
}

const AIContext = createContext<AIContextType | undefined>(undefined)

export function AIProvider({ children }: { children: React.ReactNode }) {
  const [isProcessing, setIsProcessing] = useState(false)

  const processResume = async (file: File) => {
    setIsProcessing(true)
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('/api/ai/resume/analyze', {
        method: 'POST',
        body: formData
      })

      return await response.json()
    } finally {
      setIsProcessing(false)
    }
  }

  const startInterview = async (candidateId: string, type: string) => {
    setIsProcessing(true)
    try {
      const response = await fetch('/api/interviews/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ candidate_id: candidateId, interview_type: type })
      })

      return await response.json()
    } finally {
      setIsProcessing(false)
    }
  }

  const sendMessage = async (sessionId: string, message: string) => {
    const response = await fetch(`/api/interviews/${sessionId}/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: message, type: 'text' })
    })

    return await response.json()
  }

  return (
    <AIContext.Provider value={{ 
      isProcessing, 
      processResume, 
      startInterview, 
      sendMessage 
    }}>
      {children}
    </AIContext.Provider>
  )
}

export function useAI() {
  const context = useContext(AIContext)
  if (context === undefined) {
    throw new Error('useAI must be used within an AIProvider')
  }
  return context
}