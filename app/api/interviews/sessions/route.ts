import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { getServerSession } from "next-auth/next"
import { authOptions } from "@/lib/auth"

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const sessions = await prisma.interviewSession.findMany({
      include: {
        candidate: true,
        conductor: {
          select: { id: true, name: true, email: true }
        },
        messages: {
          orderBy: { createdAt: "asc" }
        }
      },
      orderBy: { createdAt: "desc" }
    })

    return NextResponse.json(sessions)
  } catch (error) {
    console.error("Failed to fetch sessions:", error)
    return NextResponse.json({ error: "Failed to fetch sessions" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const body = await request.json()
    const { candidateId, jobId, type } = body

    if (!candidateId || !type) {
      return NextResponse.json(
        { error: "candidateId and type are required" },
        { status: 400 }
      )
    }

    const newSession = await prisma.interviewSession.create({
      data: {
        candidateId,
        jobId,
        type,
        conductorId: session.user.id,
        status: "SCHEDULED"
      },
      include: {
        candidate: true,
        conductor: {
          select: { id: true, name: true, email: true }
        }
      }
    })

    return NextResponse.json(newSession, { status: 201 })
  } catch (error) {
    console.error("Failed to create session:", error)
    return NextResponse.json({ error: "Failed to create session" }, { status: 500 })
  }
}
