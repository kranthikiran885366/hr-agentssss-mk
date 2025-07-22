import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const { userId, services } = await request.json()

    console.log(`Creating accounts for user ${userId}:`, services)

    const accounts = []

    for (const service of services) {
      // Simulate account creation time
      await new Promise((resolve) => setTimeout(resolve, 1500))

      // Mock account creation (95% success rate)
      const isSuccessful = Math.random() > 0.05

      accounts.push({
        service,
        status: isSuccessful ? "created" : "failed",
        credentials: isSuccessful
          ? {
              username: `user.${userId}`,
              email: `user.${userId}@company.com`,
              tempPassword: "TempPass123!",
            }
          : null,
        createdAt: new Date().toISOString(),
      })
    }

    return NextResponse.json({
      success: true,
      accounts,
      message: "Account creation process completed",
    })
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        message: "Account creation failed",
      },
      { status: 500 },
    )
  }
}
