import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { getServerSession } from '@/lib/auth';
import { prisma } from '@/lib/db';

// Type definitions for request/response
interface ReviewData {
  id?: string;
  employeeId: string;
  reviewerId: string;
  reviewPeriodStart: string;
  reviewPeriodEnd: string;
  status: string;
  overallRating?: number;
  strengths?: string;
  areasForImprovement?: string;
  employeeComments?: string;
  reviewerComments?: string;
  metrics?: Array<{
    name: string;
    rating: number;
    weight: number;
    comments?: string;
  }>;
}

// Helper type for API route handler
type ApiHandler = (
  req: NextRequest,
  context?: any
) => Promise<NextResponse>;

// Schema for creating/updating a review
const reviewSchema = z.object({
  employeeId: z.string().min(1, 'Employee ID is required'),
  reviewerId: z.string().min(1, 'Reviewer ID is required'),
  reviewPeriodStart: z.string().datetime(),
  reviewPeriodEnd: z.string().datetime(),
  status: z.enum(['DRAFT', 'IN_PROGRESS', 'COMPLETED', 'ARCHIVED']).default('DRAFT'),
  overallRating: z.number().min(1).max(5).optional(),
  strengths: z.string().optional(),
  areasForImprovement: z.string().optional(),
  employeeComments: z.string().optional(),
  reviewerComments: z.string().optional(),
  metrics: z.array(z.object({
    name: z.string(),
    rating: z.number().min(1).max(5),
    weight: z.number().min(0).max(100).default(100),
    comments: z.string().optional(),
  })).optional(),
});

// Schema for submitting feedback
const feedbackSchema = z.object({
  comments: z.string().min(10, 'Comments must be at least 10 characters'),
  rating: z.number().min(1).max(5).optional(),
  isSelfReview: z.boolean().default(false),
});

// Helper function to check permissions
async function checkPermissions(userId: string, employeeId?: string): Promise<boolean> {
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
    const teamMembers = await prisma.teamMember.findMany({
      where: { managerId: user.id },
      select: { userId: true },
    });
    
    if (teamMembers.some((member: { userId: string }) => member.userId === employeeId)) {
      return true;
    }
  }
  
  throw new Error('Not authorized to perform this action');
}

