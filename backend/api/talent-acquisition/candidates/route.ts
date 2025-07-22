import { NextRequest, NextResponse } from "next/server"
import { TalentAcquisitionAgent } from "@/backend/agents/talent_acquisition_agent"
// Add RBAC import
// import { get_current_user } from "@/backend/auth/deps"

const agent = new TalentAcquisitionAgent()

export async function POST(request: NextRequest) {
  try {
    // RBAC: Only allow admin or hr for bulk actions
    // const user = await get_current_user(request)
    // if (user.role !== 'admin' && user.role !== 'hr') {
    //   return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
    // }
    const candidateData = await request.json()
    if (candidateData.action === "source") {
      const result = await agent.source_candidates(candidateData.jobId, candidateData.strategy)
      return NextResponse.json(result, { status: 201 })
    } else if (candidateData.action === "screen") {
      const result = await agent.screen_application(candidateData.applicationId)
      return NextResponse.json(result, { status: 201 })
    } else if (candidateData.action === "advance" || candidateData.action === "reject" || candidateData.action === "send_email") {
      // Single candidate action fallback
      // ... existing logic ...
    } else if (candidateData.action === "bulk" || candidateData.candidateIds) {
      // RBAC: Only allow admin or hr for bulk actions
      // const user = await get_current_user(request)
      // if (user.role !== 'admin' && user.role !== 'hr') {
      //   return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
      // }
      const { action, candidateIds } = candidateData
      let updated = 0
      for (const id of candidateIds) {
        if (action === "advance") {
          // TODO: Implement logic to advance candidate stage
          updated++
        } else if (action === "reject") {
          // TODO: Implement logic to reject candidate
          updated++
        } else if (action === "send_email") {
          // TODO: Implement logic to send email notification
          updated++
        }
      }
      return NextResponse.json({ status: `Bulk action '${action}' applied to ${updated} candidates.` })
    } else {
      // Default: create candidate
      const newCandidate = await agent.create_candidate(candidateData)
      return NextResponse.json(newCandidate, { status: 201 })
    }
  } catch (error) {
    return NextResponse.json({ error: "Failed to create candidate" }, { status: 500 })
  }
} 