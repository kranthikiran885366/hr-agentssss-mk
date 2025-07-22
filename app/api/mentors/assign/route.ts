import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const { userId, preferences } = await request.json()

    console.log(`Assigning mentor for user ${userId} with preferences:`, preferences)

    // Mock mentor matching
    const mentors = [
      {
        id: "1",
        name: "Sarah Johnson",
        role: "Senior Software Engineer",
        department: "Engineering",
        experience: 8,
        skills: ["React", "Node.js", "Python", "Team Leadership"],
        rating: 4.9,
        availability: "Available",
      },
      {
        id: "2",
        name: "Michael Chen",
        role: "Product Manager",
        department: "Product",
        experience: 6,
        skills: ["Product Strategy", "Agile", "Data Analysis"],
        rating: 4.8,
        availability: "Available",
      },
    ]

    // Simulate matching algorithm
    await new Promise((resolve) => setTimeout(resolve, 3000))

    const assignedMentor = mentors[Math.floor(Math.random() * mentors.length)]

    return NextResponse.json({
      success: true,
      mentor: assignedMentor,
      message: "Mentor assigned successfully",
      assignedAt: new Date().toISOString(),
    })
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        message: "Mentor assignment failed",
      },
      { status: 500 },
    )
  }
}