export async function POST(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const data = await req.json();
    const validatedData = reviewSchema.parse(data);

    // Check permissions
    await checkPermissions(session.user.id, validatedData.employeeId);

    // Check if employee exists
    const employee = await prisma.user.findUnique({
      where: { id: validatedData.employeeId },
      select: { id: true, name: true, email: true }
    });
    
    if (!employee) {
      return NextResponse.json(
        { error: 'Employee not found' },
        { status: 404 }
      );
    }

    // Check if reviewer exists
    const reviewer = await prisma.user.findUnique({
      where: { id: validatedData.reviewerId },
      select: { id: true, name: true, email: true }
    });
    
    if (!reviewer) {
      return NextResponse.json(
        { error: 'Reviewer not found' },
        { status: 404 }
      );
    }

    const review = await prisma.performanceReview.create({
      data: {
        employeeId: validatedData.employeeId,
        reviewerId: validatedData.reviewerId,
        reviewPeriodStart: new Date(validatedData.reviewPeriodStart),
        reviewPeriodEnd: new Date(validatedData.reviewPeriodEnd),
        status: validatedData.status,
        overallRating: validatedData.overallRating,
        strengths: validatedData.strengths,
        areasForImprovement: validatedData.areasForImprovement,
        employeeComments: validatedData.employeeComments,
        reviewerComments: validatedData.reviewerComments,
        metrics: {
          create: validatedData.metrics?.map(metric => ({
            name: metric.name,
            rating: metric.rating,
            weight: metric.weight,
            comments: metric.comments,
            createdById: session.user.id,
          })) || []
        },
        createdById: session.user.id,
      },
      include: {
        employee: {
          select: { name: true, email: true, id: true }
        },
        reviewer: {
          select: { name: true, email: true, id: true }
        },
        metrics: true
      }
    });

    return NextResponse.json(review, { status: 201 });
  } catch (error) {
    console.error('Error creating performance review:', error);
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation error', details: error.errors },
        { status: 400 }
      );
    }
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to create performance review' },
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
    const reviewerId = searchParams.get('reviewerId');
    const status = searchParams.get('status');
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '10');
    const includeMetrics = searchParams.get('includeMetrics') === 'true';

    // Build where clause
    const where: any = {};
    
    // Regular users can only see their own reviews
    if (session.user.role === 'USER') {
      where.OR = [
        { employeeId: session.user.id },
        { reviewerId: session.user.id }
      ];
    } 
    // Managers can see their team's reviews and reviews they're conducting
    else if (session.user.role === 'MANAGER') {
      // Get team member IDs for this manager
      const teamMembers = await prisma.teamMember.findMany({
        where: { managerId: session.user.id },
        select: { userId: true }
      });
      
      where.OR = [
        { employeeId: { in: teamMembers.map((tm: { userId: string }) => tm.userId) } },
        { reviewerId: session.user.id }
      ];
    }
    
    // Apply filters if provided
    if (employeeId) where.employeeId = employeeId;
    if (reviewerId) where.reviewerId = reviewerId;
    if (status) where.status = status;

    const [reviews, total] = await Promise.all([
      prisma.performanceReview.findMany({
        where,
        include: {
          employee: {
            select: { name: true, email: true, id: true }
          },
          reviewer: {
            select: { name: true, email: true, id: true }
          },
          metrics: includeMetrics
        },
        orderBy: { createdAt: 'desc' },
        skip: (page - 1) * limit,
        take: limit,
      }),
      prisma.performanceReview.count({ where })
    ]);

    return NextResponse.json({
      data: reviews,
      pagination: {
        total,
        page,
        limit,
        totalPages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    console.error('Error fetching performance reviews:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to fetch performance reviews' },
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
    const { id, ...updateData } = data;

    if (!id) {
      return NextResponse.json(
        { error: 'Review ID is required' },
        { status: 400 }
      );
    }

    // Get the review to check permissions
    const review = await prisma.performanceReview.findUnique({
      where: { id },
      include: {
        employee: { select: { id: true } },
        reviewer: { select: { id: true } }
      }
    });

    if (!review) {
      return NextResponse.json(
        { error: 'Review not found' },
        { status: 404 }
      );
    }

    // Check permissions - only reviewer, admin, or employee (for self-review) can update
    const isReviewer = review.reviewerId === session.user.id;
    const isEmployee = review.employeeId === session.user.id;
    const isAdmin = session.user.role === 'ADMIN';
    
    if (!isReviewer && !isEmployee && !isAdmin) {
      return NextResponse.json(
        { error: 'Not authorized to update this review' },
        { status: 403 }
      );
    }

    // Prepare update data
    const updatePayload: any = { ...updateData };
    
    // Convert date strings to Date objects if present
    if (updateData.reviewPeriodStart) {
      updatePayload.reviewPeriodStart = new Date(updateData.reviewPeriodStart);
    }
    if (updateData.reviewPeriodEnd) {
      updatePayload.reviewPeriodEnd = new Date(updateData.reviewPeriodEnd);
    }

    // Update the review
    const updatedReview = await prisma.performanceReview.update({
      where: { id },
      data: updatePayload,
      include: {
        employee: {
          select: { name: true, email: true, id: true }
        },
        reviewer: {
          select: { name: true, email: true, id: true }
        },
        metrics: true
      }
    });

    return NextResponse.json(updatedReview);
  } catch (error) {
    console.error('Error updating performance review:', error);
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation error', details: error.errors },
        { status: 400 }
      );
    }
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to update performance review' },
      { status: 500 }
    );
  }
}

// Endpoint to submit employee feedback for a review
export async function POST_FEEDBACK(req: Request) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const data = await req.json();
    const { reviewId, ...feedbackData } = feedbackSchema.parse(data);

    // Get the review to verify it exists and is in the correct status
    const review = await prisma.performanceReview.findUnique({
      where: { id: reviewId }
    });

    if (!review) {
      return NextResponse.json(
        { error: 'Review not found' },
        { status: 404 }
      );
    }

    // Check if the user is the employee in the review
    if (review.employeeId !== session.user.id) {
      return NextResponse.json(
        { error: 'You can only submit feedback for your own review' },
        { status: 403 }
      );
    }

    // Update the review with employee feedback
    const updatedReview = await prisma.performanceReview.update({
      where: { id: reviewId },
      data: {
        employeeComments: feedbackData.comments,
        status: feedbackData.isSelfReview ? 'IN_PROGRESS' : review.status,
        // If this is a self-review, mark it as completed if all required steps are done
        ...(feedbackData.isSelfReview && {
          status: 'COMPLETED',
          completedAt: new Date()
        })
      },
      include: {
        employee: {
          select: { name: true, email: true, id: true }
        },
        reviewer: {
          select: { name: true, email: true, id: true }
        }
      }
    });

    return NextResponse.json(updatedReview);
  } catch (error) {
    console.error('Error submitting feedback:', error);
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation error', details: error.errors },
        { status: 400 }
      );
    }
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to submit feedback' },
      { status: 500 }
    );
  }
}

