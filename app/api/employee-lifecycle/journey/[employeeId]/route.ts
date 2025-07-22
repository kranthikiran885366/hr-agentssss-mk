import { type NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest, { params }: { params: { employeeId: string } }) {
  try {
    const employeeId = params.employeeId

    // Mock employee journey data
    const journeyData = {
      employee_id: employeeId,
      tracked_at: new Date().toISOString(),
      current_stage: "active_employment",
      stage_history: [
        {
          stage: "pre_hire",
          start_date: "2023-01-01",
          end_date: "2023-01-15",
          duration_days: 14,
          key_activities_completed: ["background_check", "reference_verification", "offer_negotiation"],
        },
        {
          stage: "onboarding",
          start_date: "2023-01-15",
          end_date: "2023-04-15",
          duration_days: 90,
          key_activities_completed: ["orientation", "documentation", "training", "system_access"],
        },
        {
          stage: "probation",
          start_date: "2023-04-15",
          end_date: "2023-07-15",
          duration_days: 90,
          key_activities_completed: ["performance_monitoring", "feedback_sessions", "skill_assessment"],
        },
        {
          stage: "active_employment",
          start_date: "2023-07-15",
          end_date: null,
          duration_days: 190,
          key_activities_completed: ["performance_reviews", "career_development", "training"],
        },
      ],
      milestones: [
        {
          type: "hire_date",
          date: "2023-01-15",
          description: "Employee started at the company",
        },
        {
          type: "probation_completion",
          date: "2023-07-15",
          description: "Successfully completed probation period",
        },
        {
          type: "first_performance_review",
          date: "2023-10-15",
          description: "Completed first annual performance review with rating: Exceeds Expectations",
        },
      ],
      career_progression: {
        current_track: "individual_contributor",
        current_level: "mid",
        next_level: "senior",
        progression_readiness: 75.0,
        time_in_current_level: 190,
        skills_for_next_level: ["System Design", "Mentoring", "Technical Leadership"],
        estimated_time_to_promotion: 180,
      },
      performance_trends: {
        overall_trend: "improving",
        current_rating: 4.2,
        previous_rating: 3.8,
        improvement_areas: ["Technical Skills", "Project Management"],
        strengths: ["Communication", "Teamwork", "Problem Solving"],
      },
      engagement_metrics: {
        overall_score: 78,
        satisfaction_score: 82,
        commitment_score: 75,
        advocacy_score: 76,
        last_survey_date: "2024-01-01",
      },
      risk_factors: [
        {
          type: "career_stagnation",
          severity: "low",
          description: "Employee has been in current role for 6+ months without clear progression path",
          impact: "retention_risk",
        },
      ],
      recommendations: [
        {
          type: "career_development",
          priority: "high",
          description: "Create clear progression plan to senior level",
          actions: ["Define skill development goals", "Assign mentor", "Provide leadership opportunities"],
        },
        {
          type: "engagement",
          priority: "medium",
          description: "Increase engagement through challenging projects",
          actions: ["Assign to high-visibility project", "Provide cross-functional exposure"],
        },
      ],
      predicted_outcomes: {
        retention_probability: 85,
        promotion_probability: 70,
        performance_trajectory: "positive",
        engagement_forecast: "stable",
      },
    }

    return NextResponse.json(journeyData)
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch employee journey" }, { status: 500 })
  }
}
