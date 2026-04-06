import { NextRequest, NextResponse } from "next/server"
import { getServerSession } from "next-auth/next"
import { authOptions } from "@/lib/auth"
import { prisma } from "@/lib/db"

/**
 * Screen a candidate against a job using AI agent
 * POST /api/v1/recruitment/screen-candidate
 */
export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user || (session.user.role !== "ADMIN" && session.user.role !== "HR")) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const body = await request.json()
    const { candidateId, jobId } = body

    if (!candidateId || !jobId) {
      return NextResponse.json(
        { error: "candidateId and jobId are required" },
        { status: 400 }
      )
    }

    // Fetch candidate and job from database
    const candidate = await prisma.candidate.findUnique({
      where: { id: candidateId },
      include: { resume: true }
    })

    const job = await prisma.job.findUnique({
      where: { id: jobId }
    })

    if (!candidate || !job) {
      return NextResponse.json(
        { error: "Candidate or job not found" },
        { status: 404 }
      )
    }

    // Call Python backend agent for screening
    const agentResponse = await fetch(
      `${process.env.FASTAPI_BASE || "http://localhost:8000"}/api/v1/agents/recruitment/screen-candidate`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${session.user.id}`
        },
        body: JSON.stringify({
          candidate: {
            id: candidate.id,
            name: candidate.name,
            email: candidate.email,
            experience: candidate.resume?.content || "",
            skills: candidate.resume?.analysis?.skills || [],
          },
          job: {
            id: job.id,
            title: job.title,
            description: job.description,
            requirements: job.description,
          }
        })
      }
    )

    if (!agentResponse.ok) {
      throw new Error("Agent screening failed")
    }

    const agentDecision = await agentResponse.json()

    // Update candidate score and status
    const screening_score = agentDecision.confidence * 100
    
    await prisma.candidate.update({
      where: { id: candidateId },
      data: {
        score: screening_score,
        status: agentDecision.decision === "proceed_to_interview" ? "SCREENING" : "REJECTED"
      }
    })

    return NextResponse.json({
      success: true,
      decision: agentDecision,
      screening_score,
      recommendation: agentDecision.decision,
      next_steps: agentDecision.next_steps
    })

  } catch (error) {
    console.error("Screening error:", error)
    return NextResponse.json(
      { error: "Failed to screen candidate" },
      { status: 500 }
    )
  }
}
