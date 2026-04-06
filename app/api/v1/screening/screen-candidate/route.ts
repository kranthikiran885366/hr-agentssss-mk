import { NextRequest, NextResponse } from 'next/server';

/**
 * POST /api/v1/screening/screen-candidate
 * Screen a single candidate against job requirements
 */
export async function POST(request: NextRequest) {
  try {
    const { candidate, jobRequirements } = await request.json();

    if (!candidate || !jobRequirements) {
      return NextResponse.json(
        {
          success: false,
          error: 'Missing candidate or job requirements data',
          code: 'INVALID_REQUEST'
        },
        { status: 400 }
      );
    }

    // Call Python backend screening service
    const response = await fetch(
      `${process.env.PYTHON_API_URL || 'http://localhost:8000'}/api/v1/screening/screen-candidate`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.API_SECRET_KEY || ''}`
        },
        body: JSON.stringify({
          candidate,
          jobRequirements,
          detailed: true
        })
      }
    );

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const screening = await response.json();

    return NextResponse.json({
      success: true,
      screening,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('[Screening Error]', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Screening failed',
        code: 'SCREENING_ERROR'
      },
      { status: 500 }
    );
  }
}
