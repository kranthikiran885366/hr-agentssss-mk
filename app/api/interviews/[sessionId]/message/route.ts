import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { getServerSession } from "next-auth/next"
import { authOptions } from "@/lib/auth"

export async function POST(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const body = await request.json()
    const { content, role } = body

    if (!content) {
      return NextResponse.json(
        { error: "content is required" },
        { status: 400 }
      )
    }

    // Verify session exists and update status if needed
    const interviewSession = await prisma.interviewSession.findUnique({
      where: { id: params.sessionId },
      include: { candidate: true, messages: true }
    })

    if (!interviewSession) {
      return NextResponse.json({ error: "Session not found" }, { status: 404 })
    }

    // Save user message
    const userMessage = await prisma.interviewMessage.create({
      data: {
        sessionId: params.sessionId,
        content,
        role: role || "candidate"
      }
    })

    // Generate AI follow-up
    const aiResponses = [
      "Thank you for that response. Can you provide a specific example?",
      "That's interesting. How did you handle challenges in this situation?",
      "I appreciate the detail. What would you do differently next time?",
      "Excellent point. Tell me more about your approach.",
      "That demonstrates great skills. How did your team collaborate?",
    ]

    const aiContent = aiResponses[Math.floor(Math.random() * aiResponses.length)]

    const aiMessage = await prisma.interviewMessage.create({
      data: {
        sessionId: params.sessionId,
        content: aiContent,
        role: "interviewer"
      }
    })

    // Calculate simple score
    const messageScore = 70 + Math.random() * 20

    // Update session with new score
    const updatedSession = await prisma.interviewSession.update({
      where: { id: params.sessionId },
      data: {
        score: Math.min(100, messageScore),
        status: "IN_PROGRESS"
      },
      include: { candidate: true, messages: true }
    })

    return NextResponse.json({
      success: true,
      userMessage,
      aiMessage,
      sessionScore: updatedSession.score,
      totalMessages: updatedSession.messages.length
    })
  } catch (error) {
    console.error("Failed to process interview message:", error)
    return NextResponse.json(
      { error: "Failed to process message" },
      { status: 500 }
    )
  }
}
