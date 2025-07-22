import { NextResponse } from "next/server"
import { z } from "zod"
import { prisma } from "@/lib/db"
import { getServerSession } from "next-auth"
import { authOptions } from "@/lib/auth"

// Schema for creating/updating a goal
const goalSchema = z.object({
  title: z.string().min(5, 'Title must be at least 5 characters'),
  description: z.string().min(10, 'Description must be at least 10 characters'),
  startDate: z.string().datetime(),
  endDate: z.string().datetime(),
  targetValue: z.number().min(0),
  status: z.enum(['NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'AT_RISK']).default('NOT_STARTED'),
  priority: z.enum(['LOW', 'MEDIUM', 'HIGH']).default('MEDIUM'),
  weight: z.number().min(1).max(100).default(100),
  progress: z.number().min(0).max(100).default(0),
  kpis: z.record(z.any()).optional(),
  employeeId: z.string().optional(), // Optional for updates
})

// Schema for goal check-in
const checkInSchema = z.object({
  goalId: z.string(),
  notes: z.string().optional(),
  progress: z.number().min(0).max(100),
  evidence: z.string().optional(),
})

// Helper function to check permissions
async function checkPermissions(userId: string, employeeId?: string) {
  if (!employeeId) return true;
  
  const user = await prisma.user.findUnique({
    where: { id: userId },
    select: { role: true, id: true },
  });

  if (!user) throw new Error('User not found');
  if (user.role === 'ADMIN') return true;
  if (user.id === employeeId) return true;
  
  // Check if manager of the employee
  if (user.role === 'MANAGER') {
    const isTeamMember = await prisma.teamMember.count({
      where: { userId: employeeId, managerId: user.id },
    }) > 0;
    if (isTeamMember) return true;
  }
  
  throw new Error('Not authorized to perform this action');
}

export async function POST(req: Request) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const data = await req.json();
    const validatedData = goalSchema.parse(data);
    
    // Set employee ID from session if not provided (for self-goals)
    const employeeId = validatedData.employeeId || session.user.id;
    
    // Check permissions
    await checkPermissions(session.user.id, employeeId);

    const goal = await prisma.performanceGoal.create({
      data: {
        ...validatedData,
        employeeId,
        startDate: new Date(validatedData.startDate),
        endDate: new Date(validatedData.endDate),
        kpis: validatedData.kpis || {},
        createdById: session.user.id,
      },
      include: {
        employee: {
          select: { name: true, email: true, id: true },
        },
      },
    });

    return NextResponse.json(goal, { status: 201 });
  } catch (error) {
    console.error('Error creating goal:', error);
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation error', details: error.errors },
        { status: 400 }
      );
    }
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to create goal' },
      { status: 500 }
    );
  }
}

export async function GET(req: Request) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const { searchParams } = new URL(req.url);
    const employeeId = searchParams.get('employeeId');
    const status = searchParams.get('status');
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '10');

    // Build where clause
    const where: any = {};
    
    // Regular users can only see their own goals
    if (session.user.role === 'USER') {
      where.employeeId = session.user.id;
    } 
    // Managers can see their team's goals
    else if (session.user.role === 'MANAGER' && !employeeId) {
      const teamMembers = await prisma.teamMember.findMany({
        where: { managerId: session.user.id },
        select: { userId: true },
      });
      where.employeeId = { in: teamMembers.map(tm => tm.userId) };
    }
    
    if (employeeId) where.employeeId = employeeId;
    if (status) where.status = status;

    const [goals, total] = await Promise.all([
      prisma.performanceGoal.findMany({
        where,
        include: {
          employee: {
            select: { name: true, email: true, id: true },
          },
        },
        orderBy: { createdAt: 'desc' },
        skip: (page - 1) * limit,
        take: limit,
      }),
      prisma.performanceGoal.count({ where }),
    ]);

    return NextResponse.json({
      data: goals,
      pagination: {
        total,
        page,
        limit,
        totalPages: Math.ceil(total / limit),
      },
    });
  } catch (error) {
    console.error('Error fetching goals:', error);
    return NextResponse.json(
      { error: 'Failed to fetch goals' },
      { status: 500 }
    );
  }
}

export async function PUT(req: Request) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const data = await req.json();
    const { goalId, ...checkInData } = checkInSchema.parse(data);

    // Get the goal to check permissions
    const goal = await prisma.performanceGoal.findUnique({
      where: { id: goalId },
      select: { employeeId: true, status: true },
    });

    if (!goal) {
      return NextResponse.json({ error: 'Goal not found' }, { status: 404 });
    }

    // Check permissions
    await checkPermissions(session.user.id, goal.employeeId);

    // Update the goal's progress
    const updatedGoal = await prisma.performanceGoal.update({
      where: { id: goalId },
      data: {
        progress: checkInData.progress,
        status: checkInData.completed ? 'COMPLETED' : 
               (checkInData.progress >= 90 ? 'COMPLETED' : 
               (checkInData.progress >= 50 ? 'IN_PROGRESS' : 'NOT_STARTED')),
        checkIns: {
          create: {
            notes: checkInData.notes,
            progress: checkInData.progress,
            createdById: session.user.id,
            evidence: checkInData.evidence,
          }
        }
      },
      include: {
        employee: {
          select: { name: true, email: true, id: true },
        },
        checkIns: {
          orderBy: { createdAt: 'desc' },
          take: 1
        }
      }
    });

    return NextResponse.json(updatedGoal);
  } catch (error) {
    console.error('Error updating goal:', error);
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation error', details: error.errors },
        { status: 400 }
      );
    }
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to update goal' },
      { status: 500 }
    );
  }
}

// Get goal details with check-ins
export async function GET_GOAL(req: Request, { params }: { params: { id: string } }) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const goal = await prisma.performanceGoal.findUnique({
      where: { id: params.id },
      include: {
        employee: {
          select: { name: true, email: true, id: true }
        },
        checkIns: {
          orderBy: { createdAt: 'desc' },
          include: {
            createdBy: {
              select: { name: true, email: true }
            }
          }
        },
        createdBy: {
          select: { name: true, email: true }
        }
      }
    })

    if (!goal) {
      return NextResponse.json({ error: "Goal not found" }, { status: 404 })
    }

    // Check permissions
    await checkPermissions(session.user.id, goal.employeeId, session.user.role)

    return NextResponse.json(goal)
  } catch (error) {
    console.error("Error fetching goal:", error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to fetch goal" },
      { status: 500 }
    )
  }
}

// Delete a goal
export async function DELETE_GOAL(req: Request, { params }: { params: { id: string } }) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const goal = await prisma.performanceGoal.findUnique({
      where: { id: params.id },
      select: { employeeId: true }
    })

    if (!goal) {
      return NextResponse.json({ error: "Goal not found" }, { status: 404 })
    }

    // Check permissions - only admins and the employee can delete
    if (session.user.role !== 'ADMIN' && session.user.id !== goal.employeeId) {
      return NextResponse.json({ error: "Not authorized" }, { status: 403 })
    }

    await prisma.performanceGoal.delete({
      where: { id: params.id }
    })

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error("Error deleting goal:", error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to delete goal" },
      { status: 500 }
    )
  }
}
