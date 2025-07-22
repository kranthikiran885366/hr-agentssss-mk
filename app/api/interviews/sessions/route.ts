import { type NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest) {
  try {
    // Mock interview sessions data
    const sessions = [
      {
        id: "session-1",
        candidateName: "John Doe",
        candidateEmail: "john.doe@example.com",
        position: "Senior Software Engineer",
        type: "technical",
        mode: "video",
        status: "active",
        startTime: new Date(Date.now() - 1245000).toISOString(),
        duration: 1245,
        currentScore: 78.5,
        questionsAnswered: 3,
        totalQuestions: 8,
        currentQuestion: "Tell me about a challenging project you've worked on recently.",
        aiAnalysis: {
          communication: 82.3,
          technical: 75.8,
          cultural_fit: 79.2,
          overall: 78.5,
        },
      },
      {
        id: "session-2",
        candidateName: "Jane Smith",
        candidateEmail: "jane.smith@example.com",
        position: "Product Manager",
        type: "behavioral",
        mode: "voice",
        status: "active",
        startTime: new Date(Date.now() - 890000).toISOString(),
        duration: 890,
        currentScore: 85.2,
        questionsAnswered: 4,
        totalQuestions: 6,
        currentQuestion: "How do you handle conflicts within your team?",
        aiAnalysis: {
          communication: 88.1,
          technical: 78.5,
          cultural_fit: 89.3,
          overall: 85.2,
        },
      },
      {
        id: "session-3",
        candidateName: "Mike Johnson",
        candidateEmail: "mike.johnson@example.com",
        position: "Data Scientist",
        type: "comprehensive",
        mode: "chat",
        status: "completed",
        startTime: new Date(Date.now() - 3600000).toISOString(),
        duration: 2850,
        currentScore: 72.8,
        questionsAnswered: 10,
        totalQuestions: 10,
        currentQuestion: "",
        aiAnalysis: {
          communication: 75.2,
          technical: 78.9,
          cultural_fit: 68.3,
          overall: 72.8,
        },
      },
    ]

    return NextResponse.json(sessions)
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch sessions" }, { status: 500 })
  }
}
