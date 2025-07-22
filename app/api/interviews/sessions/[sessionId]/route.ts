import { type NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest, { params }: { params: { sessionId: string } }) {
  try {
    const sessionId = params.sessionId

    // Mock session data - in production, fetch from database
    const mockSession = {
      id: sessionId,
      candidateName: "John Doe",
      candidateEmail: "john.doe@example.com",
      position: "Senior Software Engineer",
      type: "technical",
      mode: "video",
      status: "active",
      startTime: new Date().toISOString(),
      duration: 1245, // seconds
      currentScore: 78.5,
      questionsAnswered: 3,
      totalQuestions: 8,
      currentQuestion:
        "Tell me about a challenging project you've worked on recently and how you overcame the obstacles.",
      aiAnalysis: {
        communication: 82.3,
        technical: 75.8,
        cultural_fit: 79.2,
        overall: 78.5,
      },
    }

    return NextResponse.json(mockSession)
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch session" }, { status: 500 })
  }
}
