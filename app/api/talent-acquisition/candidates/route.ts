import { NextRequest, NextResponse } from "next/server"

const FASTAPI_BASE = process.env.FASTAPI_BASE || "http://localhost:8000"

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const jobId = searchParams.get("jobId")
    const stage = searchParams.get("stage")

    if (searchParams.get("pipeline")) {
      const pipeline = await fetch(`${FASTAPI_BASE}/api/talent-acquisition/manage-hiring-pipeline?jobId=${jobId}`)
      return NextResponse.json(await pipeline.json())
    }
    if (searchParams.get("diversityReport")) {
      const report = await fetch(`${FASTAPI_BASE}/api/talent-acquisition/generate-diversity-report?jobId=${jobId}&time_period=${searchParams.get("time_period") || "30d"}`)
      return NextResponse.json(await report.json())
    }
    // Default: list candidates for jobId and/or stage
    const candidates = await fetch(`${FASTAPI_BASE}/api/talent-acquisition/list-candidates?jobId=${jobId}&stage=${stage}`)
    return NextResponse.json(await candidates.json())
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch candidates" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const candidateData = await request.json()
    let res, data
    if (candidateData.action === "source") {
      res = await fetch(`${FASTAPI_BASE}/api/talent-acquisition/source`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(candidateData)
      })
      data = await res.json()
      return NextResponse.json(data, { status: res.status })
    } else if (candidateData.action === "screen") {
      res = await fetch(`${FASTAPI_BASE}/api/talent-acquisition/screen`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(candidateData)
      })
      data = await res.json()
      return NextResponse.json(data, { status: res.status })
    } else if (["advance", "reject", "send_email"].includes(candidateData.action)) {
      res = await fetch(`${FASTAPI_BASE}/api/talent-acquisition/action`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(candidateData)
      })
      data = await res.json()
      return NextResponse.json(data, { status: res.status })
    } else if (candidateData.action === "bulk" || candidateData.candidateIds) {
      res = await fetch(`${FASTAPI_BASE}/api/talent-acquisition/bulk`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(candidateData)
      })
      data = await res.json()
      return NextResponse.json(data, { status: res.status })
    } else {
      // Default: create candidate
      res = await fetch(`${FASTAPI_BASE}/api/talent-acquisition/create-candidate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(candidateData)
      })
      data = await res.json()
      return NextResponse.json(data, { status: res.status })
    }
  } catch (error) {
    return NextResponse.json({ error: "Failed to process candidate action" }, { status: 500 })
  }
}
