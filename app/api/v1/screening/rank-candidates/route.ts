import { NextRequest, NextResponse } from 'next/server';

/**
 * POST /api/v1/screening/rank-candidates
 * Rank multiple candidates against a job
 */
export async function POST(request: NextRequest) {
  try {
    const { candidates, jobRequirements, topN = 10 } = await request.json();

    if (!candidates || !Array.isArray(candidates) || candidates.length === 0) {
      return NextResponse.json(
        {
          success: false,
          error: 'Valid candidates array required',
          code: 'INVALID_REQUEST'
        },
        { status: 400 }
      );
    }

    if (!jobRequirements) {
      return NextResponse.json(
        {
          success: false,
          error: 'Job requirements are required',
          code: 'INVALID_REQUEST'
        },
        { status: 400 }
      );
    }

    // Call Python backend ranking service
    const response = await fetch(
      `${process.env.PYTHON_API_URL || 'http://localhost:8000'}/api/v1/screening/rank-candidates`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.API_SECRET_KEY || ''}`
        },
        body: JSON.stringify({
          candidates,
          jobRequirements,
          topN
        })
      }
    );

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const ranking = await response.json();

    return NextResponse.json({
      success: true,
      ranking,
      candidatesProcessed: candidates.length,
      topCandidatesReturned: ranking.ranked_candidates?.length || 0,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('[Ranking Error]', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Ranking failed',
        code: 'RANKING_ERROR'
      },
      { status: 500 }
    );
  }
}
