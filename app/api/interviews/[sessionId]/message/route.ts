import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest, { params }: { params: { sessionId: string } }) {
  try {
    const sessionId = params.sessionId
    const { message, type } = await request.json()

    // Simulate AI processing delay
    await new Promise((resolve) => setTimeout(resolve, 1500))

    // Mock AI response generation
    const responses = [
      "That's a great example! Can you tell me more about the specific technical challenges you faced?",
      "Interesting approach. How did you measure the success of your solution?",
      "I appreciate the detail in your response. What would you do differently if you encountered a similar situation again?",
      "Thank you for sharing that. Let's move on to the next question.",
      "That demonstrates good problem-solving skills. How did your team react to your solution?",
    ]

    const aiMessage = responses[Math.floor(Math.random() * responses.length)]

    // Mock analysis
    const analysis = {
      sentiment: { label: "POSITIVE", score: 0.85 },
      technical_content: { overall_technical_score: Math.random() * 30 + 70 },
      communication_quality: { overall_communication_score: Math.random() * 25 + 75 },
      relevance: Math.random() * 20 + 80,
      completeness: Math.random() * 25 + 75,
      confidence_level: Math.random() * 30 + 70,
    }

    // Mock session update
    const sessionUpdate = {
      id: sessionId,
      candidateName: "John Doe",
      candidateEmail: "john.doe@example.com",
      position: "Senior Software Engineer",
      type: "technical",
      mode: "video",
      status: "active",
      startTime: new Date().toISOString(),
      duration: 1245 + 60, // Add 60 seconds
      currentScore: 78.5 + (Math.random() * 4 - 2), // Slight variation
      questionsAnswered: 4,
      totalQuestions: 8,
      currentQuestion: "How do you approach debugging complex issues in production environments?",
      aiAnalysis: {
        communication: 82.3 + (Math.random() * 4 - 2),
        technical: 75.8 + (Math.random() * 4 - 2),
        cultural_fit: 79.2 + (Math.random() * 4 - 2),
        overall: 78.5 + (Math.random() * 4 - 2),
      },
    }

    return NextResponse.json({
      message: aiMessage,
      analysis,
      sessionUpdate,
    })
  } catch (error) {
    return NextResponse.json({ error: "Failed to process message" }, { status: 500 })
  }
}
