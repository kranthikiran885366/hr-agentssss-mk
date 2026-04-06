import { NextRequest, NextResponse } from 'next/server';

/**
 * POST /api/v1/interviews/submit-response
 * Submit a candidate response during an interview
 */
export async function POST(request: NextRequest) {
  try {
    const {
      sessionId,
      responseText,
      responseTimeSeconds = 0,
      isVoice = false
    } = await request.json();

    if (!sessionId || !responseText) {
      return NextResponse.json(
        {
          success: false,
          error: 'Session ID and response text are required',
          code: 'INVALID_REQUEST'
        },
        { status: 400 }
      );
    }

    // Call Python backend to evaluate response
    const response = await fetch(
      `${process.env.PYTHON_API_URL || 'http://localhost:8000'}/api/v1/interviews/submit-response`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.API_SECRET_KEY || ''}`
        },
        body: JSON.stringify({
          session_id: sessionId,
          response_text: responseText,
          response_time_seconds: responseTimeSeconds,
          is_voice: isVoice
        })
      }
    );

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const result = await response.json();

    return NextResponse.json({
      success: true,
      evaluation: result.evaluation,
      nextQuestion: result.next_question,
      sessionStatus: result.session_status,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('[Response Submission Error]', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to submit response',
        code: 'SUBMISSION_ERROR'
      },
      { status: 500 }
    );
  }
}