export async function GET(req: Request) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const { searchParams } = new URL(req.url)
    const employeeId = searchParams.get('employeeId')
    const reviewerId = searchParams.get('reviewerId')
    const status = searchParams.get('status')
    const page = parseInt(searchParams.get('page') || '1')
    const limit = parseInt(searchParams.get('limit') || '10')
    const includeMetrics = searchParams.get('includeMetrics') === 'true'

    // Build the where clause based on user role and filters
    const where: any = {}
    
    // Regular users can only see their own reviews
    if (session.user.role === 'USER') {
      where.OR = [
        { employeeId: session.user.id },
        { reviewerId: session.user.id }
      ]
    } 
    // Managers can see their team's reviews and reviews they're conducting
    else if (session.user.role === 'MANAGER') {
      // Get team member IDs for this manager
      const teamMembers = await prisma.teamMember.findMany({
        where: { managerId: session.user.id },
        select: { userId: true }
      })
      
      where.OR = [
        { employeeId: { in: teamMembers.map(tm => tm.userId) } },
        { reviewerId: session.user.id }
      ]
    }
    
    // Apply filters if provided
    if (employeeId) where.employeeId = employeeId
    if (reviewerId) where.reviewerId = reviewerId
    if (status) where.status = status

    const [reviews, total] = await Promise.all([
      prisma.performanceReview.findMany({
        where,
        include: {
          employee: {
            select: { name: true, email: true, id: true }
          },
          reviewer: {
            select: { name: true, email: true, id: true }
          },
          metrics: includeMetrics
        },
        orderBy: { createdAt: 'desc' },
        skip: (page - 1) * limit,
        take: limit,
      }),
      prisma.performanceReview.count({ where })
    ])

    return NextResponse.json({
      data: reviews,
      pagination: {
        total,
        page,
        limit,
        totalPages: Math.ceil(total / limit)
      }
    })
  } catch (error) {
    console.error("Error fetching performance reviews:", error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to fetch performance reviews" },
      { status: 500 }
    )
  }
}

export async function PUT(req: Request) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const data = await req.json()
    const { id, ...updateData } = updateReviewSchema.parse(data)

    // Get the review to check permissions
    const review = await prisma.performanceReview.findUnique({
      where: { id },
      include: {
        employee: { select: { id: true } },
        reviewer: { select: { id: true } }
      }
    })

    if (!review) {
      return NextResponse.json({ error: "Review not found" }, { status: 404 })
    }

    // Check permissions - only reviewer, admin, or employee (for self-review) can update
    const isReviewer = review.reviewerId === session.user.id
    const isEmployee = review.employeeId === session.user.id
    const isAdmin = session.user.role === 'ADMIN'
    
    if (!isReviewer && !isEmployee && !isAdmin) {
      return NextResponse.json(
        { error: "Not authorized to update this review" },
        { status: 403 }
      )
    }

    // Prepare update data
    const updatePayload: any = { ...updateData }
    
    // Convert date strings to Date objects if present
    if (updateData.reviewPeriodStart) {
      updatePayload.reviewPeriodStart = new Date(updateData.reviewPeriodStart)
    }
    if (updateData.reviewPeriodEnd) {
      updatePayload.reviewPeriodEnd = new Date(updateData.reviewPeriodEnd)
    }

    // Update the review
    const updatedReview = await prisma.performanceReview.update({
      where: { id },
      data: updatePayload,
      include: {
        employee: {
          select: { name: true, email: true, id: true }
        },
        reviewer: {
          select: { name: true, email: true, id: true }
        },
        metrics: true
      }
    })

    return NextResponse.json(updatedReview)
  } catch (error) {
    console.error("Error updating performance review:", error)
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: "Validation error", details: error.errors },
        { status: 400 }
      )
    }
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to update performance review" },
      { status: 500 }
    )
  }
}

// Endpoint to submit employee feedback for a review
export async function POST_FEEDBACK(req: Request) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const data = await req.json()
    const { employeeId, reviewId, feedback, isSelfReview } = submitFeedbackSchema.parse(data)

    // Check if the user is the employee in the review
    if (session.user.id !== employeeId) {
      return NextResponse.json(
        { error: "You can only submit feedback for your own review" },
        { status: 403 }
      )
    }

    // Get the review to verify it exists and is in the correct status
    const review = await prisma.performanceReview.findUnique({
      where: { id: reviewId, employeeId }
    })

    if (!review) {
      return NextResponse.json(
        { error: "Review not found or access denied" },
        { status: 404 }
      )
    }

    // Update the review with employee feedback
    const updatedReview = await prisma.performanceReview.update({
      where: { id: reviewId },
      data: {
        employeeComments: feedback,
        status: isSelfReview ? 'IN_PROGRESS' : review.status,
        // If this is a self-review, mark it as completed if all required steps are done
        ...(isSelfReview && {
          status: 'COMPLETED',
          completedAt: new Date()
        })
      },
      include: {
        employee: {
          select: { name: true, email: true, id: true }
        },
        reviewer: {
          select: { name: true, email: true, id: true }
        }
      }
    })

    return NextResponse.json(updatedReview)
  } catch (error) {
    console.error("Error submitting feedback:", error)
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: "Validation error", details: error.errors },
        { status: 400 }
      )
    }
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to submit feedback" },
      { status: 500 }
    )
  }
}
