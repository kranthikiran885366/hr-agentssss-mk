import { type NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest) {
  try {
    // Mock interview statistics
    const stats = {
      totalInterviews: 247,
      activeInterviews: 2,
      completedToday: 8,
      averageScore: 76.3,
      averageDuration: 1850, // seconds
      conversionRate: 68.5, // percentage
      byType: {
        technical: 89,
        behavioral: 76,
        screening: 45,
        comprehensive: 37,
      },
      byMode: {
        video: 134,
        voice: 78,
        chat: 35,
      },
    }

    return NextResponse.json(stats)
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch stats" }, { status: 500 })
  }
}
