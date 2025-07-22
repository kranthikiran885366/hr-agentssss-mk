"use client"

import type React from "react"
import { createContext, useContext, useState } from "react"

interface AIContextType {
  isProcessing: boolean
  setIsProcessing: (processing: boolean) => void
  generateResponse: (prompt: string, context?: any) => Promise<string>
  analyzeResume: (resumeText: string) => Promise<any>
  conductInterview: (type: "voice" | "chat", context: any) => Promise<any>
}

const AIContext = createContext<AIContextType | undefined>(undefined)

export function AIProvider({ children }: { children: React.ReactNode }) {
  const [isProcessing, setIsProcessing] = useState(false)

  const generateResponse = async (prompt: string, context?: any): Promise<string> => {
    setIsProcessing(true)
    try {
      // Simulate AI processing
      await new Promise((resolve) => setTimeout(resolve, 1000 + Math.random() * 2000))

      // Mock AI responses based on prompt
      if (prompt.includes("interview")) {
        return "Thank you for that response. Can you tell me more about your experience with React and how you've used it in previous projects?"
      } else if (prompt.includes("resume")) {
        return "I've analyzed your resume. You have strong technical skills in JavaScript and React. Let's discuss your project experience."
      } else if (prompt.includes("offer")) {
        return "Based on your experience and our discussion, I'm pleased to offer you the position. The salary range we discussed is competitive for your skill level."
      } else {
        return "I understand your question. Let me provide you with the information you need. Is there anything specific you'd like to know more about?"
      }
    } finally {
      setIsProcessing(false)
    }
  }

  const analyzeResume = async (resumeText: string) => {
    setIsProcessing(true)
    try {
      await new Promise((resolve) => setTimeout(resolve, 2000))

      return {
        score: Math.floor(Math.random() * 30) + 70, // 70-100
        skills: ["JavaScript", "React", "Node.js", "Python", "AWS"],
        experience: "3-5 years",
        education: "Bachelor's in Computer Science",
        strengths: ["Strong technical skills", "Good communication", "Team player"],
        recommendations: ["Consider for technical interview", "Good cultural fit"],
      }
    } finally {
      setIsProcessing(false)
    }
  }

  const conductInterview = async (type: "voice" | "chat", context: any) => {
    setIsProcessing(true)
    try {
      await new Promise((resolve) => setTimeout(resolve, 1500))

      return {
        questions: [
          "Tell me about yourself and your background",
          "What interests you about this position?",
          "Describe a challenging project you've worked on",
          "How do you handle working in a team environment?",
          "Where do you see yourself in 5 years?",
        ],
        evaluation: {
          technical_skills: Math.floor(Math.random() * 30) + 70,
          communication: Math.floor(Math.random() * 30) + 70,
          cultural_fit: Math.floor(Math.random() * 30) + 70,
          overall_score: Math.floor(Math.random() * 30) + 70,
        },
      }
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <AIContext.Provider
      value={{
        isProcessing,
        setIsProcessing,
        generateResponse,
        analyzeResume,
        conductInterview,
      }}
    >
      {children}
    </AIContext.Provider>
  )
}

export function useAI() {
  const context = useContext(AIContext)
  if (context === undefined) {
    throw new Error("useAI must be used within an AIProvider")
  }
  return context
}
