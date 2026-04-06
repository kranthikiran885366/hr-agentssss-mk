import { NextRequest, NextResponse } from 'next/server';

/**
 * POST /api/v1/verification/background-check
 * Initiate a background check for a candidate
 */
export async function POST(request: NextRequest) {
  try {
    const {
      candidateId,
      candidateName,
      ssn,
      includeEducationVerification = true,
      includeEmploymentVerification = true,
      includeCriminalCheck = true,
      includeSanctionsCheck = true
    } = await request.json();

    if (!candidateId || !candidateName) {
      return NextResponse.json(
        {
          success: false,
          error: 'Candidate ID and name are required',
          code: 'INVALID_REQUEST'
        },
        { status: 400 }
      );
    }

    // Call Python backend for background check
    const response = await fetch(
      `${process.env.PYTHON_API_URL || 'http://localhost:8000'}/api/v1/verification/background-check`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.API_SECRET_KEY || ''}`
        },
        body: JSON.stringify({
          candidate_id: candidateId,
          candidate_name: candidateName,
          ssn,
          include_education: includeEducationVerification,
          include_employment: includeEmploymentVerification,
          include_criminal: includeCriminalCheck,
          include_sanctions: includeSanctionsCheck
        })
      }
    );

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const checkResult = await response.json();

    return NextResponse.json({
      success: true,
      checkResult,
      status: checkResult.check_status,
      riskLevel: checkResult.risk_level,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('[Background Check Error]', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Background check failed',
        code: 'CHECK_ERROR'
      },
      { status: 500 }
    );
  }
}
