import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    endpoints: [
      { path: '/api/performance/goals', methods: ['GET', 'POST'] },
      { path: '/api/performance/goals/[id]', methods: ['GET', 'PUT', 'DELETE'] },
      { path: '/api/performance/reviews', methods: ['GET', 'POST'] },
      { path: '/api/performance/reviews/[id]', methods: ['GET', 'PUT'] },
      { path: '/api/performance/analytics', methods: ['GET'] },
    ],
  });
}
