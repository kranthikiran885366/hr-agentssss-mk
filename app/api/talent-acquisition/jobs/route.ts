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
    const status = searchParams.get("status")
    const skip = parseInt(searchParams.get("skip") || "0")
    const limit = parseInt(searchParams.get("limit") || "50")

    const where: any = {}
    if (status) where.status = status

    const jobs = await prisma.job.findMany({
      where,
      include: {
        applications: {
          include: { candidate: true }
        }
      },
      skip,
      take: limit,
      orderBy: { createdAt: "desc" }
    })

    const total = await prisma.job.count({ where })

    return NextResponse.json({
      total,
      items: jobs,
      skip,
      limit
    })
  } catch (error) {
    console.error("Failed to fetch jobs:", error)
    return NextResponse.json({ error: "Failed to fetch jobs" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user || (session.user.role !== "ADMIN" && session.user.role !== "HR")) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const body = await request.json()
    const { title, description, department, salaryMin, salaryMax, status } = body

    if (!title || !description || !department) {
      return NextResponse.json(
        { error: "title, description, and department are required" },
        { status: 400 }
      )
    }

    const newJob = await prisma.job.create({
      data: {
        title,
        description,
        department,
        salaryMin,
        salaryMax,
        status: status || "OPEN"
      }
    })

    return NextResponse.json(newJob, { status: 201 })
  } catch (error) {
    console.error("Failed to create job:", error)
    return NextResponse.json({ error: "Failed to create job" }, { status: 500 })
  }
}

export async function PUT(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user || (session.user.role !== "ADMIN" && session.user.role !== "HR")) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const body = await request.json()
    const { jobId, status } = body

    if (!jobId || !status) {
      return NextResponse.json(
        { error: "jobId and status are required" },
        { status: 400 }
      )
    }

    const updated = await prisma.job.update({
      where: { id: jobId },
      data: { status },
      include: { applications: true }
    })

    return NextResponse.json(updated)
  } catch (error) {
    console.error("Failed to update job:", error)
    return NextResponse.json({ error: "Failed to update job" }, { status: 500 })
  }
}
