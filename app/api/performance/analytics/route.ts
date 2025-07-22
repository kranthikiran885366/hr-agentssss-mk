import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { prisma } from '@/lib/db';

// Helper function to calculate date ranges
function getDateRange(days: number) {
  const end = new Date();
  const start = new Date();
  start.setDate(start.getDate() - days);
  return { start, end };
}

// Helper function to calculate average rating
function calculateAverageRating(reviews: any[]) {
  if (!reviews.length) return 0;
  const total = reviews.reduce((sum, review) => sum + (review.overallRating || 0), 0);
  return Math.round((total / reviews.length) * 10) / 10;
}

// Helper function to group data by time period
function groupByTimePeriod(data: any[], period: 'day' | 'week' | 'month' | 'year') {
  const formatOptions: Record<string, Intl.DateTimeFormatOptions> = {
    day: { month: 'short', day: 'numeric' },
    week: { year: 'numeric', week: 'numeric' },
    month: { year: 'numeric', month: 'short' },
    year: { year: 'numeric' },
  };

  const format = new Intl.DateTimeFormat('en-US', formatOptions[period]);
  
  return data.reduce((acc, item) => {
    const date = new Date(item.date || item.createdAt);
    const key = format.format(date);
    if (!acc[key]) {
      acc[key] = [];
    }
    acc[key].push(item);
    return acc;
  }, {} as Record<string, any[]>);
}

export async function GET(req: Request) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const { searchParams } = new URL(req.url)
    const employeeId = searchParams.get('employeeId')
    const department = searchParams.get('department')
    const startDate = searchParams.get('startDate')
    const endDate = searchParams.get('endDate')

    // Build the where clause based on user role and filters
    const where: any = {}
    
    // Regular users can only see their own analytics
    if (session.user.role === 'USER') {
      where.employeeId = session.user.id
    } 
    // Managers can see their team's analytics
    else if (session.user.role === 'MANAGER' && !employeeId) {
      const teamMembers = await prisma.teamMember.findMany({
        where: { managerId: session.user.id },
        select: { userId: true }
      })
      where.employeeId = { in: teamMembers.map(tm => tm.userId) }
    }
    
    // Apply filters
    if (employeeId) where.employeeId = employeeId
    if (startDate) where.createdAt = { gte: new Date(startDate) }
    if (endDate) {
      where.createdAt = {
        ...(where.createdAt as object || {}),
        lte: new Date(endDate)
      }
    }

    // Get department filter
    let departmentFilter = {}
    if (department) {
      departmentFilter = {
        employee: {
          department: department
        }
      }
    }

    // Get performance metrics
    const [
      totalGoals,
      completedGoals,
      inProgressGoals,
      atRiskGoals,
      averageGoalCompletion,
      reviewsByStatus,
      averageRatings,
      performanceTrend,
      topPerformers,
      departmentStats
    ] = await Promise.all([
      // Total goals
      prisma.performanceGoal.count({ 
        where: { ...where, ...departmentFilter } 
      }),
      
      // Completed goals
      prisma.performanceGoal.count({ 
        where: { 
          ...where, 
          ...departmentFilter,
          status: 'COMPLETED' 
        } 
      }),
      
      // In progress goals
      prisma.performanceGoal.count({ 
        where: { 
          ...where, 
          ...departmentFilter,
          status: 'IN_PROGRESS' 
        } 
      }),
      
      // At risk goals
      prisma.performanceGoal.count({ 
        where: { 
          ...where, 
          ...departmentFilter,
          status: 'AT_RISK' 
        } 
      }),
      
      // Average goal completion
      prisma.performanceGoal.aggregate({
        where: { 
          ...where, 
          ...departmentFilter,
          NOT: { status: 'NOT_STARTED' }
        },
        _avg: { progress: true }
      }),
      
      // Reviews by status
      prisma.performanceReview.groupBy({
        by: ['status'],
        _count: { _all: true },
        where: { 
          ...where, 
          ...departmentFilter 
        }
      }),
      
      // Average ratings by category
      prisma.performanceReviewMetric.groupBy({
        by: ['name'],
        _avg: { rating: true },
        where: {
          review: {
            ...where,
            ...departmentFilter
          }
        }
      }),
      
      // Performance trend over time
      prisma.$queryRaw`
        SELECT 
          DATE_TRUNC('month', "createdAt") as month,
          AVG("overallRating") as average_rating,
          COUNT(*) as review_count
        FROM "PerformanceReview"
        WHERE "employeeId" = ANY(${where.employeeId ? [where.employeeId] : []}::text[])
        GROUP BY DATE_TRUNC('month', "createdAt")
        ORDER BY month DESC
        LIMIT 12
      `,
      
      // Top performers
      prisma.$queryRaw`
        SELECT 
          u.id,
          u.name,
          u.email,
          AVG(pr."overallRating") as average_rating,
          COUNT(pr.id) as review_count
        FROM "PerformanceReview" pr
        JOIN "User" u ON pr."employeeId" = u.id
        WHERE pr."overallRating" IS NOT NULL
        GROUP BY u.id, u.name, u.email
        ORDER BY average_rating DESC
        LIMIT 5
      `,
      
      // Department statistics
      prisma.$queryRaw`
        SELECT 
          u.department,
          AVG(pr."overallRating") as average_rating,
          COUNT(pr.id) as review_count,
          COUNT(DISTINCT pr."employeeId") as employee_count
        FROM "PerformanceReview" pr
        JOIN "User" u ON pr."employeeId" = u.id
        WHERE pr."overallRating" IS NOT NULL
        GROUP BY u.department
        ORDER BY average_rating DESC
      `
    ])

    // Format the response
    const analytics = {
      summary: {
        totalGoals,
        completedGoals,
        inProgressGoals,
        atRiskGoals,
        completionRate: totalGoals > 0 ? (completedGoals / totalGoals) * 100 : 0,
        averageGoalCompletion: averageGoalCompletion._avg.progress || 0,
      },
      reviews: {
        byStatus: reviewsByStatus.reduce((acc, { status, _count }) => ({
          ...acc,
          [status.toLowerCase()]: _count._all
        }), {}),
        averageRatings: averageRatings.reduce((acc, { name, _avg }) => ({
          ...acc,
          [name]: _avg.rating
        }), {})
      },
      trends: {
        performance: performanceTrend.map((row: any) => ({
          month: row.month.toISOString().split('T')[0],
          averageRating: parseFloat(row.average_rating),
      }
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error('Error fetching performance analytics:', error);
    return NextResponse.json(
      { 
        error: error instanceof Error 
          ? error.message 
          : 'Failed to fetch performance analytics' 
      },
      { status: 500 }
    );
  }
}
