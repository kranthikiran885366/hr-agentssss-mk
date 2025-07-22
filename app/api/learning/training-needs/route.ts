import { NextResponse } from "next/server"
import { z } from "zod"
import { prisma } from "@/lib/db"
import { getServerSession } from "next-auth"
import { authOptions } from "@/lib/auth"

// Schema for training needs analysis
const trainingNeedsSchema = z.object({
  employeeId: z.string().min(1, "Employee ID is required"),
  skills: z.array(z.object({
    skillId: z.string(),
    currentLevel: z.number().min(1).max(5),
    targetLevel: z.number().min(1).max(5),
    priority: z.enum(['LOW', 'MEDIUM', 'HIGH']).default('MEDIUM'),
  })),
  goals: z.array(z.string()).optional(),
  deadline: z.string().datetime().optional(),
})

export async function POST(req: Request) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user?.id) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    const data = await req.json()
    const validatedData = trainingNeedsSchema.parse(data)

    // Check permissions (only manager or self can create)
    if (session.user.id !== validatedData.employeeId && session.user.role !== 'ADMIN' && session.user.role !== 'MANAGER') {
      return NextResponse.json(
        { error: 'Not authorized' },
        { status: 403 }
      )
    }

    // Create training needs analysis record
    const trainingNeeds = await prisma.trainingNeedsAnalysis.create({
      data: {
        employeeId: validatedData.employeeId,
        createdById: session.user.id,
        deadline: validatedData.deadline ? new Date(validatedData.deadline) : null,
        status: 'DRAFT',
        skills: {
          create: validatedData.skills.map(skill => ({
            skillId: skill.skillId,
            currentLevel: skill.currentLevel,
            targetLevel: skill.targetLevel,
            priority: skill.priority,
          }))
        }
      },
      include: {
        skills: true,
        employee: {
          select: { name: true, email: true, id: true },
        },
      },
    })

    return NextResponse.json(trainingNeeds, { status: 201 })
  } catch (error) {
    console.error('Error creating training needs analysis:', error)
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation error', details: error.errors },
        { status: 400 }
      )
    }
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to create training needs analysis' },
      { status: 500 }
    )
  }
}

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url)
    const employeeId = searchParams.get('employeeId')
    const status = searchParams.get('status')
    
    const session = await getServerSession(authOptions)
    if (!session?.user?.id) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    // Check permissions
    let where: any = {}
    if (employeeId) {
      if (session.user.id !== employeeId && session.user.role !== 'ADMIN' && session.user.role !== 'MANAGER') {
        return NextResponse.json(
          { error: 'Not authorized to view this data' },
          { status: 403 }
        )
      }
      where.employeeId = employeeId
    } else if (session.user.role !== 'ADMIN') {
      // Managers can only see their team's data
      if (session.user.role === 'MANAGER') {
        const teamMembers = await prisma.teamMember.findMany({
          where: { managerId: session.user.id },
          select: { userId: true }
        })
        where.employeeId = {
          in: teamMembers.map(member => member.userId)
        }
      } else {
        // Regular users can only see their own data
        where.employeeId = session.user.id
      }
    }

    if (status) {
      where.status = status
    }

    const analyses = await prisma.trainingNeedsAnalysis.findMany({
      where,
      include: {
        skills: {
          include: {
            skill: true
          }
        },
        employee: {
          select: { name: true, email: true, id: true },
        },
      },
      orderBy: { createdAt: 'desc' },
    })

    return NextResponse.json(analyses)
  } catch (error) {
    console.error('Error fetching training needs analyses:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to fetch training needs analyses' },
      { status: 500 }
    )
  }
}
