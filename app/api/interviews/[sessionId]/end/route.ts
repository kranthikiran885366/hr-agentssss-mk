import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest, { params }: { params: { sessionId: string } }) {
  try {
    const sessionId = params.sessionId

    // In production, update session status and generate final report
    console.log(`Ending interview session: ${sessionId}`)

    // Mock final evaluation
    const finalEvaluation = {
      sessionId,
      overallScore: 78.5,
      recommendation: "Hire",
      strengths: [
        "Strong technical problem-solving skills",
        "Clear communication style",
        "Good cultural fit indicators",
      ],
      areasForImprovement: ["Could provide more specific examples", "Expand on leadership experience"],
      detailedReport: "Candidate demonstrated solid technical competency...",
    }

    return NextResponse.json({
      success: true,
      message: "Interview ended successfully",
      evaluation: finalEvaluation,
    })
  } catch (error) {
    return NextResponse.json({ error: "Failed to end interview" }, { status: 500 })
  }
}
