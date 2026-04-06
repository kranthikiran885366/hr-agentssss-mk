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

    const { searchParams } = new URL(request.url)
    const jobId = searchParams.get("jobId")
    const status = searchParams.get("status")
    const skip = parseInt(searchParams.get("skip") || "0")
    const limit = parseInt(searchParams.get("limit") || "50")

    const where: any = {}
    if (status) where.status = status
    if (jobId) {
      where.applications = {
        some: { jobId }
      }
    }

    const candidates = await prisma.candidate.findMany({
      where,
      include: {
        resume: true,
        applications: {
          include: { job: true }
        },
        interviews: true
      },
      skip,
      take: limit,
      orderBy: { createdAt: "desc" }
    })

    const total = await prisma.candidate.count({ where })

    return NextResponse.json({
      total,
      items: candidates,
      skip,
      limit
    })
  } catch (error) {
    console.error("Failed to fetch candidates:", error)
    return NextResponse.json({ error: "Failed to fetch candidates" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const body = await request.json()
    const { action, name, email, phone, source, jobId, status, resume } = body

    if (action === "create") {
      if (!name || !email) {
        return NextResponse.json(
          { error: "name and email are required" },
          { status: 400 }
        )
      }

      const existingCandidate = await prisma.candidate.findUnique({
        where: { email }
      })

      if (existingCandidate) {
        return NextResponse.json(
          { error: "Candidate already exists" },
          { status: 400 }
        )
      }

      const newCandidate = await prisma.candidate.create({
        data: {
          name,
          email,
          phone,
          source,
          status: status || "APPLIED",
          resume: resume ? {
            create: {
              content: resume,
              score: 0
            }
          } : undefined
        },
        include: {
          resume: true,
          applications: true
        }
      })

      return NextResponse.json(newCandidate, { status: 201 })
    }

    if (action === "apply-job") {
      if (!jobId) {
        return NextResponse.json(
          { error: "jobId is required" },
          { status: 400 }
        )
      }

      const candidateId = body.candidateId
      if (!candidateId) {
        return NextResponse.json(
          { error: "candidateId is required" },
          { status: 400 }
        )
      }

      const existingApplication = await prisma.jobApplication.findUnique({
        where: {
          jobId_candidateId: {
            jobId,
            candidateId
          }
        }
      })

      if (existingApplication) {
        return NextResponse.json(
          { error: "Already applied to this job" },
          { status: 400 }
        )
      }

      const application = await prisma.jobApplication.create({
        data: {
          jobId,
          candidateId,
          status: "APPLIED"
        },
        include: {
          job: true,
          candidate: true
        }
      })

      return NextResponse.json(application, { status: 201 })
    }

    if (action === "update-status") {
      const candidateId = body.candidateId
      if (!candidateId || !status) {
        return NextResponse.json(
          { error: "candidateId and status are required" },
          { status: 400 }
        )
      }

      const updated = await prisma.candidate.update({
        where: { id: candidateId },
        data: { status },
        include: {
          resume: true,
          applications: true
        }
      })

      return NextResponse.json(updated)
    }

    return NextResponse.json(
      { error: "Unknown action" },
      { status: 400 }
    )
  } catch (error) {
    console.error("Failed to process candidate action:", error)
    return NextResponse.json({ error: "Failed to process request" }, { status: 500 })
  }
}
