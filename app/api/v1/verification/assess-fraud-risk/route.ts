import { NextRequest, NextResponse } from 'next/server';

/**
 * POST /api/v1/verification/assess-fraud-risk
 * Assess fraud risk for a candidate
 */
export async function POST(request: NextRequest) {
  try {
    const { candidateData, resumeData } = await request.json();

    if (!candidateData || !resumeData) {
      return NextResponse.json(
        {
          success: false,
          error: 'Candidate and resume data required',
          code: 'INVALID_REQUEST'
        },
        { status: 400 }
      );
    }

    // Call Python backend for fraud assessment
    const response = await fetch(
      `${process.env.PYTHON_API_URL || 'http://localhost:8000'}/api/v1/verification/assess-fraud-risk`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.API_SECRET_KEY || ''}`
        },
        body: JSON.stringify({
          candidate_data: candidateData,
          resume_data: resumeData
        })
      }
    );

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const assessment = await response.json();

    return NextResponse.json({
      success: true,
      assessment,
      requiresReview: assessment.requires_manual_review,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('[Fraud Risk Assessment Error]', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Assessment failed',
        code: 'ASSESSMENT_ERROR'
      },
      { status: 500 }
    );
  }
}
