import { type NextRequest, NextResponse } from "next/server"
import { TalentAcquisitionAgent } from "@/backend/agents/talent_acquisition_agent"

const agent = new TalentAcquisitionAgent()

export async function GET(request: NextRequest) {
  try {
    const url = new URL(request.url)
    if (url.searchParams.get('pending') === 'true') {
      const pendingJobs = await agent.list_pending_requisitions()
      return NextResponse.json(pendingJobs)
    }
    const jobs = await agent.list_jobs() // Implement this in the agent if missing
    return NextResponse.json(jobs)
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch jobs" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const jobData = await request.json()
    const newJob = await agent.submit_job_requisition(jobData)
    return NextResponse.json(newJob, { status: 201 })
  } catch (error) {
    return NextResponse.json({ error: "Failed to create job" }, { status: 500 })
  }
}

export async function PUT(request: NextRequest) {
  try {
    const { jobId, approverId, action, comment } = await request.json()
    if (action === 'approve') {
      const result = await agent.approve_requisition(jobId, approverId, comment)
      return NextResponse.json({ success: result, status: 'approved' })
    } else if (action === 'reject') {
      const result = await agent.reject_requisition(jobId, approverId, comment)
      return NextResponse.json({ success: result, status: 'rejected' })
    }
    return NextResponse.json({ error: 'Invalid action' }, { status: 400 })
  } catch (error) {
    return NextResponse.json({ error: "Failed to update requisition" }, { status: 500 })
  }
}
