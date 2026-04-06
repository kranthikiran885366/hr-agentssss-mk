import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { getServerSession } from "next-auth/next"
import { authOptions } from "@/lib/auth"

export async function GET(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const interviewSession = await prisma.interviewSession.findUnique({
      where: { id: params.sessionId },
      include: {
        candidate: true,
        conductor: {
          select: { id: true, name: true, email: true }
        },
        messages: {
          orderBy: { createdAt: "asc" }
        }
      }
    })

    if (!interviewSession) {
      return NextResponse.json(
        { error: "Interview session not found" },
        { status: 404 }
      )
    }

    return NextResponse.json({
      ...interviewSession,
      messageCount: interviewSession.messages.length,
      duration: interviewSession.endTime && interviewSession.startTime
        ? Math.round((new Date(interviewSession.endTime).getTime() - new Date(interviewSession.startTime).getTime()) / 1000)
        : 0
    })
  } catch (error) {
    console.error("Failed to fetch session:", error)
    return NextResponse.json(
      { error: "Failed to fetch session" },
      { status: 500 }
    )
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const body = await request.json()
    const { status, score, feedback, endTime } = body

    const updated = await prisma.interviewSession.update({
      where: { id: params.sessionId },
      data: {
        status,
        score,
        feedback,
        endTime
      },
      include: { candidate: true, messages: true }
    })

    return NextResponse.json(updated)
  } catch (error) {
    console.error("Failed to update session:", error)
    return NextResponse.json(
      { error: "Failed to update session" },
      { status: 500 }
    )
  }
}
