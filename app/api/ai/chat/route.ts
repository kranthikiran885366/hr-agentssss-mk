import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const { message, context } = await request.json()

    // Simulate AI processing time
    await new Promise((resolve) => setTimeout(resolve, 1000 + Math.random() * 2000))

    // Generate contextual responses based on the message
    let response = ""

    if (message.toLowerCase().includes("experience")) {
      response =
        "That's great experience! Can you tell me more about the specific technologies you worked with and any challenges you overcame in your previous role?"
    } else if (message.toLowerCase().includes("project")) {
      response =
        "Interesting project! What was your role in the team, and how did you handle any technical challenges that arose during development?"
    } else if (message.toLowerCase().includes("team")) {
      response =
        "Team collaboration is crucial. Can you share an example of how you resolved a conflict or disagreement within your team?"
    } else if (message.toLowerCase().includes("future") || message.toLowerCase().includes("years")) {
      response =
        "That's a thoughtful career vision. How do you plan to develop the skills needed to achieve those goals, and what attracts you to that direction?"
    } else {
      response =
        "Thank you for that response. I can see you have good communication skills. Let me ask you about a specific scenario..."
    }

    // Add follow-up question based on context
    if (context?.questionNumber < 5) {
      response += " This gives me good insight into your background."
    }

    return NextResponse.json({
      response,
      score: Math.floor(Math.random() * 30) + 70, // 70-100
      analysis: {
        communication: Math.floor(Math.random() * 30) + 70,
        technical_depth: Math.floor(Math.random() * 30) + 70,
        cultural_fit: Math.floor(Math.random() * 30) + 70,
      },
    })
  } catch (error) {
    return NextResponse.json({ error: "Failed to process AI request" }, { status: 500 })
  }
}
