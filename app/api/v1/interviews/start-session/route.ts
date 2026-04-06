import { NextRequest, NextResponse } from 'next/server';

/**
 * POST /api/v1/interviews/start-session
 * Start a new interview session
 */
export async function POST(request: NextRequest) {
  try {
    const {
      candidateId,
      candidateName,
      jobId,
      jobTitle,
      interviewType = 'screening'
    } = await request.json();

    if (!candidateId || !jobId || !interviewType) {
      return NextResponse.json(
        {
          success: false,
          error: 'Missing required interview parameters',
          code: 'INVALID_REQUEST'
        },
        { status: 400 }
      );
    }

    // Call Python backend to start interview
    const response = await fetch(
      `${process.env.PYTHON_API_URL || 'http://localhost:8000'}/api/v1/interviews/start-session`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.API_SECRET_KEY || ''}`
        },
        body: JSON.stringify({
          candidate_id: candidateId,
          candidate_name: candidateName,
          job_id: jobId,
          job_title: jobTitle,
          interview_type: interviewType
        })
      }
    );

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const session = await response.json();

    return NextResponse.json({
      success: true,
      session,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('[Interview Start Error]', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to start interview',
        code: 'INTERVIEW_ERROR'
      },
      { status: 500 }
    );
  }
}
