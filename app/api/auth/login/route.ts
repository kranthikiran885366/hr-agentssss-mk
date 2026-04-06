import { NextRequest, NextResponse } from "next/server"
import { authenticateUser } from "@/lib/auth"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email, password } = body

    if (!email || !password) {
      return NextResponse.json(
        { success: false, message: "Email and password are required" },
        { status: 400 }
      )
    }

    const user = await authenticateUser(email, password)

    if (user) {
      return NextResponse.json({
        success: true,
        user: {
          id: (user as any).id,
          name: (user as any).name,
          email: (user as any).email,
          role: (user as any).role,
        },
        message: "Login successful",
      })
    } else {
      return NextResponse.json(
        {
          success: false,
          message: "Invalid email or password",
        },
        { status: 401 }
      )
    }
  } catch (error) {
    console.error("Login error:", error)
    return NextResponse.json(
      {
        success: false,
        message: "Server error during login",
      },
      { status: 500 }
    )
  }
}
